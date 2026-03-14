from cli import run_cli_app
from services.persistence import JsonFilePersistence

def main():
    storage = JsonFilePersistence("orders.json")  # will persist to orders.json
    run_cli_app(storage)

if __name__ == "__main__":
    main()