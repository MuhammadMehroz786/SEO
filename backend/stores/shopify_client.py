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
        )
        response.raise_for_status()
        return response.json()

    def get_products(self, limit: int = 250) -> list:
        products = []
        params = {"limit": limit}
        data = self._get("products", params)
        products.extend(data.get("products", []))
        return products

    def get_collections(self) -> list:
        data = self._get("custom_collections")
        return data.get("custom_collections", [])

    def get_pages(self) -> list:
        data = self._get("pages")
        return data.get("pages", [])

    def update_product(self, product_id: str, updates: dict) -> dict:
        response = requests.put(
            f"{self.base_url}/products/{product_id}.json",
            headers=self.headers,
            json={"product": updates},
        )
        response.raise_for_status()
        return response.json()
