"""Fetch stock prices from Alpha Vantage and calculate the change between trading days."""
import random

import requests

from config import ALPHA_VANTAGE_KEY, REQUEST_TIMEOUT, STOCK_DEMO

URL = "https://www.alphavantage.co/query"


class StockAPIError(Exception):
    """Raised for network problems, rate limits or invalid symbols."""


def _demo_price(symbol):
    rng = random.Random(symbol.upper())          # same symbol -> same demo numbers
    prev_close = round(rng.uniform(50, 400), 2)
    change_pct = round(rng.uniform(-6, 6), 2)
    close = round(prev_close * (1 + change_pct / 100), 2)
    return {"symbol": symbol.upper(), "date": "DEMO", "close": close,
            "prev_close": prev_close, "change": round(close - prev_close, 2),
            "change_pct": change_pct}


def get_price_change(symbol):
    symbol = symbol.upper()
    if STOCK_DEMO:
        return _demo_price(symbol)
    try:
        resp = requests.get(URL, params={"function": "TIME_SERIES_DAILY", "symbol": symbol,
                                         "apikey": ALPHA_VANTAGE_KEY}, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError) as exc:
        raise StockAPIError(f"Could not reach Alpha Vantage: {exc}") from exc

    series = data.get("Time Series (Daily)")
    if not series:
        reason = data.get("Note") or data.get("Information") or data.get("Error Message") \
                 or "Unexpected response"
        raise StockAPIError(f"{symbol}: {reason}")

    latest, previous = sorted(series, reverse=True)[:2]
    close = float(series[latest]["4. close"])
    prev_close = float(series[previous]["4. close"])
    change = close - prev_close
    return {"symbol": symbol, "date": latest, "close": round(close, 2),
            "prev_close": round(prev_close, 2), "change": round(change, 2),
            "change_pct": round(change / prev_close * 100, 2)}
