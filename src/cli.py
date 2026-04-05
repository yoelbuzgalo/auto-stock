from services import Persistence

def print_menu():
    """Prints the main menu."""
    menu = """
### AUTO STOCK ###
1. Add desired order
2. View desired orders
3. Remove order
4. Exit
"""
    print(menu)


def normalize_order(order, default_spread=0.05):
    """Handles backward compatibility (tuple/list → dict)."""
    if isinstance(order, dict):
        return order
    elif isinstance(order, (list, tuple)):
        return {
            "symbol": order[0],
            "amount": order[1],
            "spread": order[2] if len(order) > 2 else default_spread
        }
    return order


def run_cli_app(persistence: Persistence) -> None:
    while True:
        print_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            symbol = input("Enter stock symbol: ").strip().upper()

            # Amount
            while True:
                try:
                    amount = float(input("Enter amount: ").strip())
                    break
                except ValueError:
                    print("Please enter a valid number for amount.")

            # Spread
            while True:
                try:
                    spread = float(input("Enter max bid/ask spread: ").strip())
                    break
                except ValueError:
                    print("Please enter a valid number for spread.")

            order = {
                "symbol": symbol,
                "amount": amount,
                "spread": spread
            }

            persistence.add_item(order)
            print(f"Order added: {symbol} @ ${amount} (spread ≤ {spread})")

        elif choice == "2":
            raw_orders = persistence.load_items()
            orders = [normalize_order(o) for o in raw_orders]

            if not orders:
                print("No orders in queue.")
            else:
                print("Current orders:")
                for idx, order in enumerate(orders, start=1):
                    print(f"{idx}. {order['symbol']} @ ${order['amount']} (spread ≤ {order['spread']})")

        elif choice == "3":
            raw_orders = persistence.load_items()
            orders = [normalize_order(o) for o in raw_orders]

            if not orders:
                print("No orders to remove.")
                continue

            print("Select order to remove:")
            for idx, order in enumerate(orders, start=1):
                print(f"{idx}. {order['symbol']} @ ${order['amount']} (spread ≤ {order['spread']})")

            while True:
                try:
                    to_remove = int(input("Enter order number to remove: ").strip())
                    if 1 <= to_remove <= len(orders):
                        persistence.remove_item(to_remove - 1)

                        removed = orders[to_remove - 1]
                        print(f"Removed order: {removed['symbol']} @ ${removed['amount']} (spread ≤ {removed['spread']})")
                        break
                    else:
                        print("Invalid number. Try again.")
                except ValueError:
                    print("Enter a valid number.")

        elif choice == "4":
            print("Exiting AUTO STOCK. Goodbye!")
            break

        else:
            print("Invalid choice, try again.")