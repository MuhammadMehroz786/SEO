from django.contrib import admin
from .models import Keyword, RankHistory


@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ["keyword", "store", "search_volume", "difficulty", "is_tracked"]
    list_filter = ["is_tracked", "store"]


@admin.register(RankHistory)
class RankHistoryAdmin(admin.ModelAdmin):
    list_display = ["keyword", "date", "position"]
