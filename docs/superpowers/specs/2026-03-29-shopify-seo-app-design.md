# Shopify SEO Application — Design Spec

## Overview

A personal web-based SEO management tool for multiple Shopify stores across different niches. Provides a unified dashboard to manage keyword research, on-page optimization, technical SEO audits, content generation, backlink monitoring, competitor intelligence, and automated reporting — all powered by AI (Claude API) and cost-effective SEO data APIs.

## Tech Stack

- **Backend:** Django 5 + Django REST Framework + Celery + Redis
- **Frontend:** React 18 + Vite + TailwindCSS + Recharts
- **Database:** PostgreSQL
- **AI Engine:** Claude API (Anthropic) — content generation, SEO analysis, recommendations
- **SEO Data APIs:**
  - SerpAPI — SERP tracking, competitor analysis ($50/mo for 5,000 searches)
  - DataForSEO — backlinks, keyword data, on-page audit (pay-as-you-go ~$0.01-0.05/task)
  - Google Search Console API — free ranking/indexing data
  - PageSpeed Insights API — free Core Web Vitals and performance data
- **Shopify Admin API** — product data, meta fields, page content sync

## Architecture

```
[React Dashboard] <--REST API--> [Django Backend] <---> [PostgreSQL]
                                      |
                                      +-- [Celery Workers] --> SEO APIs, Scraping, Audits
                                      +-- [Claude API] --> Content & Analysis
                                      +-- [Redis] --> Task Queue + Cache
```

## Feature Modules

### 1. Multi-Store Management Dashboard

- Add/remove Shopify stores with API credentials
- Per-store SEO health score (0-100) updated daily
- Overview dashboard showing all stores at a glance — rankings, traffic trends, issues count
- Store-level drill-down for detailed metrics

### 2. Keyword Research & Tracking

- **Keyword Discovery:** Enter a seed keyword -> Claude AI + DataForSEO generate keyword ideas with search volume, difficulty, CPC, and intent (informational/transactional/navigational)
- **Keyword Clustering:** Claude groups related keywords into topic clusters for content planning
- **Rank Tracking:** Daily rank tracking for target keywords per store via SerpAPI — track positions over time with historical charts
- **Competitor Keyword Gap:** Enter competitor URLs -> find keywords they rank for that you don't

### 3. On-Page SEO Optimizer

- **Bulk Meta Tag Editor:** Pull all products/pages/collections from Shopify -> edit titles, meta descriptions, URL handles in a spreadsheet-like UI -> push changes back via Shopify API
- **AI Meta Tag Generator:** Claude generates optimized titles & meta descriptions based on product data + target keywords — batch generate for entire catalog
- **Content Scoring:** Claude analyzes page content and scores it against target keywords — gives actionable recommendations (add keyword to H1, increase word count, etc.)
- **Image Alt Text Generator:** Claude generates descriptive, keyword-rich alt text for all product images — bulk push to Shopify
- **Heading Structure Analyzer:** Checks H1/H2/H3 hierarchy on every page

### 4. Technical SEO Auditor

- **Site Crawler:** Crawl all pages of a store and flag issues:
  - Broken links (404s)
  - Missing meta tags
  - Duplicate titles/descriptions
  - Missing alt text
  - Slow pages (via PageSpeed Insights API)
  - Missing schema markup
  - Redirect chains
  - Canonical tag issues
- **Schema Markup Generator:** Claude generates JSON-LD structured data (Product, BreadcrumbList, FAQ, Review) — inject via Shopify theme or metafields
- **Sitemap Analyzer:** Validate sitemap, check for missing pages
- **Core Web Vitals Tracking:** Track LCP, INP, CLS over time per store

### 5. Content Engine

- **Blog Post Generator:** Give Claude a topic + target keywords -> generates SEO-optimized blog posts with proper heading structure, internal links, meta tags
- **Product Description Rewriter:** Claude rewrites thin/duplicate product descriptions to be unique, keyword-rich, and compelling
- **Content Calendar:** Plan and schedule content creation across stores
- **Internal Linking Suggestions:** Claude analyzes your content and suggests where to add internal links between pages

### 6. Backlink Manager

- **Backlink Profile Monitor:** DataForSEO pulls your backlink profile — track new/lost links, referring domains, anchor text distribution
- **Competitor Backlink Analysis:** See where competitors get their links -> identify link building opportunities
- **Toxic Link Detector:** Flag spammy/harmful backlinks that could trigger Google penalties
- **Link Building Outreach Helper:** Claude drafts personalized outreach emails for link building based on the target site's content
- **Disavow File Generator:** Generate Google disavow files for toxic links

### 7. Competitor Intelligence

- **Competitor Tracker:** Add competitor URLs -> track their rankings, content changes, backlink growth
- **SERP Feature Tracking:** Monitor who owns featured snippets, People Also Ask, image packs for your keywords
- **Content Gap Analysis:** Find topics competitors cover that you don't

### 8. Reporting & Alerts

- **Automated Reports:** Weekly/monthly SEO reports per store — rankings, traffic, issues, progress
- **Custom Alerts:** Get notified when rankings drop, new backlinks appear, technical issues detected, or competitors make moves
- **Export:** PDF/CSV export of any report or data table

## Data Model

### Store
- id, name, shopify_url, api_key, api_secret, access_token
- seo_score, last_crawl_date

### Keyword
- id, store (FK), keyword, search_volume, difficulty, cpc, intent
- is_tracked, cluster_name

### RankHistory
- id, keyword (FK), date, position, serp_url, serp_features

### Page
- id, store (FK), shopify_id, url, page_type (product/collection/page/blog)
- title, meta_description, h1, content_score
- last_audited

### AuditIssue
- id, page (FK), issue_type, severity (critical/warning/info), description, fix_suggestion

