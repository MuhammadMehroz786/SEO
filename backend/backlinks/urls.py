from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("prospects", views.OutreachProspectViewSet, basename="prospect")
router.register("campaigns", views.OutreachCampaignViewSet, basename="campaign")
router.register("email-config", views.EmailConfigViewSet, basename="email-config")
router.register("", views.BacklinkViewSet, basename="backlink")

urlpatterns = [
    path("", include(router.urls)),
]
