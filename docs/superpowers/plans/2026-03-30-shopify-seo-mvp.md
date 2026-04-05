# Shopify SEO MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a working web dashboard that manages SEO for multiple Shopify stores — with store sync, keyword research, rank tracking, on-page meta editing with AI generation, technical site audits, and a health score dashboard.

**Architecture:** Django 5 backend with DRF REST API + Celery for background tasks + PostgreSQL. React 18 frontend with Vite + TailwindCSS. Monorepo with `backend/` and `frontend/` dirs. Shopify GraphQL API for store data. Claude API for AI content generation. SerpAPI for rank tracking. DataForSEO for keyword research and audit data. Google PageSpeed Insights for performance checks.

**Tech Stack:** Python 3.12, Django 5, DRF, Celery, Redis, PostgreSQL, React 18, Vite, TailwindCSS, Recharts, ShopifyAPI (GraphQL), Anthropic SDK, serpapi, dataforseo-client, django-fernet-encrypted-fields

---

## File Structure

```
SEO BOT/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── seobot/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   ├── asgi.py
│   │   └── celery.py
│   ├── stores/
│   │   ├── __init__.py
│   │   ├── models.py          # Store, Page, Image models
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── tasks.py           # Shopify sync Celery tasks
│   │   ├── shopify_client.py  # GraphQL client wrapper
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_models.py
│   │       ├── test_views.py
│   │       ├── test_shopify_client.py
│   │       └── test_tasks.py
│   ├── keywords/
│   │   ├── __init__.py
│   │   ├── models.py          # Keyword, RankHistory models
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── tasks.py           # Rank tracking, keyword research tasks
│   │   ├── dataforseo_client.py
│   │   ├── serp_client.py
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_models.py
│   │       ├── test_views.py
│   │       └── test_tasks.py
│   ├── audits/
│   │   ├── __init__.py
│   │   ├── models.py          # AuditRun, AuditIssue models
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── tasks.py           # Site crawl + audit tasks
│   │   ├── crawler.py         # Site crawler logic
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_models.py
│   │       ├── test_views.py
│   │       ├── test_crawler.py
│   │       └── test_tasks.py
│   ├── ai_engine/
│   │   ├── __init__.py
│   │   ├── client.py          # Claude API wrapper
│   │   ├── prompts.py         # Prompt templates for SEO tasks
│   │   ├── views.py           # AI generation endpoints
│   │   ├── urls.py
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_client.py
│   │       └── test_views.py
│   └── dashboard/
│       ├── __init__.py
│       ├── views.py           # Aggregated dashboard endpoints
│       ├── urls.py
│       └── tests/
│           ├── __init__.py
│           └── test_views.py
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── api/
│       │   └── client.js      # Axios instance + API helpers
│       ├── components/
│       │   ├── Layout.jsx     # Sidebar + main content shell
│       │   ├── StoreCard.jsx
│       │   ├── SEOScoreBadge.jsx
│       │   ├── MetaEditor.jsx
│       │   ├── KeywordTable.jsx
│       │   ├── AuditIssueList.jsx
│       │   └── RankChart.jsx
│       └── pages/
│           ├── Dashboard.jsx
│           ├── Stores.jsx
│           ├── StoreDetail.jsx
│           ├── Keywords.jsx
│           ├── OnPageSEO.jsx
│           ├── TechnicalAudit.jsx
│           └── Settings.jsx
└── docs/
```

---

### Task 1: Django Project Scaffolding

**Files:**
- Create: `backend/seobot/__init__.py`, `backend/seobot/settings.py`, `backend/seobot/urls.py`, `backend/seobot/wsgi.py`, `backend/seobot/asgi.py`, `backend/seobot/celery.py`
- Create: `backend/manage.py`, `backend/requirements.txt`, `backend/.env.example`

- [ ] **Step 1: Create backend directory and Django project**

```bash
cd "/Users/apple/Desktop/SEO BOT"
mkdir -p backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install django==5.1.* djangorestframework django-cors-headers celery redis django-celery-beat django-fernet-encrypted-fields python-dotenv psycopg2-binary
django-admin startproject seobot .
```

- [ ] **Step 2: Create requirements.txt**

Write `backend/requirements.txt`:
```
django==5.1.*
djangorestframework==3.15.*
django-cors-headers==4.6.*
celery==5.4.*
redis==5.2.*
django-celery-beat==2.9.*
django-fernet-encrypted-fields==0.6.*
python-dotenv==1.0.*
psycopg2-binary==2.9.*
anthropic==0.42.*
serpapi==0.1.*
dataforseo-client
ShopifyAPI==12.7.*
requests==2.32.*
beautifulsoup4==4.12.*
lxml==5.3.*
```

- [ ] **Step 3: Create .env.example**

Write `backend/.env.example`:
```
DEBUG=True
SECRET_KEY=change-me-to-a-random-string
DATABASE_URL=postgres://seobot:seobot@localhost:5432/seobot
REDIS_URL=redis://localhost:6379/0
ANTHROPIC_API_KEY=sk-ant-...
SERPAPI_KEY=...
DATAFORSEO_LOGIN=...
DATAFORSEO_PASSWORD=...
FIELD_ENCRYPTION_KEY=generate-with-python-c-from-cryptography.fernet-import-Fernet;print(Fernet.generate_key().decode())
```

- [ ] **Step 4: Configure Django settings**

Replace `backend/seobot/settings.py` with:
```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "insecure-dev-key-change-me")
DEBUG = os.getenv("DEBUG", "True") == "True"
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party
    "rest_framework",
    "corsheaders",
    "django_celery_beat",
    "encrypted_model_fields",
    # Local apps
    "stores",
    "keywords",
    "audits",
    "ai_engine",
    "dashboard",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "seobot.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "seobot.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "seobot"),
        "USER": os.getenv("DB_USER", "seobot"),
        "PASSWORD": os.getenv("DB_PASSWORD", "seobot"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]

# REST Framework
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
}

# Celery
CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# Encrypted fields
FIELD_ENCRYPTION_KEY = os.getenv("FIELD_ENCRYPTION_KEY", "")

# API Keys (loaded from env, used by service clients)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
DATAFORSEO_LOGIN = os.getenv("DATAFORSEO_LOGIN", "")
DATAFORSEO_PASSWORD = os.getenv("DATAFORSEO_PASSWORD", "")
```

- [ ] **Step 5: Configure Celery**

Write `backend/seobot/celery.py`:
```python
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seobot.settings")

app = Celery("seobot")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
```

Update `backend/seobot/__init__.py`:
```python
from .celery import app as celery_app

__all__ = ("celery_app",)
```

- [ ] **Step 6: Configure root URL conf**

Write `backend/seobot/urls.py`:
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
]
```

- [ ] **Step 7: Create all Django apps with empty scaffolds**

```bash
cd "/Users/apple/Desktop/SEO BOT/backend"
python manage.py startapp stores
python manage.py startapp keywords
python manage.py startapp audits
python manage.py startapp ai_engine
python manage.py startapp dashboard
mkdir -p stores/tests keywords/tests audits/tests ai_engine/tests dashboard/tests
touch stores/tests/__init__.py keywords/tests/__init__.py audits/tests/__init__.py ai_engine/tests/__init__.py dashboard/tests/__init__.py
touch stores/urls.py keywords/urls.py audits/urls.py ai_engine/urls.py dashboard/urls.py
```

Write empty URL files for each app (`stores/urls.py`, `keywords/urls.py`, `audits/urls.py`, `ai_engine/urls.py`, `dashboard/urls.py`):
```python
from django.urls import path

urlpatterns = []
```

- [ ] **Step 8: Verify Django starts**

```bash
cd "/Users/apple/Desktop/SEO BOT/backend"
python manage.py check
```
Expected: `System check identified no issues.`

- [ ] **Step 9: Commit**

```bash
git add backend/
git commit -m "feat: scaffold Django project with apps, Celery, and settings"
```

---

### Task 2: Store Models & Shopify GraphQL Client

**Files:**
- Create: `backend/stores/models.py`
- Create: `backend/stores/shopify_client.py`
- Create: `backend/stores/tests/test_models.py`
- Create: `backend/stores/tests/test_shopify_client.py`

- [ ] **Step 1: Write Store model tests**

Write `backend/stores/tests/test_models.py`:
```python
from django.test import TestCase
from stores.models import Store, Page, Image


class StoreModelTest(TestCase):
    def test_create_store(self):
        store = Store.objects.create(
            name="Test Store",
            shopify_url="test-store.myshopify.com",
            access_token="shpat_test123",
        )
        self.assertEqual(store.name, "Test Store")
        self.assertEqual(store.seo_score, 0)
        self.assertFalse(store.is_deleted)

    def test_soft_delete(self):
        store = Store.objects.create(
            name="Test Store",
            shopify_url="test-store.myshopify.com",
            access_token="shpat_test123",
        )
        store.soft_delete()
        store.refresh_from_db()
        self.assertTrue(store.is_deleted)
        self.assertEqual(Store.objects.active().count(), 0)

    def test_str(self):
        store = Store.objects.create(
            name="My Shop",
            shopify_url="my-shop.myshopify.com",
            access_token="shpat_test123",
        )
        self.assertEqual(str(store), "My Shop")


class PageModelTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(
            name="Test Store",
            shopify_url="test-store.myshopify.com",
            access_token="shpat_test123",
        )

    def test_create_page(self):
        page = Page.objects.create(
            store=self.store,
            shopify_id="gid://shopify/Product/123",
            url="/products/test-product",
            page_type="product",
            title="Test Product",
            meta_description="A test product",
        )
        self.assertEqual(page.store, self.store)
        self.assertEqual(page.content_score, 0)

    def test_page_types(self):
        for ptype in ["product", "collection", "page", "blog_post"]:
            page = Page.objects.create(
                store=self.store,
                shopify_id=f"gid://shopify/X/{ptype}",
                url=f"/{ptype}",
                page_type=ptype,
                title=f"Test {ptype}",
            )
            self.assertEqual(page.page_type, ptype)


class ImageModelTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(
            name="Test Store",
            shopify_url="test-store.myshopify.com",
            access_token="shpat_test123",
        )
        self.page = Page.objects.create(
            store=self.store,
            shopify_id="gid://shopify/Product/123",
            url="/products/test",
            page_type="product",
            title="Test",
        )

    def test_create_image(self):
        image = Image.objects.create(
            page=self.page,
            src="https://cdn.shopify.com/test.jpg",
            alt_text="",
        )
        self.assertEqual(image.ai_generated_alt, "")
        self.assertEqual(image.page, self.page)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd "/Users/apple/Desktop/SEO BOT/backend"
python manage.py test stores.tests.test_models -v 2
```
Expected: FAIL — models don't exist yet.

- [ ] **Step 3: Implement Store, Page, Image models**

Write `backend/stores/models.py`:
```python
from django.db import models


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class Store(models.Model):
    name = models.CharField(max_length=255)
    shopify_url = models.CharField(max_length=255, unique=True)
    access_token = models.CharField(max_length=255)
    seo_score = models.IntegerField(default=0)
    last_crawl_date = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ActiveManager()
    all_objects = models.Manager()

    def soft_delete(self):
        self.is_deleted = True
        self.save(update_fields=["is_deleted"])

    def active():
        return Store.objects.filter(is_deleted=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Page(models.Model):
    PAGE_TYPES = [
        ("product", "Product"),
        ("collection", "Collection"),
        ("page", "Page"),
        ("blog_post", "Blog Post"),
    ]

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="pages")
    shopify_id = models.CharField(max_length=255)
    url = models.CharField(max_length=500)
    page_type = models.CharField(max_length=20, choices=PAGE_TYPES)
    title = models.CharField(max_length=500, blank=True, default="")
    meta_description = models.TextField(blank=True, default="")
    h1 = models.CharField(max_length=500, blank=True, default="")
    content_score = models.IntegerField(default=0)
    last_audited = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["store", "shopify_id"]
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.title} ({self.page_type})"


class Image(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="images")
    src = models.URLField(max_length=1000)
    alt_text = models.TextField(blank=True, default="")
    ai_generated_alt = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Image for {self.page.title}"
```

- [ ] **Step 4: Make migrations and run tests**

```bash
cd "/Users/apple/Desktop/SEO BOT/backend"
python manage.py makemigrations stores
python manage.py test stores.tests.test_models -v 2
```
Expected: All tests PASS.

- [ ] **Step 5: Write Shopify GraphQL client tests**

Write `backend/stores/tests/test_shopify_client.py`:
```python
from unittest.mock import patch, MagicMock
from django.test import TestCase
from stores.shopify_client import ShopifyClient


