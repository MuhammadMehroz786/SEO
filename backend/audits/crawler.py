import logging
from audits.models import AuditIssue
from stores.models import Page
from .pagespeed_client import PageSpeedClient

logger = logging.getLogger(__name__)


class SiteAuditor:
    def __init__(self, store, audit_run):
        self.store = store
        self.audit_run = audit_run

    def check_page(self, page: Page) -> list:
        issues = []

        # Missing title
        if not page.title.strip():
            issues.append(AuditIssue(
                audit_run=self.audit_run, page=page,
                issue_type="missing_title", severity="critical",
                description=f"Page {page.url} has no title tag",
                fix_suggestion="Add a descriptive title of 50-60 characters including your target keyword",
            ))

        # Title too long
        elif len(page.title) > 60:
            issues.append(AuditIssue(
                audit_run=self.audit_run, page=page,
                issue_type="title_too_long", severity="warning",
                description=f"Title is {len(page.title)} chars (max 60): {page.title[:80]}...",
                fix_suggestion="Shorten the title to 50-60 characters",
            ))

        # Title too short
        elif len(page.title) < 20:
            issues.append(AuditIssue(
                audit_run=self.audit_run, page=page,
                issue_type="title_too_short", severity="warning",
                description=f"Title is only {len(page.title)} chars: {page.title}",
                fix_suggestion="Expand the title to 50-60 characters with relevant keywords",
            ))

        # Missing meta description
        if not page.meta_description.strip():
            issues.append(AuditIssue(
                audit_run=self.audit_run, page=page,
                issue_type="missing_meta_description", severity="warning",
                description=f"Page {page.url} has no meta description",
                fix_suggestion="Add a compelling meta description of 150-160 characters",
            ))

        # Meta description too long
        elif len(page.meta_description) > 160:
            issues.append(AuditIssue(
                audit_run=self.audit_run, page=page,
                issue_type="meta_desc_too_long", severity="info",
                description=f"Meta description is {len(page.meta_description)} chars (max 160)",
                fix_suggestion="Shorten to 150-160 characters to prevent truncation in search results",
            ))

        # Missing H1
        if not page.h1.strip():
            issues.append(AuditIssue(
                audit_run=self.audit_run, page=page,
                issue_type="missing_h1", severity="warning",
                description=f"Page {page.url} has no H1 heading",
                fix_suggestion="Add an H1 that includes your primary keyword",
            ))

        # Missing alt text on images
        for image in page.images.all():
            if not image.alt_text.strip():
                issues.append(AuditIssue(
                    audit_run=self.audit_run, page=page,
                    issue_type="missing_alt_text", severity="warning",
                    description=f"Image {image.src} on {page.url} has no alt text",
                    fix_suggestion="Add descriptive alt text that describes the image content",
                ))

        # Save all issues
        AuditIssue.objects.bulk_create(issues)
        return issues

    def check_duplicates(self) -> list:
        issues = []
        pages = Page.objects.filter(store=self.store)

        # Duplicate titles
        titles = {}
        for page in pages:
            if page.title.strip():
                titles.setdefault(page.title, []).append(page)
        for title, pages_with_title in titles.items():
            if len(pages_with_title) > 1:
                for page in pages_with_title:
                    issues.append(AuditIssue(
                        audit_run=self.audit_run, page=page,
                        issue_type="duplicate_title", severity="warning",
                        description=f"Title '{title}' is used on {len(pages_with_title)} pages",
                        fix_suggestion="Create unique titles for each page",
                    ))

        # Duplicate meta descriptions
        descs = {}
        for page in Page.objects.filter(store=self.store):
            if page.meta_description.strip():
                descs.setdefault(page.meta_description, []).append(page)
        for desc, pages_with_desc in descs.items():
            if len(pages_with_desc) > 1:
                for page in pages_with_desc:
                    issues.append(AuditIssue(
                        audit_run=self.audit_run, page=page,
                        issue_type="duplicate_meta_description", severity="info",
                        description=f"Meta description is duplicated across {len(pages_with_desc)} pages",
                        fix_suggestion="Write unique meta descriptions for each page",
                    ))

        AuditIssue.objects.bulk_create(issues)
        return issues

    def check_page_speed(self, page: Page) -> list:
        """Check page speed using PageSpeed Insights API."""
        issues = []
        store_url = self.store.shopify_url
        if not store_url.startswith("http"):
            full_url = f"https://{store_url}{page.url}"
        else:
            full_url = f"{store_url}{page.url}"

        try:
            client = PageSpeedClient()
            result = client.analyze(full_url)
            score = result.get("performance_score")
            if score is not None and score < 50:
                issues.append(AuditIssue(
                    audit_run=self.audit_run, page=page,
                    issue_type="slow_page", severity="warning",
                    description=f"Page performance score is {score}/100 (LCP: {result.get('lcp', 'N/A')}ms)",
                    fix_suggestion="Optimize images, reduce JavaScript, enable caching",
                ))
        except Exception:
            logger.warning("PageSpeed check failed for %s", full_url)

        if issues:
            AuditIssue.objects.bulk_create(issues)
        return issues

    def run_full_audit(self) -> int:
        total_issues = 0
        pages = Page.objects.filter(store=self.store).prefetch_related("images")

        for page in pages:
            issues = self.check_page(page)
            total_issues += len(issues)

        dup_issues = self.check_duplicates()
        total_issues += len(dup_issues)

        # Check page speed for up to 10 pages (API is rate-limited)
        for page in pages[:10]:
            speed_issues = self.check_page_speed(page)
            total_issues += len(speed_issues)

        return total_issues
