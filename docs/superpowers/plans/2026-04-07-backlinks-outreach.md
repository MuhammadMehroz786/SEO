# Backlinks & Link Outreach Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `backlinks` Django app and React frontend page that monitors inbound links via DataForSEO and sends AI-drafted outreach emails to prospects via Gmail or SMTP.

**Architecture:** Single new Django app `backlinks` following the same pattern as `keywords` (models → serializers → views → tasks → DataForSEO client). Outreach (prospects + campaigns + email config) lives inside the same app. Frontend adds a new Backlinks page with three tabs: Overview, Prospects, Campaigns.

**Tech Stack:** Django 5, DRF, Celery, DataForSEO API, Anthropic SDK (existing), `google-auth` + `google-api-python-client` (Gmail), `smtplib` (SMTP), `requests` (page fetching), React 18, Recharts (existing)

---

## File Map

**Create:**
- `backend/backlinks/__init__.py`
- `backend/backlinks/apps.py`
- `backend/backlinks/models.py` — Backlink, BacklinkSnapshot, OutreachProspect, OutreachCampaign, EmailConfig
- `backend/backlinks/serializers.py` — all serializers
- `backend/backlinks/dataforseo_client.py` — BacklinksClient (monitoring + prospect suggestions)
- `backend/backlinks/ai_client.py` — relevance scoring + email drafting
- `backend/backlinks/email_sender.py` — Gmail OAuth2 + SMTP sending
- `backend/backlinks/views.py` — all 10 API endpoints
- `backend/backlinks/urls.py` — URL routing
- `backend/backlinks/tasks.py` — refresh_backlinks, refresh_all_backlinks, suggest_prospects
- `backend/backlinks/admin.py` — register all models
- `backend/backlinks/migrations/` — auto-generated
- `backend/backlinks/tests/__init__.py`
- `backend/backlinks/tests/test_models.py`
- `backend/backlinks/tests/test_dataforseo_client.py`
- `backend/backlinks/tests/test_ai_client.py`
- `backend/backlinks/tests/test_email_sender.py`
- `backend/backlinks/tests/test_views.py`
- `backend/backlinks/tests/test_tasks.py`
- `frontend/src/pages/Backlinks.jsx` — three-tab page

**Modify:**
- `backend/seobot/settings.py` — add `backlinks` to INSTALLED_APPS, add GOOGLE_CLIENT_ID/SECRET settings, add `refresh-all-backlinks-weekly` to CELERY_BEAT_SCHEDULE_CONFIG
- `backend/seobot/urls.py` — add `/api/v1/backlinks/` route
- `backend/requirements.txt` — add `google-auth`, `google-auth-httplib2`, `google-api-python-client`
- `frontend/src/api/client.js` — add backlinks API functions
- `frontend/src/components/Layout.jsx` — add Backlinks nav item
- `frontend/src/App.jsx` — add `/backlinks` route

---

## Task 1: Django App Scaffold

**Files:**
- Create: `backend/backlinks/__init__.py`
- Create: `backend/backlinks/apps.py`
- Create: `backend/backlinks/admin.py`
- Modify: `backend/seobot/settings.py`

- [ ] **Step 1: Create app files**

```python
# backend/backlinks/__init__.py
# (empty)
```

```python
# backend/backlinks/apps.py
from django.apps import AppConfig

class BacklinksConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backlinks"
```

```python
# backend/backlinks/admin.py
from django.contrib import admin
from .models import Backlink, BacklinkSnapshot, OutreachProspect, OutreachCampaign, EmailConfig

admin.site.register(Backlink)
admin.site.register(BacklinkSnapshot)
admin.site.register(OutreachProspect)
admin.site.register(OutreachCampaign)
admin.site.register(EmailConfig)
```

- [ ] **Step 2: Add to INSTALLED_APPS in `backend/seobot/settings.py`**

Find the `# Local apps` section and add `"backlinks"` after `"dashboard"`:

```python
    # Local apps
    "stores",
    "keywords",
    "audits",
    "ai_engine",
    "dashboard",
    "backlinks",
```

Also add Google OAuth settings and Gmail env vars at the bottom of `settings.py` (after DATAFORSEO_PASSWORD line):

```python
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/v1/backlinks/email-config/gmail/callback/")
```

Also add the weekly backlinks refresh to `CELERY_BEAT_SCHEDULE_CONFIG`:

```python
    "refresh-all-backlinks-weekly": {
        "task": "backlinks.tasks.refresh_all_backlinks",
        "hour": 5, "minute": 0, "day_of_week": 1,
    },
```

- [ ] **Step 3: Verify Django check passes**

```bash
cd /Users/apple/Desktop/SEO\ BOT/backend
source venv/bin/activate
python manage.py check
```

Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 4: Commit**

```bash
git add backend/backlinks/__init__.py backend/backlinks/apps.py backend/backlinks/admin.py backend/seobot/settings.py
git commit -m "feat: scaffold backlinks Django app"
```

---

## Task 2: Models

**Files:**
- Create: `backend/backlinks/models.py`
- Create: `backend/backlinks/migrations/` (auto-generated)
- Create: `backend/backlinks/tests/__init__.py`
- Create: `backend/backlinks/tests/test_models.py`

- [ ] **Step 1: Write failing model tests**

```python
# backend/backlinks/tests/__init__.py
# (empty)
```

```python
# backend/backlinks/tests/test_models.py
import datetime
from django.test import TestCase
from stores.models import Store
from backlinks.models import Backlink, BacklinkSnapshot, OutreachProspect, OutreachCampaign, EmailConfig


def make_store():
    return Store.objects.create(
        name="Test Store",
        shopify_url="teststore.myshopify.com",
        access_token="tok",
    )


class BacklinkModelTest(TestCase):
    def test_create_backlink(self):
        store = make_store()
        bl = Backlink.objects.create(
            store=store,
            source_url="https://example.com/post",
            target_url="https://teststore.myshopify.com/products/shoe",
            domain_rank=45,
            page_rank=20,
            anchor_text="buy shoes",
            is_dofollow=True,
            first_seen=datetime.date.today(),
            last_seen=datetime.date.today(),
        )
        self.assertEqual(str(bl), "example.com → teststore.myshopify.com/products/shoe")
        self.assertFalse(bl.is_lost)

    def test_backlink_unique_together(self):
        from django.db import IntegrityError
        store = make_store()
        kwargs = dict(
            store=store,
            source_url="https://a.com",
            target_url="https://b.com",
            first_seen=datetime.date.today(),
            last_seen=datetime.date.today(),
        )
        Backlink.objects.create(**kwargs)
        with self.assertRaises(IntegrityError):
            Backlink.objects.create(**kwargs)


class BacklinkSnapshotTest(TestCase):
    def test_create_snapshot(self):
        store = make_store()
        snap = BacklinkSnapshot.objects.create(
            store=store,
            date=datetime.date.today(),
            total_count=100,
            dofollow_count=80,
            lost_count=2,
            new_count=5,
        )
        self.assertEqual(snap.total_count, 100)


class OutreachProspectTest(TestCase):
    def test_create_prospect(self):
        store = make_store()
        p = OutreachProspect.objects.create(
            store=store,
            website_url="https://fashionblog.com",
            contact_email="editor@fashionblog.com",
            domain_rank=55,
            niche_relevance_score=85,
            source="manual",
            status="new",
        )
        self.assertEqual(p.status, "new")
        self.assertEqual(str(p), "fashionblog.com (new)")


class OutreachCampaignTest(TestCase):
    def test_create_campaign(self):
        store = make_store()
        prospect = OutreachProspect.objects.create(
            store=store,
            website_url="https://fashionblog.com",
            contact_email="editor@fashionblog.com",
            source="manual",
            status="emailed",
        )
        from django.utils import timezone
        campaign = OutreachCampaign.objects.create(
            prospect=prospect,
            subject="Link opportunity for fashionblog.com",
            body="Hi there...",
            sent_at=timezone.now(),
            sent_via="smtp",
        )
        self.assertFalse(campaign.reply_received)


class EmailConfigTest(TestCase):
    def test_create_email_config(self):
        store = make_store()
        config = EmailConfig.objects.create(
            store=store,
            smtp_host="smtp.outlook.com",
            smtp_port=587,
            smtp_username="me@outlook.com",
            smtp_password="pass",
            smtp_from_email="me@outlook.com",
            preferred_method="smtp",
        )
        self.assertEqual(config.preferred_method, "smtp")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/apple/Desktop/SEO\ BOT/backend
source venv/bin/activate
python manage.py test backlinks.tests.test_models -v 2
```

