"""Streamlit dashboard: all stocks, mood scores and news on one screen.
Run with:  streamlit run dashboard.py
"""
import pandas as pd
import streamlit as st

import database as db
from config import NEWS_DEMO, PRICE_THRESHOLD, SMS_ENABLED, STOCK_DEMO
from monitor import check_all

st.set_page_config(page_title="Stock News Monitor", page_icon="📈", layout="wide")
db.init_db()
st.title("📈 Stock News Monitoring System")
st.caption(f"Prices: {'demo' if STOCK_DEMO else 'live'} · News: {'demo' if NEWS_DEMO else 'live'} · "
           f"Alerts: {'SMS' if SMS_ENABLED else 'console'}")

with st.sidebar:
    st.header("Watchlist")
    sym = st.text_input("Symbol", placeholder="TSLA").strip().upper()
    name = st.text_input("Company name", placeholder="Tesla")
    if st.button("Add stock") and sym:
        db.add_to_watchlist(sym, name or sym)
        st.rerun()
    for w in db.get_watchlist():
        c1, c2 = st.columns([3, 1])
        c1.write(f"**{w['symbol']}** {w['name']}")
        if c2.button("✕", key=f"rm_{w['symbol']}"):
            db.remove_from_watchlist(w["symbol"])
            st.rerun()
    st.divider()
    threshold = st.slider("Price-change threshold (%)", 0.5, 10.0, PRICE_THRESHOLD, 0.5)
    force = st.checkbox("Fetch news even if below threshold", value=True)
    if st.button("🔄 Refresh now", type="primary"):
        with st.spinner("Checking stocks..."):
            for r in check_all(threshold, force_news=force):
                if r["error"]:
                    st.warning(f"{r['symbol']}: {r['error']}")

watchlist = db.get_watchlist()
if not watchlist:
    st.info("Add a stock in the sidebar (try TSLA / Tesla), then press Refresh.")
    st.stop()

prices = db.get_latest_prices()
cols = st.columns(len(watchlist))
for col, w in zip(cols, watchlist):
    p = prices.get(w["symbol"])
    if p:
        col.metric(w["symbol"], f"{p['close']:.2f}", f"{p['change_pct']:+.2f}%")
    else:
        col.metric(w["symbol"], "—", "not checked")

news = pd.DataFrame(db.get_news(limit=200))
if news.empty:
    st.info("No news stored yet. Press Refresh now.")
    st.stop()

left, right = st.columns([1, 2])
with left:
    st.subheader("Mood by stock")
    counts = news.pivot_table(index="symbol", columns="mood", values="id", aggfunc="count", fill_value=0)
    counts = counts.reindex(columns=["Negative", "Neutral", "Positive"], fill_value=0)
    st.bar_chart(counts, color=["#e53935", "#9e9e9e", "#43a047"])
    st.subheader("Average mood score")
    st.bar_chart(news.groupby("symbol")["score"].mean())
with right:
    st.subheader("Latest news")
    pick = st.selectbox("Filter", ["All"] + [w["symbol"] for w in watchlist])
    view = news if pick == "All" else news[news["symbol"] == pick]
    badge = {"Positive": "🟢", "Negative": "🔴", "Neutral": "⚪"}
    for _, row in view.head(25).iterrows():
        st.markdown(f"{badge[row['mood']]} **{row['symbol']}** · {row['mood']} ({row['score']:+.2f}) · "
                    f"[{row['title']}]({row['url']})  \n<small>{row['source']} · {row['published_at']}</small>",
                    unsafe_allow_html=True)
