# Deliverable 5 — Architecture Write-Up
### Lumière Store Builder Agent · Perfomity Media Screening Assignment

---

## 1. High-Level Architecture

The agent is a **4-node LangGraph StateGraph pipeline**. Each node is a specialised step that reads from a shared state object, does one job, and writes its output back into state before passing to the next node.

```
[Input Brief]
      │
      ▼
┌──────────────────────────────────────┐
│  Node 1 — research                   │
│                                      │
│  Tools:                              │
│    • Tavily Search API               │
│    • BeautifulSoup scraper           │
│    • Groq LLaMA 3.1 70B (synthesis) │
│                                      │
│  Produces:                           │
│    state["research"] = {             │
│      competitors,                    │
│      product_trends,                 │
│      pricing_analysis,               │
│      brand_direction                 │
│    }                                 │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  Node 2 — strategy                   │
│                                      │
│  Tools: Groq LLaMA 3.1 70B          │
│                                      │
│  Produces:                           │
│    state["strategy"] = {             │
│      tagline, brand_story,           │
│      brand_values, persona,          │
│      color_palette, typography       │
│    }                                 │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  Node 3 — content                    │
│                                      │
│  Tools: Groq LLaMA 3.1 70B          │
│                                      │
│  Produces:                           │
│    state["store_assets"] = {         │
│      homepage, products (×3),        │
│      collection, about_us, seo       │
│    }                                 │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  Node 4 — shopify                    │
│                                      │
│  Tools: Shopify Admin API            │
│                                      │
│  Produces:                           │
│    → Live deploy (if keys set)       │
│    → shopify_schema.json (fallback)  │
│    → handoff_report.md (always)      │
└──────────────────────────────────────┘
```

**Why LangGraph over LangChain LCEL or plain Python:**
LangGraph provides a typed StateGraph with explicit node/edge definitions — making the pipeline easy to inspect, extend, and debug. It is also the most production-relevant framework for multi-step agent workflows, and is specifically mentioned in the assignment spec.

---

## 2. Tools at Each Node

### Node 1 — Tavily Search API
- Free tier (1,000 searches/month), no credit card required
- `search_depth: "advanced"` returns full page content not just snippets
- Returns a Tavily-synthesised answer per query in addition to raw results — doubles the signal per API call
- 3 queries: competitor discovery, trend analysis, pricing norms

### Node 1 — BeautifulSoup Scraper
- Directly scrapes competitor URLs found by Tavily
- Extracts: page title, H1/H2/H3 headings, body paragraphs, and price patterns (₹ regex)
- Graceful failure: `try/except` per URL, failed scrapes simply skipped
- Adds real scraped data on top of Tavily results for richer competitor intelligence

### Nodes 2 & 3 — Groq LLaMA 3.1 70B
- Completely free, no credit card, 130k context window
- JSON mode (`response_format: json_object`) used on every call — reliable structured output
- Temperature 0.3–0.4 for strategy (consistency), 0.7–0.8 for copy (creativity)
- Every call has a `try/except` with a hardcoded fallback dict — pipeline never crashes

### Node 4 — Shopify Admin API
- REST API, version 2024-01
- `time.sleep(0.6)` between calls to stay under the 2 req/sec dev store rate limit
- Auto-detects whether keys are configured — deploys live or exports JSON accordingly

---

## 3. Where Human Input Ends, Autonomy Begins

```
Human provides:
  ✅ One paragraph text brief
  ✅ API keys in .env file
─────────────────────────────────────────
Agent decides autonomously:
  ✓ Which 5 competitors to profile
  ✓ Which URLs to scrape
  ✓ Scent and SKU recommendations
  ✓ Exact pricing and compare-at prices
  ✓ Brand archetype, voice, tone
  ✓ Color palette hex codes
  ✓ Font pairing and rationale
  ✓ All store copy — hero, products, about
  ✓ SEO meta titles and descriptions
  ✓ Shopify JSON schema structure
  ✓ Whether to deploy live or export JSON
  ✓ Handoff report content
```

---

## 4. Biggest Failure Modes and Mitigations

### Failure Mode 1 — Generic Off-Brand Copy (Highest Risk)
**What happens:** LLM produces fluent but interchangeable luxury copy.
**Why it's hard to detect:** Grammatically correct, sounds premium, but could belong to any candle brand.
**Mitigations:**
- Negative instructions in system prompt: banned phrases list ("affordable", "premium experience", "unbox")
- Brand archetype framing forces a specific voice in every content call
- Planned v2: second-pass LLM scorer that checks copy uniqueness against competitor descriptions

### Failure Mode 2 — Tavily Returns Irrelevant Results
**What happens:** Indian D2C candle market is small; queries may return global or SEO-spam results.
**Mitigations:**
- `score` field filtered — anything below 0.5 dropped
- BeautifulSoup scraping of actual competitor URLs adds real data on top of Tavily
- Full fallback data dictionary hardcoded — pipeline produces useful output even with zero API results

### Failure Mode 3 — LLM JSON Parse Failure
**What happens:** LLM wraps JSON in markdown fences, adds preamble, or returns malformed JSON.
**Mitigations:**
- `response_format: json_object` used on all calls (Groq json_mode is reliable)
- `try/except` on every `json.loads()` call — catches any edge cases
- Every LLM call has a hardcoded fallback dict returned on failure — zero pipeline crashes

### Failure Mode 4 — Shopify API Auth or Rate Limiting
**What happens:** Invalid token, wrong store URL format, or 429 on dev store (2 req/sec limit).
**Mitigations:**
- `time.sleep(0.6)` between consecutive Shopify calls
- HTTP status code check on every request
- Graceful fallback to JSON export if auth fails or keys are missing

---

## 5. What I Would Build With More Time

### Quality Improvements
- **Human-in-the-loop checkpoints** after Node 1 and Node 3 — show output in a simple Streamlit UI before continuing
- **RAG over competitor stores** — Firecrawl full-page scrape → sentence-transformers embeddings → Chroma → query for specific copy patterns → ensures genuinely differentiated output
- **Image generation** — Stability AI / DALL-E 3 for product hero images
- **Copy quality scoring** — second LLM pass scores uniqueness and brand consistency

### Scale Improvements
- **Async execution** — `asyncio.gather()` for concurrent LLM calls, cuts 90s runtime to ~25s
- **Pydantic validation** on every node output — zero silent failures
- **Celery + Redis job queue** for 50 concurrent brief processing
- **Groq key rotation** across multiple free accounts for rate limit headroom
- **LangSmith tracing** for full observability of every node input/output
