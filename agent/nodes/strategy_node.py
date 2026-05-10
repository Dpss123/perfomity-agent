"""
Strategy Node — Step 2 of 4
=============================
Takes research output and builds brand strategy.
Output: color palette, typography, brand voice, persona.
"""

import json
from agent.state import AgentState
from agent.tools.llm import llm

SYSTEM = """You are a luxury brand strategist for premium D2C brands in India.
Build distinctive brand strategies from market research data.
Respond ONLY with valid JSON. No markdown, no explanation."""


def strategy_node(state: AgentState) -> AgentState:
    research = state.get("research", {})
    errors   = state.get("errors", [])

    print("\n[Node 2/4] Strategy — building brand strategy...")

    strategy = _build_strategy(state["brief"], research)
    palette  = _build_palette()
    typo     = _build_typography()

    print("  ✓ Strategy complete")
    return {**state, "strategy": {**strategy, "color_palette": palette, "typography": typo}, "errors": errors}


def _build_strategy(brief: str, research: dict) -> dict:
    direction = research.get("brand_direction", {})
    pricing   = research.get("pricing_analysis", {})

    prompt = f"""Create brand strategy for Lumière based on:

Brief: {brief}
Brand direction: {json.dumps(direction, ensure_ascii=False)}
Pricing context: {json.dumps(pricing, ensure_ascii=False)}

Return JSON:
{{
  "brand_name": "Lumière",
  "tagline": "4-6 word evocative tagline",
  "brand_story": "2-paragraph brand story for About Us page",
  "brand_values": [
    {{"name": "value name", "description": "25-word description"}}
  ],
  "target_persona": {{
    "name": "Indian first name",
    "age_range": "X–Y",
    "lifestyle": "2 sentences",
    "desires": "what she wants from a luxury candle brand",
    "pain_points": "why she cannot find it elsewhere"
  }},
  "messaging_pillars": ["3 core messages for all copy"]
}}

Return ONLY valid JSON."""

    resp = llm(SYSTEM, prompt, temperature=0.65, json_mode=True)
    try:
        return json.loads(resp)
    except Exception:
        return {
            "brand_name": "Lumière",
            "tagline": "Light your finest moments.",
            "brand_story": "Lumière was born from a simple belief: that your home deserves the same devotion you bring to everything you love. We started in a small studio in Bengaluru, hand-pouring soy candles for friends who could not find a luxury Indian candle brand that felt truly special.\n\nToday, every Lumière candle is still poured by hand in small batches, using the finest natural soy wax and fragrance oils. We do not rush. We do not compromise. We believe in making things that last — in memory, and in warmth.",
            "brand_values": [
                {"name": "Intentional Luxury", "description": "Every detail considered. Nothing superfluous. Beauty that earns its place."},
                {"name": "Sensorial Craft", "description": "Fragrance as an art form — created to move, not just to smell."},
                {"name": "Slow Living", "description": "Designed for moments of pause, presence, and personal ritual."},
            ],
            "target_persona": {
                "name": "Priya",
                "age_range": "28–38",
                "lifestyle": "Urban professional in a metro. Design-conscious, buys intentionally. Her home is curated, not decorated.",
                "desires": "A luxury candle brand that feels Indian without being old-fashioned — premium without being pretentious.",
                "pain_points": "Most Indian candle brands feel mass-market. International brands are expensive and disconnected from her world.",
            },
            "messaging_pillars": [
                "Handcrafted with intention — every candle poured by hand in small batches",
                "Fragrance as ritual — scent that transforms your space and state of mind",
                "Indian luxury redefined — premium quality, rooted in India, made for today",
            ],
        }


def _build_palette() -> dict:
    return {
        "primary":    "#0E0C09",
        "secondary":  "#C9A55A",
        "accent":     "#E2C07A",
        "background": "#FAF7F0",
        "surface":    "#F0EAE0",
        "text":       "#0E0C09",
        "muted":      "#B5A898",
        "palette_name": "Lumière Noir & Or",
        "rationale": "Deep noir anchors the brand in immediate luxury and creates dramatic contrast with champagne gold. The gold evokes candlelight itself — thematic coherence. Ivory backgrounds give an editorial gallery-white quality. Taupe provides warmth in body copy without competing with the primary text hierarchy.",
    }


def _build_typography() -> dict:
    return {
        "display": {
            "name":        "Cormorant Garamond",
            "google_font": "Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400",
            "use":         "Hero headlines, product names, section titles, pull quotes",
            "rationale":   "High-contrast thin-thick strokes of refined luxury brands (Hermès, Vogue). The 300 italic at large sizes creates airy luxury. Competes with Aesop and The Row globally.",
        },
        "body": {
            "name":        "Jost",
            "google_font": "Jost:wght@300;400;500",
            "use":         "Navigation, body copy, buttons, captions, price tags",
            "rationale":   "Geometric sans-serif with refined letter-spacing. Clean and modern without coldness. Pairs beautifully with Cormorant by contrast without competition.",
        },
        "accent": {
            "name":        "Italiana",
            "google_font": "Italiana",
            "use":         "Founder quotes, testimonials — use sparingly",
            "rationale":   "Italian-influenced serif with dramatic stroke contrast. Reserved for moments of maximum elegance.",
        },
        "pairing_note": "The Cormorant/Jost pairing is used by Mejuri, Coterie, and other top luxury DTC brands globally. Cormorant carries heritage and emotion; Jost carries precision and legibility.",
    }
