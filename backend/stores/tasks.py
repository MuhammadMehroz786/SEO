import logging
from celery import shared_task
from django.utils import timezone
from requests.exceptions import RequestException
from .models import Store, Page, Image
from .shopify_client import ShopifyClient

logger = logging.getLogger(__name__)


@shared_task(autoretry_for=(RequestException,), retry_backoff=60, retry_kwargs={"max_retries": 3})
def sync_store(store_id: int):
    store = Store.objects.get(id=store_id)
    client = ShopifyClient(store.shopify_url, store.access_token)

    # Sync products
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

    # Sync collections
    collections = client.get_collections()
    for collection in collections:
        Page.objects.update_or_create(
            store=store,
            shopify_id=str(collection["id"]),
            defaults={
                "url": f"/collections/{collection.get('handle', '')}",
                "page_type": "collection",
                "title": collection.get("title", ""),
                "meta_description": collection.get("body_html", "")[:500] if collection.get("body_html") else "",
            },
        )

    # Sync static pages
    pages = client.get_pages()
    for sp in pages:
        Page.objects.update_or_create(
            store=store,
            shopify_id=str(sp["id"]),
            defaults={
                "url": f"/pages/{sp.get('handle', '')}",
                "page_type": "page",
                "title": sp.get("title", ""),
                "meta_description": sp.get("body_html", "")[:500] if sp.get("body_html") else "",
            },
        )

    store.last_crawl_date = timezone.now()
    store.save(update_fields=["last_crawl_date"])
    logger.info("Synced store %s: %d products, %d collections, %d pages",
                store.name, len(products), len(collections), len(pages))


@shared_task
def sync_all_stores():
    for store in Store.objects.all():
        sync_store.delay(store.id)
