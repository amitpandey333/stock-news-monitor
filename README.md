# Stock News Monitoring System

Python project: tracks a stock watchlist, fetches prices (Alpha Vantage) and news (NewsAPI),
classifies each headline as Positive / Negative / Neutral, stores everything in SQLite,
sends alerts (Twilio SMS) for high-impact news, and shows it all on a dashboard.

## Setup
```
pip install -r requirements.txt
cp .env.example .env        # optional: add your API keys
```
No keys? It still runs in **demo mode** (fake prices and headlines), good for testing and demos.

## Run
```
python main.py              # command-line menu
streamlit run dashboard.py  # dashboard in the browser
python -m unittest test_basic -v   # self-tests
```

- Alpha Vantage: https://www.alphavantage.co/support/#api-key (free plan: about 25 requests/day, so keep the watchlist small)
- NewsAPI: https://newsapi.org/register (free developer plan)
- Twilio (optional): https://www.twilio.com/try-twilio. Trial accounts can only SMS verified numbers.

## How it works (matches your slides)
1. User picks a stock (`main.py` / `dashboard.py`)
2. `stock_api.py` gets prices and calculates the change between the last two trading days
3. If change >= threshold (default 2%), `news_api.py` fetches the latest 3 articles
4. `sentiment.py` scores each article (-1 to +1) and labels its mood
5. `database.py` stores prices and news (duplicate articles ignored by URL)
6. `monitor.py` triggers `alerts.py` when |score| >= 0.5 (high-impact news)

## Files
| File | Purpose |
|---|---|
| config.py | Settings, .env reading (file handling) |
| stock_api.py / news_api.py | API integration, with exception handling |
| sentiment.py | Mood detection (VADER plus finance words) |
| database.py | SQLite storage |
| alerts.py | Twilio SMS / console alerts |
| monitor.py | Main workflow |
| main.py | CLI menu (loops, conditionals) |
| dashboard.py | Streamlit dashboard |

## Notes
- Never commit your `.env` file or share API keys.
- Sentiment is rule-based, so it can misread sarcasm. Mention this in your limitations.
- For Indian stocks, use Alpha Vantage symbols such as `RELIANCE.BSE`.
<img width="2551" height="2268" alt="image" src="https://github.com/user-attachments/assets/03dbb19a-8cea-4ed1-8d51-e55cea875064" />
....


