from django.test import TestCase
from stores.models import Store, Page, Image
from keywords.models import Keyword, RankHistory
from audits.models import AuditRun, AuditIssue
from dashboard.tasks import calculate_seo_score
from django.utils import timezone


class SEOScoreTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(
            name="Test Store",
            shopify_url="test-store.myshopify.com",
            access_token="shpat_test123",
        )

    def test_perfect_score_no_issues(self):
        for i in range(5):
            Page.objects.create(
                store=self.store,
                shopify_id=f"gid://shopify/Product/{i}",
                url=f"/products/product-{i}",
                page_type="product",
                title=f"Great Product {i} Title Here",
                meta_description=f"A compelling meta description for product {i} that is the right length.",
                h1=f"Great Product {i}",
            )
        audit = AuditRun.objects.create(store=self.store, status="completed", issues_found=0)
        kw = Keyword.objects.create(store=self.store, keyword="test", search_volume=1000)
        RankHistory.objects.create(keyword=kw, date=timezone.now().date(), position=5)

        score = calculate_seo_score(self.store.id)
        self.assertGreater(score, 70)

    def test_low_score_many_issues(self):
        page = Page.objects.create(
            store=self.store,
            shopify_id="gid://shopify/Product/1",
            url="/products/bad",
            page_type="product",
            title="",
            meta_description="",
        )
        audit = AuditRun.objects.create(store=self.store, status="completed", issues_found=5)
        for i in range(5):
            AuditIssue.objects.create(
                audit_run=audit, page=page,
                issue_type="missing_title", severity="critical",
                description="Missing title",
            )

        score = calculate_seo_score(self.store.id)
        self.assertLess(score, 50)
