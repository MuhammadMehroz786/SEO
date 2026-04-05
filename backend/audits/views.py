from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import AuditRun
from .serializers import AuditRunSerializer
from .tasks import run_site_audit


@api_view(["POST"])
def trigger_audit(request):
    store_id = request.data.get("store_id")
    if not store_id:
        return Response({"error": "store_id is required"}, status=400)
    run_site_audit.delay(store_id)
    return Response({"status": "audit started"})


class AuditRunViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditRunSerializer

    def get_queryset(self):
        qs = AuditRun.objects.all()
        store = self.request.query_params.get("store")
        if store:
            qs = qs.filter(store_id=store)
        return qs
