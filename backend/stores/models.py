from django.db import models
from encrypted_fields.fields import EncryptedCharField


class ActiveManager(models.Manager):
    """Manager that filters out soft-deleted stores by default."""

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def active(self):
        """Return queryset of non-deleted stores."""
        return self.get_queryset()


class Store(models.Model):
    name = models.CharField(max_length=255)
    shopify_url = models.CharField(max_length=255, unique=True)
    access_token = EncryptedCharField(max_length=255)
    seo_score = models.IntegerField(default=0)
    last_crawl_date = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Default manager filters out deleted stores; all_objects gives everything
    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def soft_delete(self):
        """Mark the store as deleted without removing from the database."""
        self.is_deleted = True
        self.save(update_fields=["is_deleted", "updated_at"])


PAGE_TYPE_CHOICES = [
    ("product", "Product"),
    ("collection", "Collection"),
    ("page", "Page"),
    ("blog_post", "Blog Post"),
]


class Page(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="pages")
    shopify_id = models.CharField(max_length=255)
    url = models.CharField(max_length=2000)
    page_type = models.CharField(max_length=50, choices=PAGE_TYPE_CHOICES)
    title = models.CharField(max_length=512, blank=True, default="")
    meta_description = models.TextField(blank=True, default="")
    h1 = models.CharField(max_length=512, blank=True, default="")
    content_score = models.IntegerField(default=0)
    last_audited = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        unique_together = [("store", "shopify_id")]

    def __str__(self):
        return f"{self.page_type}: {self.title or self.url}"


class Image(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="images")
    src = models.URLField(max_length=1000)
    alt_text = models.TextField(blank=True, default="")
    ai_generated_alt = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Image({self.src[:60]})"
