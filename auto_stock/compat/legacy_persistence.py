from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable

from auto_stock.infra.validation import ensure_positive_number, normalize_symbol


class Persistence(ABC):
    @abstractmethod
    def save(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_item(self, item: tuple[str, float]) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_items(self, items: Iterable[tuple[str, float]]) -> None:
        raise NotImplementedError

    @abstractmethod
    def load_items(self) -> list[tuple[str, float]]:
        raise NotImplementedError

    @abstractmethod
    def remove_item(self, index: int) -> None:
        raise NotImplementedError


class JsonFilePersistence(Persistence):
    def __init__(self, filename: str) -> None:
        self.filename = Path(filename)
        self._items = self.load_items()

    def save(self) -> None:
        self.filename.write_text(json.dumps(self._items, indent=2), encoding="utf-8")

    def add_item(self, item: tuple[str, float]) -> None:
        symbol, amount = item
        self._items.append((normalize_symbol(symbol), ensure_positive_number(amount, "amount")))
        self.save()

    def add_items(self, items: Iterable[tuple[str, float]]) -> None:
        for item in items:
            self.add_item(item)

    def load_items(self) -> list[tuple[str, float]]:
        if not self.filename.exists():
            return []
        try:
            raw = json.loads(self.filename.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
        items: list[tuple[str, float]] = []
        for item in raw:
            if not isinstance(item, (list, tuple)) or len(item) != 2:
                continue
            try:
                items.append((normalize_symbol(str(item[0])), ensure_positive_number(item[1], "amount")))
            except Exception:
                continue
        return items

    def remove_item(self, index: int) -> None:
        if not 0 <= index < len(self._items):
            raise IndexError("Item index out of range")
        self._items.pop(index)
        self.save()
