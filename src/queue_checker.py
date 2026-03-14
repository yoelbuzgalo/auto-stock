from modules import JsonFilePersistence

def run_order_job():
    persistence = JsonFilePersistence("orders.json")

    orders = persistence.load_items()

    if not orders:
        print("No queued orders.")
        return

    print("Processing queued orders...\n")

    for symbol, amount in orders:
        print("Preparing HTTP request:")
        print(f"POST https://api.broker.com/orders")
        print(f"Payload: {{ 'symbol': '{symbol}', 'amount': {amount} }}")
        print("-" * 40)

    # After it sends request to Schwab broker API, we want to send at 11 AM
    # Check the bid/ask spread
    # Send to the user text/discord message
    # The user can press yes/no/snooze
    # When a response is received, handle accordingly
    # Either by sending POST request to go ahead and place the order @ market order
    # or not doing it at all
    # or snooze for 1 hour and then come back and check price again

def main():
    run_order_job()

if __name__ == "__main__":
    main()