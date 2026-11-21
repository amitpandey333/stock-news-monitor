"""News mood detection: Positive (Good), Negative (Bad) or Neutral.

Uses VADER (with extra finance words) when installed, otherwise a built-in word list.
"""
import re

FINANCE_WORDS = {
    # good for investors
    "surge": 2.5, "soar": 2.5, "soars": 2.5, "rally": 2.0, "beat": 2.0, "beats": 2.0,
    "record": 1.5, "upgrade": 2.0, "growth": 1.5, "profit": 1.8, "gain": 1.5, "gains": 1.5,
    "boost": 1.8, "approval": 1.5, "partnership": 1.2, "dividend": 1.2, "outperform": 2.0,
    "bullish": 2.2, "jumps": 2.0, "climbs": 1.8, "rises": 1.5, "strong": 1.5, "wins": 1.8,
    # bad for investors
    "fraud": -3.0, "lawsuit": -2.0, "sued": -2.0, "sues": -2.0, "penalty": -2.2, "fine": -1.5,
    "miss": -2.0, "misses": -2.0, "plunge": -2.8, "tumble": -2.2, "crash": -3.0,
    "downgrade": -2.0, "bankruptcy": -3.2, "recall": -2.2, "probe": -1.8,
    "investigation": -1.8, "layoffs": -2.0, "loss": -1.8, "losses": -1.8, "decline": -1.5,
    "slump": -2.2, "scandal": -2.8, "cuts": -1.2, "overvalued": -2.5, "outage": -2.2,
    "outages": -2.2, "concerns": -1.8, "concern": -1.8, "worries": -1.8, "risk": -1.5,
    "risks": -1.5, "lows": -2.0, "warning": -2.0, "weak": -1.8, "falls": -1.8, "drops": -1.8,
    "drop": -1.8, "sinks": -2.2, "selloff": -2.5, "bearish": -2.2, "delays": -1.5,
    "delay": -1.5, "ban": -2.0, "antitrust": -1.8, "shortfall": -2.0, "halt": -1.8,
}

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    _vader = SentimentIntensityAnalyzer()
    _vader.lexicon.update(FINANCE_WORDS)
except ImportError:  # fallback keeps the project runnable without the library
    _vader = None


def _lexicon_score(text):
    words = re.findall(r"[a-z']+", text.lower())
    hits = [FINANCE_WORDS[w] for w in words if w in FINANCE_WORDS]
    if not hits:
        return 0.0
    return max(-1.0, min(1.0, sum(hits) / (len(hits) * 3.0) * (1 + 0.15 * (len(hits) - 1))))


def analyze(text):
    """Return (mood, score) where score is between -1 and +1."""
    text = (text or "").strip()
    if not text:
        return "Neutral", 0.0
    score = _vader.polarity_scores(text)["compound"] if _vader else _lexicon_score(text)
    if score >= 0.05:
        mood = "Positive"
    elif score <= -0.05:
        mood = "Negative"
    else:
        mood = "Neutral"
    return mood, round(score, 3)