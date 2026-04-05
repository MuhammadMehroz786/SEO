import serpapi
from django.conf import settings


class SerpClient:
    def __init__(self):
        self.client = serpapi.Client(api_key=settings.SERPAPI_KEY)

    def check_ranking(self, keyword: str, domain: str, location: str = "United States") -> dict:
        results = self.client.search({
            "engine": "google",
            "q": keyword,
            "location": location,
            "num": 100,
        })
        position = None
        serp_url = ""
        serp_features = []
        for i, result in enumerate(results.get("organic_results", []), 1):
            if domain in result.get("link", ""):
                position = i
                serp_url = result.get("link", "")
                break
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
        return {"position": position, "serp_url": serp_url, "serp_features": serp_features}
