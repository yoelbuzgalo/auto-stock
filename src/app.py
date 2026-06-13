from .gui import run_gui_app
from modules import JsonFilePersistence
from pathlib import Path

def main():
    path = "data/orders.json"
    storage = JsonFilePersistence(path)  # will persist to orders.json
    run_gui_app(storage=storage)

if __name__ == "__main__":
    main()