"""SQLite storage for the watchlist, prices and analysed news (Database Connectivity)."""
import sqlite3
from contextlib import closing
from datetime import datetime

from config import DB_PATH


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with closing(_connect()) as conn, conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS watchlist (
                symbol TEXT PRIMARY KEY,
                name   TEXT
            );
            CREATE TABLE IF NOT EXISTS prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT, trade_date TEXT, close REAL,
                prev_close REAL, change_pct REAL, checked_at TEXT
            );
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT, title TEXT, description TEXT,
                url TEXT UNIQUE, source TEXT, published_at TEXT,
                mood TEXT, score REAL, alerted INTEGER DEFAULT 0
            );
            """
        )


def add_to_watchlist(symbol, name=None):
    with closing(_connect()) as conn, conn:
        conn.execute("INSERT OR REPLACE INTO watchlist (symbol, name) VALUES (?, ?)",
                     (symbol.upper(), name or symbol.upper()))


def remove_from_watchlist(symbol):
    with closing(_connect()) as conn, conn:
        conn.execute("DELETE FROM watchlist WHERE symbol = ?", (symbol.upper(),))


def get_watchlist():
    with closing(_connect()) as conn:
        return [dict(r) for r in conn.execute("SELECT symbol, name FROM watchlist ORDER BY symbol")]


def save_price(p):
    with closing(_connect()) as conn, conn:
        conn.execute(
            "INSERT INTO prices (symbol, trade_date, close, prev_close, change_pct, checked_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (p["symbol"], p["date"], p["close"], p["prev_close"], p["change_pct"],
             datetime.now().isoformat(timespec="seconds")),
        )


def get_latest_prices():
    """Most recent saved price row for every symbol."""
    with closing(_connect()) as conn:
        rows = conn.execute(
            "SELECT * FROM prices WHERE id IN (SELECT MAX(id) FROM prices GROUP BY symbol)"
        )
        return {r["symbol"]: dict(r) for r in rows}


def save_news(symbol, a):
    """Insert an article. Returns True if it is new, False if the URL was already stored."""
    with closing(_connect()) as conn, conn:
        cur = conn.execute(
            "INSERT OR IGNORE INTO news (symbol, title, description, url, source, published_at, mood, score) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (symbol, a["title"], a.get("description", ""), a["url"], a.get("source", ""),
             a.get("published_at", ""), a["mood"], a["score"]),
        )
        return cur.rowcount == 1


def mark_alerted(url):
    with closing(_connect()) as conn, conn:
        conn.execute("UPDATE news SET alerted = 1 WHERE url = ?", (url,))


def get_news(symbol=None, limit=50):
    query = "SELECT * FROM news"
    args = []
    if symbol:
        query += " WHERE symbol = ?"
        args.append(symbol.upper())
    query += " ORDER BY published_at DESC, id DESC LIMIT ?"
    args.append(limit)
    with closing(_connect()) as conn:
        return [dict(r) for r in conn.execute(query, args)]
