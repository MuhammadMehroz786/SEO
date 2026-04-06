# SEO Bot — Shopify SEO Manager

A full-stack SEO management application for multiple Shopify stores. Built with Django + React.

## Features

- **Multi-Store Dashboard** — Manage SEO for all your Shopify stores in one place
- **Keyword Research & Tracking** — Discover keywords via DataForSEO, track rankings via SerpAPI
- **On-Page SEO Optimizer** — Bulk edit meta tags, AI-generate titles & descriptions with Claude
- **Technical SEO Auditor** — Crawl pages, detect missing titles/descriptions/alt text, duplicate content
- **AI-Powered Content** — Generate meta tags, alt text, and content scores using Claude API
- **Automated Scheduling** — Daily store syncs, rank tracking, weekly audits via Celery Beat

## Tech Stack

- **Backend:** Django 5, Django REST Framework, Celery, Redis, PostgreSQL
- **Frontend:** React 18, Vite, TailwindCSS, Recharts
- **AI:** Claude API (Anthropic)
- **SEO Data:** SerpAPI, DataForSEO

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL
- Redis

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys and database credentials
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Celery (background tasks)

```bash
cd backend
celery -A seobot worker -l info
celery -A seobot beat -l info
```

## Environment Variables

See `backend/.env.example` for all required configuration.

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD` | PostgreSQL credentials |
| `ANTHROPIC_API_KEY` | Claude API key for AI features |
| `SERPAPI_KEY` | SerpAPI key for rank tracking |
| `DATAFORSEO_LOGIN/PASSWORD` | DataForSEO credentials for keyword research |
| `FIELD_ENCRYPTION_KEY` | Fernet key for encrypting Shopify access tokens |
| `REDIS_URL` | Redis URL for Celery task queue |

## API Endpoints

```
/api/v1/stores/           — Store CRUD, sync trigger
/api/v1/keywords/         — Keyword tracking, rank history
/api/v1/keywords/research — Keyword discovery
/api/v1/audits/           — Site audits
/api/v1/ai/               — AI content generation
/api/v1/dashboard/        — Dashboard metrics
```
