"""
Content Node — Step 3 of 4
============================
Generates ALL store assets required by Deliverable 3:
  - Homepage sections (hero, 3 value props, social proof)
  - 3 product listings (min 150 words each, bullet features, SEO meta tags)
  - 1 collection page description
  - 1 About Us section (~100 words)
  - Colour palette + font pairing rationale
"""

import json
from agent.state import AgentState
from agent.tools.llm import llm

SYSTEM = """You are a luxury brand copywriter for premium D2C brands in India.
You write for Lumière — premium handcrafted soy candles targeting urban women 25-40.
Tone: Refined, Poetic, Warm, Aspirational. Reference: Aesop, Jo Malone, Forest Essentials.
Respond ONLY with valid JSON. No markdown, no explanation."""


def content_node(state: AgentState) -> AgentState:
    strategy = state.get("strategy", {})
    errors   = state.get("errors", [])

    print("\n[Node 3/4] Content — generating all store assets...")

    print("  → Generating homepage copy...")
    homepage = _homepage(strategy)

    print("  → Writing 3 product listings...")
    products = _products()

    print("  → Writing collection page...")
    collection = _collection()

    print("  → Writing About Us...")
    about = _about(strategy)

    print("  → Generating SEO metadata...")
    seo = _seo()

    store_assets = {
        "homepage":      homepage,
        "products":      products,
        "collection":    collection,
        "about_us":      about,
        "seo":           seo,
        "color_palette": strategy.get("color_palette", {}),
        "typography":    strategy.get("typography", {}),
    }

    print("  ✓ Content complete")
    return {**state, "store_assets": store_assets, "errors": errors}


# ── Homepage ────────────────────────────────────────────────────────

def _homepage(strategy: dict) -> dict:
    tagline = strategy.get("tagline", "Light your finest moments.")
    values  = strategy.get("brand_values", [])

    prompt = f"""Write homepage content for Lumière luxury soy candle brand.
Tagline: {tagline}
Brand values: {json.dumps(values)}

Return JSON:
{{
  "hero_headline": "4-7 word poetic headline — a state of being, not a product description",
  "hero_subheadline": "15-20 word supporting line, sensory and personal",
  "hero_cta_primary": "3-4 word CTA button text",
  "hero_cta_secondary": "2-3 word secondary link",
  "value_propositions": [
    {{
      "icon": "simple icon name",
      "title": "3-4 word title",
      "body": "25-30 word description, sensory and specific"
    }},
    {{
      "icon": "simple icon name",
      "title": "3-4 word title",
      "body": "25-30 word description, sensory and specific"
    }},
    {{
      "icon": "simple icon name",
      "title": "3-4 word title",
      "body": "25-30 word description, sensory and specific"
    }}
  ],
  "social_proof": {{
    "section_headline": "5-7 word headline",
    "testimonial": "40-50 word customer review, specific and believable, not generic",
    "customer_name": "Indian first name + last initial",
    "customer_city": "Indian metro city",
    "rating": 5
  }},
  "featured_collection_headline": "4-5 word section headline",
  "newsletter_headline": "5-7 words",
  "newsletter_subtext": "15-20 words"
}}

Return ONLY valid JSON."""

    resp = llm(SYSTEM, prompt, temperature=0.8, json_mode=True)
    try:
        return json.loads(resp)
    except Exception:
        return {
            "hero_headline": "Where Light Becomes Memory",
            "hero_subheadline": "Handcrafted soy candles for the woman who curates her world with intention. Poured in small batches. Designed to last.",
            "hero_cta_primary": "Explore the Collection",
            "hero_cta_secondary": "Our Story",
            "value_propositions": [
                {"icon": "leaf", "title": "100% Natural Soy", "body": "Every Lumière candle is poured with premium natural soy wax — clean-burning, long-lasting, and kind to your home. Zero toxins. Zero compromise."},
                {"icon": "hands", "title": "Hand-Poured in India", "body": "Crafted in small batches by artisan hands in Bengaluru. Each pour is intentional, unhurried, and uniquely yours. We never mass-produce."},
                {"icon": "gift", "title": "Luxury Unboxed", "body": "The ritual begins before you light the wick. Our packaging is designed to delight from first touch to last flicker. Every box is ready to give."},
            ],
            "social_proof": {
                "section_headline": "Loved by those who live beautifully",
                "testimonial": "I have tried every premium candle brand and nothing compares. The Sandalwood & Rose fills my entire apartment and the packaging is absolutely stunning. This is the only brand I gift now.",
                "customer_name": "Ananya M.",
                "customer_city": "Mumbai",
                "rating": 5,
            },
            "featured_collection_headline": "Discover Your Signature Scent",
            "newsletter_headline": "Join the Lumière Circle",
            "newsletter_subtext": "Be first to discover new collections, exclusive rituals, and moments made for you.",
        }


