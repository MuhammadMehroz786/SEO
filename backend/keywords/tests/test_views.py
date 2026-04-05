from unittest.mock import patch, MagicMock
from django.test import TestCase
from rest_framework.test import APIClient
from stores.models import Store
from keywords.models import Keyword, RankHistory
from django.utils import timezone


class KeywordAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.store = Store.objects.create(
            name="Test Store",
            shopify_url="test-store.myshopify.com",
            access_token="shpat_test123",
        )
        self.keyword = Keyword.objects.create(
            store=self.store,
            keyword="buy shoes online",
            search_volume=5000,
            difficulty=45,
        )

    def test_list_keywords(self):
        response = self.client.get(f"/api/v1/keywords/?store={self.store.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    def test_create_keyword(self):
        response = self.client.post("/api/v1/keywords/", {
            "store": self.store.id,
            "keyword": "red sneakers",
            "search_volume": 1200,
            "difficulty": 30,
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Keyword.objects.count(), 2)

    def test_rank_history(self):
        RankHistory.objects.create(
            keyword=self.keyword,
            date=timezone.now().date(),
            position=15,
        )
        response = self.client.get(f"/api/v1/keywords/{self.keyword.id}/rank-history/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["position"], 15)

    @patch("keywords.views.DataForSEOClient")
    def test_research_keywords(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client.keyword_research.return_value = [
            {"keyword": "shoes sale", "search_volume": 3000, "difficulty": 40, "cpc": 0.90, "competition_level": "MEDIUM"},
        ]
        mock_client_cls.return_value = mock_client
        response = self.client.post("/api/v1/keywords/research/", {"keyword": "shoes"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["keyword"], "shoes sale")