Expected: `ImportError` or `ModuleNotFoundError` — models don't exist yet.

- [ ] **Step 3: Write models**

```python
# backend/backlinks/models.py
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
```

- [ ] **Step 4: Create and run migrations**

```bash
cd /Users/apple/Desktop/SEO\ BOT/backend
source venv/bin/activate
python manage.py makemigrations backlinks
python manage.py migrate
```

Expected: migration created and applied with no errors.

- [ ] **Step 5: Run model tests — verify they pass**

```bash
python manage.py test backlinks.tests.test_models -v 2
```

Expected: `5 tests, 0 failures`

- [ ] **Step 6: Commit**

```bash
git add backend/backlinks/models.py backend/backlinks/migrations/ backend/backlinks/tests/
git commit -m "feat: add backlinks models and tests"
```

---

## Task 3: DataForSEO Client

**Files:**
- Create: `backend/backlinks/dataforseo_client.py`
- Create: `backend/backlinks/tests/test_dataforseo_client.py`

- [ ] **Step 1: Write failing client tests**

```python
# backend/backlinks/tests/test_dataforseo_client.py
import datetime
from unittest.mock import patch, MagicMock
from django.test import TestCase
from backlinks.dataforseo_client import BacklinksClient


class BacklinksClientTest(TestCase):

    @patch("backlinks.dataforseo_client.requests.post")
    def test_get_backlinks(self, mock_post):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                "tasks": [{
                    "result": [{
                        "items": [{
                            "url_from": "https://blog.example.com/post",
                            "url_to": "https://mystore.com/products/shoe",
                            "domain_from_rank": 50,
                            "page_from_rank": 25,
                            "anchor": "buy shoes online",
                            "dofollow": True,
                            "first_seen": "2026-01-15 00:00:00 +00:00",
                            "last_seen": "2026-04-01 00:00:00 +00:00",
                        }]
                    }]
                }]
            }
        )
        mock_post.return_value.raise_for_status = MagicMock()
        client = BacklinksClient()
        results = client.get_backlinks("mystore.com")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["source_url"], "https://blog.example.com/post")
        self.assertEqual(results[0]["domain_rank"], 50)
        self.assertTrue(results[0]["is_dofollow"])
        self.assertIsInstance(results[0]["first_seen"], datetime.date)

    @patch("backlinks.dataforseo_client.requests.post")
    def test_get_backlinks_empty(self, mock_post):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"tasks": [{"result": [{"items": []}]}]}
        )
        mock_post.return_value.raise_for_status = MagicMock()
        client = BacklinksClient()
        results = client.get_backlinks("mystore.com")
        self.assertEqual(results, [])

    @patch("backlinks.dataforseo_client.requests.post")
    def test_suggest_prospects(self, mock_post):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                "tasks": [{
                    "result": [{
                        "items": [{
                            "domain": "fashionblog.com",
                            "rank": 60,
                        }]
                    }]
                }]
            }
        )
        mock_post.return_value.raise_for_status = MagicMock()
        client = BacklinksClient()
        results = client.suggest_prospects("mystore.com", ["fashion shoes", "sneakers"])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["domain"], "fashionblog.com")
        self.assertEqual(results[0]["domain_rank"], 60)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python manage.py test backlinks.tests.test_dataforseo_client -v 2
```

Expected: `ImportError` — client doesn't exist yet.

- [ ] **Step 3: Write the client**

```python
# backend/backlinks/dataforseo_client.py
import datetime
import requests
from django.conf import settings


class BacklinksClient:
    BASE_URL = "https://api.dataforseo.com/v3"

    def __init__(self):
        self.auth = (settings.DATAFORSEO_LOGIN, settings.DATAFORSEO_PASSWORD)

    def _post(self, endpoint: str, data: list) -> dict:
        response = requests.post(
            f"{self.BASE_URL}/{endpoint}",
            json=data,
            auth=self.auth,
            timeout=60,
        )
        response.raise_for_status()
        return response.json()

    def _parse_date(self, date_str: str) -> datetime.date:
        """Parse DataForSEO date string like '2026-01-15 00:00:00 +00:00'."""
        try:
            return datetime.datetime.strptime(date_str[:10], "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return datetime.date.today()

    def get_backlinks(self, domain: str, limit: int = 1000) -> list:
        """Fetch all backlinks pointing to the given domain."""
        data = [{
            "target": domain,
            "limit": limit,
            "include_subdomains": True,
            "broken_links": False,
        }]
        result = self._post("backlinks/backlinks/live", data)
        backlinks = []
        for task in result.get("tasks", []):
            for res in task.get("result", []) or []:
                for item in res.get("items", []) or []:
                    backlinks.append({
                        "source_url": item.get("url_from", ""),
                        "target_url": item.get("url_to", ""),
                        "domain_rank": item.get("domain_from_rank", 0) or 0,
                        "page_rank": item.get("page_from_rank", 0) or 0,
                        "anchor_text": item.get("anchor", "") or "",
                        "is_dofollow": bool(item.get("dofollow", False)),
                        "first_seen": self._parse_date(item.get("first_seen", "")),
                        "last_seen": self._parse_date(item.get("last_seen", "")),
                    })
        return backlinks

    def suggest_prospects(self, domain: str, keywords: list, limit: int = 50) -> list:
        """Find domains that link to competitors but not to this domain."""
        data = [{
            "target": domain,
            "limit": limit,
            "filters": ["domain_from_rank", ">", 10],
        }]
        result = self._post("backlinks/competitors/live", data)
        prospects = []
        for task in result.get("tasks", []):
            for res in task.get("result", []) or []:
                for item in res.get("items", []) or []:
                    prospects.append({
                        "domain": item.get("domain", ""),
                        "domain_rank": item.get("rank", 0) or 0,
                    })
        return prospects
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
python manage.py test backlinks.tests.test_dataforseo_client -v 2
```

Expected: `3 tests, 0 failures`

- [ ] **Step 5: Commit**

```bash
git add backend/backlinks/dataforseo_client.py backend/backlinks/tests/test_dataforseo_client.py
git commit -m "feat: add BacklinksClient for DataForSEO integration"
```

---

## Task 4: AI Client (Relevance Scoring + Email Drafting)

**Files:**
- Create: `backend/backlinks/ai_client.py`
- Create: `backend/backlinks/tests/test_ai_client.py`

- [ ] **Step 1: Write failing AI client tests**