# ── Products ────────────────────────────────────────────────────────

def _products() -> list:
    prompt = """Write 3 complete luxury product listings for Lumière soy candles.

Products:
1. Lumière Noir — Sandalwood & Oud — 200g matte-black jar — ₹1,299 — evening, dark, resinous
2. Lumière Blanc — White Tea & Bergamot — 150g ivory ceramic jar, gold lid — ₹999 — morning, fresh, minimal
3. La Nuit Gift Set — Rose Jasmine + Cedarwood Vetiver — 2×100g magnetic velvet gift box — ₹2,199 — gifting

Return a JSON array of exactly 3 product objects. Each must have:
{
  "handle": "url-slug",
  "title": "product name",
  "subtitle": "5-7 word evocative subtitle",
  "description_html": "full HTML description, MINIMUM 150 words, rich sensory language, no bullet points inside",
  "bullet_features": ["exactly 5 bullet points covering specs and benefits"],
  "price": integer INR,
  "compare_at_price": integer INR (10-15% higher for perceived value),
  "weight_grams": integer,
  "burn_time_hours": integer,
  "scent_notes": {
    "top": ["2-3 top notes"],
    "heart": ["2-3 heart notes"],
    "base": ["2-3 base notes"]
  },
  "seo_meta_tags": {
    "title": "SEO title, max 60 chars",
    "description": "SEO description, max 155 chars",
    "keywords": ["keyword1", "keyword2", "keyword3"]
  },
  "shopify_tags": ["5 Shopify product tags"],
  "product_type": "Scented Candle or Gift Set",
  "vendor": "Lumière",
  "variants": [{"title": "size", "price": integer, "sku": "SKU-CODE", "inventory_quantity": integer}]
}

Return ONLY the JSON array. No other text."""

    resp = llm(SYSTEM, prompt, temperature=0.75, json_mode=True)
    try:
        parsed = json.loads(resp)
        if isinstance(parsed, list):
            return parsed
        for v in parsed.values():
            if isinstance(v, list):
                return v
    except Exception:
        pass
    return _fallback_products()


# ── Collection page ─────────────────────────────────────────────────

def _collection() -> dict:
    prompt = """Write the primary collection page for Lumière's "The Signature Collection".

Return JSON:
{
  "title": "The Signature Collection",
  "handle": "signature-collection",
  "description_html": "Rich HTML body, 100-120 words, evocative luxury tone, no bullet points",
  "seo_title": "max 60 chars",
  "seo_description": "max 155 chars"
}

Return ONLY valid JSON."""

    resp = llm(SYSTEM, prompt, temperature=0.7, json_mode=True)
    try:
        return json.loads(resp)
    except Exception:
        return {
            "title": "The Signature Collection",
            "handle": "signature-collection",
            "description_html": "<p>Every great interior has a scent.</p><p>The Lumière Signature Collection is our finest expression of handcrafted luxury — a curated edit of soy candles designed for the spaces you love most. Each fragrance was developed over months of careful iteration, blending rare botanicals with premium fragrance oils to create scents that feel <em>familiar, yet entirely new</em>.</p><p>Light one and you will understand why scent is the most powerful memory-maker we have. Available in our signature apothecary jars with hand-tied silk ribbon and sealed with embossed wax. This is not just a candle. This is your new ritual.</p>",
            "seo_title": "The Signature Collection — Lumière Premium Soy Candles India",
            "seo_description": "Lumière's finest handcrafted soy candles. Premium fragrances in luxury packaging, hand-poured in India. Free shipping above ₹1,500.",
        }


# ── About Us ────────────────────────────────────────────────────────

