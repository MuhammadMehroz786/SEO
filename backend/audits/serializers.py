from rest_framework import serializers
from .models import AuditRun, AuditIssue


class AuditIssueSerializer(serializers.ModelSerializer):
    page_url = serializers.CharField(source="page.url", read_only=True, default="")
    page_title = serializers.CharField(source="page.title", read_only=True, default="")

    class Meta:
        model = AuditIssue
        fields = [
            "id", "issue_type", "severity", "description",
            "fix_suggestion", "page_url", "page_title",
        ]


class AuditRunSerializer(serializers.ModelSerializer):
    issues = AuditIssueSerializer(many=True, read_only=True)
    issue_summary = serializers.SerializerMethodField()

    class Meta:
        model = AuditRun
        fields = [
            "id", "store", "status", "started_at", "completed_at",
            "pages_crawled", "issues_found", "issues", "issue_summary",
        ]

    def get_issue_summary(self, obj):
        issues = obj.issues.all()
        return {
            "critical": issues.filter(severity="critical").count(),
            "warning": issues.filter(severity="warning").count(),
            "info": issues.filter(severity="info").count(),
        }
