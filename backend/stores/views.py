from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Store, Page
from .serializers import (
    StoreListSerializer,
    StoreCreateSerializer,
    StoreDetailSerializer,
    PageSerializer,
)
from .tasks import sync_store


class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return StoreCreateSerializer
        if self.action == "retrieve":
            return StoreDetailSerializer
        return StoreListSerializer

    def destroy(self, request, *args, **kwargs):
        store = self.get_object()
        store.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def sync(self, request, pk=None):
        store = self.get_object()
        sync_store.delay(store.id)
        return Response({"status": "sync started"})


class PageViewSet(viewsets.ModelViewSet):
    serializer_class = PageSerializer

    def get_queryset(self):
        return Page.objects.filter(store_id=self.kwargs["store_pk"])
