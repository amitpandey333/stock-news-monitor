"""Re-score all saved news with the current sentiment rules."""
import sqlite3

from config import DB_PATH
from sentiment import analyze

conn = sqlite3.connect(DB_PATH)
rows = conn.execute("SELECT id, title FROM news").fetchall()
for news_id, title in rows:
    mood, score = analyze(title)
    conn.execute("UPDATE news SET mood = ?, score = ? WHERE id = ?", (mood, score, news_id))
conn.commit()
conn.close()
print(f"Re-scored {len(rows)} articles.")