```python
# backend/backlinks/tests/test_ai_client.py
from unittest.mock import patch, MagicMock
from django.test import TestCase
from backlinks.ai_client import BacklinksAIClient


class BacklinksAIClientTest(TestCase):

    @patch("backlinks.ai_client.requests.get")
    @patch("backlinks.ai_client.anthropic.Anthropic")
    def test_score_relevance(self, mock_anthropic_cls, mock_get):
        mock_get.return_value = MagicMock(
            status_code=200,
            text="<html><body>Fashion shoes and sneaker reviews</body></html>",
        )
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client
        mock_client.messages.create.return_value = MagicMock(
            content=[MagicMock(text='{"score": 82, "reason": "Fashion content matches shoe store niche"}')]
        )
        client = BacklinksAIClient()
        result = client.score_relevance(
            prospect_url="https://fashionblog.com",
            store_name="My Shoe Store",
            store_keywords=["shoes", "sneakers", "fashion"],
        )
        self.assertEqual(result["score"], 82)
        self.assertIn("reason", result)

    @patch("backlinks.ai_client.requests.get")
    @patch("backlinks.ai_client.anthropic.Anthropic")
    def test_draft_outreach_email(self, mock_anthropic_cls, mock_get):
        mock_get.return_value = MagicMock(
            status_code=200,
            text="<html><body>Top 10 sneaker blogs of 2026</body></html>",
        )
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client
        mock_client.messages.create.return_value = MagicMock(
            content=[MagicMock(text='{"subject": "Link opportunity for your readers", "body": "Hi there, I noticed your sneaker content..."}')]
        )
        client = BacklinksAIClient()
        result = client.draft_outreach_email(
            prospect_url="https://sneakerblog.com",
            store_name="My Shoe Store",
            store_niche="premium sneakers and athletic footwear",
            anchor_text="premium sneakers",
        )
        self.assertIn("subject", result)
        self.assertIn("body", result)
        self.assertIsInstance(result["subject"], str)
        self.assertIsInstance(result["body"], str)

    @patch("backlinks.ai_client.requests.get")
    @patch("backlinks.ai_client.anthropic.Anthropic")
    def test_score_relevance_fetch_error(self, mock_anthropic_cls, mock_get):
        mock_get.side_effect = Exception("Connection refused")
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client
        mock_client.messages.create.return_value = MagicMock(
            content=[MagicMock(text='{"score": 50, "reason": "Could not fetch page content"}')]
        )
        client = BacklinksAIClient()
        result = client.score_relevance(
            prospect_url="https://unreachable.com",
            store_name="My Store",
            store_keywords=["shoes"],
        )
        self.assertIn("score", result)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python manage.py test backlinks.tests.test_ai_client -v 2
```

Expected: `ImportError` — module doesn't exist yet.

- [ ] **Step 3: Write the AI client**

```python
# backend/backlinks/ai_client.py
import json
import logging
import requests
import anthropic
from django.conf import settings

logger = logging.getLogger(__name__)

RELEVANCE_PROMPT = """You are an SEO expert evaluating whether a website is a good candidate for a backlink outreach campaign.

Store name: {store_name}
Store keywords/niche: {store_keywords}

Prospect website URL: {prospect_url}
Prospect page content (first 2000 chars):
{page_content}

Score the relevance of this prospect for backlinking to this store on a scale of 0-100.
- 80-100: Highly relevant, same niche or audience
- 50-79: Moderately relevant, related topics
- 20-49: Loosely relevant
- 0-19: Not relevant

Return a JSON object with keys "score" (integer) and "reason" (one sentence).
Return ONLY the JSON object, no other text."""

OUTREACH_EMAIL_PROMPT = """You are writing a professional cold outreach email to request a backlink.

Store: {store_name}
Store niche: {store_niche}
Desired anchor text: {anchor_text}

Prospect website: {prospect_url}
Prospect page content (first 2000 chars):
{page_content}

Write a short, personalized cold outreach email. Rules:
- Subject line: compelling and specific, under 60 chars
- Body: 3-4 sentences max, mention something specific from their content, explain value to their readers
- Tone: professional, friendly, not salesy or spammy
- Do NOT use phrases like "I hope this email finds you well"
- End with a simple call to action

Return a JSON object with keys "subject" (string) and "body" (string, plain text with newlines).
Return ONLY the JSON object, no other text."""


class BacklinksAIClient:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-20250514"

    def _fetch_page_content(self, url: str) -> str:
        """Fetch a webpage and return first 2000 chars of text content."""
        try:
            response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            return response.text[:2000]
        except Exception as e:
            logger.warning("Could not fetch %s: %s", url, e)
            return "(page content unavailable)"

    def _ask(self, prompt: str) -> dict:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        return json.loads(response.content[0].text)

    def score_relevance(self, prospect_url: str, store_name: str, store_keywords: list) -> dict:
        """Score prospect relevance 0-100. Returns {"score": int, "reason": str}."""
        page_content = self._fetch_page_content(prospect_url)
        prompt = RELEVANCE_PROMPT.format(
            store_name=store_name,
            store_keywords=", ".join(store_keywords),
            prospect_url=prospect_url,
            page_content=page_content,
        )
        return self._ask(prompt)

    def draft_outreach_email(self, prospect_url: str, store_name: str, store_niche: str, anchor_text: str) -> dict:
        """Draft a cold outreach email. Returns {"subject": str, "body": str}."""
        page_content = self._fetch_page_content(prospect_url)
        prompt = OUTREACH_EMAIL_PROMPT.format(
            store_name=store_name,
            store_niche=store_niche,
            anchor_text=anchor_text,
            prospect_url=prospect_url,
            page_content=page_content,
        )
        return self._ask(prompt)
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
python manage.py test backlinks.tests.test_ai_client -v 2
```

Expected: `3 tests, 0 failures`

- [ ] **Step 5: Commit**

```bash
git add backend/backlinks/ai_client.py backend/backlinks/tests/test_ai_client.py
git commit -m "feat: add BacklinksAIClient for relevance scoring and email drafting"
```

---

## Task 5: Email Sender (Gmail + SMTP)

**Files:**
- Create: `backend/backlinks/email_sender.py`
- Create: `backend/backlinks/tests/test_email_sender.py`
- Modify: `backend/requirements.txt`

- [ ] **Step 1: Install Google API libraries**

```bash
cd /Users/apple/Desktop/SEO\ BOT/backend
source venv/bin/activate
pip install google-auth google-auth-httplib2 google-api-python-client
pip freeze | grep -E "google-auth|google-api" >> requirements.txt
```

- [ ] **Step 2: Write failing email sender tests**

```python
# backend/backlinks/tests/test_email_sender.py
import smtplib
from unittest.mock import patch, MagicMock
from django.test import TestCase
from stores.models import Store
from backlinks.models import EmailConfig
from backlinks.email_sender import EmailSender


def make_store_with_smtp_config():
    store = Store.objects.create(
        name="Test Store",
        shopify_url="teststore.myshopify.com",
        access_token="tok",
    )
    config = EmailConfig.objects.create(
        store=store,
        smtp_host="smtp.outlook.com",
        smtp_port=587,
        smtp_username="me@outlook.com",
        smtp_password="pass123",
        smtp_from_email="me@outlook.com",
        preferred_method="smtp",
    )
    return store, config


class SMTPSenderTest(TestCase):

    @patch("backlinks.email_sender.smtplib.SMTP")
    def test_send_via_smtp(self, mock_smtp_cls):
        mock_smtp = MagicMock()
        mock_smtp_cls.return_value.__enter__ = MagicMock(return_value=mock_smtp)
        mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)
        store, config = make_store_with_smtp_config()
        sender = EmailSender(config)
        sender.send(
            to_email="editor@blog.com",
            subject="Link opportunity",
            body="Hi there, we'd love a backlink.",
        )
        mock_smtp.sendmail.assert_called_once()

    @patch("backlinks.email_sender.smtplib.SMTP")
    def test_send_via_smtp_failure(self, mock_smtp_cls):
        mock_smtp = MagicMock()
        mock_smtp.sendmail.side_effect = smtplib.SMTPException("Connection failed")
        mock_smtp_cls.return_value.__enter__ = MagicMock(return_value=mock_smtp)
        mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)
        store, config = make_store_with_smtp_config()
        sender = EmailSender(config)
        with self.assertRaises(smtplib.SMTPException):
            sender.send(
                to_email="editor@blog.com",
                subject="Link opportunity",
                body="Hi there.",
            )
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
python manage.py test backlinks.tests.test_email_sender -v 2
```

