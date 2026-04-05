from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("", views.StoreViewSet, basename="store")

urlpatterns = [
    path("", include(router.urls)),
    path("<int:store_pk>/pages/", views.PageViewSet.as_view({"get": "list", "post": "create"}), name="store-pages"),
]
