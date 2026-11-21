"""Quick self-checks:  python -m unittest test_basic -v"""
import os
import tempfile
import unittest

os.environ["FORCE_DEMO"] = "true"
os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "test.db")

import database as db
from monitor import check_stock
from sentiment import analyze


class Tests(unittest.TestCase):
    def test_sentiment(self):
        self.assertEqual(analyze("Shares surge after record profit")[0], "Positive")
        self.assertEqual(analyze("Company faces fraud probe and penalty")[0], "Negative")
        self.assertEqual(analyze("Company holds annual meeting")[0], "Neutral")

    def test_pipeline(self):
        db.init_db()
        db.add_to_watchlist("TSLA", "Tesla")
        r = check_stock("TSLA", "Tesla", force_news=True)
        self.assertIsNone(r["error"])
        self.assertEqual(len(r["news"]), 3)
        self.assertEqual(db.get_watchlist()[0]["symbol"], "TSLA")


if __name__ == "__main__":
    unittest.main()