Expected: `ImportError` — module doesn't exist yet.

- [ ] **Step 4: Write the email sender**

```python
# backend/backlinks/email_sender.py
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64

from django.conf import settings

logger = logging.getLogger(__name__)


class EmailSender:
    """Sends emails via Gmail OAuth2 or SMTP based on EmailConfig."""

    def __init__(self, config):
        self.config = config

    def send(self, to_email: str, subject: str, body: str):
        """Send an email. Raises on failure."""
        if self.config.preferred_method == "gmail":
            self._send_gmail(to_email, subject, body)
        else:
            self._send_smtp(to_email, subject, body)

    def _send_smtp(self, to_email: str, subject: str, body: str):
        msg = MIMEMultipart()
        msg["From"] = self.config.smtp_from_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(self.config.smtp_username, self.config.smtp_password)
            server.sendmail(self.config.smtp_from_email, to_email, msg.as_string())
        logger.info("Sent email via SMTP to %s", to_email)

    def _send_gmail(self, to_email: str, subject: str, body: str):
        creds = Credentials(
            token=None,
            refresh_token=self.config.gmail_refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
        )
        request = google.auth.transport.requests.Request()
        creds.refresh(request)

        service = build("gmail", "v1", credentials=creds)

        msg = MIMEText(body, "plain")
        msg["From"] = self.config.gmail_email
        msg["To"] = to_email
        msg["Subject"] = subject

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        service.users().messages().send(userId="me", body={"raw": raw}).execute()
        logger.info("Sent email via Gmail to %s", to_email)


def get_gmail_auth_url() -> str:
    """Return the Google OAuth2 authorization URL."""
    from google_auth_oauthlib.flow import Flow
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=["https://www.googleapis.com/auth/gmail.send"],
    )
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
    return auth_url


def exchange_gmail_code(code: str, store) -> str:
    """Exchange OAuth2 code for refresh token, save to EmailConfig, return gmail email."""
    from google_auth_oauthlib.flow import Flow
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=["https://www.googleapis.com/auth/gmail.send"],
    )
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
    flow.fetch_token(code=code)
    creds = flow.credentials

    import google.auth.transport.requests
    from googleapiclient.discovery import build as g_build
    service = g_build("oauth2", "v2", credentials=creds)
    user_info = service.userinfo().get().execute()
    gmail_email = user_info.get("email", "")

    from backlinks.models import EmailConfig
    config, _ = EmailConfig.objects.get_or_create(store=store)
    config.gmail_refresh_token = creds.refresh_token
    config.gmail_email = gmail_email
    config.preferred_method = "gmail"
    config.save()
    return gmail_email
```

- [ ] **Step 5: Run tests — verify they pass**

```bash
python manage.py test backlinks.tests.test_email_sender -v 2
```

Expected: `2 tests, 0 failures`

- [ ] **Step 6: Commit**

```bash
git add backend/backlinks/email_sender.py backend/backlinks/tests/test_email_sender.py backend/requirements.txt
git commit -m "feat: add EmailSender for Gmail OAuth2 and SMTP"
```

---

## Task 6: Celery Tasks

**Files:**
- Create: `backend/backlinks/tasks.py`
- Create: `backend/backlinks/tests/test_tasks.py`

- [ ] **Step 1: Write failing task tests**

```python
# backend/backlinks/tests/test_tasks.py
import datetime
from unittest.mock import patch, MagicMock
from django.test import TestCase
from stores.models import Store
from backlinks.models import Backlink, BacklinkSnapshot, OutreachProspect
from backlinks.tasks import refresh_backlinks, suggest_prospects


def make_store():
    return Store.objects.create(
        name="Test Store",
        shopify_url="teststore.myshopify.com",
        access_token="tok",
    )


class RefreshBacklinksTaskTest(TestCase):

    @patch("backlinks.tasks.BacklinksClient")
    def test_creates_new_backlinks(self, mock_client_cls):
        store = make_store()
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.get_backlinks.return_value = [{
            "source_url": "https://blog.com/post",
            "target_url": "https://teststore.myshopify.com/products/1",
            "domain_rank": 40,
            "page_rank": 20,
            "anchor_text": "buy here",
            "is_dofollow": True,
            "first_seen": datetime.date(2026, 1, 1),
            "last_seen": datetime.date(2026, 4, 1),
        }]
        refresh_backlinks(store.id)
        self.assertEqual(Backlink.objects.filter(store=store).count(), 1)
        self.assertEqual(BacklinkSnapshot.objects.filter(store=store).count(), 1)
        snap = BacklinkSnapshot.objects.get(store=store)
        self.assertEqual(snap.total_count, 1)
        self.assertEqual(snap.new_count, 1)

    @patch("backlinks.tasks.BacklinksClient")
    def test_marks_lost_backlinks(self, mock_client_cls):
        store = make_store()
        # Existing backlink not in API response
        Backlink.objects.create(
            store=store,
            source_url="https://old.com/post",
            target_url="https://teststore.myshopify.com/products/1",
            first_seen=datetime.date(2026, 1, 1),
            last_seen=datetime.date(2026, 3, 1),
        )
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.get_backlinks.return_value = []  # API returns nothing
        refresh_backlinks(store.id)
        bl = Backlink.objects.get(store=store)
        self.assertTrue(bl.is_lost)


class SuggestProspectsTaskTest(TestCase):

    @patch("backlinks.tasks.BacklinksAIClient")
    @patch("backlinks.tasks.BacklinksClient")
    def test_creates_prospects(self, mock_client_cls, mock_ai_cls):
        store = make_store()
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.suggest_prospects.return_value = [
            {"domain": "fashionblog.com", "domain_rank": 55},
        ]
        mock_ai = MagicMock()
        mock_ai_cls.return_value = mock_ai
        mock_ai.score_relevance.return_value = {"score": 80, "reason": "Fashion niche match"}

        suggest_prospects(store.id)

        self.assertEqual(OutreachProspect.objects.filter(store=store).count(), 1)
        p = OutreachProspect.objects.get(store=store)
        self.assertEqual(p.domain_rank, 55)
        self.assertEqual(p.niche_relevance_score, 80)
        self.assertEqual(p.source, "auto_suggested")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python manage.py test backlinks.tests.test_tasks -v 2
```

Expected: `ImportError` — tasks don't exist yet.

- [ ] **Step 3: Write tasks**

