from rest_framework import serializers
from .models import Store, Page, Image


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ["id", "src", "alt_text", "ai_generated_alt"]


class PageSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = Page
        fields = [
            "id", "store", "shopify_id", "url", "page_type",
            "title", "meta_description", "h1", "content_score",
            "last_audited", "images", "created_at", "updated_at",
        ]


class StoreListSerializer(serializers.ModelSerializer):
    pages_count = serializers.IntegerField(source="pages.count", read_only=True)

    class Meta:
        model = Store
        fields = [
            "id", "name", "shopify_url", "seo_score",
            "last_crawl_date", "pages_count", "created_at",
        ]


class StoreCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ["id", "name", "shopify_url", "access_token"]
        extra_kwargs = {"access_token": {"write_only": True}}


class StoreDetailSerializer(serializers.ModelSerializer):
    pages = PageSerializer(many=True, read_only=True)

    class Meta:
        model = Store
        fields = [
            "id", "name", "shopify_url", "seo_score",
            "last_crawl_date", "pages", "created_at", "updated_at",
        ]