### Image
- id, page (FK), src, alt_text, ai_generated_alt

### Backlink
- id, store (FK), source_url, target_url, anchor_text, domain_authority
- is_toxic, status (active/lost), first_seen, last_seen

### Competitor
- id, store (FK), name, url

### CompetitorKeyword
- id, competitor (FK), keyword, position, search_volume

### CompetitorBacklink
- id, competitor (FK), source_url, anchor_text, domain_authority

### ContentPlan
- id, store (FK), topic, target_keywords, status (planned/draft/published)
- scheduled_date, content_type (blog/product_desc)
- ai_generated_content, final_content

### Report
- id, store (FK), report_type (weekly/monthly/custom), generated_date
- data (JSONField), pdf_url

### Alert
- id, store (FK), alert_type (rank_drop/new_backlink/technical_issue/competitor)
- condition, threshold, is_active

### AlertHistory
- id, alert (FK), triggered_date, details, acknowledged

## External API Integration

| API | Purpose | Frequency | Cost Model |
|-----|---------|-----------|------------|
| Shopify Admin API | Sync products/pages/collections, push meta tag updates, image alt text | On-demand + daily sync | Free (own stores) |
| Claude API (Anthropic) | Content generation, meta tags, analysis, outreach emails, recommendations | On-demand per user action | Pay per token |
| SerpAPI | Rank tracking, SERP features, competitor SERPs | Daily for tracked keywords | $50/mo for 5,000 searches |
| DataForSEO | Backlinks, keyword research, on-page audit data, competitor data | On-demand + weekly backlink refresh | Pay-as-you-go ~$0.01-0.05/task |
| Google Search Console API | Real ranking data, impressions, clicks, indexing status | Daily pull | Free |
| PageSpeed Insights API | Core Web Vitals, performance scores | Weekly per page | Free |

## Background Task Schedule (Celery Beat)

| Task | Frequency | Description |
|------|-----------|-------------|
| Rank Tracking | Daily (early morning) | Check positions for all tracked keywords across all stores |
| Store Sync | Daily | Pull latest products/pages/collections from Shopify |
| Backlink Refresh | Weekly | Update backlink profiles from DataForSEO |
| Site Audit | Weekly | Full crawl + technical SEO checks per store |
| Core Web Vitals | Weekly | PageSpeed check for all pages |
| SEO Score Recalc | Daily (after rank tracking) | Recalculate per-store health scores |
| GSC Data Pull | Daily | Import Search Console data |
| Alert Evaluation | After each task | Check if any alert conditions are triggered |

## Internal API Structure

```
/api/v1/
  /stores/                  — CRUD stores, sync trigger
  /stores/{id}/pages/       — pages, audit issues, content scores
  /stores/{id}/keywords/    — keyword tracking, rank history
  /stores/{id}/backlinks/   — backlink profile, toxic links
  /stores/{id}/competitors/ — competitor data
  /stores/{id}/audit/       — trigger/view site audits
  /stores/{id}/reports/     — generate/view reports
  /keywords/research/       — keyword discovery + clustering
  /content/generate/        — AI content generation endpoints
  /content/calendar/        — content planning
  /alerts/                  — manage alert rules
  /dashboard/               — aggregated metrics for all stores
```

## Frontend Structure

### Navigation (Sidebar)
- Dashboard (overview of all stores)
- Stores (manage stores, per-store drill-down)
- Keywords (research, tracking, clusters)
- On-Page SEO (meta editor, content scoring, alt text)
- Technical SEO (audits, schema, Core Web Vitals)
- Content (generator, calendar, internal links)
- Backlinks (profile, competitors, toxic, outreach)
- Competitors (tracking, gap analysis)
- Reports (automated reports, exports)
- Settings (API keys, alert rules, scheduling)

### Key Page Descriptions

1. **Dashboard** — Cards per store showing SEO score, ranking trend sparkline, issues count, top gaining/losing keywords. Overall summary at top.

2. **Keyword Research** — Search bar for seed keyword -> results table with volume, difficulty, CPC, intent. One-click "track" button. Cluster view groups related keywords.

3. **Bulk Meta Editor** — Spreadsheet-like table of all products/pages. Inline editing for title, description, URL. "AI Generate" button per row or bulk. Color-coded cells (red = too long, yellow = missing keyword, green = good).

4. **Site Audit** — Summary cards (critical/warning/info issue counts). Expandable issue list grouped by type. "Fix with AI" button where applicable.

5. **Content Generator** — Form: select store, topic, target keywords, content type -> Claude generates draft -> rich text editor for review/edit -> publish to Shopify.

6. **Backlink Dashboard** — Donut chart of link quality distribution. New/lost links timeline. Referring domains table. Toxic link flagging with one-click disavow list generation.

7. **Competitor View** — Side-by-side comparison charts. Keyword overlap visualization. AI-powered strategy recommendations from Claude.

## Security & Error Handling

### API Key Storage
- All API keys encrypted at rest using django-encrypted-model-fields
- Environment variables for app-level secrets (Django secret key, DB password, Redis URL)
- .env file for local dev, never committed

### Rate Limiting & Cost Protection
- Daily API budget caps per external service — stop making calls if budget exceeded
- Queue-based rate limiting in Celery to respect API rate limits
- Dashboard shows API usage/spend tracking

### Error Handling
- Celery tasks retry with exponential backoff on API failures (max 3 retries)
- Failed tasks logged with full error details — visible in dashboard under "Task History"
- Shopify API sync failures don't block other stores — each store processes independently
- Claude API fallback: if content generation fails, save the prompt for manual retry

### Data Protection
- PostgreSQL daily backups
- Soft-delete for stores/keywords (nothing permanently lost on accidental delete)
