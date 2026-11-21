"""Fetch company news from NewsAPI."""
import requests

from config import NEWS_API_KEY, NEWS_DEMO, REQUEST_TIMEOUT

URL = "https://newsapi.org/v2/everything"


class NewsAPIError(Exception):
    """Raised for network problems, bad keys or rate limits."""


_DEMO_HEADLINES = [
    ("{n} shares surge after record quarterly profit beats expectations",
     "Analysts upgrade the stock following strong growth across all divisions."),
    ("{n} faces regulatory probe and potential penalty over disclosure issues",
     "Investors worry as the investigation could lead to heavy fines."),
    ("{n} announces new product line at annual event",
     "The company presented its roadmap for the coming year."),
    ("{n} stock tumbles as earnings miss estimates, layoffs expected",
     "Shares plunge in early trading after weak guidance."),
]


def _demo_news(symbol, name, limit):
    return [{"title": t.format(n=name), "description": d,
             "url": f"https://demo.example/{symbol}/{i}", "source": "Demo Wire",
             "published_at": f"2026-01-0{i + 1}T09:00:00Z"}
            for i, (t, d) in enumerate(_DEMO_HEADLINES[:limit])]


def fetch_news(symbol, name=None, limit=3):
    name = name or symbol
    if NEWS_DEMO:
        return _demo_news(symbol, name, limit)
    query = f'("{name}" OR "{symbol}") AND (stock OR shares OR earnings OR investors OR market)'
    params = {"q": query, "searchIn": "title,description", "language": "en",
              "sortBy": "publishedAt", "pageSize": limit, "apiKey": NEWS_API_KEY}
    try:
        resp = requests.get(URL, params=params, timeout=REQUEST_TIMEOUT)
        data = resp.json()
    except (requests.RequestException, ValueError) as exc:
        raise NewsAPIError(f"Could not reach NewsAPI: {exc}") from exc
    if data.get("status") != "ok":
        raise NewsAPIError(data.get("message", "NewsAPI returned an error"))

    return [{"title": a.get("title") or "", "description": a.get("description") or "",
             "url": a.get("url") or "", "source": (a.get("source") or {}).get("name", ""),
             "published_at": a.get("publishedAt") or ""}
            for a in data.get("articles", []) if a.get("title") and a.get("url")]