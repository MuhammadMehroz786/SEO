from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("", views.KeywordViewSet, basename="keyword")

urlpatterns = [
    path("research/", views.research_keywords, name="keyword-research"),
    path("", include(router.urls)),
]
