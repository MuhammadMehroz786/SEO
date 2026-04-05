from unittest.mock import patch, MagicMock
from django.test import TestCase
from ai_engine.client import AIClient


class AIClientTest(TestCase):
    @patch("ai_engine.client.anthropic.Anthropic")
    def test_generate_meta_tags(self, mock_anthropic_cls):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='{"title": "Best Running Shoes | Free Shipping", "description": "Shop the best running shoes with free shipping. Top brands, great prices."}')]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_cls.return_value = mock_client

        ai = AIClient()
        result = ai.generate_meta_tags(
            product_title="Running Shoes",
            product_description="Great shoes for running",
            target_keywords=["running shoes", "best running shoes"],
        )
        self.assertIn("title", result)
        self.assertIn("description", result)

    @patch("ai_engine.client.anthropic.Anthropic")
    def test_generate_alt_text(self, mock_anthropic_cls):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Red leather running shoes with white sole, side view")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_cls.return_value = mock_client

        ai = AIClient()
        result = ai.generate_alt_text(
            product_title="Red Running Shoes",
            image_context="product photo",
        )
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    @patch("ai_engine.client.anthropic.Anthropic")
    def test_score_content(self, mock_anthropic_cls):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='{"score": 65, "recommendations": ["Add target keyword to H1", "Increase content length to 500+ words"]}')]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_cls.return_value = mock_client

        ai = AIClient()
        result = ai.score_content(
            page_title="Shoes",
            page_content="Buy shoes here.",
            target_keywords=["running shoes"],
        )
        self.assertIn("score", result)
        self.assertIn("recommendations", result)
