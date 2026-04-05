from celery import shared_task
from django.utils import timezone
from .models import Keyword, RankHistory
from .serp_client import SerpClient


@shared_task
def track_keyword_rankings(store_id: int):
    keywords = Keyword.objects.filter(store_id=store_id, is_tracked=True)
    if not keywords.exists():
        return
    store = keywords.first().store
    domain = store.shopify_url.replace(".myshopify.com", "")
    client = SerpClient()
    today = timezone.now().date()
    for kw in keywords:
        result = client.check_ranking(kw.keyword, domain)
        RankHistory.objects.update_or_create(
            keyword=kw,
            date=today,
            defaults={
                "position": result["position"] or 0,
                "serp_url": result["serp_url"],
                "serp_features": result["serp_features"],
            },
        )


@shared_task
def track_all_rankings():
    from stores.models import Store
    for store in Store.objects.all():
        track_keyword_rankings.delay(store.id)
