import json
from abc import ABC, abstractmethod
from typing import Tuple, Iterable, List

class Persistence(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def save(self) -> None:
        """Save current state to the persistence medium"""
        pass

    @abstractmethod
    def add_item(self, item: Tuple[str, float]) -> None:
        """Add a single item (symbol, amount) to persistence"""
        pass

    @abstractmethod
    def add_items(self, items: Iterable[Tuple[str, float]]) -> None:
        """Add multiple items (symbol, amount) to persistence"""
        pass

    @abstractmethod
    def load_items(self) -> List[Tuple[str, float]]:
        """Load all items as a list of (symbol, amount)"""
        pass

    @abstractmethod
    def remove_item(self, index: int) -> None:
        """Remove an item by index"""
        pass


class JsonFilePersistence(Persistence):
    def __init__(self, filename: str):
        super().__init__()
        self.filename = filename
        self._items: List[Tuple[str, float]] = self.load_items()

    def save(self) -> None:
        """Save current items to the JSON file"""
        with open(self.filename, "w") as f:
            json.dump(self._items, f)

    def add_item(self, item: Tuple[str, float]) -> None:
        self._items.append(item)
        self.save()

    def add_items(self, items: Iterable[Tuple[str, float]]) -> None:
        self._items.extend(items)
        self.save()

    def load_items(self) -> List[Tuple[str, float]]:
        try:
            with open(self.filename, "r") as f:
                data = json.load(f)
                return [tuple(item) for item in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def remove_item(self, index: int) -> None:
        """Remove an item by index (0-based)"""
        if 0 <= index < len(self._items):
            self._items.pop(index)
            self.save()
        else:
            raise IndexError("Item index out of range")