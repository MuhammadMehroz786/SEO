from django.db import models
from stores.models import Store, Page


class AuditRun(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="audit_runs")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    pages_crawled = models.IntegerField(default=0)
    issues_found = models.IntegerField(default=0)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"Audit {self.id} - {self.store.name} ({self.status})"


class AuditIssue(models.Model):
    SEVERITY_CHOICES = [
        ("critical", "Critical"),
        ("warning", "Warning"),
        ("info", "Info"),
    ]
    ISSUE_TYPES = [
        ("missing_title", "Missing Title"),
        ("missing_meta_description", "Missing Meta Description"),
        ("title_too_long", "Title Too Long"),
        ("title_too_short", "Title Too Short"),
        ("meta_desc_too_long", "Meta Description Too Long"),
        ("meta_desc_too_short", "Meta Description Too Short"),
        ("missing_h1", "Missing H1"),
        ("duplicate_title", "Duplicate Title"),
        ("duplicate_meta_description", "Duplicate Meta Description"),
        ("missing_alt_text", "Missing Image Alt Text"),
        ("broken_link", "Broken Link"),
        ("slow_page", "Slow Page"),
        ("missing_schema", "Missing Schema Markup"),
        ("redirect_chain", "Redirect Chain"),
        ("missing_canonical", "Missing Canonical"),
    ]

    audit_run = models.ForeignKey(AuditRun, on_delete=models.CASCADE, related_name="issues")
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="audit_issues", null=True, blank=True)
    issue_type = models.CharField(max_length=50, choices=ISSUE_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    description = models.TextField()
    fix_suggestion = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["severity", "issue_type"]

    def __str__(self):
        return f"{self.issue_type} ({self.severity})"
