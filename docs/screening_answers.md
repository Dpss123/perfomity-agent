# Screening Questions — Answers
### Q1 to Q5

---

## Q1 — Which agent framework did you use and why?

I used **LangGraph** (StateGraph) with **Groq LLaMA 3.1 70B** as the LLM backbone.

I chose LangGraph over plain LangChain or CrewAI because this is a sequential pipeline — not a loop or multi-agent conversation — and LangGraph's node/edge model maps exactly to that structure. Each step (research, strategy, content, Shopify) becomes a named node with a typed state object passing between them. This makes the pipeline easy to read, debug, and extend: if I want to add a human-approval checkpoint after content generation, it is literally one conditional edge. CrewAI would add unnecessary abstraction for a 4-step sequential flow with no agent-to-agent negotiation needed.

---

## Q2 — How does the agent handle ambiguous or incomplete briefs?

The agent makes **confident autonomous assumptions** rather than stalling to ask clarifying questions, because interrupting the pipeline defeats the purpose of autonomy.

When the brief says "Forest Essentials vibes", the research node infers: minimal luxury aesthetic, warm earth tones, serif typography, Ayurvedic-adjacent but modern. These inferences are embedded in the strategy node's system prompt as brand archetype mappings. All assumptions are logged explicitly in `output/handoff_report.md` under the Decisions section so a human reviewer can override them before the Shopify deploy step.

In production I would add an optional pre-flight clarification form (name, category, price range, 3 competitors you admire) that pre-populates the brief with structured context before the pipeline runs — reducing ambiguity without blocking on back-and-forth.

---

## Q3 — What is the worst failure mode of your agent and how did you handle it?

The worst failure mode is **generic, off-brand copy** — the LLM produces fluent but interchangeable luxury language that could belong to any candle brand. It is the hardest failure to detect automatically because the output is grammatically correct and sounds premium.

How I handled it:
1. Negative instructions in every content system prompt — explicit banned phrases ("affordable", "premium experience", "unboxing journey", "quality products")
2. Brand archetype framing in the strategy node forces a specific named voice before copy is generated — the content node receives that archetype as context
3. BeautifulSoup scraping of real competitor pages gives the LLM actual examples of what competitors are saying — making differentiation more concrete

Planned for v2: a second-pass LLM scorer that computes semantic similarity between generated copy and competitor descriptions, flags anything above 0.80 cosine similarity for human review.

---

## Q4 — How would you scale this to handle 50 simultaneous store builds?

Current bottleneck: the pipeline is fully synchronous — one brief at a time, sequential LLM calls. At 50 simultaneous briefs, Groq's free-tier rate limits and ~90 second per-pipeline runtime would result in ~75 minutes total.

Fix in three layers:

**1. Async within each pipeline**
Switch all Groq calls to `asyncio` with `asyncio.gather()` — research, strategy, and content LLM calls that don't depend on each other can run concurrently. Cuts per-pipeline time from ~90s to ~25s.

**2. Job queue across pipelines**
Wrap each brief in a Celery task with Redis as the broker. 50 briefs queue up and process across worker processes. Each worker handles one pipeline at a time with async LLM calls inside.

**3. Rate limit management**
Rotate Groq API keys across multiple free accounts (5 keys = 5× the free quota). Cache Tavily research results for similar briefs (same niche + city = reuse research output, skip to strategy). Add exponential backoff retry on 429 responses.

Target: 50 briefs processed in under 10 minutes.

---

## Q5 — What is the most impressive AI agent or automation you have built?

**REDACT — AI-Powered Document PII Masking Tool**
*(National Hackathon Winner — 1st place)*

REDACT is an agent that ingests documents (PDFs, DOCX, scanned images), detects all PII (names, Aadhaar numbers, phone numbers, addresses, financial data, email addresses), and redacts them with pixel-level precision — producing a clean, audit-ready output document.

What I am most proud of technically is the **two-stage detection pipeline**:
- Stage 1: spaCy NER + regex patterns catches obvious PII fast (names, phone numbers, email)
- Stage 2: Groq LLaMA does a second pass over the full document context to catch *contextual PII* that pattern-matching misses — for example, "my sister Priya" where "Priya" only reads as PII because of the surrounding sentence

The two stages are cheaper and more accurate together than either approach alone. Stage 1 handles 90% of cases in milliseconds; Stage 2 handles the hard 10% that requires reading context.

GitHub: https://github.com/YOUR_USERNAME/redact

> ⚠️ Replace the GitHub link above with your actual REDACT repository URL before submitting.
