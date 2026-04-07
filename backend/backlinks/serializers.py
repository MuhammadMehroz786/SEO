from rest_framework import serializers
from .models import Backlink, BacklinkSnapshot, OutreachProspect, OutreachCampaign, EmailConfig


class BacklinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Backlink
        fields = [
            "id", "store", "source_url", "target_url", "domain_rank",
            "page_rank", "anchor_text", "is_dofollow", "first_seen",
            "last_seen", "is_lost", "created_at",
        ]


class BacklinkSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = BacklinkSnapshot
        fields = ["id", "store", "date", "total_count", "dofollow_count", "lost_count", "new_count"]


class OutreachProspectSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutreachProspect
        fields = [
            "id", "store", "website_url", "contact_email", "domain_rank",
            "niche_relevance_score", "source", "status", "notes", "created_at", "updated_at",
        ]


class OutreachCampaignSerializer(serializers.ModelSerializer):
    prospect_url = serializers.CharField(source="prospect.website_url", read_only=True)

    class Meta:
        model = OutreachCampaign
        fields = [
            "id", "prospect", "prospect_url", "subject", "body",
            "sent_at", "sent_via", "reply_received", "created_at",
        ]


class EmailConfigSerializer(serializers.ModelSerializer):
    smtp_password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = EmailConfig
        fields = [
            "id", "store", "gmail_email", "smtp_host", "smtp_port",
            "smtp_username", "smtp_password", "smtp_from_email", "preferred_method",
        ]
