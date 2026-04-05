from django.test import TestCase
from rest_framework.test import APIClient
from stores.models import Store


class StoreAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.store = Store.objects.create(
            name="Test Store",
            shopify_url="test-store.myshopify.com",
            access_token="shpat_test123",
        )

    def test_list_stores(self):
        response = self.client.get("/api/v1/stores/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    def test_create_store(self):
        response = self.client.post("/api/v1/stores/", {
            "name": "New Store",
            "shopify_url": "new-store.myshopify.com",
            "access_token": "shpat_new123",
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Store.objects.count(), 2)

    def test_soft_delete_store(self):
        response = self.client.delete(f"/api/v1/stores/{self.store.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Store.objects.count(), 0)
        self.assertEqual(Store.all_objects.count(), 1)
