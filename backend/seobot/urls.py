from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/stores/", include("stores.urls")),
    path("api/v1/keywords/", include("keywords.urls")),
    path("api/v1/audits/", include("audits.urls")),
    path("api/v1/ai/", include("ai_engine.urls")),
    path("api/v1/dashboard/", include("dashboard.urls")),
    path("api/v1/backlinks/", include("backlinks.urls")),
]
