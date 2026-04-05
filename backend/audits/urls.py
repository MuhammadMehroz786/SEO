from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"runs", views.AuditRunViewSet, basename="audit-run")

urlpatterns = [
    path("trigger/", views.trigger_audit, name="trigger-audit"),
    path("", include(router.urls)),
]
