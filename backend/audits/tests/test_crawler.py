from django.test import TestCase
from stores.models import Store, Page, Image
from audits.models import AuditRun
from audits.crawler import SiteAuditor


class SiteAuditorTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(
            name="Test Store",
            shopify_url="test-store.myshopify.com",
            access_token="shpat_test123",
        )
        self.audit_run = AuditRun.objects.create(store=self.store, status="running")

    def test_flag_missing_title(self):
        page = Page.objects.create(
            store=self.store,
            shopify_id="gid://shopify/Product/1",
            url="/products/no-title",
            page_type="product",
            title="",
        )
        auditor = SiteAuditor(self.store, self.audit_run)
        issues = auditor.check_page(page)
        issue_types = [i.issue_type for i in issues]
        self.assertIn("missing_title", issue_types)

    def test_flag_missing_meta_description(self):
        page = Page.objects.create(
            store=self.store,
            shopify_id="gid://shopify/Product/2",
            url="/products/no-desc",
            page_type="product",
            title="Has Title",
            meta_description="",
        )
        auditor = SiteAuditor(self.store, self.audit_run)
        issues = auditor.check_page(page)
        issue_types = [i.issue_type for i in issues]
        self.assertIn("missing_meta_description", issue_types)

    def test_flag_title_too_long(self):
        page = Page.objects.create(
            store=self.store,
            shopify_id="gid://shopify/Product/3",
            url="/products/long-title",
            page_type="product",
            title="A" * 70,
            meta_description="Good description here for this product page.",
        )
        auditor = SiteAuditor(self.store, self.audit_run)
        issues = auditor.check_page(page)
        issue_types = [i.issue_type for i in issues]
        self.assertIn("title_too_long", issue_types)

    def test_flag_missing_alt_text(self):
        page = Page.objects.create(
            store=self.store,
            shopify_id="gid://shopify/Product/4",
            url="/products/no-alt",
            page_type="product",
            title="Product",
            meta_description="Description",
        )
        Image.objects.create(page=page, src="https://cdn.shopify.com/img.jpg", alt_text="")
        auditor = SiteAuditor(self.store, self.audit_run)
        issues = auditor.check_page(page)
        issue_types = [i.issue_type for i in issues]
        self.assertIn("missing_alt_text", issue_types)

    def test_no_issues_for_good_page(self):
        page = Page.objects.create(
            store=self.store,
            shopify_id="gid://shopify/Product/5",
            url="/products/good",
            page_type="product",
            title="Great Product Title Here",
            meta_description="A compelling meta description that is the right length for SEO purposes and Google display.",
            h1="Great Product Title Here",
        )
        auditor = SiteAuditor(self.store, self.audit_run)
        issues = auditor.check_page(page)
        self.assertEqual(len(issues), 0)

    def test_detect_duplicate_titles(self):
        Page.objects.create(
            store=self.store, shopify_id="gid://shopify/Product/6",
            url="/products/dup1", page_type="product",
            title="Same Title", meta_description="Desc 1",
        )
        Page.objects.create(
            store=self.store, shopify_id="gid://shopify/Product/7",
            url="/products/dup2", page_type="product",
            title="Same Title", meta_description="Desc 2",
        )
        auditor = SiteAuditor(self.store, self.audit_run)
        issues = auditor.check_duplicates()
        issue_types = [i.issue_type for i in issues]
        self.assertIn("duplicate_title", issue_types)
