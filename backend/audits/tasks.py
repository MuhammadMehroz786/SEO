import logging
from celery import shared_task
from django.utils import timezone
from stores.models import Store
from .models import AuditRun
from .crawler import SiteAuditor

logger = logging.getLogger(__name__)


@shared_task(autoretry_for=(Exception,), retry_backoff=120, retry_kwargs={"max_retries": 2})
def run_site_audit(store_id: int):
    store = Store.objects.get(id=store_id)
    audit_run = AuditRun.objects.create(store=store, status="running")

    try:
        auditor = SiteAuditor(store, audit_run)
        total_issues = auditor.run_full_audit()

        pages_count = store.pages.count()
        audit_run.status = "completed"
        audit_run.completed_at = timezone.now()
        audit_run.pages_crawled = pages_count
        audit_run.issues_found = total_issues
        audit_run.save()

        store.last_crawl_date = timezone.now()
        store.save(update_fields=["last_crawl_date"])
        logger.info("Audit completed for %s: %d pages, %d issues",
                     store.name, pages_count, total_issues)
    except Exception:
        audit_run.status = "failed"
        audit_run.save(update_fields=["status"])
        logger.exception("Audit failed for store %s", store.name)
        raise


@shared_task
def audit_all_stores():
    for store in Store.objects.all():
        run_site_audit.delay(store.id)
