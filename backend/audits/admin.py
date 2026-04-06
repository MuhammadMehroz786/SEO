from django.contrib import admin
from .models import AuditRun, AuditIssue


@admin.register(AuditRun)
class AuditRunAdmin(admin.ModelAdmin):
    list_display = ["store", "status", "started_at", "pages_crawled", "issues_found"]
    list_filter = ["status", "store"]


@admin.register(AuditIssue)
class AuditIssueAdmin(admin.ModelAdmin):
    list_display = ["audit_run", "issue_type", "severity", "page"]
    list_filter = ["severity", "issue_type"]
