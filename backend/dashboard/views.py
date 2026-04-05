from rest_framework.decorators import api_view
from rest_framework.response import Response
from stores.models import Store, Page
from keywords.models import Keyword, RankHistory
from audits.models import AuditRun


@api_view(["GET"])
def dashboard_overview(request):
    stores = Store.objects.all()
    store_data = []
    for store in stores:
        latest_audit = store.audit_runs.first()
        store_data.append({
            "id": store.id,
            "name": store.name,
            "shopify_url": store.shopify_url,
            "seo_score": store.seo_score,
            "pages_count": store.pages.count(),
            "keywords_count": store.keywords.count(),
            "last_crawl_date": store.last_crawl_date,
            "issues_count": latest_audit.issues_found if latest_audit else 0,
        })

    return Response({
        "total_stores": stores.count(),
        "total_pages": Page.objects.count(),
        "total_keywords": Keyword.objects.count(),
        "stores": store_data,
    })


@api_view(["GET"])
def store_dashboard(request, store_id):
    store = Store.objects.get(id=store_id)

    # Top keywords by position
    tracked_keywords = Keyword.objects.filter(store=store, is_tracked=True)[:10]
    top_keywords = []
    for kw in tracked_keywords:
        latest = kw.rank_history.first()
        top_keywords.append({
            "keyword": kw.keyword,
            "search_volume": kw.search_volume,
            "position": latest.position if latest else None,
        })

    # Recent audit
    recent_audit = store.audit_runs.first()
    audit_data = None
    if recent_audit:
        audit_data = {
            "id": recent_audit.id,
            "status": recent_audit.status,
            "started_at": recent_audit.started_at,
            "pages_crawled": recent_audit.pages_crawled,
            "issues_found": recent_audit.issues_found,
            "critical": recent_audit.issues.filter(severity="critical").count(),
            "warnings": recent_audit.issues.filter(severity="warning").count(),
        }

    return Response({
        "store": {
            "id": store.id,
            "name": store.name,
            "shopify_url": store.shopify_url,
            "seo_score": store.seo_score,
        },
        "pages_count": store.pages.count(),
        "keywords_count": store.keywords.count(),
        "top_keywords": top_keywords,
        "recent_audit": audit_data,
    })
