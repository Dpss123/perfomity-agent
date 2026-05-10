

import sys
import os
from dotenv import load_dotenv

load_dotenv(override=True)

DEFAULT_BRIEF = """
We want to sell premium handcrafted soy candles targeting urban women aged 25-40 in India.
Brand name is 'Lumière'. Products are scented candles in luxury packaging — price range
₹599 to ₹2,499. We want to feel like a modern, minimal luxury brand, similar to Forest
Essentials but for home fragrance. We need a homepage, a collections page, and 3 sample
product listings.
"""


def main():
    brief = " ".join(sys.argv[1:]).strip() if len(sys.argv) > 1 else DEFAULT_BRIEF.strip()

    print("\n" + "=" * 60)
    print("  LUMIÈRE — SHOPIFY STORE BUILDER AGENT")
    print("  Perfomity Media · AI Agent Assignment")
    print("=" * 60)
    print(f"\nBrief: {brief[:120]}...")
    print()

    # Import here so dotenv loads first
    from agent.graph import build_graph

    graph = build_graph()

    initial_state = {
        "brief":        brief,
        "research":     None,
        "strategy":     None,
        "store_assets": None,
        "shopify":      None,
        "errors":       [],
    }

    final_state = graph.invoke(initial_state)

    print("\n" + "=" * 60)
    print("  ALL DONE")
    print()
    print("  output/research_output.json   → Deliverable 2")
    print("  output/store_assets.json      → Deliverable 3")
    print("  output/shopify_schema.json    → Deliverable 4")
    print("  output/handoff_report.md      → Handoff Report")
    print("=" * 60 + "\n")

    if final_state.get("errors"):
        print("Errors encountered:")
        for e in final_state["errors"]:
            print(f"  - {e}")

    return final_state


if __name__ == "__main__":
    main()
