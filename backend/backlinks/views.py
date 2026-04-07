import logging
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Backlink, BacklinkSnapshot, OutreachProspect, OutreachCampaign, EmailConfig
from .serializers import (
    BacklinkSerializer, BacklinkSnapshotSerializer,
    OutreachProspectSerializer, OutreachCampaignSerializer, EmailConfigSerializer,
)

logger = logging.getLogger(__name__)


class BacklinkViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BacklinkSerializer

    def get_queryset(self):
        qs = Backlink.objects.all()
        store_id = self.request.query_params.get("store_id")
        if store_id:
            qs = qs.filter(store_id=store_id)
        return qs

    @action(detail=False, methods=["post"])
    def refresh(self, request):
        store_id = request.data.get("store_id")
        if not store_id:
            return Response({"error": "store_id is required"}, status=400)
        from .tasks import refresh_backlinks
        refresh_backlinks.delay(store_id)
        return Response({"status": "refresh queued"})

    @action(detail=False, methods=["get"])
    def snapshot(self, request):
        store_id = request.query_params.get("store_id")
        qs = BacklinkSnapshot.objects.all()
        if store_id:
            qs = qs.filter(store_id=store_id)
        serializer = BacklinkSnapshotSerializer(qs[:90], many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def summary(self, request):
        store_id = request.query_params.get("store_id")
        qs = Backlink.objects.filter(is_lost=False)
        if store_id:
            qs = qs.filter(store_id=store_id)
        total = qs.count()
        dofollow = qs.filter(is_dofollow=True).count()
        dofollow_pct = round((dofollow / total * 100), 1) if total else 0

        snap_qs = BacklinkSnapshot.objects.all()
        if store_id:
            snap_qs = snap_qs.filter(store_id=store_id)
        latest = snap_qs.first()

        return Response({
            "total": total,
            "dofollow": dofollow,
            "dofollow_pct": dofollow_pct,
            "new_this_week": latest.new_count if latest else 0,
            "lost_this_week": latest.lost_count if latest else 0,
        })


class OutreachProspectViewSet(viewsets.ModelViewSet):
    serializer_class = OutreachProspectSerializer

    def get_queryset(self):
        qs = OutreachProspect.objects.all()
        store_id = self.request.query_params.get("store_id")
        if store_id:
            qs = qs.filter(store_id=store_id)
        return qs

    @action(detail=False, methods=["post"])
    def suggest(self, request):
        store_id = request.data.get("store_id")
        if not store_id:
            return Response({"error": "store_id is required"}, status=400)
        from .tasks import suggest_prospects
        suggest_prospects.delay(store_id)
        return Response({"status": "suggestion queued"})

    @action(detail=True, methods=["post"])
    def email(self, request, pk=None):
        prospect = self.get_object()
        store = prospect.store

        try:
            config = store.email_config
        except EmailConfig.DoesNotExist:
            return Response(
                {"error": "No email config found for this store. Set up email in Settings."},
                status=400,
            )

        from .ai_client import BacklinksAIClient
        ai = BacklinksAIClient()
        try:
            draft = ai.draft_outreach_email(
                prospect_url=prospect.website_url,
                store_name=store.name,
                store_niche=", ".join(
                    store.keywords.filter(is_tracked=True).values_list("keyword", flat=True)[:5]
                ),
                anchor_text=store.name,
            )
        except Exception as e:
            logger.error("AI email drafting failed: %s", e)
            return Response({"error": "AI drafting failed"}, status=503)

        from .email_sender import EmailSender
        sender = EmailSender(config)
        try:
            sender.send(
                to_email=prospect.contact_email,
                subject=draft["subject"],
                body=draft["body"],
            )
            sent_at = timezone.now()
        except Exception as e:
            logger.error("Email send failed: %s", e)
            campaign = OutreachCampaign.objects.create(
                prospect=prospect,
                subject=draft["subject"],
                body=draft["body"],
                sent_at=None,
                sent_via=config.preferred_method,
            )
            return Response({"error": f"Email send failed: {e}"}, status=500)

        campaign = OutreachCampaign.objects.create(
            prospect=prospect,
            subject=draft["subject"],
            body=draft["body"],
            sent_at=sent_at,
            sent_via=config.preferred_method,
        )
        prospect.status = "emailed"
        prospect.save(update_fields=["status", "updated_at"])

        return Response(OutreachCampaignSerializer(campaign).data, status=201)

    @action(detail=True, methods=["patch"])
    def status(self, request, pk=None):
        prospect = self.get_object()
        new_status = request.data.get("status")
        valid = [s[0] for s in OutreachProspect._meta.get_field("status").choices]
        if new_status not in valid:
            return Response({"error": f"Invalid status. Must be one of: {valid}"}, status=400)
        prospect.status = new_status
        prospect.save(update_fields=["status", "updated_at"])
        return Response(OutreachProspectSerializer(prospect).data)


class OutreachCampaignViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OutreachCampaignSerializer

    def get_queryset(self):
        qs = OutreachCampaign.objects.select_related("prospect").all()
        store_id = self.request.query_params.get("store_id")
        if store_id:
            qs = qs.filter(prospect__store_id=store_id)
        return qs


class EmailConfigViewSet(viewsets.ModelViewSet):
    serializer_class = EmailConfigSerializer

    def get_queryset(self):
        qs = EmailConfig.objects.all()
        store_id = self.request.query_params.get("store_id")
        if store_id:
            qs = qs.filter(store_id=store_id)
        return qs

    @action(detail=False, methods=["get"], url_path="gmail/auth-url")
    def gmail_auth_url(self, request):
        from .email_sender import get_gmail_auth_url
        store_id = request.query_params.get("store_id")
        if not store_id:
            return Response({"error": "store_id is required"}, status=400)
        url = get_gmail_auth_url(store_id)
        return Response({"auth_url": url})

    @action(detail=False, methods=["get"], url_path="gmail/callback")
    def gmail_callback(self, request):
        code = request.query_params.get("code")
        store_id = request.query_params.get("state")
        if not code or not store_id:
            return Response({"error": "Missing code or state"}, status=400)
        from stores.models import Store
        from .email_sender import exchange_gmail_code
        try:
            store = Store.objects.get(id=store_id)
            gmail_email = exchange_gmail_code(code, store)
            return Response({"gmail_email": gmail_email})
        except Exception as e:
            logger.error("Gmail OAuth callback failed: %s", e)
            return Response({"error": str(e)}, status=500)
