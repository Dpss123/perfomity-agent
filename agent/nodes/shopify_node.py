"""
Shopify Node — Step 4 of 4
============================
If SHOPIFY_ACCESS_TOKEN + SHOPIFY_STORE_URL set → deploy live.
Otherwise → export schema-ready JSON to output/shopify_schema.json
Also generates the handoff report (output/handoff_report.md).
"""

import json
import os
from datetime import datetime
from agent.state import AgentState
from agent.tools.shopify_tool import is_configured, create_collection, create_product, create_page


def shopify_node(state: AgentState) -> AgentState:
    store_assets = state.get("store_assets", {})
    research     = state.get("research", {})
    strategy     = state.get("strategy", {})
    errors       = state.get("errors", [])

    print("\n[Node 4/4] Shopify — deploying or exporting...")

    os.makedirs("output", exist_ok=True)

    # Save research output — Deliverable 2
    with open("output/research_output.json", "w", encoding="utf-8") as f:
        json.dump(research, f, indent=2, ensure_ascii=False)

    # Save store assets — Deliverable 3
    with open("output/store_assets.json", "w", encoding="utf-8") as f:
        json.dump(store_assets, f, indent=2, ensure_ascii=False)

    # Deploy or export — Deliverable 4
    if is_configured():
        shopify_result = _deploy_live(store_assets)
    else:
        shopify_result = _export_schema(store_assets)

    # Generate handoff report
    _generate_handoff_report(state, shopify_result)

    print("  ✓ Shopify step complete")
    return {**state, "shopify": shopify_result, "errors": errors}


# ── Live Deployment ────────────────────────────────────────────────

def _deploy_live(assets: dict) -> dict:
    results = {
        "status":    "deployed",
        "store_url": os.getenv("SHOPIFY_STORE_URL"),
        "created":   {},
    }

    # Collection
    try:
        col = assets.get("collection", {})
        print(f"  → Creating collection: {col.get('title')}")
        r = create_collection(col.get("title", "The Signature Collection"), col.get("description_html", ""))
        results["created"]["collection"] = r
        print("    ✓ Collection created")
    except Exception as e:
        results["created"]["collection"] = {"error": str(e)}
        print(f"    ✗ Collection failed: {e}")

    # Products
    results["created"]["products"] = []
    for p in assets.get("products", []):
        try:
            print(f"  → Creating product: {p.get('title')}")
            shopify_p = {
                "title":        p.get("title"),
                "handle":       p.get("handle"),
                "body_html":    p.get("description_html", ""),
                "vendor":       p.get("vendor", "Lumière"),
                "product_type": p.get("product_type", "Scented Candle"),
                "tags":         ", ".join(p.get("shopify_tags", [])),
                "published":    True,
                "variants":     p.get("variants", []),
                "metafields_global_title_tag":       p.get("seo_meta_tags", {}).get("title", ""),
                "metafields_global_description_tag": p.get("seo_meta_tags", {}).get("description", ""),
            }
            r = create_product(shopify_p)
            results["created"]["products"].append(r)
            print(f"    ✓ Product created: {p.get('title')}")
        except Exception as e:
            results["created"]["products"].append({"title": p.get("title"), "error": str(e)})
            print(f"    ✗ Product failed: {e}")

    # About Us page
    try:
        about = assets.get("about_us", {})
        print("  → Creating About Us page")
        r = create_page(about.get("headline", "Our Story"), about.get("body_html", ""), handle="about-us")
        results["created"]["about_page"] = r
        print("    ✓ About Us page created")
    except Exception as e:
        results["created"]["about_page"] = {"error": str(e)}
        print(f"    ✗ About page failed: {e}")

    # Also export JSON alongside live deploy
    _export_schema(assets)
    return results


# ── JSON Export ────────────────────────────────────────────────────

def _export_schema(assets: dict) -> dict:
    shopify_products = []
    for p in assets.get("products", []):
        shopify_products.append({
            "title":        p.get("title"),
            "handle":       p.get("handle"),
            "body_html":    p.get("description_html"),
            "vendor":       p.get("vendor", "Lumière"),
            "product_type": p.get("product_type"),
            "tags":         ", ".join(p.get("shopify_tags", [])),
            "published":    True,
            "metafields_global_title_tag":       p.get("seo_meta_tags", {}).get("title", ""),
            "metafields_global_description_tag": p.get("seo_meta_tags", {}).get("description", ""),
            "variants": p.get("variants", []),
            "_scent_notes":     p.get("scent_notes"),
            "_bullet_features": p.get("bullet_features"),
        })

    schema = {
        "store_name":  "Lumière",
        "api_version": "2024-01",
        "collections": [assets.get("collection", {})],
        "products":    shopify_products,
        "pages": [{
            "title":     assets.get("about_us", {}).get("headline", "Our Story"),
            "handle":    "about-us",
            "body_html": assets.get("about_us", {}).get("body_html", ""),
            "published": True,
        }],
        "seo":           assets.get("seo", {}),
        "homepage":      assets.get("homepage", {}),
        "color_palette": assets.get("color_palette", {}),
        "typography":    assets.get("typography", {}),
    }

    path = "output/shopify_schema.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)

    print(f"  ✓ Schema-ready JSON → {path}")
    return {
        "status": "json_exported",
        "file":   path,
        "note":   "Add SHOPIFY_ACCESS_TOKEN + SHOPIFY_STORE_URL to .env for live deployment",
    }


