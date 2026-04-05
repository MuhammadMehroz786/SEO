from django.test import TestCase
from django.utils import timezone
from stores.models import Store
from keywords.models import Keyword, RankHistory


class KeywordModelTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(
            name="Test Store",
            shopify_url="test-store.myshopify.com",
            access_token="shpat_test123",
        )

    def test_create_keyword(self):
        kw = Keyword.objects.create(
            store=self.store,
            keyword="buy shoes online",
            search_volume=5000,
            difficulty=45,
            cpc=1.20,
            intent="transactional",
        )
        self.assertEqual(kw.keyword, "buy shoes online")
        self.assertTrue(kw.is_tracked)

    def test_rank_history(self):
        kw = Keyword.objects.create(
            store=self.store,
            keyword="buy shoes online",
            search_volume=5000,
        )
        rh = RankHistory.objects.create(
            keyword=kw,
            date=timezone.now().date(),
            position=15,
        )
        self.assertEqual(rh.keyword, kw)
        self.assertEqual(rh.position, 15)
        self.assertEqual(kw.rank_history.count(), 1)

    def test_keyword_str(self):
        kw = Keyword.objects.create(
            store=self.store,
            keyword="red sneakers",
            search_volume=1200,
        )
        self.assertEqual(str(kw), "red sneakers (Test Store)")
