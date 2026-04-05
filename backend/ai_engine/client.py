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
