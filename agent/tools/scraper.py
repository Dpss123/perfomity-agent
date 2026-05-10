"""
BeautifulSoup Web Scraper
Used to extract product info, pricing, and copy from competitor pages.
"""

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def scrape_page(url: str, timeout: int = 8) -> dict:
    """
    Scrape a URL and return {url, title, headings, paragraphs, prices}.
    Returns empty dict on failure — caller must handle gracefully.
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove script/style noise
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()

        title = soup.title.string.strip() if soup.title else ""

        headings = [
            h.get_text(strip=True)
            for h in soup.find_all(["h1", "h2", "h3"])
            if h.get_text(strip=True)
        ][:10]

        paragraphs = [
            p.get_text(strip=True)
            for p in soup.find_all("p")
            if len(p.get_text(strip=True)) > 40
        ][:8]

        # Basic price extraction — look for ₹ or Rs patterns
        import re
        raw_text = soup.get_text()
        prices = re.findall(r"₹[\s]?\d[\d,]+", raw_text)[:10]

        return {
            "url":        url,
            "title":      title,
            "headings":   headings,
            "paragraphs": paragraphs,
            "prices":     list(set(prices)),
        }

    except Exception as e:
        print(f"  [Scraper] Failed to scrape {url}: {e}")
        return {"url": url, "error": str(e)}


def scrape_multiple(urls: list[str]) -> list[dict]:
    """Scrape multiple URLs, skip failures."""
    results = []
    for url in urls:
        data = scrape_page(url)
        if "error" not in data:
            results.append(data)
    return results
