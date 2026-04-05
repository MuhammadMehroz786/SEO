from django.contrib import admin
from .models import Store, Page, Image


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ["name", "shopify_url", "seo_score", "last_crawl_date", "is_deleted"]
    list_filter = ["is_deleted"]


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ["title", "store", "page_type", "content_score", "last_audited"]
    list_filter = ["page_type", "store"]


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ["page", "src", "alt_text"]
