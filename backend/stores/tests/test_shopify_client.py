from unittest.mock import patch, MagicMock
from django.test import TestCase
from stores.shopify_client import ShopifyClient


class ShopifyClientTest(TestCase):
    def setUp(self):
        self.client = ShopifyClient("test-store.myshopify.com", "shpat_test123")

    @patch("stores.shopify_client.requests.get")
    def test_get_products(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "products": [
                {"id": "123", "title": "Test Product", "handle": "test-product", "images": []},
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        products = self.client.get_products()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]["title"], "Test Product")

    @patch("stores.shopify_client.requests.get")
    def test_get_collections(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "custom_collections": [
                {"id": "456", "title": "Test Collection"},
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        collections = self.client.get_collections()
        self.assertEqual(len(collections), 1)
