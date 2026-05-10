"""
Tavily Web Search Tool
Free tier: 1000 searches/month — tavily.com
"""

import os
from tavily import TavilyClient

_client = None


def get_client() -> TavilyClient:
    
    return _client


def search(query: str, max_results: int = 5) -> list[dict]:
    """Search the web. Returns list of {title, url, content, score}."""
    try:
        client = get_client()
        resp = client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_answer=True,
        )
        return [
            {
                "title":   r.get("title", ""),
                "url":     r.get("url", ""),
                "content": r.get("content", "")[:1000],
                "score":   r.get("score", 0),
            }
            for r in resp.get("results", [])
        ]
    except Exception as e:
        print(f"  [Tavily] search failed: {e}")
        return []


def search_answer(query: str) -> str:
    """Returns Tavily's AI-synthesised answer for a query."""
    try:
        client = get_client()
        resp = client.search(
            query=query,
            search_depth="advanced",
            max_results=5,
            include_answer=True,
        )
        return resp.get("answer", "") or ""
    except Exception as e:
        print(f"  [Tavily] answer search failed: {e}")
        return ""
