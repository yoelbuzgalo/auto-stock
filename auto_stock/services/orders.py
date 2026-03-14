from __future__ import annotations

from dataclasses import replace
from uuid import uuid4

from auto_stock.domain.broker import OrderSide
from auto_stock.infra.errors import ValidationError
from auto_stock.domain.watchlist import PlannedOrder
from auto_stock.infra.validation import ensure_positive_number, normalize_optional_text, normalize_symbol
from auto_stock.persistence.state import AppState, StateRepository


class OrderPlanService:
    def __init__(self, repository: StateRepository) -> None:
        self.repository = repository

    def list_orders(self) -> list[PlannedOrder]:
        return list(self.repository.load_state().planned_orders)

    def add_order(
        self,
        symbol: str,
        *,
        side: str = "BUY",
        quantity: float = 1.0,
        target_price: float | None = None,
        note: str = "",
    ) -> PlannedOrder:
        normalized_side = side.strip().upper()
        if normalized_side not in OrderSide._value2member_map_:
            raise ValidationError("Side must be BUY or SELL.")
        order = PlannedOrder(
            order_id=uuid4().hex[:10],
            symbol=normalize_symbol(symbol),
            side=OrderSide(normalized_side),
            quantity=ensure_positive_number(quantity, "quantity"),
            target_price=(
                ensure_positive_number(target_price, "target price") if target_price not in (None, "") else None
            ),
            note=normalize_optional_text(note),
        )

        def updater(state: AppState) -> AppState:
            return replace(state, planned_orders=(*state.planned_orders, order))

        self.repository.update_state(updater)
        return order

    def remove_order(self, order_id: str) -> bool:
        normalized_order_id = order_id.strip()
        removed = False

        def updater(state: AppState) -> AppState:
            nonlocal removed
            filtered = tuple(order for order in state.planned_orders if order.order_id != normalized_order_id)
            removed = len(filtered) != len(state.planned_orders)
            return replace(state, planned_orders=filtered)

        self.repository.update_state(updater)
        return removed
