import re
import requests


class ShopifyClient:
    API_VERSION = "2024-01"

    def __init__(self, shop_url: str, access_token: str):
        self.shop_url = shop_url.rstrip("/")
        self.access_token = access_token
        self.base_url = f"https://{self.shop_url}/admin/api/{self.API_VERSION}"
        self.headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json",
        }

    def _get(self, endpoint: str, params: dict = None) -> dict:
        response = requests.get(
            f"{self.base_url}/{endpoint}.json",
            headers=self.headers,
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        return response.json(), response.headers

    def get_products(self, limit: int = 250) -> list:
        products = []
        params = {"limit": limit}
        while True:
            data, headers = self._get("products", params)
            products.extend(data.get("products", []))
            # Follow pagination via Link header
            link = headers.get("Link", "")
            match = re.search(r'<([^>]+)>;\s*rel="next"', link)
            if not match:
                break
            # Extract page_info for cursor-based pagination
            next_url = match.group(1)
            page_info_match = re.search(r'page_info=([^&]+)', next_url)
            if not page_info_match:
                break
            params = {"limit": limit, "page_info": page_info_match.group(1)}
        return products

    def get_collections(self) -> list:
        data, _ = self._get("custom_collections")
        return data.get("custom_collections", [])

    def get_pages(self) -> list:
        data, _ = self._get("pages")
        return data.get("pages", [])

    def update_product(self, product_id: str, updates: dict) -> dict:
        response = requests.put(
            f"{self.base_url}/products/{product_id}.json",
            headers=self.headers,
            json={"product": updates},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
