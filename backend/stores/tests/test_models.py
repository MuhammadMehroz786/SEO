from django.test import TestCase
from stores.models import Store, Page, Image


class StoreModelTest(TestCase):
    def test_create_store(self):
        store = Store.objects.create(
            name="Test Store",
            shopify_url="test-store.myshopify.com",
            access_token="shpat_test123",
        )
        self.assertEqual(store.name, "Test Store")
        self.assertEqual(store.seo_score, 0)
        self.assertFalse(store.is_deleted)

    def test_soft_delete(self):
        store = Store.objects.create(
            name="Test Store",
            shopify_url="test-store.myshopify.com",
            access_token="shpat_test123",
        )
        store.soft_delete()
        self.assertTrue(store.is_deleted)
        self.assertEqual(Store.objects.count(), 0)
        self.assertEqual(Store.all_objects.count(), 1)

    def test_create_page(self):
        store = Store.objects.create(
            name="Test Store",
            shopify_url="test-store.myshopify.com",
            access_token="shpat_test123",
        )
        page = Page.objects.create(
            store=store,
            shopify_id="gid://shopify/Product/123",
            url="/products/test",
            page_type="product",
            title="Test Product",
        )
        self.assertEqual(page.store, store)
        self.assertEqual(store.pages.count(), 1)
