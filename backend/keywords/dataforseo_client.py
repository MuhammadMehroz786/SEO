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
            timeout=60,
        )
        response.raise_for_status()
        return response.json()

    def keyword_research(self, keyword: str, location_code: int = 2840, language_code: str = "en") -> list:
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
