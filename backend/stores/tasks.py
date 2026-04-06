from celery import shared_task
from django.utils import timezone
from .models import Store, Page, Image
from .shopify_client import ShopifyClient


@shared_task
def sync_store(store_id: int):
    store = Store.objects.get(id=store_id)
    client = ShopifyClient(store.shopify_url, store.access_token)
    products = client.get_products()
    for product in products:
        page, _ = Page.objects.update_or_create(
            store=store,
            shopify_id=str(product["id"]),
            defaults={
                "url": f"/products/{product['handle']}",
                "page_type": "product",
                "title": product.get("title", ""),
                "meta_description": product.get("body_html", "")[:500] if product.get("body_html") else "",
            },
        )
        for image in product.get("images", []):
            Image.objects.update_or_create(
                page=page,
                src=image["src"],
                defaults={"alt_text": image.get("alt", "")},
            )
    store.last_crawl_date = timezone.now()
    store.save(update_fields=["last_crawl_date"])


@shared_task
def sync_all_stores():
    for store in Store.objects.all():
        sync_store.delay(store.id)
