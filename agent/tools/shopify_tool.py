"""
Shopify Admin API Tool
Free dev store: partners.shopify.com
Admin → Settings → Apps → Develop apps → Create app
Scopes needed: write_products, write_collections, write_content
"""

import os
import time
import requests

API_VERSION = "2024-01"


def _headers():
    token = os.getenv("SHOPIFY_ACCESS_TOKEN")
    if not token:
        return None
    return {
        "X-Shopify-Access-Token": token,
        "Content-Type": "application/json",
    }


def _base():
    store = os.getenv("SHOPIFY_STORE_URL", "").strip().rstrip("/")
    if not store:
        return None
    if not store.startswith("https://"):
        store = f"https://{store}"
    return f"{store}/admin/api/{API_VERSION}"


def is_configured() -> bool:
    return bool(os.getenv("SHOPIFY_ACCESS_TOKEN") and os.getenv("SHOPIFY_STORE_URL"))


def _post(endpoint: str, payload: dict) -> dict:
    base    = _base()
    headers = _headers()
    if not base or not headers:
        return {"error": "Shopify not configured"}
    time.sleep(0.6)  # Stay under 2 req/sec rate limit
    try:
        r = requests.post(f"{base}{endpoint}", headers=headers, json=payload, timeout=15)
        r.raise_for_status()
        return r.json()
    except requests.HTTPError as e:
        return {"error": str(e), "body": r.text}
    except Exception as e:
        return {"error": str(e)}


def create_collection(title: str, description_html: str) -> dict:
    return _post("/custom_collections.json", {
        "custom_collection": {
            "title":      title,
            "body_html":  description_html,
            "published":  True,
            "sort_order": "best-selling",
        }
    })


def create_product(product: dict) -> dict:
    return _post("/products.json", {"product": product})


def create_page(title: str, body_html: str, handle: str = None) -> dict:
    payload = {"page": {"title": title, "body_html": body_html, "published": True}}
    if handle:
        payload["page"]["handle"] = handle
    return _post("/pages.json", payload)
