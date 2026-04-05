from celery import shared_task
from stores.models import Store
from keywords.models import Keyword
from audits.models import AuditRun


@shared_task
def calculate_seo_score(store_id: int) -> int:
    store = Store.objects.get(id=store_id)
    score = 100

    # Factor 1: Audit issues (up to -40 points)
    latest_audit = store.audit_runs.filter(status="completed").first()
    if latest_audit:
        critical = latest_audit.issues.filter(severity="critical").count()
        warnings = latest_audit.issues.filter(severity="warning").count()
        pages = store.pages.count() or 1
        issue_ratio = (critical * 3 + warnings) / pages
        score -= min(40, int(issue_ratio * 20))
    else:
        score -= 20  # No audit run yet

    # Factor 2: Meta tag coverage (up to -30 points)
    total_pages = store.pages.count()
    if total_pages > 0:
        missing_title = store.pages.filter(title="").count()
        missing_desc = store.pages.filter(meta_description="").count()
        coverage = 1 - ((missing_title + missing_desc) / (total_pages * 2))
        score -= int((1 - coverage) * 30)
    else:
        score -= 15

    # Factor 3: Keyword rankings (up to -30 points)
    tracked = Keyword.objects.filter(store=store, is_tracked=True)
    if tracked.exists():
        ranked = 0
        top_10 = 0
        for kw in tracked:
            latest = kw.rank_history.first()
            if latest and latest.position > 0:
                ranked += 1
                if latest.position <= 10:
                    top_10 += 1
        if tracked.count() > 0:
            rank_ratio = ranked / tracked.count()
            top_ratio = top_10 / tracked.count() if ranked > 0 else 0
            score -= int((1 - rank_ratio) * 15)
            score -= int((1 - top_ratio) * 15)
    # No penalty if no keywords tracked yet

    score = max(0, min(100, score))
    store.seo_score = score
    store.save(update_fields=["seo_score"])
    return score


@shared_task
def recalculate_all_scores():
    for store in Store.objects.all():
        calculate_seo_score.delay(store.id)
