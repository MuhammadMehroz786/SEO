import requests


class PageSpeedClient:
    """Client for Google PageSpeed Insights API (free, no key required)."""
    BASE_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

    def analyze(self, url: str, strategy: str = "mobile") -> dict:
        response = requests.get(
            self.BASE_URL,
            params={"url": url, "strategy": strategy, "category": "performance"},
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()

        lighthouse = data.get("lighthouseResult", {})
        audits = lighthouse.get("audits", {})
        categories = lighthouse.get("categories", {})

        performance_score = categories.get("performance", {}).get("score")
        if performance_score is not None:
            performance_score = int(performance_score * 100)

        return {
            "performance_score": performance_score,
            "lcp": audits.get("largest-contentful-paint", {}).get("numericValue"),
            "fid": audits.get("max-potential-fid", {}).get("numericValue"),
            "cls": audits.get("cumulative-layout-shift", {}).get("numericValue"),
            "ttfb": audits.get("server-response-time", {}).get("numericValue"),
            "speed_index": audits.get("speed-index", {}).get("numericValue"),
        }
