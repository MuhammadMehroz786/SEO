from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("", views.StoreViewSet, basename="store")

urlpatterns = [
    path("<int:store_pk>/pages/", views.PageViewSet.as_view({"get": "list", "post": "create"}), name="store-pages"),
    path("<int:store_pk>/pages/<int:pk>/", views.PageViewSet.as_view({"get": "retrieve", "patch": "partial_update"}), name="store-page-detail"),
    path("", include(router.urls)),
]
