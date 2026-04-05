import json
from abc import ABC, abstractmethod
from typing import Dict, Iterable, List

class Persistence(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def save(self) -> None:
        """Save current state to the persistence medium"""
        pass

    @abstractmethod
    def add_item(self, item: Dict) -> None:
        """Add a single order dict to persistence"""
        pass

    @abstractmethod
    def add_items(self, items: Iterable[Dict]) -> None:
        """Add multiple order dicts to persistence"""
        pass

    @abstractmethod
    def load_items(self) -> List[Dict]:
        """Load all orders as a list of dicts"""
        pass

    @abstractmethod
    def remove_item(self, index: int) -> None:
        """Remove an item by index"""
        pass


class JsonFilePersistence(Persistence):
    def __init__(self, filename: str):
        super().__init__()
        self.filename = filename
        self._items: List[Dict] = self.load_items()

    def save(self) -> None:
        """Save current items to the JSON file"""
        with open(self.filename, "w") as f:
            json.dump(self._items, f, indent=2)

    def add_item(self, item: Dict) -> None:
        self._items.append(item)
        self.save()

    def add_items(self, items: Iterable[Dict]) -> None:
        self._items.extend(items)
        self.save()

    def load_items(self) -> List[Dict]:
        try:
            with open(self.filename, "r") as f:
                data = json.load(f)
                # Ensure all items are dicts
                return [item if isinstance(item, dict) else {} for item in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def remove_item(self, index: int) -> None:
        """Remove an item by index (0-based)"""
        if 0 <= index < len(self._items):
            self._items.pop(index)
            self.save()
        else:
            raise IndexError("Item index out of range")