class ShopifyClientTest(TestCase):
    def setUp(self):
        self.client = ShopifyClient(
            shop_url="test-store.myshopify.com",
            access_token="shpat_test123",
        )

    @patch("stores.shopify_client.requests.post")
    def test_fetch_products(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "products": {
                    "edges": [
                        {
                            "node": {
                                "id": "gid://shopify/Product/123",
                                "title": "Test Product",
                                "handle": "test-product",
                                "descriptionHtml": "<p>Description</p>",
                                "seo": {
                                    "title": "SEO Title",
                                    "description": "SEO Description",
                                },
                                "images": {
                                    "edges": [
                                        {
                                            "node": {
                                                "url": "https://cdn.shopify.com/test.jpg",
                                                "altText": "Alt text",
                                            }
                                        }
                                    ]
                                },
                            },
                            "cursor": "abc123",
                        }
                    ],
                    "pageInfo": {"hasNextPage": False},
                }
            }
        }
        mock_post.return_value = mock_response

        products = self.client.fetch_products()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]["id"], "gid://shopify/Product/123")
        self.assertEqual(products[0]["title"], "Test Product")
        self.assertEqual(products[0]["seo"]["title"], "SEO Title")

    @patch("stores.shopify_client.requests.post")
    def test_update_product_seo(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "productUpdate": {
                    "product": {"id": "gid://shopify/Product/123"},
                    "userErrors": [],
                }
            }
        }
        mock_post.return_value = mock_response

        result = self.client.update_product_seo(
            product_id="gid://shopify/Product/123",
            title="New SEO Title",
            description="New SEO Description",
        )
        self.assertEqual(result["product"]["id"], "gid://shopify/Product/123")
        self.assertEqual(result["userErrors"], [])
```

- [ ] **Step 6: Run Shopify client tests to verify they fail**

```bash
cd "/Users/apple/Desktop/SEO BOT/backend"
python manage.py test stores.tests.test_shopify_client -v 2
```
Expected: FAIL — `shopify_client` module doesn't exist yet.

- [ ] **Step 7: Implement Shopify GraphQL client**

Write `backend/stores/shopify_client.py`:
```python
import requests


PRODUCTS_QUERY = """
query ($cursor: String) {
    products(first: 50, after: $cursor) {
        edges {
            node {
                id
                title
                handle
                descriptionHtml
                seo {
                    title
                    description
                }
                images(first: 10) {
                    edges {
                        node {
                            url
                            altText
                        }
                    }
                }
            }
            cursor
        }
        pageInfo {
            hasNextPage
        }
    }
}
"""

COLLECTIONS_QUERY = """
query ($cursor: String) {
    collections(first: 50, after: $cursor) {
        edges {
            node {
                id
                title
                handle
                descriptionHtml
                seo {
                    title
                    description
                }
                image {
                    url
                    altText
                }
            }
            cursor
        }
        pageInfo {
            hasNextPage
        }
    }
}
"""

PAGES_QUERY = """
query ($cursor: String) {
    pages(first: 50, after: $cursor) {
        edges {
            node {
                id
                title
                handle
                body
                seo {
                    title
                    description
                }
            }
            cursor
        }
        pageInfo {
            hasNextPage
        }
    }
}
"""

BLOG_ARTICLES_QUERY = """
query ($cursor: String) {
    articles(first: 50, after: $cursor) {
        edges {
            node {
                id
                title
                handle
                contentHtml
                seo {
                    title
                    description
                }
                image {
                    url
                    altText
                }
                blog {
                    title
                }
            }
            cursor
        }
        pageInfo {
            hasNextPage
        }
    }
}
"""

UPDATE_PRODUCT_SEO_MUTATION = """
mutation productUpdate($input: ProductInput!) {
    productUpdate(input: $input) {
        product {
            id
        }
        userErrors {
            field
            message
        }
    }
}
"""

UPDATE_PRODUCT_IMAGE_ALT_MUTATION = """
mutation productUpdate($input: ProductInput!) {
    productUpdate(input: $input) {
        product {
            id
        }
        userErrors {
            field
            message
        }
    }
}
"""


