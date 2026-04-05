from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from .models import Keyword, RankHistory
from .serializers import KeywordSerializer, RankHistorySerializer
from .dataforseo_client import DataForSEOClient


class KeywordViewSet(viewsets.ModelViewSet):
    serializer_class = KeywordSerializer

    def get_queryset(self):
        qs = Keyword.objects.all()
        store = self.request.query_params.get("store")
        if store:
            qs = qs.filter(store_id=store)
        return qs

    @action(detail=True, methods=["get"], url_path="rank-history")
    def rank_history(self, request, pk=None):
        keyword = self.get_object()
        history = keyword.rank_history.all()[:90]
        serializer = RankHistorySerializer(history, many=True)
        return Response(serializer.data)


@api_view(["POST"])
def research_keywords(request):
    seed_keyword = request.data.get("keyword", "")
    if not seed_keyword:
        return Response({"error": "keyword is required"}, status=400)
    client = DataForSEOClient()
    results = client.keyword_research(seed_keyword)
    return Response(results)
