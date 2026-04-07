import datetime
import requests
from django.conf import settings


class BacklinksClient:
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

    def _parse_date(self, date_str: str) -> datetime.date:
        try:
            return datetime.datetime.strptime(date_str[:10], "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return datetime.date.today()

    def get_backlinks(self, domain: str, limit: int = 1000) -> list:
        data = [{
            "target": domain,
            "limit": limit,
            "include_subdomains": True,
            "broken_links": False,
        }]
        result = self._post("backlinks/backlinks/live", data)
        backlinks = []
        for task in result.get("tasks", []):
            for res in task.get("result", []) or []:
                for item in res.get("items", []) or []:
                    backlinks.append({
                        "source_url": item.get("url_from", ""),
                        "target_url": item.get("url_to", ""),
                        "domain_rank": item.get("domain_from_rank", 0) or 0,
                        "page_rank": item.get("page_from_rank", 0) or 0,
                        "anchor_text": item.get("anchor", "") or "",
                        "is_dofollow": bool(item.get("dofollow", False)),
                        "first_seen": self._parse_date(item.get("first_seen", "")),
                        "last_seen": self._parse_date(item.get("last_seen", "")),
                    })
        return backlinks

    def suggest_prospects(self, domain: str, keywords: list, limit: int = 50) -> list:
        data = [{
            "target": domain,
            "limit": limit,
            "filters": ["domain_from_rank", ">", 10],
        }]
        result = self._post("backlinks/competitors/live", data)
        prospects = []
        for task in result.get("tasks", []):
            for res in task.get("result", []) or []:
                for item in res.get("items", []) or []:
                    prospects.append({
                        "domain": item.get("domain", ""),
                        "domain_rank": item.get("rank", 0) or 0,
                    })
        return prospects
