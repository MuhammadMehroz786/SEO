from celery import shared_task
from django.utils import timezone
from stores.models import Store
from .models import AuditRun
from .crawler import SiteAuditor


@shared_task
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

        # Update store last crawl date
        store.last_crawl_date = timezone.now()
        store.save(update_fields=["last_crawl_date"])
    except Exception as e:
        audit_run.status = "failed"
        audit_run.save(update_fields=["status"])
        raise


@shared_task
def audit_all_stores():
    for store in Store.objects.all():
        run_site_audit.delay(store.id)
