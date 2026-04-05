from unittest.mock import patch, MagicMock
from django.test import TestCase
from rest_framework.test import APIClient
from stores.models import Store, Page


class AIViewsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.store = Store.objects.create(
            name="Test Store",
            shopify_url="test-store.myshopify.com",
            access_token="shpat_test123",
        )
        self.page = Page.objects.create(
            store=self.store,
            shopify_id="gid://shopify/Product/123",
            url="/products/test",
            page_type="product",
            title="Test Product",
            meta_description="A test product",
        )

    @patch("ai_engine.views.AIClient")
    def test_generate_meta(self, mock_ai_cls):
        mock_ai = MagicMock()
        mock_ai.generate_meta_tags.return_value = {
            "title": "Best Test Product | Free Shipping",
            "description": "Shop our test product today. Great quality, fast delivery.",
        }
        mock_ai_cls.return_value = mock_ai

        response = self.client.post("/api/v1/ai/generate-meta/", {
            "page_id": self.page.id,
            "target_keywords": ["test product", "best test"],
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("title", response.data)

    @patch("ai_engine.views.AIClient")
    def test_generate_alt_text(self, mock_ai_cls):
        mock_ai = MagicMock()
        mock_ai.generate_alt_text.return_value = "Red test product in studio setting"
        mock_ai_cls.return_value = mock_ai

        response = self.client.post("/api/v1/ai/generate-alt/", {
            "page_id": self.page.id,
        }, format="json")
        self.assertEqual(response.status_code, 200)

    @patch("ai_engine.views.AIClient")
    def test_score_content(self, mock_ai_cls):
        mock_ai = MagicMock()
        mock_ai.score_content.return_value = {
            "score": 65,
            "recommendations": ["Add keyword to H1"],
        }
        mock_ai_cls.return_value = mock_ai

        response = self.client.post("/api/v1/ai/score-content/", {
            "page_id": self.page.id,
            "target_keywords": ["test product"],
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["score"], 65)
