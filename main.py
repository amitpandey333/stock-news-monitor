"""Command-line interface for the Stock News Monitoring System."""
import time

import database as db
from config import NEWS_DEMO, PRICE_THRESHOLD, SMS_ENABLED, STOCK_DEMO
from monitor import check_all, check_stock

MOOD_ICON = {"Positive": "[+]", "Negative": "[-]", "Neutral": "[=]"}


def show_result(r):
    if r["error"]:
        print(f"  {r['symbol']}: ERROR - {r['error']}")
        if not r["price"]:
            return
    p = r["price"]
    print(f"\n{r['symbol']}  close {p['close']}  (prev {p['prev_close']})  {p['change_pct']:+.2f}%"
          f"  {'<-- above threshold' if r['triggered'] else ''}")
    for a in r["news"]:
        print(f"   {MOOD_ICON[a['mood']]} {a['mood']:<8} ({a['score']:+.2f})  {a['title']}")
    if r["alerts"]:
        print(f"   {r['alerts']} alert(s) sent")


def ask_symbol():
    return input("Stock symbol (e.g. TSLA): ").strip().upper()


def menu():
    db.init_db()
    print("=" * 55)
    print(" STOCK NEWS MONITORING SYSTEM")
    print(f" Prices: {'DEMO' if STOCK_DEMO else 'live'} | News: {'DEMO' if NEWS_DEMO else 'live'} | "
          f"Alerts: {'SMS' if SMS_ENABLED else 'console'} | Threshold: {PRICE_THRESHOLD}%")
    print("=" * 55)
    while True:
        print("\n1 Add stock   2 Remove stock   3 Show watchlist   4 Check one stock\n"
              "5 Check all   6 Saved news     7 Auto-monitor     8 Exit")
        choice = input("Choose: ").strip()
        if choice == "1":
            sym = ask_symbol()
            if sym:
                db.add_to_watchlist(sym, input("Company name (for news search): ").strip() or sym)
                print("Added.")
        elif choice == "2":
            db.remove_from_watchlist(ask_symbol())
            print("Removed.")
        elif choice == "3":
            for w in db.get_watchlist() or [{"symbol": "(empty)", "name": ""}]:
                print(f"  {w['symbol']:<8} {w['name']}")
        elif choice == "4":
            sym = ask_symbol()
            name = next((w["name"] for w in db.get_watchlist() if w["symbol"] == sym), sym)
            show_result(check_stock(sym, name, force_news=True))
                elif choice == "5":
            if not db.get_watchlist():
                print("Watchlist is empty. Choose 1 to add a stock first.")
            for r in check_all():
                show_result(r)
        elif choice == "6":
            for n in db.get_news(limit=20):
                print(f"  {n['symbol']:<6} {n['mood']:<8} {n['score']:+.2f}  {n['title']}")
        elif choice == "7":
            try:
                minutes = float(input("Check every how many minutes? ") or 15)
            except ValueError:
                print("Enter a number.")
                continue
            print("Monitoring... press Ctrl+C to stop.")
            try:
                while True:
                    for r in check_all():
                        show_result(r)
                    time.sleep(minutes * 60)
            except KeyboardInterrupt:
                print("\nStopped.")
        elif choice == "8":
            print("Bye!")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    menu()
