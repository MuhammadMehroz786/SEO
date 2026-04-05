from django.db import models


class Keyword(models.Model):
    store = models.ForeignKey("stores.Store", on_delete=models.CASCADE, related_name="keywords")
    keyword = models.CharField(max_length=500)
    search_volume = models.IntegerField(default=0)
    difficulty = models.IntegerField(default=0)
    cpc = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    intent = models.CharField(max_length=50, blank=True, default="")
    is_tracked = models.BooleanField(default=True)
    cluster_name = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-search_volume"]

    def __str__(self):
        return f"{self.keyword} ({self.store.name})"


class RankHistory(models.Model):
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE, related_name="rank_history")
    date = models.DateField()
    position = models.IntegerField(default=0)
    serp_url = models.URLField(max_length=2000, blank=True, default="")
    serp_features = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["-date"]
        unique_together = [("keyword", "date")]

    def __str__(self):
        return f"{self.keyword.keyword} - {self.date}: #{self.position}"