# ── Handoff Report ─────────────────────────────────────────────────

def _generate_handoff_report(state: dict, shopify_result: dict):
    research     = state.get("research", {})
    strategy     = state.get("strategy", {})
    store_assets = state.get("store_assets", {})
    brief        = state.get("brief", "")

    competitors = research.get("competitors", [])
    pricing     = research.get("pricing_analysis", {})
    direction   = research.get("brand_direction", {})
    products    = store_assets.get("products", [])
    palette     = strategy.get("color_palette", {})

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        "# Lumière Store Builder Agent — Handoff Report",
        f"Generated: {now}",
        "",
        "---",
        "",
        "## 1. Input Brief",
        "",
        brief.strip(),
        "",
        "---",
        "",
        "## 2. Research Decisions",
        "",
        "### Competitors Identified",
    ]

    for i, c in enumerate(competitors[:5], 1):
        lines.append(f"{i}. **{c.get('name')}** ({c.get('url')}) — {c.get('positioning', '')[:80]}")

    lines += [
        "",
        f"### Pricing Decision",
        f"- Entry price selected: ₹{pricing.get('recommended_entry_price', 999)}",
        f"- Hero price selected: ₹{pricing.get('recommended_hero_price', 1299)}",
        f"- Gift set price selected: ₹{pricing.get('recommended_gift_price', 2199)}",
        f"- Rationale: {pricing.get('launch_strategy', '')}",
        "",
        "### Brand Direction",
        f"- Archetype: {direction.get('brand_archetype', '')}",
        f"- Tone: {', '.join(direction.get('tone_adjectives', []))}",
        f"- Brand Promise: {direction.get('brand_promise', '')}",
        "",
        "---",
        "",
        "## 3. Strategy Decisions",
        "",
        f"- Tagline: *{strategy.get('tagline', '')}*",
        f"- Palette: {palette.get('palette_name', '')}",
        f"  - Primary: {palette.get('primary', '')}",
        f"  - Gold accent: {palette.get('secondary', '')}",
        f"  - Background: {palette.get('background', '')}",
        f"- Display font: {strategy.get('typography', {}).get('display', {}).get('name', '')}",
        f"- Body font: {strategy.get('typography', {}).get('body', {}).get('name', '')}",
        "",
        "---",
        "",
        "## 4. Content Generated",
        "",
        "### Homepage",
        f"- Hero headline: *{store_assets.get('homepage', {}).get('hero_headline', '')}*",
        f"- Hero subheadline: {store_assets.get('homepage', {}).get('hero_subheadline', '')}",
        "",
        "### Products Created",
    ]

    for p in products:
        lines.append(f"- **{p.get('title')}** — ₹{p.get('price')} (compare ₹{p.get('compare_at_price')}) — {p.get('subtitle', '')}")

    lines += [
        "",
        "### Collection",
        f"- {store_assets.get('collection', {}).get('title', '')} ({store_assets.get('collection', {}).get('handle', '')})",
        "",
        "---",
        "",
        "## 5. Shopify Output",
        "",
        f"- Status: **{shopify_result.get('status', '')}**",
    ]

    if shopify_result.get("file"):
        lines.append(f"- Schema file: `{shopify_result.get('file')}`")
    if shopify_result.get("store_url"):
        lines.append(f"- Store URL: {shopify_result.get('store_url')}")
    if shopify_result.get("note"):
        lines.append(f"- Note: {shopify_result.get('note')}")

    lines += [
        "",
        "---",
        "",
        "## 6. Files Generated",
        "",
        "| File | Contents |",
        "|------|----------|",
        "| `output/research_output.json` | Competitors, trends, pricing, brand direction |",
        "| `output/store_assets.json` | All generated copy, products, collection, about us |",
        "| `output/shopify_schema.json` | Shopify Admin API-ready JSON |",
        "| `output/handoff_report.md` | This document |",
        "",
        "---",
        "",
        "## 7. Known Limitations",
        "",
        "- No product images generated — placeholder image URLs used",
        "- BeautifulSoup scraping may be blocked on some competitor sites; fallback data used",
        "- Shopify theme/CSS customisation requires a separate manual step",
        "- Agent runs sequentially — parallel execution not implemented in this version",
        "",
        "*End of handoff report.*",
    ]

    path = "output/handoff_report.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"  ✓ Handoff report → {path}")