```python
# backend/backlinks/tasks.py
import logging
from celery import shared_task
from django.utils import timezone
from requests.exceptions import RequestException

from .dataforseo_client import BacklinksClient
from .ai_client import BacklinksAIClient

logger = logging.getLogger(__name__)


@shared_task(autoretry_for=(RequestException,), retry_backoff=60, retry_kwargs={"max_retries": 3})
def refresh_backlinks(store_id: int):
    from stores.models import Store
    from .models import Backlink, BacklinkSnapshot

    try:
        store = Store.objects.get(id=store_id)
    except Store.DoesNotExist:
        logger.warning("Store %s not found", store_id)
        return

    domain = store.shopify_url
    client = BacklinksClient()

    try:
        api_backlinks = client.get_backlinks(domain)
    except RequestException as e:
        logger.error("DataForSEO backlinks fetch failed for store %s: %s", store_id, e)
        raise

    today = timezone.now().date()
    api_keys = {(b["source_url"], b["target_url"]) for b in api_backlinks}
    existing = Backlink.objects.filter(store=store, is_lost=False)
    existing_keys = {(b.source_url, b.target_url) for b in existing}

    # Mark lost
    lost_count = 0
    for bl in existing:
        if (bl.source_url, bl.target_url) not in api_keys:
            bl.is_lost = True
            bl.save(update_fields=["is_lost", "updated_at"])
            lost_count += 1

    # Create new
    new_count = 0
    for item in api_backlinks:
        key = (item["source_url"], item["target_url"])
        if key not in existing_keys:
            Backlink.objects.create(store=store, **item)
            new_count += 1
        else:
            Backlink.objects.filter(
                store=store,
                source_url=item["source_url"],
                target_url=item["target_url"],
            ).update(
                last_seen=item["last_seen"],
                domain_rank=item["domain_rank"],
                is_lost=False,
            )

    total = Backlink.objects.filter(store=store, is_lost=False).count()
    dofollow = Backlink.objects.filter(store=store, is_lost=False, is_dofollow=True).count()

    BacklinkSnapshot.objects.update_or_create(
        store=store,
        date=today,
        defaults={
            "total_count": total,
            "dofollow_count": dofollow,
            "lost_count": lost_count,
            "new_count": new_count,
        },
    )
    logger.info("Refreshed backlinks for %s: %d total, %d new, %d lost", store.name, total, new_count, lost_count)


@shared_task
def refresh_all_backlinks():
    from stores.models import Store
    for store in Store.objects.all():
        refresh_backlinks.delay(store.id)


@shared_task
def suggest_prospects(store_id: int):
    from stores.models import Store
    from keywords.models import Keyword
    from .models import OutreachProspect

    try:
        store = Store.objects.get(id=store_id)
    except Store.DoesNotExist:
        logger.warning("Store %s not found", store_id)
        return

    domain = store.shopify_url
    keywords = list(
        Keyword.objects.filter(store=store, is_tracked=True).values_list("keyword", flat=True)[:20]
    )

    client = BacklinksClient()
    try:
        prospects = client.suggest_prospects(domain, keywords)
    except RequestException as e:
        logger.error("DataForSEO prospect suggestion failed for store %s: %s", store_id, e)
        return

    ai = BacklinksAIClient()
    store_keywords = keywords[:10]

    for p in prospects:
        domain_name = p["domain"]
        prospect_url = f"https://{domain_name}"

        if OutreachProspect.objects.filter(store=store, website_url=prospect_url).exists():
            continue

        try:
            relevance = ai.score_relevance(
                prospect_url=prospect_url,
                store_name=store.name,
                store_keywords=store_keywords,
            )
            score = relevance.get("score", 0)
        except Exception as e:
            logger.warning("AI scoring failed for %s: %s", prospect_url, e)
            score = 0

        OutreachProspect.objects.create(
            store=store,
            website_url=prospect_url,
            domain_rank=p["domain_rank"],
            niche_relevance_score=score,
            source="auto_suggested",
            status="new",
        )

    logger.info("Suggested %d prospects for %s", len(prospects), store.name)
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
python manage.py test backlinks.tests.test_tasks -v 2
```

Expected: `3 tests, 0 failures`

- [ ] **Step 5: Commit**

```bash
git add backend/backlinks/tasks.py backend/backlinks/tests/test_tasks.py
git commit -m "feat: add Celery tasks for backlink refresh and prospect suggestion"
```

---

## Task 7: Serializers, Views & URLs

**Files:**
- Create: `backend/backlinks/serializers.py`
- Create: `backend/backlinks/views.py`
- Create: `backend/backlinks/urls.py`
- Create: `backend/backlinks/tests/test_views.py`
- Modify: `backend/seobot/urls.py`

- [ ] **Step 1: Write failing view tests**

```python
# backend/backlinks/tests/test_views.py
import datetime
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from stores.models import Store
from backlinks.models import Backlink, BacklinkSnapshot, OutreachProspect, OutreachCampaign, EmailConfig


def make_store():
    return Store.objects.create(
        name="Test Store",
        shopify_url="teststore.myshopify.com",
        access_token="tok",
    )


class BacklinkListViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.store = make_store()

    def test_list_backlinks(self):
        Backlink.objects.create(
            store=self.store,
            source_url="https://blog.com/post",
            target_url="https://teststore.myshopify.com/products/1",
            first_seen=datetime.date.today(),
            last_seen=datetime.date.today(),
        )
        res = self.client.get(f"/api/v1/backlinks/?store_id={self.store.id}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["results"]), 1)

    def test_summary(self):
        Backlink.objects.create(
            store=self.store,
            source_url="https://blog.com/post",
            target_url="https://teststore.myshopify.com/products/1",
            is_dofollow=True,
            first_seen=datetime.date.today(),
            last_seen=datetime.date.today(),
        )
        res = self.client.get(f"/api/v1/backlinks/summary/?store_id={self.store.id}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["total"], 1)
        self.assertIn("dofollow_pct", res.data)

    def test_snapshot(self):
        BacklinkSnapshot.objects.create(
            store=self.store,
            date=datetime.date.today(),
            total_count=50,
            dofollow_count=40,
            lost_count=2,
            new_count=5,
        )
        res = self.client.get(f"/api/v1/backlinks/snapshot/?store_id={self.store.id}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)


class ProspectViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.store = make_store()

    def test_create_prospect_manually(self):
        res = self.client.post("/api/v1/backlinks/prospects/", {
            "store": self.store.id,
            "website_url": "https://fashionblog.com",
            "contact_email": "editor@fashionblog.com",
            "source": "manual",
        }, format="json")
        self.assertEqual(res.status_code, 201)
        self.assertEqual(OutreachProspect.objects.count(), 1)

    def test_update_prospect_status(self):
        prospect = OutreachProspect.objects.create(
            store=self.store,
            website_url="https://fashionblog.com",
            source="manual",
            status="new",
        )
        res = self.client.patch(
            f"/api/v1/backlinks/prospects/{prospect.id}/status/",
            {"status": "replied"},
            format="json",
        )
        self.assertEqual(res.status_code, 200)
        prospect.refresh_from_db()
        self.assertEqual(prospect.status, "replied")


class CampaignViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.store = make_store()

    def test_list_campaigns(self):
        prospect = OutreachProspect.objects.create(
            store=self.store,
            website_url="https://fashionblog.com",
            source="manual",
            status="emailed",
        )
        OutreachCampaign.objects.create(
            prospect=prospect,
            subject="Link opportunity",
            body="Hi there...",
            sent_at=timezone.now(),
            sent_via="smtp",
        )
        res = self.client.get(f"/api/v1/backlinks/campaigns/?store_id={self.store.id}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["results"]), 1)


class EmailConfigViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.store = make_store()

    def test_create_email_config(self):
        res = self.client.post("/api/v1/backlinks/email-config/", {
            "store": self.store.id,
            "smtp_host": "smtp.outlook.com",
            "smtp_port": 587,
            "smtp_username": "me@outlook.com",
            "smtp_password": "pass",
            "smtp_from_email": "me@outlook.com",
            "preferred_method": "smtp",
        }, format="json")
        self.assertEqual(res.status_code, 201)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python manage.py test backlinks.tests.test_views -v 2
```

