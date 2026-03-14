from src.services.persistence import Persistence

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


def run_cli_app(persistence: Persistence) -> None:
    while True:
        print_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            symbol = input("Enter stock symbol: ").strip().upper()
            while True:
                try:
                    amount = float(input("Enter amount: ").strip())
                    break
                except ValueError:
                    print("Please enter a valid number for amount.")
            persistence.add_item((symbol, amount))
            print(f"Order added: {symbol} @ ${amount}")

        elif choice == "2":
            orders = persistence.load_items()
            if not orders:
                print("No orders in queue.")
            else:
                print("Current orders:")
                for idx, (symbol, amount) in enumerate(orders, start=1):
                    print(f"{idx}. {symbol} @ ${amount}")

        elif choice == "3":
            orders = persistence.load_items()
            if not orders:
                print("No orders to remove.")
                continue
            print("Select order to remove:")
            for idx, (symbol, amount) in enumerate(orders, start=1):
                print(f"{idx}. {symbol} @ ${amount}")
            while True:
                try:
                    to_remove = int(input("Enter order number to remove: ").strip())
                    if 1 <= to_remove <= len(orders):
                        persistence.remove_item(to_remove - 1)  # remove via Persistence
                        removed = orders[to_remove - 1]
                        print(f"Removed order: {removed[0]} @ ${removed[1]}")
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