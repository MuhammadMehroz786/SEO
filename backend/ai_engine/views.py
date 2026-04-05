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