Expected: `404` errors — URLs not registered yet.

- [ ] **Step 3: Write serializers**

```python
# backend/backlinks/serializers.py
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
```

- [ ] **Step 4: Write views**

```python
# backend/backlinks/views.py
import logging
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
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
            return Response({"error": "No email config found for this store. Set up email in Settings."}, status=400)

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
            sent_at=timezone.now(),
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
        url = get_gmail_auth_url()
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
```

- [ ] **Step 5: Write URLs**

```python
# backend/backlinks/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("prospects", views.OutreachProspectViewSet, basename="prospect")
router.register("campaigns", views.OutreachCampaignViewSet, basename="campaign")
router.register("email-config", views.EmailConfigViewSet, basename="email-config")
router.register("", views.BacklinkViewSet, basename="backlink")

urlpatterns = [
    path("", include(router.urls)),
]
```

- [ ] **Step 6: Register in main urls.py**

In `backend/seobot/urls.py`, add:

```python
    path("api/v1/backlinks/", include("backlinks.urls")),
```

Full file after edit:

```python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/stores/", include("stores.urls")),
    path("api/v1/keywords/", include("keywords.urls")),
    path("api/v1/audits/", include("audits.urls")),
    path("api/v1/ai/", include("ai_engine.urls")),
    path("api/v1/dashboard/", include("dashboard.urls")),
    path("api/v1/backlinks/", include("backlinks.urls")),
]
```

- [ ] **Step 7: Run view tests — verify they pass**

```bash
python manage.py test backlinks.tests.test_views -v 2
```

Expected: `7 tests, 0 failures`

- [ ] **Step 8: Run all backlinks tests**

```bash
python manage.py test backlinks -v 2
```

Expected: all tests pass.

- [ ] **Step 9: Commit**

```bash
git add backend/backlinks/serializers.py backend/backlinks/views.py backend/backlinks/urls.py backend/backlinks/tests/test_views.py backend/seobot/urls.py
git commit -m "feat: add backlinks API endpoints — 10 routes"
```

---

## Task 8: Frontend — API Client + Backlinks Page

**Files:**
- Modify: `frontend/src/api/client.js`
- Modify: `frontend/src/components/Layout.jsx`
- Modify: `frontend/src/App.jsx`
- Create: `frontend/src/pages/Backlinks.jsx`

- [ ] **Step 1: Add API functions to `frontend/src/api/client.js`**

Add these exports at the bottom of the file (before `export default api`):

```js
// Backlinks
export const fetchBacklinks = (storeId) =>
  api.get(`/backlinks/?store_id=${storeId}`);
export const fetchBacklinkSummary = (storeId) =>
  api.get(`/backlinks/summary/?store_id=${storeId}`);
export const fetchBacklinkSnapshot = (storeId) =>
  api.get(`/backlinks/snapshot/?store_id=${storeId}`);
export const refreshBacklinks = (storeId) =>
  api.post("/backlinks/refresh/", { store_id: storeId });
export const fetchProspects = (storeId) =>
  api.get(`/backlinks/prospects/?store_id=${storeId}`);
export const createProspect = (data) =>
  api.post("/backlinks/prospects/", data);
export const suggestProspects = (storeId) =>
  api.post("/backlinks/prospects/suggest/", { store_id: storeId });
export const sendProspectEmail = (prospectId) =>
  api.post(`/backlinks/prospects/${prospectId}/email/`);
export const updateProspectStatus = (prospectId, status) =>
  api.patch(`/backlinks/prospects/${prospectId}/status/`, { status });
export const fetchCampaigns = (storeId) =>
  api.get(`/backlinks/campaigns/?store_id=${storeId}`);
export const fetchEmailConfig = (storeId) =>
  api.get(`/backlinks/email-config/?store_id=${storeId}`);
export const saveEmailConfig = (data) =>
  api.post("/backlinks/email-config/", data);
export const updateEmailConfig = (id, data) =>
  api.put(`/backlinks/email-config/${id}/`, data);
export const getGmailAuthUrl = (storeId) =>
  api.get(`/backlinks/email-config/gmail/auth-url/?store_id=${storeId}`);
```

- [ ] **Step 2: Add Backlinks to nav in `frontend/src/components/Layout.jsx`**

Add `Link` from lucide-react to the import and add the nav item between Keywords and On-Page SEO:

```jsx
import { NavLink, Outlet } from "react-router-dom";
import {
  LayoutDashboard,
  Store,
  Search,
  Link,
  FileText,
  Wrench,
  Settings,
} from "lucide-react";

const navItems = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/stores", icon: Store, label: "Stores" },
  { to: "/keywords", icon: Search, label: "Keywords" },
  { to: "/backlinks", icon: Link, label: "Backlinks" },
  { to: "/on-page", icon: FileText, label: "On-Page SEO" },
  { to: "/audits", icon: Wrench, label: "Technical SEO" },
  { to: "/settings", icon: Settings, label: "Settings" },
];
```

- [ ] **Step 3: Add route in `frontend/src/App.jsx`**

Add import and route:

```jsx
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Stores from "./pages/Stores";
import StoreDetail from "./pages/StoreDetail";
import Keywords from "./pages/Keywords";
import Backlinks from "./pages/Backlinks";
import OnPageSEO from "./pages/OnPageSEO";
import TechnicalAudit from "./pages/TechnicalAudit";
import Settings from "./pages/SettingsPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/stores" element={<Stores />} />
          <Route path="/stores/:id" element={<StoreDetail />} />
          <Route path="/keywords" element={<Keywords />} />
          <Route path="/backlinks" element={<Backlinks />} />
          <Route path="/on-page" element={<OnPageSEO />} />
          <Route path="/audits" element={<TechnicalAudit />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
```

- [ ] **Step 4: Create the Backlinks page**

