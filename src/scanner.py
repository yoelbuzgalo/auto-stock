import requests
from services import JsonFilePersistence
from datetime import datetime

JSON_FILE = "orders.json"

SCHWAB_API_URL = "https://api.schwabapi.com/marketdata/quotes"
API_KEY = "YOUR_API_KEY"


def fetch_quote(symbol):
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    params = {
        "symbols": symbol
    }

    response = requests.get(SCHWAB_API_URL, headers=headers, params=params)
    data = response.json()

    quote = data[symbol]["quote"]

    return {
        "bid": quote["bidPrice"],
        "ask": quote["askPrice"]
    }


def analyze(symbol, data, order):
    bid = data["bid"]
    ask = data["ask"]

    if bid == 0:
        print(f"{symbol}: Invalid bid (0), skipping")
        return

    spread = ask - bid
    spread_percent = (spread / bid) * 100

    print(f"\n[{symbol}]")
    print(f"Bid: {bid}, Ask: {ask}")
    print(f"Spread: {spread:.4f} ({spread_percent:.2f}%)")

    if spread_percent >= order["max_spread_percent"]:
        print("⚠️ Spread threshold exceeded")


def main():
    print(f"Running spread check at {datetime.now()}")

    storage = JsonFilePersistence("orders.json")  # will persist to orders.json
    orders = storage.load_items()

    for order in orders:
        symbol = order["symbol"]
        try:
            data = fetch_quote(symbol)
            analyze(symbol, data, order)
        except Exception as e:
            print(f"Error processing {symbol}: {e}")


if __name__ == "__main__":
    main()