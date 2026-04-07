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
        page_content = self._fetch_page_content(prospect_url)
        prompt = RELEVANCE_PROMPT.format(
            store_name=store_name,
            store_keywords=", ".join(store_keywords),
            prospect_url=prospect_url,
            page_content=page_content,
        )
        return self._ask(prompt)

    def draft_outreach_email(self, prospect_url: str, store_name: str, store_niche: str, anchor_text: str) -> dict:
        page_content = self._fetch_page_content(prospect_url)
        prompt = OUTREACH_EMAIL_PROMPT.format(
            store_name=store_name,
            store_niche=store_niche,
            anchor_text=anchor_text,
            prospect_url=prospect_url,
            page_content=page_content,
        )
        return self._ask(prompt)
