from django.test import TestCase
from stores.models import Store, Page
from audits.models import AuditRun, AuditIssue


class AuditModelTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(
            name="Test Store",
            shopify_url="test-store.myshopify.com",
            access_token="shpat_test123",
        )

    def test_create_audit_run(self):
        run = AuditRun.objects.create(
            store=self.store,
            status="completed",
            pages_crawled=50,
            issues_found=12,
        )
        self.assertEqual(run.store, self.store)
        self.assertEqual(run.status, "completed")

    def test_create_audit_issue(self):
        run = AuditRun.objects.create(store=self.store, status="completed")
        page = Page.objects.create(
            store=self.store,
            shopify_id="gid://shopify/Product/1",
            url="/products/test",
            page_type="product",
            title="Test",
        )
        issue = AuditIssue.objects.create(
            audit_run=run,
            page=page,
            issue_type="missing_meta_description",
            severity="warning",
            description="Page is missing a meta description",
            fix_suggestion="Add a compelling meta description of 150-160 characters",
        )
        self.assertEqual(issue.severity, "warning")
        self.assertEqual(run.issues.count(), 1)