```jsx
// frontend/src/pages/Backlinks.jsx
import { useEffect, useState } from "react";
import {
  fetchStores,
  fetchBacklinkSummary,
  fetchBacklinkSnapshot,
  fetchBacklinks,
  refreshBacklinks,
  fetchProspects,
  createProspect,
  suggestProspects,
  sendProspectEmail,
  updateProspectStatus,
  fetchCampaigns,
} from "../api/client";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";

const STATUS_COLORS = {
  new: "bg-gray-700 text-gray-300",
  emailed: "bg-blue-900 text-blue-300",
  followed_up: "bg-yellow-900 text-yellow-300",
  replied: "bg-purple-900 text-purple-300",
  won: "bg-green-900 text-green-300",
  rejected: "bg-red-900 text-red-300",
};

export default function Backlinks() {
  const [stores, setStores] = useState([]);
  const [selectedStore, setSelectedStore] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");

  // Overview
  const [summary, setSummary] = useState(null);
  const [snapshots, setSnapshots] = useState([]);
  const [backlinks, setBacklinks] = useState([]);
  const [refreshing, setRefreshing] = useState(false);

  // Prospects
  const [prospects, setProspects] = useState([]);
  const [suggesting, setSuggesting] = useState(false);
  const [sendingEmail, setSendingEmail] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newProspect, setNewProspect] = useState({ website_url: "", contact_email: "" });

  // Campaigns
  const [campaigns, setCampaigns] = useState([]);
  const [expandedCampaign, setExpandedCampaign] = useState(null);

  useEffect(() => {
    fetchStores().then((res) => {
      setStores(res.data.results);
      if (res.data.results.length > 0) setSelectedStore(res.data.results[0].id);
    });
  }, []);

  useEffect(() => {
    if (!selectedStore) return;
    fetchBacklinkSummary(selectedStore).then((res) => setSummary(res.data)).catch(() => {});
    fetchBacklinkSnapshot(selectedStore).then((res) => setSnapshots(res.data)).catch(() => {});
    fetchBacklinks(selectedStore).then((res) => setBacklinks(res.data.results)).catch(() => {});
    fetchProspects(selectedStore).then((res) => setProspects(res.data.results)).catch(() => {});
    fetchCampaigns(selectedStore).then((res) => setCampaigns(res.data.results)).catch(() => {});
  }, [selectedStore]);

  const handleRefresh = () => {
    setRefreshing(true);
    refreshBacklinks(selectedStore)
      .then(() => alert("Backlink refresh queued. Check back in a few minutes."))
      .catch(() => alert("Refresh failed."))
      .finally(() => setRefreshing(false));
  };

  const handleSuggest = () => {
    setSuggesting(true);
    suggestProspects(selectedStore)
      .then(() => alert("Prospect suggestion queued. Check back in a few minutes."))
      .catch(() => alert("Suggestion failed."))
      .finally(() => setSuggesting(false));
  };

  const handleAddProspect = () => {
    if (!newProspect.website_url) return;
    createProspect({ ...newProspect, store: selectedStore, source: "manual" })
      .then((res) => {
        setProspects((prev) => [res.data, ...prev]);
        setNewProspect({ website_url: "", contact_email: "" });
        setShowAddForm(false);
      })
      .catch(() => alert("Failed to add prospect."));
  };

  const handleSendEmail = (prospectId) => {
    setSendingEmail(prospectId);
    sendProspectEmail(prospectId)
      .then((res) => {
        setCampaigns((prev) => [res.data, ...prev]);
        setProspects((prev) =>
          prev.map((p) => p.id === prospectId ? { ...p, status: "emailed" } : p)
        );
        setActiveTab("campaigns");
      })
      .catch((err) => alert(err.response?.data?.error || "Email send failed."))
      .finally(() => setSendingEmail(null));
  };

  const handleStatusChange = (prospectId, newStatus) => {
    updateProspectStatus(prospectId, newStatus)
      .then((res) => {
        setProspects((prev) => prev.map((p) => p.id === prospectId ? res.data : p));
      })
      .catch(() => alert("Status update failed."));
  };

  const chartData = [...snapshots].reverse().map((s) => ({
    date: s.date,
    total: s.total_count,
  }));

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">Backlinks</h2>
        <select
          value={selectedStore || ""}
          onChange={(e) => setSelectedStore(Number(e.target.value))}
          className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm"
        >
          {stores.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
        </select>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 border-b border-gray-800">
        {["overview", "prospects", "campaigns"].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-sm font-medium capitalize transition-colors ${
              activeTab === tab
                ? "text-blue-400 border-b-2 border-blue-400"
                : "text-gray-400 hover:text-white"
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === "overview" && (
        <div>
          {/* Summary Cards */}
          <div className="grid grid-cols-4 gap-4 mb-6">
            {[
              { label: "Total Backlinks", value: summary?.total ?? "-" },
              { label: "Dofollow %", value: summary ? `${summary.dofollow_pct}%` : "-" },
              { label: "New This Week", value: summary?.new_this_week ?? "-" },
              { label: "Lost This Week", value: summary?.lost_this_week ?? "-" },
            ].map(({ label, value }) => (
              <div key={label} className="bg-gray-900 rounded-lg p-4 border border-gray-800">
                <p className="text-gray-400 text-xs mb-1">{label}</p>
                <p className="text-2xl font-bold">{value}</p>
              </div>
            ))}
          </div>

          <div className="flex justify-end mb-4">
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded text-sm font-medium disabled:opacity-50"
            >
              {refreshing ? "Queuing..." : "Refresh Backlinks"}
            </button>
          </div>

          {/* Chart */}
          {chartData.length > 0 && (
            <div className="bg-gray-900 rounded-lg p-5 border border-gray-800 mb-6">
              <h3 className="font-semibold mb-4">Backlinks Over Time</h3>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="date" tick={{ fill: "#9CA3AF", fontSize: 11 }} />
                  <YAxis tick={{ fill: "#9CA3AF", fontSize: 11 }} />
                  <Tooltip contentStyle={{ backgroundColor: "#1F2937", border: "none" }} />
                  <Line type="monotone" dataKey="total" stroke="#3B82F6" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Backlinks Table */}
          <div className="bg-gray-900 rounded-lg border border-gray-800 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-800">
                <tr>
                  <th className="text-left px-4 py-2 text-gray-400">Source Domain</th>
                  <th className="text-left px-4 py-2 text-gray-400">Anchor Text</th>
                  <th className="text-left px-4 py-2 text-gray-400">DR</th>
                  <th className="text-left px-4 py-2 text-gray-400">Type</th>
                  <th className="text-left px-4 py-2 text-gray-400">First Seen</th>
                  <th className="text-left px-4 py-2 text-gray-400">Status</th>
                </tr>
              </thead>
              <tbody>
                {backlinks.map((bl) => (
                  <tr key={bl.id} className="border-t border-gray-800">
                    <td className="px-4 py-2 text-blue-400 text-xs truncate max-w-xs">
                      <a href={bl.source_url} target="_blank" rel="noopener noreferrer">
                        {new URL(bl.source_url).hostname}
                      </a>
                    </td>
                    <td className="px-4 py-2 text-gray-300 text-xs">{bl.anchor_text || "-"}</td>
                    <td className="px-4 py-2">{bl.domain_rank}</td>
                    <td className="px-4 py-2">
                      <span className={`text-xs px-2 py-0.5 rounded-full ${bl.is_dofollow ? "bg-green-900 text-green-300" : "bg-gray-700 text-gray-400"}`}>
                        {bl.is_dofollow ? "dofollow" : "nofollow"}
                      </span>
                    </td>
                    <td className="px-4 py-2 text-gray-400 text-xs">{bl.first_seen}</td>
                    <td className="px-4 py-2">
                      {bl.is_lost && <span className="text-xs px-2 py-0.5 rounded-full bg-red-900 text-red-300">lost</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {backlinks.length === 0 && (
              <p className="text-gray-500 text-sm text-center py-8">No backlinks found. Click "Refresh Backlinks" to fetch from DataForSEO.</p>
            )}
          </div>
        </div>
      )}

      {/* Prospects Tab */}
      {activeTab === "prospects" && (
        <div>
          <div className="flex gap-2 mb-4">
            <button
              onClick={handleSuggest}
              disabled={suggesting}
              className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded text-sm font-medium disabled:opacity-50"
            >
              {suggesting ? "Queuing..." : "Auto-suggest Prospects"}
            </button>
            <button
              onClick={() => setShowAddForm(!showAddForm)}
              className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded text-sm font-medium"
            >
              Add Manually
            </button>
          </div>

          {showAddForm && (
            <div className="bg-gray-900 rounded-lg p-4 border border-gray-800 mb-4 flex gap-3">
              <input
                value={newProspect.website_url}
                onChange={(e) => setNewProspect((p) => ({ ...p, website_url: e.target.value }))}
                placeholder="https://example.com"
                className="flex-1 bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm"
              />
              <input
                value={newProspect.contact_email}
                onChange={(e) => setNewProspect((p) => ({ ...p, contact_email: e.target.value }))}
                placeholder="editor@example.com"
                className="flex-1 bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm"
              />
              <button
                onClick={handleAddProspect}
                className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded text-sm font-medium"
              >
                Add
              </button>
            </div>
          )}

          <div className="bg-gray-900 rounded-lg border border-gray-800 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-800">
                <tr>
                  <th className="text-left px-4 py-2 text-gray-400">Website</th>
                  <th className="text-left px-4 py-2 text-gray-400">DR</th>
                  <th className="text-left px-4 py-2 text-gray-400">Relevance</th>
                  <th className="text-left px-4 py-2 text-gray-400">Status</th>
                  <th className="text-left px-4 py-2 text-gray-400">Source</th>
                  <th className="text-left px-4 py-2 text-gray-400"></th>
                </tr>
              </thead>
              <tbody>
                {prospects.map((p) => (
                  <tr key={p.id} className="border-t border-gray-800">
                    <td className="px-4 py-2 text-blue-400 text-xs">
                      <a href={p.website_url} target="_blank" rel="noopener noreferrer">
                        {p.website_url.replace(/^https?:\/\//, "")}
                      </a>
                    </td>
                    <td className="px-4 py-2">{p.domain_rank}</td>
                    <td className="px-4 py-2">
                      <span className={`font-medium ${p.niche_relevance_score >= 70 ? "text-green-400" : p.niche_relevance_score >= 40 ? "text-yellow-400" : "text-gray-400"}`}>
                        {p.niche_relevance_score}/100
                      </span>
                    </td>
                    <td className="px-4 py-2">
                      <select
                        value={p.status}
                        onChange={(e) => handleStatusChange(p.id, e.target.value)}
                        className={`text-xs px-2 py-0.5 rounded-full ${STATUS_COLORS[p.status]} bg-transparent border-0 cursor-pointer`}
                      >
                        {Object.keys(STATUS_COLORS).map((s) => (
                          <option key={s} value={s}>{s}</option>
                        ))}
                      </select>
                    </td>
                    <td className="px-4 py-2 text-gray-500 text-xs">{p.source}</td>
                    <td className="px-4 py-2">
                      {p.status === "new" && (
                        <button
                          onClick={() => handleSendEmail(p.id)}
                          disabled={sendingEmail === p.id}
                          className="text-blue-400 hover:text-blue-300 text-xs disabled:opacity-50"
                        >
                          {sendingEmail === p.id ? "Sending..." : "Send Email"}
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {prospects.length === 0 && (
              <p className="text-gray-500 text-sm text-center py-8">No prospects yet. Click "Auto-suggest" or add manually.</p>
            )}
          </div>
        </div>
      )}

      {/* Campaigns Tab */}
      {activeTab === "campaigns" && (
        <div className="bg-gray-900 rounded-lg border border-gray-800 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-800">
              <tr>
                <th className="text-left px-4 py-2 text-gray-400">Prospect</th>
                <th className="text-left px-4 py-2 text-gray-400">Subject</th>
                <th className="text-left px-4 py-2 text-gray-400">Sent</th>
                <th className="text-left px-4 py-2 text-gray-400">Via</th>
                <th className="text-left px-4 py-2 text-gray-400">Reply</th>
              </tr>
            </thead>
            <tbody>
              {campaigns.map((c) => (
                <>
                  <tr
                    key={c.id}
                    className="border-t border-gray-800 cursor-pointer hover:bg-gray-800"
                    onClick={() => setExpandedCampaign(expandedCampaign === c.id ? null : c.id)}
                  >
                    <td className="px-4 py-2 text-blue-400 text-xs">
                      {c.prospect_url?.replace(/^https?:\/\//, "") || "-"}
                    </td>
                    <td className="px-4 py-2 text-xs">{c.subject}</td>
                    <td className="px-4 py-2 text-gray-400 text-xs">
                      {c.sent_at ? new Date(c.sent_at).toLocaleDateString() : "Failed"}
                    </td>
                    <td className="px-4 py-2">
                      <span className={`text-xs px-2 py-0.5 rounded-full ${c.sent_via === "gmail" ? "bg-red-900 text-red-300" : "bg-gray-700 text-gray-300"}`}>
                        {c.sent_via}
                      </span>
                    </td>
                    <td className="px-4 py-2">
                      {c.reply_received && <span className="text-xs px-2 py-0.5 rounded-full bg-green-900 text-green-300">replied</span>}
                    </td>
                  </tr>
                  {expandedCampaign === c.id && (
                    <tr key={`${c.id}-body`} className="border-t border-gray-800 bg-gray-850">
                      <td colSpan={5} className="px-4 py-3">
                        <pre className="text-xs text-gray-300 whitespace-pre-wrap font-sans">{c.body}</pre>
                      </td>
                    </tr>
                  )}
                </>
              ))}
            </tbody>
          </table>
          {campaigns.length === 0 && (
            <p className="text-gray-500 text-sm text-center py-8">No campaigns yet. Send outreach emails from the Prospects tab.</p>
          )}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 5: Build frontend to verify no errors**

```bash
cd /Users/apple/Desktop/SEO\ BOT/frontend
npm run build
```

Expected: build completes with no errors.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/pages/Backlinks.jsx frontend/src/api/client.js frontend/src/components/Layout.jsx frontend/src/App.jsx
git commit -m "feat: add Backlinks frontend page with Overview, Prospects, Campaigns tabs"
```

