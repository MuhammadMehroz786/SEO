from django.db import models
from encrypted_fields.fields import EncryptedCharField


class Backlink(models.Model):
    store = models.ForeignKey("stores.Store", on_delete=models.CASCADE, related_name="backlinks")
    source_url = models.URLField(max_length=2000)
    target_url = models.URLField(max_length=2000)
    domain_rank = models.IntegerField(default=0)
    page_rank = models.IntegerField(default=0)
    anchor_text = models.CharField(max_length=500, blank=True, default="")
    is_dofollow = models.BooleanField(default=True)
    first_seen = models.DateField()
    last_seen = models.DateField()
    is_lost = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-domain_rank"]
        unique_together = [("store", "source_url", "target_url")]

    def __str__(self):
        from urllib.parse import urlparse
        src = urlparse(self.source_url).netloc
        tgt = urlparse(self.target_url).netloc + urlparse(self.target_url).path
        return f"{src} → {tgt}"


class BacklinkSnapshot(models.Model):
    store = models.ForeignKey("stores.Store", on_delete=models.CASCADE, related_name="backlink_snapshots")
    date = models.DateField()
    total_count = models.IntegerField(default=0)
    dofollow_count = models.IntegerField(default=0)
    lost_count = models.IntegerField(default=0)
    new_count = models.IntegerField(default=0)

    class Meta:
        ordering = ["-date"]
        unique_together = [("store", "date")]

    def __str__(self):
        return f"{self.store.name} snapshot {self.date}"


PROSPECT_SOURCE_CHOICES = [
    ("manual", "Manual"),
    ("auto_suggested", "Auto Suggested"),
]

PROSPECT_STATUS_CHOICES = [
    ("new", "New"),
    ("emailed", "Emailed"),
    ("followed_up", "Followed Up"),
    ("replied", "Replied"),
    ("won", "Won"),
    ("rejected", "Rejected"),
]


class OutreachProspect(models.Model):
    store = models.ForeignKey("stores.Store", on_delete=models.CASCADE, related_name="outreach_prospects")
    website_url = models.URLField(max_length=2000)
    contact_email = models.CharField(max_length=255, blank=True, default="")
    domain_rank = models.IntegerField(default=0)
    niche_relevance_score = models.IntegerField(default=0)
    source = models.CharField(max_length=20, choices=PROSPECT_SOURCE_CHOICES, default="manual")
    status = models.CharField(max_length=20, choices=PROSPECT_STATUS_CHOICES, default="new")
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-domain_rank"]

    def __str__(self):
        from urllib.parse import urlparse
        domain = urlparse(self.website_url).netloc
        return f"{domain} ({self.status})"


class OutreachCampaign(models.Model):
    prospect = models.ForeignKey(OutreachProspect, on_delete=models.CASCADE, related_name="campaigns")
    subject = models.CharField(max_length=500)
    body = models.TextField()
    sent_at = models.DateTimeField(null=True, blank=True)
    sent_via = models.CharField(max_length=10, choices=[("gmail", "Gmail"), ("smtp", "SMTP")])
    reply_received = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Email to {self.prospect} via {self.sent_via}"


PREFERRED_METHOD_CHOICES = [
    ("gmail", "Gmail"),
    ("smtp", "SMTP"),
]


class EmailConfig(models.Model):
    store = models.OneToOneField("stores.Store", on_delete=models.CASCADE, related_name="email_config")
    gmail_refresh_token = EncryptedCharField(max_length=1000, blank=True, default="")
    gmail_email = models.CharField(max_length=255, blank=True, default="")
    smtp_host = models.CharField(max_length=255, blank=True, default="")
    smtp_port = models.IntegerField(default=587)
    smtp_username = models.CharField(max_length=255, blank=True, default="")
    smtp_password = EncryptedCharField(max_length=255, blank=True, default="")
    smtp_from_email = models.CharField(max_length=255, blank=True, default="")
    preferred_method = models.CharField(max_length=10, choices=PREFERRED_METHOD_CHOICES, default="smtp")

    def __str__(self):
        return f"EmailConfig for {self.store.name}"
