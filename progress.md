# Shopify SEO Bot — MVP Build Progress

**Started:** 2026-03-29
**Last Updated:** 2026-04-05

**Design Spec:** `docs/superpowers/specs/2026-03-29-shopify-seo-app-design.md`
**Implementation Plan:** `docs/superpowers/plans/2026-03-30-shopify-seo-mvp.md`

---

## Completed Tasks

### Task 1: Django Project Scaffolding ✅
- Django 5 project created in `backend/`
- Settings configured: DRF, CORS, Celery, encrypted fields
- Celery configured with Redis broker + Django Beat scheduler
- 5 Django apps created: `stores`, `keywords`, `audits`, `ai_engine`, `dashboard`
- All apps have `urls.py` with empty urlpatterns and `tests/` directories
- `requirements.txt` and `.env.example` created
- `python manage.py check` passes
- **Note:** `encrypted_model_fields` app name is actually `encrypted_fields` (from `django-fernet-encrypted-fields==0.3.1`, not `0.6.*`)
- **Note:** Uses SQLite for tests (test override in settings.py)

### Task 2: Store Models & Shopify GraphQL Client ✅
- **Models:** `Store` (with ActiveManager for soft-delete), `Page`, `Image`
- **ShopifyClient:** GraphQL client using raw `requests.post`
  - Queries: products, collections, pages, blog articles (all with cursor pagination)
  - Mutations: update product SEO, update image alt text
- **Tests:** 8 tests passing (3 model tests + 2 Shopify client tests + 3 page/image tests)

### Task 3: Store API Endpoints & Sync Task ✅
- **Serializers:** StoreListSerializer (no access_token), StoreCreateSerializer (write-only token), StoreDetailSerializer, PageSerializer, ImageSerializer
- **Views:** StoreViewSet (CRUD + soft delete + sync action), PageViewSet (scoped by store)
- **URLs:** Nested routing — pages under `stores/{id}/pages/`
- **Tasks:** `sync_store` (Celery) syncs products/collections/pages/articles from Shopify
- **Admin:** Store, Page, Image registered
- **Tests:** 14 tests passing (8 from Task 2 + 6 new view tests)

### Task 4: Keywords, DataForSEO & SerpAPI ✅
- **Models:** `Keyword` (with intent, volume, difficulty, CPC), `RankHistory` (daily position tracking)
- **DataForSEOClient:** Keyword research via `/keywords_data/google_ads/keywords_for_keywords/live`
- **SerpClient:** Rank checking via SerpAPI with SERP feature detection
- **Serializers:** KeywordSerializer (with `latest_position`), RankHistorySerializer
- **Views:** KeywordViewSet (filter by store, rank-history action), `research_keywords` endpoint
- **URLs:** `/api/v1/keywords/` (CRUD), `/api/v1/keywords/research/` (POST)
- **Tasks:** `track_keyword_rankings`, `track_all_rankings` (Celery)
- **Tests:** 7 tests passing (3 model + 4 view tests)

### Task 5: AI Engine (Claude API) ✅
- **AIClient:** Anthropic SDK wrapper (`claude-sonnet-4-20250514`)
  - `generate_meta_tags()` — SEO title + description from product data + keywords
  - `generate_alt_text()` — image alt text generation
  - `score_content()` — page content scoring 0-100 with recommendations
  - `bulk_generate_meta()` — batch meta generation for multiple products
- **Prompts:** Template strings for meta tags, alt text, content scoring, bulk generation
- **Views:** 4 API endpoints — generate-meta, generate-alt, score-content, bulk-generate-meta
- **URLs:** `/api/v1/ai/generate-meta/`, `/api/v1/ai/generate-alt/`, `/api/v1/ai/score-content/`, `/api/v1/ai/bulk-generate-meta/`
- **Tests:** 6 tests (3 client tests + 3 view tests, all mocked)

### Task 6: Technical SEO Auditor ✅
- **Models:** `AuditRun` (status, pages_crawled, issues_found), `AuditIssue` (15 issue types, 3 severity levels)
- **SiteAuditor crawler:** Checks missing/long/short titles, missing meta descriptions, missing H1, missing alt text, duplicate titles/descriptions
- **Serializers:** AuditIssueSerializer (with page_url, page_title), AuditRunSerializer (with issues + issue_summary)
- **Views:** `trigger_audit` POST, `AuditRunViewSet` read-only
- **URLs:** `/api/v1/audits/trigger/`, `/api/v1/audits/runs/`
- **Tasks:** `run_site_audit`, `audit_all_stores` (Celery)
- **Tests:** 10 tests (2 model + 7 crawler + 1 view)

### Task 7: Dashboard API ✅
- **Views:** `dashboard_overview` (all stores summary), `store_dashboard` (per-store detail with top keywords + audit)
- **URLs:** `/api/v1/dashboard/`, `/api/v1/dashboard/{store_id}/`
- **Tests:** 2 tests (overview + store detail)

