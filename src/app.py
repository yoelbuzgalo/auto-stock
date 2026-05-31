from cli import run_cli_app
from gui import run_gui_app
from modules import JsonFilePersistence

def main():
    storage = JsonFilePersistence("orders.json")  # will persist to orders.json
    run_gui_app()

if __name__ == "__main__":
    main()