class ShopifyClient:
    def __init__(self, shop_url: str, access_token: str):
        self.shop_url = shop_url
        self.access_token = access_token
        self.api_url = f"https://{shop_url}/admin/api/2024-10/graphql.json"
        self.headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": access_token,
        }

    def _execute(self, query: str, variables: dict = None) -> dict:
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        response = requests.post(self.api_url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def _paginate(self, query: str, resource_key: str) -> list:
        all_items = []
        cursor = None
        while True:
            result = self._execute(query, {"cursor": cursor})
            data = result["data"][resource_key]
            edges = data["edges"]
            all_items.extend([edge["node"] for edge in edges])
            if not data["pageInfo"]["hasNextPage"]:
                break
            cursor = edges[-1]["cursor"]
        return all_items

    def fetch_products(self) -> list:
        return self._paginate(PRODUCTS_QUERY, "products")

    def fetch_collections(self) -> list:
        return self._paginate(COLLECTIONS_QUERY, "collections")

    def fetch_pages(self) -> list:
        return self._paginate(PAGES_QUERY, "pages")

    def fetch_blog_articles(self) -> list:
        return self._paginate(BLOG_ARTICLES_QUERY, "articles")

    def update_product_seo(self, product_id: str, title: str, description: str) -> dict:
        variables = {
            "input": {
                "id": product_id,
                "seo": {
                    "title": title,
                    "description": description,
                },
            }
        }
        result = self._execute(UPDATE_PRODUCT_SEO_MUTATION, variables)
        return result["data"]["productUpdate"]

    def update_image_alt_text(self, product_id: str, image_id: str, alt_text: str) -> dict:
        variables = {
            "input": {
                "id": product_id,
                "images": [{"id": image_id, "altText": alt_text}],
            }
        }
        result = self._execute(UPDATE_PRODUCT_IMAGE_ALT_MUTATION, variables)
        return result["data"]["productUpdate"]
```

- [ ] **Step 8: Run all stores tests**

```bash
cd "/Users/apple/Desktop/SEO BOT/backend"
python manage.py test stores -v 2
```
Expected: All tests PASS.

- [ ] **Step 9: Commit**

```bash
git add backend/stores/
git commit -m "feat: add Store/Page/Image models and Shopify GraphQL client"
```

---

### Task 3: Store API Endpoints & Sync Task

**Files:**
- Create: `backend/stores/serializers.py`
- Create: `backend/stores/views.py`
- Create: `backend/stores/urls.py`
- Create: `backend/stores/tasks.py`
- Create: `backend/stores/admin.py`
- Create: `backend/stores/tests/test_views.py`
- Create: `backend/stores/tests/test_tasks.py`

- [ ] **Step 1: Write API endpoint tests**

Write `backend/stores/tests/test_views.py`:
```python
from django.test import TestCase
from rest_framework.test import APIClient
from stores.models import Store, Page


class StoreAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.store = Store.objects.create(
            name="Test Store",
            shopify_url="test-store.myshopify.com",
            access_token="shpat_test123",
        )

    def test_list_stores(self):
        response = self.client.get("/api/v1/stores/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Test Store")
        # access_token should not be in the response
        self.assertNotIn("access_token", response.data["results"][0])

    def test_create_store(self):
        response = self.client.post("/api/v1/stores/", {
            "name": "New Store",
            "shopify_url": "new-store.myshopify.com",
            "access_token": "shpat_new123",
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Store.objects.count(), 2)

    def test_retrieve_store(self):
        response = self.client.get(f"/api/v1/stores/{self.store.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Test Store")

    def test_delete_store_soft_deletes(self):
        response = self.client.delete(f"/api/v1/stores/{self.store.id}/")
        self.assertEqual(response.status_code, 204)
        self.store.refresh_from_db()
        self.assertTrue(self.store.is_deleted)
        # Should not appear in list
        response = self.client.get("/api/v1/stores/")
        self.assertEqual(len(response.data["results"]), 0)

    def test_list_store_pages(self):
        Page.objects.create(
            store=self.store,
            shopify_id="gid://shopify/Product/1",
            url="/products/test",
            page_type="product",
            title="Test Product",
        )
        response = self.client.get(f"/api/v1/stores/{self.store.id}/pages/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    def test_update_page_meta(self):
        page = Page.objects.create(
            store=self.store,
            shopify_id="gid://shopify/Product/1",
            url="/products/test",
            page_type="product",
            title="Old Title",
            meta_description="Old desc",
        )
        response = self.client.patch(
            f"/api/v1/stores/{self.store.id}/pages/{page.id}/",
            {"title": "New Title", "meta_description": "New desc"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        page.refresh_from_db()
        self.assertEqual(page.title, "New Title")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd "/Users/apple/Desktop/SEO BOT/backend"
python manage.py test stores.tests.test_views -v 2
```
Expected: FAIL — serializers/views/urls not implemented.

- [ ] **Step 3: Implement serializers**

Write `backend/stores/serializers.py`:
```python
from rest_framework import serializers
from .models import Store, Page, Image


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ["id", "src", "alt_text", "ai_generated_alt", "created_at"]


class PageSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = Page
        fields = [
            "id", "shopify_id", "url", "page_type", "title",
            "meta_description", "h1", "content_score", "last_audited",
            "images", "created_at", "updated_at",
        ]


class StoreListSerializer(serializers.ModelSerializer):
    page_count = serializers.IntegerField(source="pages.count", read_only=True)

    class Meta:
        model = Store
        fields = [
            "id", "name", "shopify_url", "seo_score",
            "last_crawl_date", "page_count", "created_at", "updated_at",
        ]


class StoreCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ["id", "name", "shopify_url", "access_token"]
        extra_kwargs = {"access_token": {"write_only": True}}


class StoreDetailSerializer(serializers.ModelSerializer):
    page_count = serializers.IntegerField(source="pages.count", read_only=True)

    class Meta:
        model = Store
        fields = [
            "id", "name", "shopify_url", "seo_score",
            "last_crawl_date", "page_count", "created_at", "updated_at",
        ]
```

- [ ] **Step 4: Implement views**

Write `backend/stores/views.py`:
```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Store, Page
from .serializers import (
    StoreListSerializer,
    StoreCreateSerializer,
    StoreDetailSerializer,
    PageSerializer,
)
from .tasks import sync_store


class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return StoreCreateSerializer
        if self.action == "retrieve":
            return StoreDetailSerializer
        return StoreListSerializer

    def destroy(self, request, *args, **kwargs):
        store = self.get_object()
        store.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def sync(self, request, pk=None):
        store = self.get_object()
        sync_store.delay(store.id)
        return Response({"status": "sync started"})


class PageViewSet(viewsets.ModelViewSet):
    serializer_class = PageSerializer

    def get_queryset(self):
        return Page.objects.filter(store_id=self.kwargs["store_pk"])
```

- [ ] **Step 5: Implement URLs**

Write `backend/stores/urls.py`:
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"", views.StoreViewSet, basename="store")

page_router = DefaultRouter()
page_router.register(r"", views.PageViewSet, basename="page")

urlpatterns = [
    path("<int:store_pk>/pages/", include(page_router.urls)),
    path("", include(router.urls)),
]
```

- [ ] **Step 6: Implement sync task (stubbed for now)**

Write `backend/stores/tasks.py`:
```python
from celery import shared_task
from .models import Store, Page, Image
from .shopify_client import ShopifyClient


@shared_task
def sync_store(store_id: int):
    store = Store.all_objects.get(id=store_id)
    client = ShopifyClient(store.shopify_url, store.access_token)

    # Sync products
    products = client.fetch_products()
    for product in products:
        page, _ = Page.objects.update_or_create(
            store=store,
            shopify_id=product["id"],
            defaults={
                "url": f"/products/{product['handle']}",
                "page_type": "product",
                "title": product["seo"]["title"] or product["title"],
                "meta_description": product["seo"]["description"] or "",
                "h1": product["title"],
            },
        )
        # Sync images
        for img_edge in product.get("images", {}).get("edges", []):
            img = img_edge["node"]
            Image.objects.update_or_create(
                page=page,
                src=img["url"],
                defaults={"alt_text": img.get("altText") or ""},
            )

    # Sync collections
    collections = client.fetch_collections()
    for collection in collections:
        Page.objects.update_or_create(
            store=store,
            shopify_id=collection["id"],
            defaults={
                "url": f"/collections/{collection['handle']}",
                "page_type": "collection",
                "title": collection["seo"]["title"] or collection["title"],
                "meta_description": collection["seo"]["description"] or "",
                "h1": collection["title"],
            },
        )

    # Sync pages
    pages = client.fetch_pages()
    for pg in pages:
        Page.objects.update_or_create(
            store=store,
            shopify_id=pg["id"],
            defaults={
                "url": f"/pages/{pg['handle']}",
                "page_type": "page",
                "title": pg["seo"]["title"] or pg["title"],
                "meta_description": pg["seo"]["description"] or "",
                "h1": pg["title"],
            },
        )

    # Sync blog articles
    articles = client.fetch_blog_articles()
    for article in articles:
        Page.objects.update_or_create(
            store=store,
            shopify_id=article["id"],
            defaults={
                "url": f"/blogs/{article['handle']}",
                "page_type": "blog_post",
                "title": article["seo"]["title"] or article["title"],
                "meta_description": article["seo"]["description"] or "",
                "h1": article["title"],
            },
        )


@shared_task
def sync_all_stores():
    for store in Store.objects.all():
        sync_store.delay(store.id)
```

- [ ] **Step 7: Register models in admin**

Write `backend/stores/admin.py`:
```python
from django.contrib import admin
from .models import Store, Page, Image


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ["name", "shopify_url", "seo_score", "last_crawl_date", "is_deleted"]
    list_filter = ["is_deleted"]


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ["title", "store", "page_type", "content_score", "last_audited"]
    list_filter = ["page_type", "store"]


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ["page", "src", "alt_text"]
```

- [ ] **Step 8: Run all stores tests**

```bash
cd "/Users/apple/Desktop/SEO BOT/backend"
python manage.py test stores -v 2
```
Expected: All tests PASS.

- [ ] **Step 9: Commit**

```bash
git add backend/stores/
git commit -m "feat: add Store API endpoints, serializers, sync task"
```

---

### Task 4: Keyword Models, DataForSEO Client & Research API

**Files:**
- Create: `backend/keywords/models.py`
- Create: `backend/keywords/dataforseo_client.py`
- Create: `backend/keywords/serp_client.py`
- Create: `backend/keywords/serializers.py`
- Create: `backend/keywords/views.py`
- Create: `backend/keywords/urls.py`
- Create: `backend/keywords/tasks.py`
- Create: `backend/keywords/tests/test_models.py`
- Create: `backend/keywords/tests/test_views.py`
- Create: `backend/keywords/tests/test_tasks.py`

- [ ] **Step 1: Write Keyword model tests**

Write `backend/keywords/tests/test_models.py`:
```python
from django.test import TestCase
from django.utils import timezone
from stores.models import Store
from keywords.models import Keyword, RankHistory


class KeywordModelTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(
            name="Test Store",
            shopify_url="test-store.myshopify.com",
            access_token="shpat_test123",
        )

    def test_create_keyword(self):
        kw = Keyword.objects.create(
            store=self.store,
            keyword="buy shoes online",
            search_volume=5000,
            difficulty=45,
            cpc=1.20,
            intent="transactional",
        )
        self.assertEqual(kw.keyword, "buy shoes online")
        self.assertTrue(kw.is_tracked)

    def test_rank_history(self):
        kw = Keyword.objects.create(
            store=self.store,
            keyword="buy shoes online",
            search_volume=5000,
        )
        rh = RankHistory.objects.create(
            keyword=kw,
            date=timezone.now().date(),
            position=15,
        )
        self.assertEqual(rh.keyword, kw)
        self.assertEqual(rh.position, 15)
        self.assertEqual(kw.rank_history.count(), 1)

    def test_keyword_str(self):
        kw = Keyword.objects.create(
            store=self.store,
            keyword="red sneakers",
            search_volume=1200,
        )
        self.assertEqual(str(kw), "red sneakers (Test Store)")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python manage.py test keywords.tests.test_models -v 2
```
Expected: FAIL.

- [ ] **Step 3: Implement Keyword and RankHistory models**

Write `backend/keywords/models.py`:
```python
from django.db import models
from stores.models import Store


class Keyword(models.Model):
    INTENT_CHOICES = [
        ("informational", "Informational"),
        ("transactional", "Transactional"),
        ("navigational", "Navigational"),
        ("commercial", "Commercial"),
    ]

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="keywords")
    keyword = models.CharField(max_length=500)
    search_volume = models.IntegerField(default=0)
    difficulty = models.IntegerField(default=0)
    cpc = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    intent = models.CharField(max_length=20, choices=INTENT_CHOICES, blank=True, default="")
    is_tracked = models.BooleanField(default=True)
    cluster_name = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["store", "keyword"]
        ordering = ["-search_volume"]

    def __str__(self):
        return f"{self.keyword} ({self.store.name})"


class RankHistory(models.Model):
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE, related_name="rank_history")
    date = models.DateField()
    position = models.IntegerField()
    serp_url = models.URLField(max_length=1000, blank=True, default="")
    serp_features = models.JSONField(default=list, blank=True)

    class Meta:
        unique_together = ["keyword", "date"]
        ordering = ["-date"]

    def __str__(self):
        return f"{self.keyword.keyword} - #{self.position} on {self.date}"
```

- [ ] **Step 4: Make migrations and run model tests**

```bash
python manage.py makemigrations keywords
python manage.py test keywords.tests.test_models -v 2
```
Expected: All PASS.

- [ ] **Step 5: Write DataForSEO client**

Write `backend/keywords/dataforseo_client.py`:
```python
import requests
from django.conf import settings


class DataForSEOClient:
    BASE_URL = "https://api.dataforseo.com/v3"

    def __init__(self):
        self.auth = (settings.DATAFORSEO_LOGIN, settings.DATAFORSEO_PASSWORD)

    def _post(self, endpoint: str, data: list) -> dict:
        response = requests.post(
            f"{self.BASE_URL}/{endpoint}",
            json=data,
            auth=self.auth,
        )
        response.raise_for_status()
        return response.json()

    def keyword_research(self, keyword: str, location_code: int = 2840, language_code: str = "en") -> list:
        """Get keyword suggestions with volume, difficulty, CPC."""
        data = [
            {
                "keyword": keyword,
                "location_code": location_code,
                "language_code": language_code,
                "include_seed_keyword": True,
                "limit": 50,
            }
        ]
        result = self._post("keywords_data/google_ads/keywords_for_keywords/live", data)
        keywords = []
        for task in result.get("tasks", []):
            for item in task.get("result", []) or []:
                for kw in item.get("items", []) or []:
                    keywords.append({
                        "keyword": kw.get("keyword", ""),
                        "search_volume": kw.get("search_volume", 0),
                        "difficulty": kw.get("keyword_info", {}).get("keyword_difficulty", 0)
                        if kw.get("keyword_info") else 0,
                        "cpc": kw.get("cpc", 0),
                        "competition_level": kw.get("competition_level", ""),
                    })
        return keywords
```

- [ ] **Step 6: Write SerpAPI client**

Write `backend/keywords/serp_client.py`:
```python
import serpapi
from django.conf import settings


class SerpClient:
    def __init__(self):
        self.client = serpapi.Client(api_key=settings.SERPAPI_KEY)

    def check_ranking(self, keyword: str, domain: str, location: str = "United States") -> dict:
        """Check where a domain ranks for a keyword."""
        results = self.client.search({
            "engine": "google",
            "q": keyword,
            "location": location,
            "num": 100,
        })
        position = None
        serp_url = ""
        serp_features = []

        # Check organic results
        for i, result in enumerate(results.get("organic_results", []), 1):
            if domain in result.get("link", ""):
                position = i
                serp_url = result.get("link", "")
                break

        # Collect SERP features present
        if results.get("answer_box"):
            serp_features.append("answer_box")
        if results.get("knowledge_graph"):
            serp_features.append("knowledge_graph")
        if results.get("related_questions"):
            serp_features.append("people_also_ask")
        if results.get("shopping_results"):
            serp_features.append("shopping")
        if results.get("local_results"):
            serp_features.append("local_pack")

        return {
            "position": position,
            "serp_url": serp_url,
            "serp_features": serp_features,
        }
```

- [ ] **Step 7: Write keyword API tests**

Write `backend/keywords/tests/test_views.py`:
```python
from unittest.mock import patch, MagicMock
from django.test import TestCase
from rest_framework.test import APIClient
from stores.models import Store
from keywords.models import Keyword, RankHistory
from django.utils import timezone


class KeywordAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.store = Store.objects.create(
            name="Test Store",
            shopify_url="test-store.myshopify.com",
            access_token="shpat_test123",
        )
        self.keyword = Keyword.objects.create(
            store=self.store,
            keyword="buy shoes online",
            search_volume=5000,
            difficulty=45,
        )

    def test_list_keywords(self):
        response = self.client.get(f"/api/v1/keywords/?store={self.store.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    def test_create_keyword(self):
        response = self.client.post("/api/v1/keywords/", {
            "store": self.store.id,
            "keyword": "red sneakers",
            "search_volume": 1200,
            "difficulty": 30,
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Keyword.objects.count(), 2)

    def test_rank_history(self):
        RankHistory.objects.create(
            keyword=self.keyword,
            date=timezone.now().date(),
            position=15,
        )
        response = self.client.get(f"/api/v1/keywords/{self.keyword.id}/rank-history/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["position"], 15)

    @patch("keywords.views.DataForSEOClient")
    def test_research_keywords(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client.keyword_research.return_value = [
            {"keyword": "shoes sale", "search_volume": 3000, "difficulty": 40, "cpc": 0.90, "competition_level": "MEDIUM"},
        ]
        mock_client_cls.return_value = mock_client

        response = self.client.post("/api/v1/keywords/research/", {"keyword": "shoes"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["keyword"], "shoes sale")
```

- [ ] **Step 8: Implement keyword serializers, views, URLs**

Write `backend/keywords/serializers.py`:
```python
from rest_framework import serializers
from .models import Keyword, RankHistory


class RankHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RankHistory
        fields = ["id", "date", "position", "serp_url", "serp_features"]


class KeywordSerializer(serializers.ModelSerializer):
    latest_position = serializers.SerializerMethodField()

    class Meta:
        model = Keyword
        fields = [
            "id", "store", "keyword", "search_volume", "difficulty",
            "cpc", "intent", "is_tracked", "cluster_name",
            "latest_position", "created_at",
        ]

    def get_latest_position(self, obj):
        latest = obj.rank_history.first()
        return latest.position if latest else None
```

Write `backend/keywords/views.py`:
```python
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from .models import Keyword, RankHistory
from .serializers import KeywordSerializer, RankHistorySerializer
from .dataforseo_client import DataForSEOClient


class KeywordViewSet(viewsets.ModelViewSet):
    serializer_class = KeywordSerializer

    def get_queryset(self):
        qs = Keyword.objects.all()
        store = self.request.query_params.get("store")
        if store:
            qs = qs.filter(store_id=store)
        return qs

    @action(detail=True, methods=["get"], url_path="rank-history")
    def rank_history(self, request, pk=None):
        keyword = self.get_object()
        history = keyword.rank_history.all()[:90]
        serializer = RankHistorySerializer(history, many=True)
        return Response(serializer.data)


@api_view(["POST"])
def research_keywords(request):
    seed_keyword = request.data.get("keyword", "")
    if not seed_keyword:
        return Response({"error": "keyword is required"}, status=400)
    client = DataForSEOClient()
    results = client.keyword_research(seed_keyword)
    return Response(results)
```

Write `backend/keywords/urls.py`:
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"", views.KeywordViewSet, basename="keyword")

urlpatterns = [
    path("research/", views.research_keywords, name="keyword-research"),
    path("", include(router.urls)),
]
```

- [ ] **Step 9: Implement rank tracking task**

Write `backend/keywords/tasks.py`:
```python
from celery import shared_task
from django.utils import timezone
from .models import Keyword, RankHistory
from .serp_client import SerpClient


@shared_task
def track_keyword_rankings(store_id: int):
    keywords = Keyword.objects.filter(store_id=store_id, is_tracked=True)
    if not keywords.exists():
        return

    store = keywords.first().store
    domain = store.shopify_url.replace(".myshopify.com", "")
    client = SerpClient()
    today = timezone.now().date()

    for kw in keywords:
        result = client.check_ranking(kw.keyword, domain)
        RankHistory.objects.update_or_create(
            keyword=kw,
            date=today,
            defaults={
                "position": result["position"] or 0,
                "serp_url": result["serp_url"],
                "serp_features": result["serp_features"],
            },
        )


@shared_task
def track_all_rankings():
    from stores.models import Store
    for store in Store.objects.all():
        track_keyword_rankings.delay(store.id)
```

- [ ] **Step 10: Run all keyword tests**

```bash
python manage.py test keywords -v 2
```
Expected: All PASS.

- [ ] **Step 11: Commit**

```bash
git add backend/keywords/
git commit -m "feat: add keyword research, rank tracking, DataForSEO & SerpAPI clients"
```

---

### Task 5: AI Engine (Claude API Integration)

**Files:**
- Create: `backend/ai_engine/client.py`
- Create: `backend/ai_engine/prompts.py`
- Create: `backend/ai_engine/views.py`
- Create: `backend/ai_engine/urls.py`
- Create: `backend/ai_engine/tests/test_client.py`
- Create: `backend/ai_engine/tests/test_views.py`

- [ ] **Step 1: Write AI client tests**

Write `backend/ai_engine/tests/test_client.py`:
```python
from unittest.mock import patch, MagicMock
from django.test import TestCase
from ai_engine.client import AIClient


class AIClientTest(TestCase):
    @patch("ai_engine.client.anthropic.Anthropic")
    def test_generate_meta_tags(self, mock_anthropic_cls):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='{"title": "Best Running Shoes | Free Shipping", "description": "Shop the best running shoes with free shipping. Top brands, great prices."}')]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_cls.return_value = mock_client

        ai = AIClient()
        result = ai.generate_meta_tags(
            product_title="Running Shoes",
            product_description="Great shoes for running",
            target_keywords=["running shoes", "best running shoes"],
        )
        self.assertIn("title", result)
        self.assertIn("description", result)

    @patch("ai_engine.client.anthropic.Anthropic")
    def test_generate_alt_text(self, mock_anthropic_cls):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Red leather running shoes with white sole, side view")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_cls.return_value = mock_client

        ai = AIClient()
        result = ai.generate_alt_text(
            product_title="Red Running Shoes",
            image_context="product photo",
        )
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    @patch("ai_engine.client.anthropic.Anthropic")
    def test_score_content(self, mock_anthropic_cls):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='{"score": 65, "recommendations": ["Add target keyword to H1", "Increase content length to 500+ words"]}')]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_cls.return_value = mock_client

        ai = AIClient()
        result = ai.score_content(
            page_title="Shoes",
            page_content="Buy shoes here.",
            target_keywords=["running shoes"],
        )
        self.assertIn("score", result)
        self.assertIn("recommendations", result)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python manage.py test ai_engine.tests.test_client -v 2
