"""Core logic: price check -> (if big move) news -> sentiment -> save -> alert."""
import database as db
from alerts import send_alert
from config import HIGH_IMPACT, NEWS_LIMIT, PRICE_THRESHOLD
from news_api import NewsAPIError, fetch_news
from sentiment import analyze
from stock_api import StockAPIError, get_price_change


def check_stock(symbol, name=None, threshold=PRICE_THRESHOLD, force_news=False):
    """Run the full workflow for one stock and return a result dictionary."""
    result = {"symbol": symbol.upper(), "price": None, "triggered": False,
              "news": [], "alerts": 0, "error": None}
    try:
        price = get_price_change(symbol)
    except StockAPIError as exc:
        result["error"] = str(exc)
        return result

    db.save_price(price)
    result["price"] = price
    result["triggered"] = abs(price["change_pct"]) >= threshold

    if not (result["triggered"] or force_news):
        return result

    try:
        articles = fetch_news(symbol, name, NEWS_LIMIT)
    except NewsAPIError as exc:
        result["error"] = str(exc)
        return result

    for article in articles:
        article["mood"], article["score"] = analyze(article["title"])
        is_new = db.save_news(result["symbol"], article)
        result["news"].append(article)
        if is_new and abs(article["score"]) >= HIGH_IMPACT:
            send_alert(f"{result['symbol']} {price['change_pct']:+.2f}% | "
                       f"{article['mood']} news: {article['title']}")
            db.mark_alerted(article["url"])
            result["alerts"] += 1
    return result


def check_all(threshold=PRICE_THRESHOLD, force_news=False):
    return [check_stock(w["symbol"], w["name"], threshold, force_news) for w in db.get_watchlist()]
