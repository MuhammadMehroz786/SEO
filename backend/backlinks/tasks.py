import logging
from celery import shared_task
from django.utils import timezone
from requests.exceptions import RequestException

from .dataforseo_client import BacklinksClient
from .ai_client import BacklinksAIClient

logger = logging.getLogger(__name__)


@shared_task(autoretry_for=(RequestException,), retry_backoff=60, retry_kwargs={"max_retries": 3})
def refresh_backlinks(store_id: int):
    from stores.models import Store
    from .models import Backlink, BacklinkSnapshot

    try:
        store = Store.objects.get(id=store_id)
    except Store.DoesNotExist:
        logger.warning("Store %s not found", store_id)
        return

    domain = store.shopify_url
    client = BacklinksClient()

    try:
        api_backlinks = client.get_backlinks(domain)
    except RequestException as e:
        logger.error("DataForSEO backlinks fetch failed for store %s: %s", store_id, e)
        raise

    today = timezone.now().date()
    api_keys = {(b["source_url"], b["target_url"]) for b in api_backlinks}
    existing = list(Backlink.objects.filter(store=store, is_lost=False))
    existing_keys = {(b.source_url, b.target_url) for b in existing}

    # Mark lost
    lost_count = 0
    for bl in existing:
        if (bl.source_url, bl.target_url) not in api_keys:
            bl.is_lost = True
            bl.save(update_fields=["is_lost", "updated_at"])
            lost_count += 1

    # Create new / update existing
    new_count = 0
    for item in api_backlinks:
        key = (item["source_url"], item["target_url"])
        if key not in existing_keys:
            Backlink.objects.create(store=store, **item)
            new_count += 1
        else:
            Backlink.objects.filter(
                store=store,
                source_url=item["source_url"],
                target_url=item["target_url"],
            ).update(
                last_seen=item["last_seen"],
                domain_rank=item["domain_rank"],
                is_lost=False,
            )

    total = Backlink.objects.filter(store=store, is_lost=False).count()
    dofollow = Backlink.objects.filter(store=store, is_lost=False, is_dofollow=True).count()

    BacklinkSnapshot.objects.update_or_create(
        store=store,
        date=today,
        defaults={
            "total_count": total,
            "dofollow_count": dofollow,
            "lost_count": lost_count,
            "new_count": new_count,
        },
    )
    logger.info("Refreshed backlinks for %s: %d total, %d new, %d lost", store.name, total, new_count, lost_count)


@shared_task
def refresh_all_backlinks():
    from stores.models import Store
    for store in Store.objects.all():
        refresh_backlinks.delay(store.id)


@shared_task
def suggest_prospects(store_id: int):
    from stores.models import Store
    from keywords.models import Keyword
    from .models import OutreachProspect

    try:
        store = Store.objects.get(id=store_id)
    except Store.DoesNotExist:
        logger.warning("Store %s not found", store_id)
        return

    domain = store.shopify_url
    keywords = list(
        Keyword.objects.filter(store=store, is_tracked=True).values_list("keyword", flat=True)[:20]
    )

    client = BacklinksClient()
    try:
        prospects = client.suggest_prospects(domain, keywords)
    except RequestException as e:
        logger.error("DataForSEO prospect suggestion failed for store %s: %s", store_id, e)
        return

    ai = BacklinksAIClient()
    store_keywords = keywords[:10]

    for p in prospects:
        domain_name = p["domain"]
        prospect_url = f"https://{domain_name}"

        if OutreachProspect.objects.filter(store=store, website_url=prospect_url).exists():
            continue

        try:
            relevance = ai.score_relevance(
                prospect_url=prospect_url,
                store_name=store.name,
                store_keywords=store_keywords,
            )
            score = relevance.get("score", 0)
        except Exception as e:
            logger.warning("AI scoring failed for %s: %s", prospect_url, e)
            score = 0

        OutreachProspect.objects.create(
            store=store,
            website_url=prospect_url,
            domain_rank=p["domain_rank"],
            niche_relevance_score=score,
            source="auto_suggested",
            status="new",
        )

    logger.info("Suggested %d prospects for %s", len(prospects), store.name)