def _about(strategy: dict) -> dict:
    brand_story = strategy.get("brand_story", "")

    prompt = f"""Write an About Us section for Lumière based on this brand story:
{brand_story}

Requirements: approximately 100 words, warm and personal, on-brand luxury tone.

Return JSON:
{{
  "headline": "evocative headline — not just 'Our Story'",
  "body_html": "HTML formatted body, approximately 100 words",
  "founder_note": "short 25-30 word quote from founder",
  "founder_name": "Priya",
  "founder_title": "Founder, Lumière"
}}

Return ONLY valid JSON."""

    resp = llm(SYSTEM, prompt, temperature=0.7, json_mode=True)
    try:
        return json.loads(resp)
    except Exception:
        return {
            "headline": "The Light Behind Lumière",
            "body_html": "<p>Lumière was born from a simple belief: that your home deserves the same devotion you bring to everything you love.</p><p>We started in a small studio in Bengaluru, hand-pouring soy candles for friends who could not find a luxury Indian candle brand that felt truly special. What began as a personal obsession became something we had to share with the world.</p><p>Today, every Lumière candle is still poured by hand in small batches. We do not rush. We do not compromise. We believe in making things that last — in memory, and in warmth.</p>",
            "founder_note": "I wanted to create the candle I could not find anywhere. Something Indian, luxurious, and deeply personal.",
            "founder_name": "Priya",
            "founder_title": "Founder, Lumière",
        }


# ── SEO ─────────────────────────────────────────────────────────────

def _seo() -> dict:
    return {
        "homepage_title":       "Lumière — Premium Handcrafted Soy Candles India",
        "homepage_description": "Discover Lumière's collection of luxury handcrafted soy candles. Natural, artisan-poured, beautifully packaged. Premium home fragrance for the modern Indian woman.",
        "homepage_keywords":    ["luxury soy candles India", "premium handcrafted candles", "scented candles India", "artisan candles", "luxury home fragrance India"],
        "og_title":             "Lumière — Light Your Finest Moments",
        "og_description":       "Handcrafted soy candles for the modern luxury home. Explore Lumière's Signature Collection.",
    }


# ── Product fallback ────────────────────────────────────────────────