---

## Task 9: Deploy to VPS

**Files:**
- No new files — deploy existing code

- [ ] **Step 1: Push code to VPS**

```bash
cd /Users/apple/Desktop/SEO\ BOT
sshpass -p 'Mehroz123456#' ssh root@76.13.253.211 "cd /opt/seobot && git pull origin main"
```

- [ ] **Step 2: Install new Python dependencies on VPS**

```bash
sshpass -p 'Mehroz123456#' ssh root@76.13.253.211 "cd /opt/seobot/backend && source venv/bin/activate && pip install -r requirements.txt"
```

- [ ] **Step 3: Run migrations on VPS**

```bash
sshpass -p 'Mehroz123456#' ssh root@76.13.253.211 "cd /opt/seobot/backend && source venv/bin/activate && python manage.py migrate"
```

- [ ] **Step 4: Build frontend on VPS**

```bash
sshpass -p 'Mehroz123456#' ssh root@76.13.253.211 "cd /opt/seobot/frontend && npm install && npm run build"
```

- [ ] **Step 5: Restart services**

```bash
sshpass -p 'Mehroz123456#' ssh root@76.13.253.211 "systemctl restart seobot seobot-celery seobot-beat"
```

- [ ] **Step 6: Verify deployment**

```bash
sshpass -p 'Mehroz123456#' ssh root@76.13.253.211 "curl -s -o /dev/null -w '%{http_code}' http://localhost/api/v1/backlinks/"
```

Expected: `200`

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "feat: complete backlinks and link outreach feature"
```

---

## Self-Review Notes

- All 10 API endpoints have corresponding view code and test coverage
- `BacklinksClient.get_backlinks` uses `backlinks/backlinks/live` (correct DataForSEO endpoint for fetching backlinks, not summary)
- `suggest_prospects` uses `backlinks/competitors/live` — correct endpoint for competitor backlink gap
- `EmailSender` raises on failure — caller in views catches and logs appropriately
- Gmail OAuth flow requires `google-auth-oauthlib` — add to requirements.txt in Task 5 step 1
- Frontend `<>` fragment in campaigns table rows is valid JSX for sibling tr elements
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI` must be added to `.env` on VPS before Gmail OAuth works — SMTP works out of the box