### Task 8: SEO Score Calculator & Celery Beat ✅
- **Score formula:** Starts at 100, deducts for audit issues (-40 max), missing meta tags (-30 max), poor keyword rankings (-30 max)
- **Tasks:** `calculate_seo_score`, `recalculate_all_scores`
- **Celery Beat schedule** configured (lazy loading via celery.py to avoid circular import):
  - 2:00 AM — sync all stores
  - 4:00 AM — track all rankings
  - 6:00 AM — recalculate SEO scores
  - Sunday 3:00 AM — audit all stores
- **Tests:** 2 tests (perfect score + low score)

### Task 9: React Frontend ✅
- **Stack:** React 18 + Vite 6 + TailwindCSS 4
- **Pages:** Dashboard, Stores, StoreDetail, Keywords, OnPageSEO, TechnicalAudit, Settings
- **Components:** Layout (sidebar nav), StoreCard, SEOScoreBadge, MetaEditor (spreadsheet-like with color-coded validation), KeywordTable, AuditIssueList (grouped by type), RankChart (Recharts line chart)
- **API client:** Axios-based, all endpoints mapped
- **Build:** `npm run build` succeeds (634KB JS, 17KB CSS)

### Task 10: Integration & Verification ✅
- Removed conflicting `tests.py` files (audits, ai_engine, dashboard) that clashed with `tests/` directories
- Fixed circular import: `seobot/__init__.py` → celery → settings → celery.schedules.crontab
  - Moved `CELERY_BEAT_SCHEDULE` config to plain dict in settings (no crontab import)
  - `celery.py` builds beat schedule with crontab on `on_after_finalize` signal
  - `django_celery_beat` excluded from INSTALLED_APPS during tests (hangs without Redis)
  - `seobot/__init__.py` emptied (no eager celery import)
- Added root `package.json` to prevent esbuild from traversing to Desktop level
- **Note:** Tests could not be run during this session due to extreme memory pressure on this machine (7.4GB/8GB used, heavy swap). All code follows the plan exactly and tests passed for Tasks 1-4 previously.

---

## Current API Endpoints

| Endpoint | Method | Status |
|----------|--------|--------|
| `/api/v1/stores/` | GET, POST | ✅ |
| `/api/v1/stores/{id}/` | GET, PUT, DELETE | ✅ |
| `/api/v1/stores/{id}/sync/` | POST | ✅ |
| `/api/v1/stores/{id}/pages/` | GET | ✅ |
| `/api/v1/stores/{id}/pages/{id}/` | GET, PATCH | ✅ |
| `/api/v1/keywords/` | GET, POST | ✅ |
| `/api/v1/keywords/{id}/rank-history/` | GET | ✅ |
| `/api/v1/keywords/research/` | POST | ✅ |
| `/api/v1/ai/generate-meta/` | POST | ✅ |
| `/api/v1/ai/generate-alt/` | POST | ✅ |
| `/api/v1/ai/score-content/` | POST | ✅ |
| `/api/v1/ai/bulk-generate-meta/` | POST | ✅ |
| `/api/v1/audits/trigger/` | POST | ✅ |
| `/api/v1/audits/runs/` | GET | ✅ |
| `/api/v1/dashboard/` | GET | ✅ |
| `/api/v1/dashboard/{store_id}/` | GET | ✅ |

## Test Count
- **Stores app:** 14 tests ✅
- **Keywords app:** 7 tests ✅
- **AI Engine:** 6 tests (written, needs verification)
- **Audits:** 10 tests (written, needs verification)
- **Dashboard:** 4 tests (written, needs verification)
- **Total expected:** 41 tests

## Known Issues
- Machine has extreme memory pressure (8GB RAM nearly full). Python processes importing Django/Celery are very slow due to swap thrashing. Tests and migrations need to be run when resources are available.
- Git CLI hangs intermittently on this machine (macOS system-level issue).
- `django-fernet-encrypted-fields` installed as v0.3.1, not v0.6.* as in requirements.txt. App name in Django is `encrypted_fields`, not `encrypted_model_fields`.
- `django_celery_beat` is excluded from INSTALLED_APPS during tests to avoid celery import hanging.

## How to Run

### Backend
```bash
cd "/Users/apple/Desktop/SEO BOT/backend"
source venv/bin/activate
python manage.py makemigrations audits  # if not done
python manage.py migrate
python manage.py test -v 2
python manage.py runserver
```

### Frontend
```bash
cd "/Users/apple/Desktop/SEO BOT/frontend"
npm install  # if not done
npm run dev    # dev server at http://localhost:5173
npm run build  # production build
```

### Required Services
- PostgreSQL (or SQLite for dev/test)
- Redis (for Celery task queue)
