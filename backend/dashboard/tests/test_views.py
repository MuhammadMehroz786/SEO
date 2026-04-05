from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from stores.models import Store, Page
from keywords.models import Keyword, RankHistory
from audits.models import AuditRun, AuditIssue


class DashboardAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.store = Store.objects.create(
            name="Test Store",
            shopify_url="test-store.myshopify.com",
            access_token="shpat_test123",
            seo_score=72,
        )
        self.page = Page.objects.create(
            store=self.store,
            shopify_id="gid://shopify/Product/1",
            url="/products/test",
            page_type="product",
            title="Test Product",
            meta_description="Test description",
        )
        self.keyword = Keyword.objects.create(
            store=self.store,
            keyword="test keyword",
            search_volume=1000,
        )
        RankHistory.objects.create(
            keyword=self.keyword,
            date=timezone.now().date(),
            position=15,
        )

    def test_dashboard_overview(self):
        response = self.client.get("/api/v1/dashboard/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["stores"]), 1)
        self.assertEqual(response.data["stores"][0]["name"], "Test Store")
        self.assertEqual(response.data["stores"][0]["seo_score"], 72)
        self.assertIn("total_stores", response.data)
        self.assertIn("total_pages", response.data)
        self.assertIn("total_keywords", response.data)

    def test_store_dashboard(self):
        response = self.client.get(f"/api/v1/dashboard/{self.store.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["store"]["name"], "Test Store")
        self.assertIn("pages_count", response.data)
        self.assertIn("keywords_count", response.data)
        self.assertIn("top_keywords", response.data)
        self.assertIn("recent_audit", response.data)
