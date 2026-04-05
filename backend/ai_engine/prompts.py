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
