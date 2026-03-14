from __future__ import annotations

from dataclasses import replace

from auto_stock.domain.watchlist import WatchlistItem
from auto_stock.infra.errors import ValidationError
from auto_stock.infra.validation import ensure_positive_number, normalize_optional_text, normalize_symbol
from auto_stock.persistence.state import AppState, StateRepository


class WatchlistService:
    def __init__(self, repository: StateRepository) -> None:
        self.repository = repository

    def list_items(self) -> list[WatchlistItem]:
        return list(self.repository.load_state().watchlist)

    def add_item(self, symbol: str, *, note: str = "", target_price: float | None = None) -> WatchlistItem:
        normalized_symbol = normalize_symbol(symbol)
        normalized_note = normalize_optional_text(note)
        normalized_target = (
            ensure_positive_number(target_price, "target price") if target_price not in (None, "") else None
        )
        created_item = WatchlistItem(
            symbol=normalized_symbol,
            note=normalized_note,
            target_price=normalized_target,
        )

        def updater(state: AppState) -> AppState:
            if any(item.symbol == normalized_symbol for item in state.watchlist):
                raise ValidationError(f"{normalized_symbol} is already in the watchlist.")
            return replace(state, watchlist=(*state.watchlist, created_item))

        self.repository.update_state(updater)
        return created_item

    def remove_item(self, symbol: str) -> bool:
        normalized_symbol = normalize_symbol(symbol)
        removed = False

        def updater(state: AppState) -> AppState:
            nonlocal removed
            filtered = tuple(item for item in state.watchlist if item.symbol != normalized_symbol)
            removed = len(filtered) != len(state.watchlist)
            return replace(state, watchlist=filtered)

        self.repository.update_state(updater)
        return removed
