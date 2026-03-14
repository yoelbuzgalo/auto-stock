from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Callable

from auto_stock.domain.broker import OrderSide
from auto_stock.domain.watchlist import PlannedOrder, WatchlistItem
from auto_stock.infra.errors import PersistenceError
from auto_stock.infra.validation import ensure_positive_number, normalize_optional_text, normalize_symbol


@dataclass(frozen=True, slots=True)
class AppState:
    watchlist: tuple[WatchlistItem, ...] = ()
    planned_orders: tuple[PlannedOrder, ...] = ()


class StateRepository(ABC):
    @abstractmethod
    def load_state(self) -> AppState:
        raise NotImplementedError

    @abstractmethod
    def save_state(self, state: AppState) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_state(self, updater: Callable[[AppState], AppState]) -> AppState:
        raise NotImplementedError


class JsonStateRepository(StateRepository):
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._lock = Lock()
        self._logger = logging.getLogger(__name__)

    def load_state(self) -> AppState:
        with self._lock:
            return self._load_state_unlocked()

    def save_state(self, state: AppState) -> None:
        with self._lock:
            self._save_state_unlocked(state)

    def update_state(self, updater: Callable[[AppState], AppState]) -> AppState:
        with self._lock:
            current = self._load_state_unlocked()
            updated = updater(current)
            self._save_state_unlocked(updated)
            return updated

    def _load_state_unlocked(self) -> AppState:
        if not self.path.exists():
            return AppState()

        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise PersistenceError(f"State file is not valid JSON: {self.path}") from exc
        except OSError as exc:
            raise PersistenceError(f"Unable to read state file: {self.path}") from exc

        watchlist: list[WatchlistItem] = []
        for entry in raw.get("watchlist", []):
            if not isinstance(entry, dict):
                self._logger.warning("Skipping malformed watchlist entry: %s", entry)
                continue
            parsed = self._parse_watchlist_item(entry)
            if parsed is not None:
                watchlist.append(parsed)

        planned_orders: list[PlannedOrder] = []
        for entry in raw.get("planned_orders", []):
            if not isinstance(entry, dict):
                self._logger.warning("Skipping malformed planned order entry: %s", entry)
                continue
            parsed_order = self._parse_planned_order(entry)
            if parsed_order is not None:
                planned_orders.append(parsed_order)

        return AppState(
            watchlist=tuple(watchlist),
            planned_orders=tuple(planned_orders),
        )

    def _save_state_unlocked(self, state: AppState) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": 1,
            "watchlist": [self._dump_watchlist_item(item) for item in state.watchlist],
            "planned_orders": [self._dump_planned_order(order) for order in state.planned_orders],
        }
        temp_path = self.path.with_suffix(f"{self.path.suffix}.tmp")
        try:
            temp_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            temp_path.replace(self.path)
        except OSError as exc:
            raise PersistenceError(f"Unable to write state file: {self.path}") from exc

    def _parse_watchlist_item(self, entry: dict[str, object]) -> WatchlistItem | None:
        try:
            return WatchlistItem(
                symbol=normalize_symbol(str(entry["symbol"])),
                note=normalize_optional_text(str(entry.get("note", ""))),
                target_price=self._optional_positive_number(entry.get("target_price")),
                added_at=datetime.fromisoformat(str(entry.get("added_at") or datetime.now(timezone.utc).isoformat())),
            )
        except Exception as exc:
            self._logger.warning("Skipping malformed watchlist item %s: %s", entry, exc)
            return None

    def _parse_planned_order(self, entry: dict[str, object]) -> PlannedOrder | None:
        try:
            side = OrderSide(str(entry.get("side", OrderSide.BUY.value)).upper())
            return PlannedOrder(
                order_id=str(entry["order_id"]),
                symbol=normalize_symbol(str(entry["symbol"])),
                side=side,
                quantity=ensure_positive_number(str(entry["quantity"]), "quantity"),
                target_price=self._optional_positive_number(entry.get("target_price")),
                note=normalize_optional_text(str(entry.get("note", ""))),
                created_at=datetime.fromisoformat(
                    str(entry.get("created_at") or datetime.now(timezone.utc).isoformat())
                ),
            )
        except Exception as exc:
            self._logger.warning("Skipping malformed planned order %s: %s", entry, exc)
            return None

    @staticmethod
    def _dump_watchlist_item(item: WatchlistItem) -> dict[str, object]:
        return {
            "symbol": item.symbol,
            "note": item.note,
            "target_price": item.target_price,
            "added_at": item.added_at.isoformat(),
        }

    @staticmethod
    def _dump_planned_order(order: PlannedOrder) -> dict[str, object]:
        return {
            "order_id": order.order_id,
            "symbol": order.symbol,
            "side": order.side.value,
            "quantity": order.quantity,
            "target_price": order.target_price,
            "note": order.note,
            "created_at": order.created_at.isoformat(),
        }

    @staticmethod
    def _optional_positive_number(value: object) -> float | None:
        if value in (None, ""):
            return None
        return ensure_positive_number(str(value), "target price")
