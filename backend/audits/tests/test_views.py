from django.test import TestCase
from rest_framework.test import APIClient
from stores.models import Store
from audits.models import AuditRun, AuditIssue


class AuditViewsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.store = Store.objects.create(
            name="Test Store",
            shopify_url="test-store.myshopify.com",
            access_token="shpat_test123",
        )

    def test_list_audit_runs(self):
        AuditRun.objects.create(store=self.store, status="completed", pages_crawled=10, issues_found=3)
        response = self.client.get(f"/api/v1/audits/runs/?store={self.store.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["status"], "completed")