```
Expected: FAIL.

- [ ] **Step 3: Implement prompt templates**

Write `backend/ai_engine/prompts.py`:
```python
META_TAG_PROMPT = """You are an SEO expert. Generate an optimized meta title and meta description for this product page.

Product: {product_title}
Description: {product_description}
Target Keywords: {target_keywords}

Rules:
- Meta title: 50-60 characters, include primary keyword near the start
- Meta description: 150-160 characters, include a call to action, include primary keyword
- Make it compelling for users to click

Return ONLY a JSON object with "title" and "description" keys. No other text."""

ALT_TEXT_PROMPT = """You are an SEO expert. Generate descriptive alt text for a product image.

Product: {product_title}
Image Context: {image_context}

Rules:
- 80-125 characters
- Describe what is visible in the image
- Include relevant product details naturally
- Don't start with "image of" or "photo of"

Return ONLY the alt text string. No quotes, no other text."""

CONTENT_SCORE_PROMPT = """You are an SEO expert. Analyze this page content and score it for SEO quality.

Page Title: {page_title}
Target Keywords: {target_keywords}
Content:
{page_content}

Evaluate:
1. Keyword usage in title, headings, and body
2. Content length and depth
3. Readability
4. Internal linking opportunities
5. Missing elements (meta description, alt text, schema, etc.)

Return ONLY a JSON object with:
- "score": integer 0-100
- "recommendations": array of specific, actionable improvement strings

No other text."""

BULK_META_PROMPT = """You are an SEO expert. Generate optimized meta titles and descriptions for these products.

Products:
{products_json}

Rules:
- Meta title: 50-60 characters, include primary keyword near the start
- Meta description: 150-160 characters, include a call to action
- Each product should have unique, compelling copy

Return ONLY a JSON array where each item has "shopify_id", "title", and "description" keys. No other text."""
```

- [ ] **Step 4: Implement AI client**

Write `backend/ai_engine/client.py`:
```python
import json
import anthropic
from django.conf import settings
from .prompts import META_TAG_PROMPT, ALT_TEXT_PROMPT, CONTENT_SCORE_PROMPT, BULK_META_PROMPT


class AIClient:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-20250514"

    def _ask(self, prompt: str, max_tokens: int = 1024) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    def generate_meta_tags(self, product_title: str, product_description: str, target_keywords: list) -> dict:
        prompt = META_TAG_PROMPT.format(
            product_title=product_title,
            product_description=product_description,
            target_keywords=", ".join(target_keywords),
        )
        result = self._ask(prompt)
        return json.loads(result)

    def generate_alt_text(self, product_title: str, image_context: str) -> str:
        prompt = ALT_TEXT_PROMPT.format(
            product_title=product_title,
            image_context=image_context,
        )
        return self._ask(prompt, max_tokens=256).strip()

    def score_content(self, page_title: str, page_content: str, target_keywords: list) -> dict:
        prompt = CONTENT_SCORE_PROMPT.format(
            page_title=page_title,
            page_content=page_content,
            target_keywords=", ".join(target_keywords),
        )
        result = self._ask(prompt)
        return json.loads(result)

    def bulk_generate_meta(self, products: list) -> list:
        prompt = BULK_META_PROMPT.format(products_json=json.dumps(products, indent=2))
        result = self._ask(prompt, max_tokens=4096)
        return json.loads(result)
```

- [ ] **Step 5: Run AI client tests**

```bash
python manage.py test ai_engine.tests.test_client -v 2
```
Expected: All PASS.

- [ ] **Step 6: Write AI API view tests**

Write `backend/ai_engine/tests/test_views.py`:
```python
from unittest.mock import patch, MagicMock
from django.test import TestCase
from rest_framework.test import APIClient
from stores.models import Store, Page


class AIViewsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.store = Store.objects.create(
            name="Test Store",
            shopify_url="test-store.myshopify.com",
            access_token="shpat_test123",
        )
        self.page = Page.objects.create(
            store=self.store,
            shopify_id="gid://shopify/Product/123",
            url="/products/test",
            page_type="product",
            title="Test Product",
            meta_description="A test product",
        )

    @patch("ai_engine.views.AIClient")
    def test_generate_meta(self, mock_ai_cls):
        mock_ai = MagicMock()
        mock_ai.generate_meta_tags.return_value = {
            "title": "Best Test Product | Free Shipping",
            "description": "Shop our test product today. Great quality, fast delivery.",
        }
        mock_ai_cls.return_value = mock_ai

        response = self.client.post("/api/v1/ai/generate-meta/", {
            "page_id": self.page.id,
            "target_keywords": ["test product", "best test"],
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("title", response.data)

    @patch("ai_engine.views.AIClient")
    def test_generate_alt_text(self, mock_ai_cls):
        mock_ai = MagicMock()
        mock_ai.generate_alt_text.return_value = "Red test product in studio setting"
        mock_ai_cls.return_value = mock_ai

        response = self.client.post("/api/v1/ai/generate-alt/", {
            "page_id": self.page.id,
        }, format="json")
        self.assertEqual(response.status_code, 200)

    @patch("ai_engine.views.AIClient")
    def test_score_content(self, mock_ai_cls):
        mock_ai = MagicMock()
        mock_ai.score_content.return_value = {
            "score": 65,
            "recommendations": ["Add keyword to H1"],
        }
        mock_ai_cls.return_value = mock_ai

        response = self.client.post("/api/v1/ai/score-content/", {
            "page_id": self.page.id,
            "target_keywords": ["test product"],
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["score"], 65)
```

- [ ] **Step 7: Implement AI views and URLs**

Write `backend/ai_engine/views.py`:
```python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from stores.models import Page, Image
from .client import AIClient


@api_view(["POST"])
def generate_meta(request):
    page_id = request.data.get("page_id")
    target_keywords = request.data.get("target_keywords", [])
    if not page_id:
        return Response({"error": "page_id is required"}, status=400)

    page = Page.objects.get(id=page_id)
    ai = AIClient()
    result = ai.generate_meta_tags(
        product_title=page.title,
        product_description=page.meta_description,
        target_keywords=target_keywords,
    )
    return Response(result)


@api_view(["POST"])
def generate_alt_text(request):
    page_id = request.data.get("page_id")
    if not page_id:
        return Response({"error": "page_id is required"}, status=400)

    page = Page.objects.get(id=page_id)
    ai = AIClient()
    images = page.images.all()
    results = []
    for image in images:
        alt = ai.generate_alt_text(
            product_title=page.title,
            image_context=f"product image for {page.title}",
        )
        image.ai_generated_alt = alt
        image.save(update_fields=["ai_generated_alt"])
        results.append({"image_id": image.id, "alt_text": alt})
    return Response(results)


@api_view(["POST"])
def score_content(request):
    page_id = request.data.get("page_id")
    target_keywords = request.data.get("target_keywords", [])
    if not page_id:
        return Response({"error": "page_id is required"}, status=400)

    page = Page.objects.get(id=page_id)
    ai = AIClient()
    result = ai.score_content(
        page_title=page.title,
        page_content=page.meta_description,
        target_keywords=target_keywords,
    )
    page.content_score = result["score"]
    page.save(update_fields=["content_score"])
    return Response(result)


@api_view(["POST"])
def bulk_generate_meta(request):
    page_ids = request.data.get("page_ids", [])
    if not page_ids:
        return Response({"error": "page_ids is required"}, status=400)

    pages = Page.objects.filter(id__in=page_ids)
    products = [
        {
            "shopify_id": p.shopify_id,
            "title": p.title,
            "description": p.meta_description,
        }
        for p in pages
    ]
    ai = AIClient()
    results = ai.bulk_generate_meta(products)
    return Response(results)
```

Write `backend/ai_engine/urls.py`:
```python
from django.urls import path
from . import views

urlpatterns = [
    path("generate-meta/", views.generate_meta, name="generate-meta"),
    path("generate-alt/", views.generate_alt_text, name="generate-alt"),
    path("score-content/", views.score_content, name="score-content"),
    path("bulk-generate-meta/", views.bulk_generate_meta, name="bulk-generate-meta"),
]
```

- [ ] **Step 8: Run all AI engine tests**

```bash
python manage.py test ai_engine -v 2
```
Expected: All PASS.

- [ ] **Step 9: Commit**

```bash
git add backend/ai_engine/
git commit -m "feat: add Claude AI engine for meta tags, alt text, content scoring"
```

---

### Task 6: Technical SEO Auditor

**Files:**
- Create: `backend/audits/models.py`
- Create: `backend/audits/crawler.py`
- Create: `backend/audits/serializers.py`
- Create: `backend/audits/views.py`
- Create: `backend/audits/urls.py`
- Create: `backend/audits/tasks.py`
- Create: `backend/audits/tests/test_models.py`
- Create: `backend/audits/tests/test_crawler.py`
- Create: `backend/audits/tests/test_views.py`

- [ ] **Step 1: Write audit model tests**

Write `backend/audits/tests/test_models.py`:
```python
from django.test import TestCase
from django.utils import timezone
from stores.models import Store, Page
from audits.models import AuditRun, AuditIssue


class AuditModelTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(
            name="Test Store",
            shopify_url="test-store.myshopify.com",
            access_token="shpat_test123",
        )

    def test_create_audit_run(self):
        run = AuditRun.objects.create(
            store=self.store,
            status="completed",
            pages_crawled=50,
            issues_found=12,
        )
        self.assertEqual(run.store, self.store)
        self.assertEqual(run.status, "completed")

    def test_create_audit_issue(self):
        run = AuditRun.objects.create(store=self.store, status="completed")
        page = Page.objects.create(
            store=self.store,
            shopify_id="gid://shopify/Product/1",
            url="/products/test",
            page_type="product",
            title="Test",
        )
        issue = AuditIssue.objects.create(
            audit_run=run,
            page=page,
            issue_type="missing_meta_description",
            severity="warning",
            description="Page is missing a meta description",
            fix_suggestion="Add a compelling meta description of 150-160 characters",
        )
        self.assertEqual(issue.severity, "warning")
        self.assertEqual(run.issues.count(), 1)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python manage.py test audits.tests.test_models -v 2
```
Expected: FAIL.

- [ ] **Step 3: Implement audit models**

Write `backend/audits/models.py`:
```python
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
```

- [ ] **Step 4: Make migrations and run model tests**

```bash
python manage.py makemigrations audits
python manage.py test audits.tests.test_models -v 2
```
Expected: All PASS.

- [ ] **Step 5: Write crawler tests**

Write `backend/audits/tests/test_crawler.py`:
```python
from django.test import TestCase
from stores.models import Store, Page, Image
from audits.models import AuditRun
from audits.crawler import SiteAuditor


class SiteAuditorTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(
            name="Test Store",
            shopify_url="test-store.myshopify.com",
            access_token="shpat_test123",
        )
        self.audit_run = AuditRun.objects.create(store=self.store, status="running")

    def test_flag_missing_title(self):
        page = Page.objects.create(
            store=self.store,
            shopify_id="gid://shopify/Product/1",
            url="/products/no-title",
            page_type="product",
            title="",
        )
        auditor = SiteAuditor(self.store, self.audit_run)
        issues = auditor.check_page(page)
        issue_types = [i.issue_type for i in issues]
        self.assertIn("missing_title", issue_types)

    def test_flag_missing_meta_description(self):
        page = Page.objects.create(
            store=self.store,
            shopify_id="gid://shopify/Product/2",
            url="/products/no-desc",
            page_type="product",
            title="Has Title",
            meta_description="",
        )
        auditor = SiteAuditor(self.store, self.audit_run)
        issues = auditor.check_page(page)
        issue_types = [i.issue_type for i in issues]
        self.assertIn("missing_meta_description", issue_types)

    def test_flag_title_too_long(self):
        page = Page.objects.create(
            store=self.store,
            shopify_id="gid://shopify/Product/3",
            url="/products/long-title",
            page_type="product",
            title="A" * 70,
            meta_description="Good description here for this product page.",
        )
        auditor = SiteAuditor(self.store, self.audit_run)
        issues = auditor.check_page(page)
        issue_types = [i.issue_type for i in issues]
        self.assertIn("title_too_long", issue_types)

    def test_flag_missing_alt_text(self):
        page = Page.objects.create(
            store=self.store,
            shopify_id="gid://shopify/Product/4",
            url="/products/no-alt",
            page_type="product",
            title="Product",
            meta_description="Description",
        )
        Image.objects.create(page=page, src="https://cdn.shopify.com/img.jpg", alt_text="")
        auditor = SiteAuditor(self.store, self.audit_run)
        issues = auditor.check_page(page)
        issue_types = [i.issue_type for i in issues]
        self.assertIn("missing_alt_text", issue_types)

    def test_no_issues_for_good_page(self):
        page = Page.objects.create(
            store=self.store,
            shopify_id="gid://shopify/Product/5",
            url="/products/good",
            page_type="product",
            title="Great Product Title Here",
            meta_description="A compelling meta description that is the right length for SEO purposes and Google display.",
            h1="Great Product Title Here",
        )
        auditor = SiteAuditor(self.store, self.audit_run)
        issues = auditor.check_page(page)
        self.assertEqual(len(issues), 0)

    def test_detect_duplicate_titles(self):
        Page.objects.create(
            store=self.store, shopify_id="gid://shopify/Product/6",
            url="/products/dup1", page_type="product",
            title="Same Title", meta_description="Desc 1",
        )
        Page.objects.create(
            store=self.store, shopify_id="gid://shopify/Product/7",
            url="/products/dup2", page_type="product",
            title="Same Title", meta_description="Desc 2",
        )
        auditor = SiteAuditor(self.store, self.audit_run)
        issues = auditor.check_duplicates()
        issue_types = [i.issue_type for i in issues]
        self.assertIn("duplicate_title", issue_types)
```

- [ ] **Step 6: Implement site auditor crawler**

Write `backend/audits/crawler.py`:
```python
from audits.models import AuditIssue
from stores.models import Page


class SiteAuditor:
    def __init__(self, store, audit_run):
        self.store = store
        self.audit_run = audit_run

    def check_page(self, page: Page) -> list:
        issues = []

        # Missing title
        if not page.title.strip():
            issues.append(AuditIssue(
                audit_run=self.audit_run, page=page,
                issue_type="missing_title", severity="critical",
                description=f"Page {page.url} has no title tag",
                fix_suggestion="Add a descriptive title of 50-60 characters including your target keyword",
            ))

        # Title too long
        elif len(page.title) > 60:
            issues.append(AuditIssue(
                audit_run=self.audit_run, page=page,
                issue_type="title_too_long", severity="warning",
                description=f"Title is {len(page.title)} chars (max 60): {page.title[:80]}...",
                fix_suggestion="Shorten the title to 50-60 characters",
            ))

        # Title too short
        elif len(page.title) < 20:
            issues.append(AuditIssue(
                audit_run=self.audit_run, page=page,
                issue_type="title_too_short", severity="warning",
                description=f"Title is only {len(page.title)} chars: {page.title}",
                fix_suggestion="Expand the title to 50-60 characters with relevant keywords",
            ))

        # Missing meta description
        if not page.meta_description.strip():
            issues.append(AuditIssue(
                audit_run=self.audit_run, page=page,
                issue_type="missing_meta_description", severity="warning",
                description=f"Page {page.url} has no meta description",
                fix_suggestion="Add a compelling meta description of 150-160 characters",
            ))

        # Meta description too long
        elif len(page.meta_description) > 160:
            issues.append(AuditIssue(
                audit_run=self.audit_run, page=page,
                issue_type="meta_desc_too_long", severity="info",
                description=f"Meta description is {len(page.meta_description)} chars (max 160)",
                fix_suggestion="Shorten to 150-160 characters to prevent truncation in search results",
            ))

        # Missing H1
        if not page.h1.strip():
            issues.append(AuditIssue(
                audit_run=self.audit_run, page=page,
                issue_type="missing_h1", severity="warning",
                description=f"Page {page.url} has no H1 heading",
                fix_suggestion="Add an H1 that includes your primary keyword",
            ))

        # Missing alt text on images
        for image in page.images.all():
            if not image.alt_text.strip():
                issues.append(AuditIssue(
                    audit_run=self.audit_run, page=page,
                    issue_type="missing_alt_text", severity="warning",
                    description=f"Image {image.src} on {page.url} has no alt text",
                    fix_suggestion="Add descriptive alt text that describes the image content",
                ))

        # Save all issues
        AuditIssue.objects.bulk_create(issues)
        return issues

    def check_duplicates(self) -> list:
        issues = []
        pages = Page.objects.filter(store=self.store)

        # Duplicate titles
        titles = {}
        for page in pages:
            if page.title.strip():
                titles.setdefault(page.title, []).append(page)
        for title, pages_with_title in titles.items():
            if len(pages_with_title) > 1:
                for page in pages_with_title:
                    issues.append(AuditIssue(
                        audit_run=self.audit_run, page=page,
                        issue_type="duplicate_title", severity="warning",
                        description=f"Title '{title}' is used on {len(pages_with_title)} pages",
                        fix_suggestion="Create unique titles for each page",
                    ))

        # Duplicate meta descriptions
        descs = {}
        for page in Page.objects.filter(store=self.store):
            if page.meta_description.strip():
                descs.setdefault(page.meta_description, []).append(page)
        for desc, pages_with_desc in descs.items():
            if len(pages_with_desc) > 1:
                for page in pages_with_desc:
                    issues.append(AuditIssue(
                        audit_run=self.audit_run, page=page,
                        issue_type="duplicate_meta_description", severity="info",
                        description=f"Meta description is duplicated across {len(pages_with_desc)} pages",
                        fix_suggestion="Write unique meta descriptions for each page",
                    ))

        AuditIssue.objects.bulk_create(issues)
        return issues

    def run_full_audit(self) -> int:
        total_issues = 0
        pages = Page.objects.filter(store=self.store).prefetch_related("images")

        for page in pages:
            issues = self.check_page(page)
            total_issues += len(issues)

        dup_issues = self.check_duplicates()
        total_issues += len(dup_issues)

        return total_issues
```

- [ ] **Step 7: Run crawler tests**

```bash
python manage.py test audits.tests.test_crawler -v 2
```
Expected: All PASS.

- [ ] **Step 8: Implement audit views, serializers, URLs, tasks**

Write `backend/audits/serializers.py`:
```python
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
```

Write `backend/audits/views.py`:
```python
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import AuditRun
from .serializers import AuditRunSerializer
from .tasks import run_site_audit


@api_view(["POST"])
def trigger_audit(request):
    store_id = request.data.get("store_id")
    if not store_id:
        return Response({"error": "store_id is required"}, status=400)
    run_site_audit.delay(store_id)
    return Response({"status": "audit started"})


class AuditRunViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditRunSerializer

    def get_queryset(self):
        qs = AuditRun.objects.all()
        store = self.request.query_params.get("store")
        if store:
            qs = qs.filter(store_id=store)
        return qs
```

Write `backend/audits/urls.py`:
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"runs", views.AuditRunViewSet, basename="audit-run")

urlpatterns = [
    path("trigger/", views.trigger_audit, name="trigger-audit"),
    path("", include(router.urls)),
]
```

Write `backend/audits/tasks.py`:
```python
from celery import shared_task
from django.utils import timezone
from stores.models import Store
from .models import AuditRun
from .crawler import SiteAuditor


@shared_task
def run_site_audit(store_id: int):
    store = Store.objects.get(id=store_id)
    audit_run = AuditRun.objects.create(store=store, status="running")

    try:
        auditor = SiteAuditor(store, audit_run)
        total_issues = auditor.run_full_audit()

        pages_count = store.pages.count()
        audit_run.status = "completed"
        audit_run.completed_at = timezone.now()
        audit_run.pages_crawled = pages_count
        audit_run.issues_found = total_issues
        audit_run.save()

        # Update store last crawl date
        store.last_crawl_date = timezone.now()
        store.save(update_fields=["last_crawl_date"])
    except Exception as e:
        audit_run.status = "failed"
        audit_run.save(update_fields=["status"])
        raise


@shared_task
def audit_all_stores():
    for store in Store.objects.all():
        run_site_audit.delay(store.id)
```

- [ ] **Step 9: Run all audit tests**

```bash
python manage.py test audits -v 2
```
Expected: All PASS.

- [ ] **Step 10: Commit**

```bash
git add backend/audits/
git commit -m "feat: add technical SEO auditor with site crawler and issue detection"
```

---

### Task 7: Dashboard API (Aggregated Metrics)

**Files:**
- Create: `backend/dashboard/views.py`
- Create: `backend/dashboard/urls.py`
- Create: `backend/dashboard/tests/test_views.py`

- [ ] **Step 1: Write dashboard tests**

Write `backend/dashboard/tests/test_views.py`:
```python
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from stores.models import Store, Page
from keywords.models import Keyword, RankHistory
from audits.models import AuditRun, AuditIssue


class DashboardAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.store = Store.objects.create(
            name="Test Store",
            shopify_url="test-store.myshopify.com",
            access_token="shpat_test123",
            seo_score=72,
        )
        self.page = Page.objects.create(
            store=self.store,
            shopify_id="gid://shopify/Product/1",
            url="/products/test",
            page_type="product",
            title="Test Product",
            meta_description="Test description",
        )
        self.keyword = Keyword.objects.create(
            store=self.store,
            keyword="test keyword",
            search_volume=1000,
        )
        RankHistory.objects.create(
            keyword=self.keyword,
            date=timezone.now().date(),
            position=15,
        )

    def test_dashboard_overview(self):
        response = self.client.get("/api/v1/dashboard/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["stores"]), 1)
        self.assertEqual(response.data["stores"][0]["name"], "Test Store")
        self.assertEqual(response.data["stores"][0]["seo_score"], 72)
        self.assertIn("total_stores", response.data)
        self.assertIn("total_pages", response.data)
        self.assertIn("total_keywords", response.data)

    def test_store_dashboard(self):
        response = self.client.get(f"/api/v1/dashboard/{self.store.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["store"]["name"], "Test Store")
        self.assertIn("pages_count", response.data)
        self.assertIn("keywords_count", response.data)
        self.assertIn("top_keywords", response.data)
        self.assertIn("recent_audit", response.data)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python manage.py test dashboard.tests.test_views -v 2
```
Expected: FAIL.

- [ ] **Step 3: Implement dashboard views**

Write `backend/dashboard/views.py`:
```python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from stores.models import Store, Page
from keywords.models import Keyword, RankHistory
from audits.models import AuditRun


@api_view(["GET"])
def dashboard_overview(request):
    stores = Store.objects.all()
    store_data = []
    for store in stores:
        latest_audit = store.audit_runs.first()
        store_data.append({
            "id": store.id,
            "name": store.name,
            "shopify_url": store.shopify_url,
            "seo_score": store.seo_score,
            "pages_count": store.pages.count(),
            "keywords_count": store.keywords.count(),
            "last_crawl_date": store.last_crawl_date,
            "issues_count": latest_audit.issues_found if latest_audit else 0,
        })

    return Response({
        "total_stores": stores.count(),
        "total_pages": Page.objects.count(),
        "total_keywords": Keyword.objects.count(),
        "stores": store_data,
    })


@api_view(["GET"])
def store_dashboard(request, store_id):
    store = Store.objects.get(id=store_id)

    # Top keywords by position
    tracked_keywords = Keyword.objects.filter(store=store, is_tracked=True)[:10]
    top_keywords = []
    for kw in tracked_keywords:
        latest = kw.rank_history.first()
        top_keywords.append({
            "keyword": kw.keyword,
            "search_volume": kw.search_volume,
            "position": latest.position if latest else None,
        })

    # Recent audit
    recent_audit = store.audit_runs.first()
    audit_data = None
    if recent_audit:
        audit_data = {
            "id": recent_audit.id,
            "status": recent_audit.status,
            "started_at": recent_audit.started_at,
            "pages_crawled": recent_audit.pages_crawled,
            "issues_found": recent_audit.issues_found,
            "critical": recent_audit.issues.filter(severity="critical").count(),
            "warnings": recent_audit.issues.filter(severity="warning").count(),
        }

    return Response({
        "store": {
            "id": store.id,
            "name": store.name,
            "shopify_url": store.shopify_url,
            "seo_score": store.seo_score,
        },
        "pages_count": store.pages.count(),
        "keywords_count": store.keywords.count(),
        "top_keywords": top_keywords,
        "recent_audit": audit_data,
    })
```

Write `backend/dashboard/urls.py`:
```python
from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard_overview, name="dashboard-overview"),
    path("<int:store_id>/", views.store_dashboard, name="store-dashboard"),
]
```

- [ ] **Step 4: Run dashboard tests**

```bash
python manage.py test dashboard -v 2
```
Expected: All PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/dashboard/
git commit -m "feat: add dashboard API with overview and per-store metrics"
```

---

### Task 8: SEO Score Calculator & Celery Beat Scheduling

**Files:**
- Create: `backend/dashboard/tasks.py`
- Modify: `backend/seobot/settings.py` (add beat schedule)

- [ ] **Step 1: Write SEO score calculator tests**

Write `backend/dashboard/tests/test_score.py`:
```python
from django.test import TestCase
from stores.models import Store, Page, Image
from keywords.models import Keyword, RankHistory
from audits.models import AuditRun, AuditIssue
from dashboard.tasks import calculate_seo_score
from django.utils import timezone


class SEOScoreTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(
            name="Test Store",
            shopify_url="test-store.myshopify.com",
            access_token="shpat_test123",
        )

    def test_perfect_score_no_issues(self):
        # Store with pages, all good meta, tracked keywords ranking well
        for i in range(5):
            Page.objects.create(
                store=self.store,
                shopify_id=f"gid://shopify/Product/{i}",
                url=f"/products/product-{i}",
                page_type="product",
                title=f"Great Product {i} Title Here",
                meta_description=f"A compelling meta description for product {i} that is the right length.",
                h1=f"Great Product {i}",
            )
        audit = AuditRun.objects.create(store=self.store, status="completed", issues_found=0)
        kw = Keyword.objects.create(store=self.store, keyword="test", search_volume=1000)
        RankHistory.objects.create(keyword=kw, date=timezone.now().date(), position=5)

        score = calculate_seo_score(self.store.id)
        self.assertGreater(score, 70)

    def test_low_score_many_issues(self):
        page = Page.objects.create(
            store=self.store,
            shopify_id="gid://shopify/Product/1",
            url="/products/bad",
            page_type="product",
            title="",
            meta_description="",
        )
        audit = AuditRun.objects.create(store=self.store, status="completed", issues_found=5)
        for i in range(5):
            AuditIssue.objects.create(
                audit_run=audit, page=page,
                issue_type="missing_title", severity="critical",
                description="Missing title",
            )

        score = calculate_seo_score(self.store.id)
        self.assertLess(score, 50)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python manage.py test dashboard.tests.test_score -v 2
```
Expected: FAIL.

- [ ] **Step 3: Implement SEO score calculator**

Write `backend/dashboard/tasks.py`:
```python
from celery import shared_task
from stores.models import Store
from keywords.models import Keyword
from audits.models import AuditRun


@shared_task
def calculate_seo_score(store_id: int) -> int:
    store = Store.objects.get(id=store_id)
    score = 100

    # Factor 1: Audit issues (up to -40 points)
    latest_audit = store.audit_runs.filter(status="completed").first()
    if latest_audit:
        critical = latest_audit.issues.filter(severity="critical").count()
        warnings = latest_audit.issues.filter(severity="warning").count()
        pages = store.pages.count() or 1
        issue_ratio = (critical * 3 + warnings) / pages
        score -= min(40, int(issue_ratio * 20))
    else:
        score -= 20  # No audit run yet

    # Factor 2: Meta tag coverage (up to -30 points)
    total_pages = store.pages.count()
    if total_pages > 0:
        missing_title = store.pages.filter(title="").count()
        missing_desc = store.pages.filter(meta_description="").count()
        coverage = 1 - ((missing_title + missing_desc) / (total_pages * 2))
        score -= int((1 - coverage) * 30)
    else:
        score -= 15

    # Factor 3: Keyword rankings (up to -30 points)
    tracked = Keyword.objects.filter(store=store, is_tracked=True)
    if tracked.exists():
        ranked = 0
        top_10 = 0
        for kw in tracked:
            latest = kw.rank_history.first()
            if latest and latest.position > 0:
                ranked += 1
                if latest.position <= 10:
                    top_10 += 1
        if tracked.count() > 0:
            rank_ratio = ranked / tracked.count()
            top_ratio = top_10 / tracked.count() if ranked > 0 else 0
            score -= int((1 - rank_ratio) * 15)
            score -= int((1 - top_ratio) * 15)
    # No penalty if no keywords tracked yet

    score = max(0, min(100, score))
    store.seo_score = score
    store.save(update_fields=["seo_score"])
    return score


@shared_task
def recalculate_all_scores():
    for store in Store.objects.all():
        calculate_seo_score.delay(store.id)
```

- [ ] **Step 4: Run score tests**

```bash
python manage.py test dashboard.tests.test_score -v 2
```
Expected: All PASS.

- [ ] **Step 5: Add Celery Beat schedule to settings**

Append to `backend/seobot/settings.py`:
```python
# Celery Beat Schedule
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "sync-all-stores-daily": {
        "task": "stores.tasks.sync_all_stores",
        "schedule": crontab(hour=2, minute=0),
    },
    "track-all-rankings-daily": {
        "task": "keywords.tasks.track_all_rankings",
        "schedule": crontab(hour=4, minute=0),
    },
    "recalculate-seo-scores-daily": {
        "task": "dashboard.tasks.recalculate_all_scores",
        "schedule": crontab(hour=6, minute=0),
    },
    "audit-all-stores-weekly": {
        "task": "audits.tasks.audit_all_stores",
        "schedule": crontab(hour=3, minute=0, day_of_week=0),
    },
}
```

- [ ] **Step 6: Commit**

```bash
git add backend/dashboard/ backend/seobot/settings.py
git commit -m "feat: add SEO score calculator and Celery Beat daily/weekly schedules"
```

---

### Task 9: React Frontend Scaffolding

**Files:**
- Create: `frontend/package.json`, `frontend/vite.config.js`, `frontend/tailwind.config.js`, `frontend/postcss.config.js`, `frontend/index.html`
- Create: `frontend/src/main.jsx`, `frontend/src/App.jsx`
- Create: `frontend/src/api/client.js`
- Create: `frontend/src/components/Layout.jsx`

- [ ] **Step 1: Scaffold React + Vite project**

```bash
cd "/Users/apple/Desktop/SEO BOT"
npm create vite@latest frontend -- --template react
cd frontend
npm install
npm install -D tailwindcss @tailwindcss/vite
npm install react-router-dom axios recharts lucide-react
```

- [ ] **Step 2: Configure Vite for API proxy**

Write `frontend/vite.config.js`:
```javascript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
```

- [ ] **Step 3: Configure TailwindCSS**

Write `frontend/src/index.css`:
```css
@import "tailwindcss";
```

- [ ] **Step 4: Create API client**

Write `frontend/src/api/client.js`:
```javascript
import axios from "axios";

const api = axios.create({
  baseURL: "/api/v1",
  headers: { "Content-Type": "application/json" },
});

// Stores
export const fetchStores = () => api.get("/stores/");
export const createStore = (data) => api.post("/stores/", data);
export const deleteStore = (id) => api.delete(`/stores/${id}/`);
export const syncStore = (id) => api.post(`/stores/${id}/sync/`);
export const fetchPages = (storeId) => api.get(`/stores/${storeId}/pages/`);
export const updatePage = (storeId, pageId, data) =>
  api.patch(`/stores/${storeId}/pages/${pageId}/`, data);

// Keywords
export const fetchKeywords = (storeId) =>
  api.get(`/keywords/?store=${storeId}`);
export const createKeyword = (data) => api.post("/keywords/", data);
export const researchKeywords = (keyword) =>
  api.post("/keywords/research/", { keyword });
export const fetchRankHistory = (keywordId) =>
  api.get(`/keywords/${keywordId}/rank-history/`);

// Audits
export const triggerAudit = (storeId) =>
  api.post("/audits/trigger/", { store_id: storeId });
export const fetchAuditRuns = (storeId) =>
  api.get(`/audits/runs/?store=${storeId}`);

// AI
export const generateMeta = (pageId, targetKeywords) =>
  api.post("/ai/generate-meta/", { page_id: pageId, target_keywords: targetKeywords });
export const generateAltText = (pageId) =>
  api.post("/ai/generate-alt/", { page_id: pageId });
export const scoreContent = (pageId, targetKeywords) =>
  api.post("/ai/score-content/", { page_id: pageId, target_keywords: targetKeywords });
export const bulkGenerateMeta = (pageIds) =>
  api.post("/ai/bulk-generate-meta/", { page_ids: pageIds });

// Dashboard
export const fetchDashboard = () => api.get("/dashboard/");
export const fetchStoreDashboard = (storeId) =>
  api.get(`/dashboard/${storeId}/`);

export default api;
```

- [ ] **Step 5: Create Layout component**

Write `frontend/src/components/Layout.jsx`:
```jsx
import { NavLink, Outlet } from "react-router-dom";
import {
  LayoutDashboard,
  Store,
  Search,
  FileText,
  Wrench,
  Settings,
} from "lucide-react";

const navItems = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/stores", icon: Store, label: "Stores" },
  { to: "/keywords", icon: Search, label: "Keywords" },
  { to: "/on-page", icon: FileText, label: "On-Page SEO" },
  { to: "/audits", icon: Wrench, label: "Technical SEO" },
  { to: "/settings", icon: Settings, label: "Settings" },
];

export default function Layout() {
  return (
    <div className="flex h-screen bg-gray-950 text-gray-100">
      {/* Sidebar */}
      <nav className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col">
        <div className="p-6 border-b border-gray-800">
          <h1 className="text-xl font-bold text-white">SEO Bot</h1>
          <p className="text-sm text-gray-400 mt-1">Shopify SEO Manager</p>
        </div>
        <div className="flex-1 py-4">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                `flex items-center gap-3 px-6 py-3 text-sm transition-colors ${
                  isActive
                    ? "bg-blue-600/20 text-blue-400 border-r-2 border-blue-400"
                    : "text-gray-400 hover:text-white hover:bg-gray-800"
                }`
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </div>
      </nav>

      {/* Main content */}
      <main className="flex-1 overflow-auto p-8">
        <Outlet />
      </main>
    </div>
  );
}
```

- [ ] **Step 6: Create App with routes**

Write `frontend/src/App.jsx`:
```jsx
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Stores from "./pages/Stores";
import StoreDetail from "./pages/StoreDetail";
import Keywords from "./pages/Keywords";
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
          <Route path="/on-page" element={<OnPageSEO />} />
          <Route path="/audits" element={<TechnicalAudit />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
```

Update `frontend/src/main.jsx`:
```jsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>
);
```

- [ ] **Step 7: Create placeholder pages**

Write `frontend/src/pages/Dashboard.jsx`:
```jsx
import { useEffect, useState } from "react";
import { fetchDashboard } from "../api/client";
import StoreCard from "../components/StoreCard";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboard()
      .then((res) => setData(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-gray-400">Loading...</div>;
  if (!data) return <div className="text-red-400">Failed to load dashboard</div>;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Dashboard</h2>

      {/* Summary cards */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
          <p className="text-gray-400 text-sm">Total Stores</p>
          <p className="text-3xl font-bold mt-1">{data.total_stores}</p>
        </div>
        <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
          <p className="text-gray-400 text-sm">Total Pages</p>
          <p className="text-3xl font-bold mt-1">{data.total_pages}</p>
        </div>
        <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
          <p className="text-gray-400 text-sm">Tracked Keywords</p>
          <p className="text-3xl font-bold mt-1">{data.total_keywords}</p>
        </div>
      </div>

      {/* Store cards */}
      <h3 className="text-lg font-semibold mb-4">Your Stores</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {data.stores.map((store) => (
          <StoreCard key={store.id} store={store} />
        ))}
      </div>
    </div>
  );
}
```

Write `frontend/src/components/StoreCard.jsx`:
```jsx
import { Link } from "react-router-dom";
import SEOScoreBadge from "./SEOScoreBadge";

export default function StoreCard({ store }) {
  return (
    <Link
      to={`/stores/${store.id}`}
      className="bg-gray-900 rounded-lg p-5 border border-gray-800 hover:border-gray-600 transition-colors"
    >
      <div className="flex justify-between items-start mb-3">
        <div>
          <h4 className="font-semibold text-white">{store.name}</h4>
          <p className="text-sm text-gray-400">{store.shopify_url}</p>
        </div>
        <SEOScoreBadge score={store.seo_score} />
      </div>
      <div className="grid grid-cols-3 gap-2 text-sm">
        <div>
          <p className="text-gray-500">Pages</p>
          <p className="font-medium">{store.pages_count}</p>
        </div>
        <div>
          <p className="text-gray-500">Keywords</p>
          <p className="font-medium">{store.keywords_count}</p>
        </div>
        <div>
          <p className="text-gray-500">Issues</p>
          <p className="font-medium">{store.issues_count}</p>
        </div>
      </div>
    </Link>
  );
}
```

Write `frontend/src/components/SEOScoreBadge.jsx`:
```jsx
export default function SEOScoreBadge({ score }) {
  const color =
    score >= 80
      ? "text-green-400 border-green-400/30 bg-green-400/10"
      : score >= 50
        ? "text-yellow-400 border-yellow-400/30 bg-yellow-400/10"
        : "text-red-400 border-red-400/30 bg-red-400/10";

  return (
    <div className={`rounded-full w-12 h-12 flex items-center justify-center border text-sm font-bold ${color}`}>
      {score}
    </div>
  );
}
```

Write `frontend/src/pages/Stores.jsx`:
```jsx
import { useEffect, useState } from "react";
import { fetchStores, createStore, deleteStore, syncStore } from "../api/client";
import StoreCard from "../components/StoreCard";

export default function Stores() {
  const [stores, setStores] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", shopify_url: "", access_token: "" });

  const load = () => {
    fetchStores().then((res) => setStores(res.data.results));
  };

  useEffect(load, []);

  const handleCreate = (e) => {
    e.preventDefault();
    createStore(form).then(() => {
      setShowForm(false);
      setForm({ name: "", shopify_url: "", access_token: "" });
      load();
    });
  };

  const handleSync = (id) => {
    syncStore(id).then(() => alert("Sync started!"));
  };

  const handleDelete = (id) => {
    if (confirm("Delete this store?")) {
      deleteStore(id).then(load);
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Stores</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        >
          Add Store
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="bg-gray-900 rounded-lg p-5 border border-gray-800 mb-6">
          <div className="grid grid-cols-3 gap-4">
            <input
              placeholder="Store Name"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm"
              required
            />
            <input
              placeholder="store-name.myshopify.com"
              value={form.shopify_url}
              onChange={(e) => setForm({ ...form, shopify_url: e.target.value })}
              className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm"
              required
            />
            <input
              placeholder="Access Token (shpat_...)"
              value={form.access_token}
              onChange={(e) => setForm({ ...form, access_token: e.target.value })}
              className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm"
              type="password"
              required
            />
          </div>
          <button type="submit" className="mt-3 bg-green-600 hover:bg-green-700 px-4 py-2 rounded text-sm font-medium">
            Save Store
          </button>
        </form>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {stores.map((store) => (
          <div key={store.id} className="relative">
            <StoreCard store={store} />
            <div className="absolute top-3 right-3 flex gap-2">
              <button
                onClick={(e) => { e.preventDefault(); handleSync(store.id); }}
                className="text-xs bg-blue-600/20 text-blue-400 px-2 py-1 rounded hover:bg-blue-600/30"
              >
                Sync
              </button>
              <button
                onClick={(e) => { e.preventDefault(); handleDelete(store.id); }}
                className="text-xs bg-red-600/20 text-red-400 px-2 py-1 rounded hover:bg-red-600/30"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

Write `frontend/src/pages/StoreDetail.jsx`:
```jsx
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { fetchStoreDashboard } from "../api/client";
import SEOScoreBadge from "../components/SEOScoreBadge";

export default function StoreDetail() {
  const { id } = useParams();
  const [data, setData] = useState(null);

  useEffect(() => {
    fetchStoreDashboard(id).then((res) => setData(res.data));
  }, [id]);

  if (!data) return <div className="text-gray-400">Loading...</div>;

  return (
    <div>
      <div className="flex items-center gap-4 mb-6">
        <SEOScoreBadge score={data.store.seo_score} />
        <div>
          <h2 className="text-2xl font-bold">{data.store.name}</h2>
          <p className="text-gray-400">{data.store.shopify_url}</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-8">
        <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
          <p className="text-gray-400 text-sm">Pages</p>
          <p className="text-2xl font-bold">{data.pages_count}</p>
        </div>
        <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
          <p className="text-gray-400 text-sm">Tracked Keywords</p>
          <p className="text-2xl font-bold">{data.keywords_count}</p>
        </div>
      </div>

      {/* Top Keywords */}
      <h3 className="text-lg font-semibold mb-3">Top Keywords</h3>
      <div className="bg-gray-900 rounded-lg border border-gray-800 overflow-hidden mb-8">
        <table className="w-full text-sm">
          <thead className="bg-gray-800">
            <tr>
              <th className="text-left px-4 py-2 text-gray-400">Keyword</th>
              <th className="text-left px-4 py-2 text-gray-400">Volume</th>
              <th className="text-left px-4 py-2 text-gray-400">Position</th>
            </tr>
          </thead>
          <tbody>
            {data.top_keywords.map((kw, i) => (
              <tr key={i} className="border-t border-gray-800">
                <td className="px-4 py-2">{kw.keyword}</td>
                <td className="px-4 py-2">{kw.search_volume}</td>
                <td className="px-4 py-2">
                  {kw.position ? `#${kw.position}` : "Not ranked"}
                </td>
              </tr>
            ))}
            {data.top_keywords.length === 0 && (
              <tr><td colSpan={3} className="px-4 py-4 text-gray-500 text-center">No keywords tracked yet</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Recent Audit */}
      <h3 className="text-lg font-semibold mb-3">Latest Audit</h3>
      {data.recent_audit ? (
        <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
          <div className="grid grid-cols-4 gap-4">
            <div>
              <p className="text-gray-400 text-sm">Status</p>
              <p className="font-medium capitalize">{data.recent_audit.status}</p>
            </div>
            <div>
              <p className="text-gray-400 text-sm">Pages Crawled</p>
              <p className="font-medium">{data.recent_audit.pages_crawled}</p>
            </div>
            <div>
              <p className="text-gray-400 text-sm">Critical</p>
              <p className="font-medium text-red-400">{data.recent_audit.critical}</p>
            </div>
            <div>
              <p className="text-gray-400 text-sm">Warnings</p>
              <p className="font-medium text-yellow-400">{data.recent_audit.warnings}</p>
            </div>
          </div>
        </div>
      ) : (
        <p className="text-gray-500">No audits run yet</p>
      )}
    </div>
  );
}
```

Write `frontend/src/pages/Keywords.jsx`:
```jsx
import { useEffect, useState } from "react";
import {
  fetchStores,
  fetchKeywords,
  createKeyword,
  researchKeywords,
  fetchRankHistory,
} from "../api/client";
import RankChart from "../components/RankChart";

export default function Keywords() {
  const [stores, setStores] = useState([]);
  const [selectedStore, setSelectedStore] = useState(null);
  const [keywords, setKeywords] = useState([]);
  const [researchResults, setResearchResults] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [searching, setSearching] = useState(false);
  const [selectedKw, setSelectedKw] = useState(null);
  const [rankHistory, setRankHistory] = useState([]);

  useEffect(() => {
    fetchStores().then((res) => {
      setStores(res.data.results);
      if (res.data.results.length > 0) setSelectedStore(res.data.results[0].id);
    });
  }, []);

  useEffect(() => {
    if (selectedStore) {
      fetchKeywords(selectedStore).then((res) => setKeywords(res.data.results));
    }
  }, [selectedStore]);

  const handleResearch = () => {
    setSearching(true);
    researchKeywords(searchTerm)
      .then((res) => setResearchResults(res.data))
      .finally(() => setSearching(false));
  };

  const handleTrack = (kw) => {
    createKeyword({
      store: selectedStore,
      keyword: kw.keyword,
      search_volume: kw.search_volume,
      difficulty: kw.difficulty,
      cpc: kw.cpc || 0,
    }).then(() => fetchKeywords(selectedStore).then((res) => setKeywords(res.data.results)));
  };

  const handleViewHistory = (kwId) => {
    setSelectedKw(kwId);
    fetchRankHistory(kwId).then((res) => setRankHistory(res.data));
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Keyword Research & Tracking</h2>

      {/* Store selector */}
      <select
        value={selectedStore || ""}
        onChange={(e) => setSelectedStore(Number(e.target.value))}
        className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm mb-6"
      >
        {stores.map((s) => (
          <option key={s.id} value={s.id}>{s.name}</option>
        ))}
      </select>

      {/* Research */}
      <div className="bg-gray-900 rounded-lg p-5 border border-gray-800 mb-6">
        <h3 className="font-semibold mb-3">Keyword Research</h3>
        <div className="flex gap-2">
          <input
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Enter seed keyword..."
            className="flex-1 bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm"
            onKeyDown={(e) => e.key === "Enter" && handleResearch()}
          />
          <button
            onClick={handleResearch}
            disabled={searching}
            className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded text-sm font-medium disabled:opacity-50"
          >
            {searching ? "Searching..." : "Research"}
          </button>
        </div>
        {researchResults.length > 0 && (
          <table className="w-full text-sm mt-4">
            <thead>
              <tr className="text-gray-400 text-left">
                <th className="py-2">Keyword</th>
                <th className="py-2">Volume</th>
                <th className="py-2">Difficulty</th>
                <th className="py-2">CPC</th>
                <th className="py-2"></th>
              </tr>
            </thead>
            <tbody>
              {researchResults.map((kw, i) => (
                <tr key={i} className="border-t border-gray-800">
                  <td className="py-2">{kw.keyword}</td>
                  <td className="py-2">{kw.search_volume}</td>
                  <td className="py-2">{kw.difficulty}</td>
                  <td className="py-2">${kw.cpc || 0}</td>
                  <td className="py-2">
                    <button
                      onClick={() => handleTrack(kw)}
                      className="text-blue-400 hover:text-blue-300 text-xs"
                    >
                      Track
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Tracked Keywords */}
      <h3 className="font-semibold mb-3">Tracked Keywords</h3>
      <div className="bg-gray-900 rounded-lg border border-gray-800 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-800">
            <tr>
              <th className="text-left px-4 py-2 text-gray-400">Keyword</th>
              <th className="text-left px-4 py-2 text-gray-400">Volume</th>
              <th className="text-left px-4 py-2 text-gray-400">Difficulty</th>
              <th className="text-left px-4 py-2 text-gray-400">Position</th>
              <th className="text-left px-4 py-2 text-gray-400"></th>
            </tr>
          </thead>
          <tbody>
            {keywords.map((kw) => (
              <tr key={kw.id} className="border-t border-gray-800">
                <td className="px-4 py-2">{kw.keyword}</td>
                <td className="px-4 py-2">{kw.search_volume}</td>
                <td className="px-4 py-2">{kw.difficulty}</td>
                <td className="px-4 py-2">
                  {kw.latest_position ? `#${kw.latest_position}` : "-"}
                </td>
                <td className="px-4 py-2">
                  <button
                    onClick={() => handleViewHistory(kw.id)}
                    className="text-blue-400 hover:text-blue-300 text-xs"
                  >
                    History
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Rank History Chart */}
      {selectedKw && rankHistory.length > 0 && (
        <div className="mt-6">
          <RankChart data={rankHistory} />
        </div>
      )}
    </div>
  );
}
```

Write `frontend/src/components/RankChart.jsx`:
```jsx
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function RankChart({ data }) {
  const chartData = [...data].reverse().map((d) => ({
    date: d.date,
    position: d.position,
  }));

  return (
    <div className="bg-gray-900 rounded-lg p-5 border border-gray-800">
      <h4 className="font-semibold mb-4">Rank History</h4>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={chartData}>
          <XAxis dataKey="date" stroke="#6b7280" fontSize={12} />
          <YAxis reversed stroke="#6b7280" fontSize={12} domain={[1, "auto"]} />
          <Tooltip
            contentStyle={{ backgroundColor: "#1f2937", border: "1px solid #374151", borderRadius: "8px" }}
            labelStyle={{ color: "#9ca3af" }}
          />
          <Line type="monotone" dataKey="position" stroke="#3b82f6" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
```

Write `frontend/src/pages/OnPageSEO.jsx`:
```jsx
import { useEffect, useState } from "react";
import { fetchStores, fetchPages, updatePage, generateMeta, bulkGenerateMeta } from "../api/client";
import MetaEditor from "../components/MetaEditor";

export default function OnPageSEO() {
  const [stores, setStores] = useState([]);
  const [selectedStore, setSelectedStore] = useState(null);
  const [pages, setPages] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchStores().then((res) => {
      setStores(res.data.results);
      if (res.data.results.length > 0) setSelectedStore(res.data.results[0].id);
    });
  }, []);

  useEffect(() => {
    if (selectedStore) {
      setLoading(true);
      fetchPages(selectedStore)
        .then((res) => setPages(res.data.results))
        .finally(() => setLoading(false));
    }
  }, [selectedStore]);

  const handleSave = (pageId, data) => {
    updatePage(selectedStore, pageId, data).then(() => {
      setPages((prev) =>
        prev.map((p) => (p.id === pageId ? { ...p, ...data } : p))
      );
    });
  };

  const handleAIGenerate = async (pageId) => {
    const res = await generateMeta(pageId, []);
    return res.data;
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">On-Page SEO</h2>

      <select
        value={selectedStore || ""}
        onChange={(e) => setSelectedStore(Number(e.target.value))}
        className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm mb-6"
      >
        {stores.map((s) => (
          <option key={s.id} value={s.id}>{s.name}</option>
        ))}
      </select>

      {loading ? (
        <p className="text-gray-400">Loading pages...</p>
      ) : (
        <MetaEditor pages={pages} onSave={handleSave} onAIGenerate={handleAIGenerate} />
      )}
    </div>
  );
}
```

Write `frontend/src/components/MetaEditor.jsx`:
```jsx
import { useState } from "react";

function titleColor(title) {
  if (!title) return "border-red-500/50 bg-red-500/5";
  if (title.length > 60) return "border-yellow-500/50 bg-yellow-500/5";
  if (title.length < 20) return "border-yellow-500/50 bg-yellow-500/5";
  return "border-green-500/50 bg-green-500/5";
}

function descColor(desc) {
  if (!desc) return "border-red-500/50 bg-red-500/5";
  if (desc.length > 160) return "border-yellow-500/50 bg-yellow-500/5";
  if (desc.length < 50) return "border-yellow-500/50 bg-yellow-500/5";
  return "border-green-500/50 bg-green-500/5";
}

export default function MetaEditor({ pages, onSave, onAIGenerate }) {
  const [editing, setEditing] = useState({});
  const [generating, setGenerating] = useState({});

  const startEdit = (page) => {
    setEditing((prev) => ({
      ...prev,
      [page.id]: { title: page.title, meta_description: page.meta_description },
    }));
  };

  const handleGenerate = async (pageId) => {
    setGenerating((prev) => ({ ...prev, [pageId]: true }));
    try {
      const result = await onAIGenerate(pageId);
      setEditing((prev) => ({
        ...prev,
        [pageId]: { title: result.title, meta_description: result.description },
      }));
    } finally {
      setGenerating((prev) => ({ ...prev, [pageId]: false }));
    }
  };

  const handleSave = (pageId) => {
    onSave(pageId, editing[pageId]);
    setEditing((prev) => {
      const next = { ...prev };
      delete next[pageId];
      return next;
    });
  };

  return (
    <div className="space-y-3">
      {pages.map((page) => (
        <div key={page.id} className="bg-gray-900 rounded-lg p-4 border border-gray-800">
          <div className="flex justify-between items-start mb-2">
            <div>
              <span className="text-xs text-gray-500 uppercase">{page.page_type}</span>
              <p className="text-sm text-gray-400">{page.url}</p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => handleGenerate(page.id)}
                disabled={generating[page.id]}
                className="text-xs bg-purple-600/20 text-purple-400 px-2 py-1 rounded hover:bg-purple-600/30 disabled:opacity-50"
              >
                {generating[page.id] ? "Generating..." : "AI Generate"}
              </button>
              {!editing[page.id] && (
                <button
                  onClick={() => startEdit(page)}
                  className="text-xs bg-blue-600/20 text-blue-400 px-2 py-1 rounded hover:bg-blue-600/30"
                >
                  Edit
                </button>
              )}
            </div>
          </div>

          {editing[page.id] ? (
            <div className="space-y-2">
              <div>
                <label className="text-xs text-gray-500">Title ({editing[page.id].title.length}/60)</label>
                <input
                  value={editing[page.id].title}
                  onChange={(e) =>
                    setEditing((prev) => ({
                      ...prev,
                      [page.id]: { ...prev[page.id], title: e.target.value },
                    }))
                  }
                  className={`w-full border rounded px-3 py-2 text-sm bg-transparent ${titleColor(editing[page.id].title)}`}
                />
              </div>
              <div>
                <label className="text-xs text-gray-500">
                  Meta Description ({editing[page.id].meta_description.length}/160)
                </label>
                <textarea
                  value={editing[page.id].meta_description}
                  onChange={(e) =>
                    setEditing((prev) => ({
                      ...prev,
                      [page.id]: { ...prev[page.id], meta_description: e.target.value },
                    }))
                  }
                  rows={2}
                  className={`w-full border rounded px-3 py-2 text-sm bg-transparent ${descColor(editing[page.id].meta_description)}`}
                />
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => handleSave(page.id)}
                  className="text-xs bg-green-600 hover:bg-green-700 px-3 py-1 rounded font-medium"
                >
                  Save
                </button>
                <button
                  onClick={() =>
                    setEditing((prev) => {
                      const next = { ...prev };
                      delete next[page.id];
                      return next;
                    })
                  }
                  className="text-xs text-gray-400 hover:text-white px-3 py-1"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <div>
              <p className={`text-sm px-2 py-1 rounded border mb-1 ${titleColor(page.title)}`}>
                {page.title || <span className="text-red-400 italic">Missing title</span>}
              </p>
              <p className={`text-sm px-2 py-1 rounded border ${descColor(page.meta_description)}`}>
                {page.meta_description || <span className="text-red-400 italic">Missing description</span>}
              </p>
            </div>
          )}
        </div>
      ))}
      {pages.length === 0 && (
        <p className="text-gray-500 text-center py-8">No pages found. Sync your store first.</p>
      )}
    </div>
  );
}
```

Write `frontend/src/pages/TechnicalAudit.jsx`:
```jsx
import { useEffect, useState } from "react";
import { fetchStores, triggerAudit, fetchAuditRuns } from "../api/client";
import AuditIssueList from "../components/AuditIssueList";

export default function TechnicalAudit() {
  const [stores, setStores] = useState([]);
  const [selectedStore, setSelectedStore] = useState(null);
  const [auditRuns, setAuditRuns] = useState([]);
  const [selectedRun, setSelectedRun] = useState(null);

  useEffect(() => {
    fetchStores().then((res) => {
      setStores(res.data.results);
      if (res.data.results.length > 0) setSelectedStore(res.data.results[0].id);
    });
  }, []);

  useEffect(() => {
    if (selectedStore) {
      fetchAuditRuns(selectedStore).then((res) => {
        setAuditRuns(res.data.results);
        if (res.data.results.length > 0) setSelectedRun(res.data.results[0]);
      });
    }
  }, [selectedStore]);

  const handleTrigger = () => {
    triggerAudit(selectedStore).then(() => alert("Audit started! Refresh in a moment."));
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Technical SEO Audit</h2>
        <button
          onClick={handleTrigger}
          className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg text-sm font-medium"
        >
          Run Audit
        </button>
      </div>

      <select
        value={selectedStore || ""}
        onChange={(e) => setSelectedStore(Number(e.target.value))}
        className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm mb-6"
      >
        {stores.map((s) => (
          <option key={s.id} value={s.id}>{s.name}</option>
        ))}
      </select>

      {selectedRun && (
        <>
          {/* Summary cards */}
          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
              <p className="text-gray-400 text-sm">Status</p>
              <p className="font-medium capitalize">{selectedRun.status}</p>
            </div>
            <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
              <p className="text-gray-400 text-sm">Critical</p>
              <p className="text-2xl font-bold text-red-400">{selectedRun.issue_summary?.critical || 0}</p>
            </div>
            <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
              <p className="text-gray-400 text-sm">Warnings</p>
              <p className="text-2xl font-bold text-yellow-400">{selectedRun.issue_summary?.warning || 0}</p>
            </div>
            <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
              <p className="text-gray-400 text-sm">Info</p>
              <p className="text-2xl font-bold text-blue-400">{selectedRun.issue_summary?.info || 0}</p>
            </div>
          </div>

          <AuditIssueList issues={selectedRun.issues || []} />
        </>
      )}

      {!selectedRun && (
        <p className="text-gray-500 text-center py-8">No audits run yet. Click "Run Audit" to start.</p>
      )}
    </div>
  );
}
```

Write `frontend/src/components/AuditIssueList.jsx`:
```jsx
const severityStyles = {
  critical: "bg-red-500/10 border-red-500/30 text-red-400",
  warning: "bg-yellow-500/10 border-yellow-500/30 text-yellow-400",
  info: "bg-blue-500/10 border-blue-500/30 text-blue-400",
};

export default function AuditIssueList({ issues }) {
  const grouped = {};
  issues.forEach((issue) => {
    if (!grouped[issue.issue_type]) grouped[issue.issue_type] = [];
    grouped[issue.issue_type].push(issue);
  });

  return (
    <div className="space-y-4">
      {Object.entries(grouped).map(([type, items]) => (
        <details key={type} className="bg-gray-900 rounded-lg border border-gray-800">
          <summary className="px-4 py-3 cursor-pointer flex justify-between items-center">
            <span className="font-medium text-sm">
              {type.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
            </span>
            <span className={`text-xs px-2 py-1 rounded border ${severityStyles[items[0].severity]}`}>
              {items.length} {items[0].severity}
            </span>
          </summary>
          <div className="px-4 pb-3 space-y-2">
            {items.map((issue) => (
              <div key={issue.id} className="text-sm border-t border-gray-800 pt-2">
                <p className="text-gray-300">{issue.description}</p>
                {issue.page_url && <p className="text-gray-500 text-xs">{issue.page_url}</p>}
                {issue.fix_suggestion && (
                  <p className="text-green-400/70 text-xs mt-1">Fix: {issue.fix_suggestion}</p>
                )}
              </div>
            ))}
          </div>
        </details>
      ))}
      {issues.length === 0 && (
        <p className="text-gray-500 text-center py-4">No issues found!</p>
      )}
    </div>
  );
}
```

Write `frontend/src/pages/SettingsPage.jsx`:
```jsx
export default function SettingsPage() {
  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Settings</h2>
      <div className="bg-gray-900 rounded-lg p-5 border border-gray-800">
        <p className="text-gray-400">
          API keys and scheduling are configured via environment variables on the server.
          See <code className="text-blue-400">.env.example</code> for required keys.
        </p>
        <div className="mt-4 space-y-2 text-sm">
          <p className="text-gray-300">Required API Keys:</p>
          <ul className="list-disc list-inside text-gray-400 space-y-1">
            <li>ANTHROPIC_API_KEY — Claude AI for content generation</li>
            <li>SERPAPI_KEY — Rank tracking</li>
            <li>DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD — Keyword research</li>
            <li>Shopify access tokens — Per-store (added in Stores page)</li>
          </ul>
        </div>
        <div className="mt-4 space-y-2 text-sm">
          <p className="text-gray-300">Automated Schedule:</p>
          <ul className="list-disc list-inside text-gray-400 space-y-1">
            <li>2:00 AM — Sync all stores from Shopify</li>
            <li>4:00 AM — Track keyword rankings</li>
            <li>6:00 AM — Recalculate SEO scores</li>
            <li>Sunday 3:00 AM — Full site audit</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 8: Verify frontend builds**

```bash
cd "/Users/apple/Desktop/SEO BOT/frontend"
npm run build
```
Expected: Build succeeds with no errors.

- [ ] **Step 9: Commit**

```bash
cd "/Users/apple/Desktop/SEO BOT"
git add frontend/
git commit -m "feat: add React frontend with dashboard, stores, keywords, on-page, audit pages"
```

---

### Task 10: Final Integration & Run Verification

**Files:**
- Create: `backend/.gitignore`
- Create: `frontend/.gitignore` (if not created by Vite)

- [ ] **Step 1: Create backend .gitignore**

Write `backend/.gitignore`:
```
venv/
__pycache__/
*.pyc
.env
db.sqlite3
*.egg-info/
```

- [ ] **Step 2: Create root .gitignore**

Write `.gitignore`:
```
# Python
__pycache__/
*.pyc
venv/
.env

# Node
node_modules/
dist/

# IDE
.vscode/
.idea/
*.swp
```

- [ ] **Step 3: Run all backend tests**

```bash
cd "/Users/apple/Desktop/SEO BOT/backend"
source venv/bin/activate
python manage.py test -v 2
```
Expected: All tests pass.

- [ ] **Step 4: Run migrations**

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

- [ ] **Step 5: Verify backend starts**

```bash
python manage.py runserver
```
Expected: Server starts on http://localhost:8000

- [ ] **Step 6: Verify frontend starts**

```bash
cd "/Users/apple/Desktop/SEO BOT/frontend"
npm run dev
```
Expected: Dev server starts on http://localhost:5173, dashboard loads.

- [ ] **Step 7: Commit**

```bash
cd "/Users/apple/Desktop/SEO BOT"
git add .gitignore backend/.gitignore
git commit -m "chore: add gitignore files"
```

- [ ] **Step 8: Final commit — tag as MVP**

```bash
git tag v0.1.0-mvp
```
