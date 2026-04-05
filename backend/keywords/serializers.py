from rest_framework import serializers
from .models import Keyword, RankHistory


class RankHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RankHistory
        fields = ["id", "date", "position", "serp_url", "serp_features"]


class KeywordSerializer(serializers.ModelSerializer):
    latest_position = serializers.SerializerMethodField()

    class Meta:
        model = Keyword
        fields = [
            "id", "store", "keyword", "search_volume", "difficulty",
            "cpc", "intent", "is_tracked", "cluster_name",
            "latest_position", "created_at",
        ]

    def get_latest_position(self, obj):
        latest = obj.rank_history.first()
        return latest.position if latest else None
