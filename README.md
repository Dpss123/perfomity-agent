# Lumière - Shopify Store Builder AI Agent
**Perfomity Media · AI Agent Developer Screening Assignment**

[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-gold?style=flat-square&logo=github)](https://github.com/Dpss123/perfomity-agent)

---

## Architecture Overview

A **4-node LangGraph pipeline** that accepts a text business brief and autonomously:
1. Researches the market (Tavily search + BeautifulSoup scraping)
2. Builds brand strategy from research data
3. Generates all store copy and product listings
4. Deploys to Shopify or exports schema-ready JSON

```
[Input Brief]
      │
      ▼
┌─────────────┐    Tavily API + BeautifulSoup
│ research    │──► competitor scraping, trends, pricing
└──────┬──────┘
       │
       ▼
┌─────────────┐    Groq LLaMA 3.1 70B
│  strategy   │──► brand voice, palette, typography
└──────┬──────┘
       │
       ▼
┌─────────────┐    Groq LLaMA 3.1 70B
│  content    │──► homepage, products, collection, about us
└──────┬──────┘
       │
       ▼
┌─────────────┐    Shopify Admin API
│  shopify    │──► deploy live OR export JSON schema
└─────────────┘
       │
       ▼
output/research_output.json
output/store_assets.json
output/shopify_schema.json
output/handoff_report.md
```

---

## How to Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set API keys
```bash
cp .env.example .env
# Open .env and fill in your keys
```

### 3. Run the agent
```bash
python main.py
```

The agent accepts the default brief or a custom one:
```bash
python main.py "Your custom business brief here"
```

### 4. View output
All outputs saved to `output/` folder:
- `research_output.json` - competitor data, trends, pricing
- `store_assets.json` - all generated copy and product listings
- `shopify_schema.json` - Shopify API-ready JSON
- `handoff_report.md` - decision summary report

---

## APIs / Keys Required

| Key | Required | Free Tier | Get It At |
|-----|----------|-----------|-----------|
| `GROQ_API_KEY` | ✅ Yes | ✅ Free | console.groq.com |
| `TAVILY_API_KEY` | ✅ Yes | ✅ Free (1000/mo) | tavily.com |
| `SHOPIFY_ACCESS_TOKEN` | Optional | ✅ Free dev store | partners.shopify.com |
| `SHOPIFY_STORE_URL` | Optional | ✅ Free dev store | partners.shopify.com |

> Shopify keys are optional. Without them, the agent exports a schema-ready JSON file instead of deploying live.

---

## Limitations

- Research quality depends on Tavily results for the Indian candle market (smaller data pool than Western markets)
- No image generation - placeholder image URLs used in product listings
- Shopify theme/CSS customisation requires a separate manual step
- Agent runs sequentially - parallel execution not implemented in this version
- BeautifulSoup scraping may be blocked by some sites; fallback data used in that case

---

## Framework

Built with **LangGraph** (StateGraph) - chosen because it provides explicit node/edge control over the pipeline, clean state passing between steps, and is the most production-relevant framework for multi-step agent workflows per the assignment spec.