def _fallback_products() -> list:
    return [
        {
            "handle": "lumiere-noir-sandalwood-oud",
            "title": "Lumière Noir",
            "subtitle": "Sandalwood, Oud & Dark Amber",
            "description_html": "<p><em>For evenings that belong entirely to you.</em></p><p>Lumière Noir is our most beloved evening candle — a deep, resinous blend of aged sandalwood, pure Oud, and warm dark amber that transforms any room into a sanctuary of calm. Inspired by the hushed opulence of Indian palace interiors, this fragrance opens with a whisper of smoky incense before settling into a rich, woody heart that lingers for hours after the flame is extinguished.</p><p>Hand-poured in small batches into our signature matte-black apothecary jar, Lumière Noir is finished with a hand-stamped wax seal and a single silk ribbon. It is not just a candle. It is an atmosphere.</p><p>Each jar provides 45–50 hours of clean, even burn with zero soot. Our natural soy wax formula ensures a fragrance throw that fills the room without overwhelming it. The vessel, once emptied, is designed to be repurposed as a small planter, a pen holder, or a vessel for dried florals.</p>",
            "bullet_features": ["100% natural soy wax — clean, toxin-free burn", "45–50 hour burn time", "200g / Matte black apothecary jar with gold foil label", "Hand-poured in small batches, Bengaluru, India", "Fragrance: Sandalwood, Oud, Dark Amber, Incense, Vetiver"],
            "price": 1299, "compare_at_price": 1499, "weight_grams": 200, "burn_time_hours": 48,
            "scent_notes": {"top": ["Black Pepper", "Incense"], "heart": ["Oud", "Sandalwood"], "base": ["Dark Amber", "Musk", "Vetiver"]},
            "seo_meta_tags": {
                "title": "Lumière Noir — Sandalwood & Oud Luxury Soy Candle | Lumière",
                "description": "Hand-poured luxury soy candle with Sandalwood, Oud & Dark Amber. 200g matte black jar, 48hr burn. Premium home fragrance by Lumière India.",
                "keywords": ["sandalwood oud candle India", "luxury soy candle", "premium scented candle India"],
            },
            "shopify_tags": ["soy-candle", "luxury", "sandalwood", "oud", "evening-scent"],
            "product_type": "Scented Candle", "vendor": "Lumière",
            "variants": [{"title": "200g", "price": 1299, "sku": "LUM-NOIR-200", "inventory_quantity": 50}],
        },
        {
            "handle": "lumiere-blanc-white-tea-bergamot",
            "title": "Lumière Blanc",
            "subtitle": "White Tea, Bergamot & Fresh Linen",
            "description_html": "<p><em>The scent of a Sunday morning with nowhere to be.</em></p><p>Lumière Blanc is pure, quiet luxury. A blend of delicate white tea, sun-bright bergamot, and the barely-there freshness of warm linen — this is the candle you light when you want your home to breathe. When you want lightness, clarity, and a sense that everything is exactly as it should be.</p><p>This fragrance was designed for morning rituals — the unhurried cup of chai, the slow read, the moment before the day begins in full. It is the olfactory equivalent of white space. Minimal. Considered. Completely itself.</p><p>Housed in our signature ivory ceramic jar with a brushed gold lid, Lumière Blanc is the piece every considered home needs. The jar is designed to be repurposed — as a trinket dish, a pen holder, a vessel for small flowers. Because beautiful things should last beyond their first purpose.</p>",
            "bullet_features": ["100% natural soy wax — long clean soot-free burn", "40–45 hour burn time", "150g / Ivory ceramic jar with brushed gold lid", "Reusable vessel — designed to outlast the candle", "Fragrance: White Tea, Bergamot, Fresh Linen, White Musk"],
            "price": 999, "compare_at_price": 1150, "weight_grams": 150, "burn_time_hours": 42,
            "scent_notes": {"top": ["Bergamot", "Green Tea"], "heart": ["White Tea", "Jasmine Petals"], "base": ["Fresh Linen", "White Musk"]},
            "seo_meta_tags": {
                "title": "Lumière Blanc — White Tea & Bergamot Candle | Lumière",
                "description": "Luxury soy candle — White Tea, Bergamot & Fresh Linen. 150g ivory ceramic jar with gold lid. Minimal luxury by Lumière India.",
                "keywords": ["white tea bergamot candle India", "luxury morning candle", "ivory ceramic candle India"],
            },
            "shopify_tags": ["soy-candle", "luxury", "white-tea", "bergamot", "morning-ritual"],
            "product_type": "Scented Candle", "vendor": "Lumière",
            "variants": [{"title": "150g", "price": 999, "sku": "LUM-BLANC-150", "inventory_quantity": 60}],
        },
        {
            "handle": "la-nuit-gift-set",
            "title": "La Nuit Gift Set",
            "subtitle": "Two Candles. One Unforgettable Gift.",
            "description_html": "<p><em>Because some things are worth giving beautifully.</em></p><p>La Nuit is our definitive luxury gift — a curated pairing of two of Lumière's finest fragrances, presented in a hand-assembled magnetic gift box lined with black velvet. This is the gift that people do not just receive. They remember.</p><p>Inside: one Lumière Rose & Jasmine (a lush, romantic floral with Indian origins — heady, feminine, deeply beautiful) and one Lumière Cedarwood & Vetiver (grounding, woody, effortlessly sophisticated). Together, they tell a complete olfactory story — day into night, softness into depth.</p><p>The La Nuit box is tied with a hand-cut satin ribbon and includes a personalised gift note card, added at checkout. No additional wrapping needed. It arrives as a gift should: perfectly considered, completely ready. Whether for Diwali, a birthday, or simply because — La Nuit is the Lumière gift.</p>",
            "bullet_features": ["2 × 100g premium soy candles — Rose Jasmine + Cedarwood Vetiver", "Magnetic gift box with black velvet lining", "Hand-tied satin ribbon with embossed wax seal", "Personalised gift note included — add message at checkout", "Free gift wrapping — arrives ready to give"],
            "price": 2199, "compare_at_price": 2599, "weight_grams": 250, "burn_time_hours": 40,
            "scent_notes": {"top": ["Rose", "Bergamot", "Cedarwood"], "heart": ["Jasmine", "Vetiver"], "base": ["White Musk", "Sandalwood"]},
            "seo_meta_tags": {
                "title": "La Nuit Gift Set — Luxury Candle Gift India | Lumière",
                "description": "Two premium soy candles in a luxury magnetic gift box. Perfect for Diwali, birthdays & anniversaries. Free personalised note.",
                "keywords": ["luxury candle gift India", "Diwali gift candle", "premium candle gift set India"],
            },
            "shopify_tags": ["gift-set", "luxury", "gifting", "rose-jasmine", "cedarwood"],
            "product_type": "Gift Set", "vendor": "Lumière",
            "variants": [{"title": "2-Candle Set", "price": 2199, "sku": "LUM-NUIT-GIFT-SET", "inventory_quantity": 30}],
        },
    ]
