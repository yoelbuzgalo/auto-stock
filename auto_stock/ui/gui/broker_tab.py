from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from auto_stock.domain.broker import BrokerSnapshot


class BrokerTab(ttk.Frame):
    def __init__(self, master: tk.Misc, *, services, run_async, set_status, default_account_id: str | None) -> None:
        super().__init__(master, style="App.TFrame", padding=16)
        self.services = services
        self.run_async = run_async
        self.set_status = set_status

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)

        self.account_var = tk.StringVar(value=default_account_id or "")
        self.feedback_var = tk.StringVar(value="Load broker data when credentials and account ID are configured.")
        self.summary_vars = {
            "account": tk.StringVar(value="-"),
            "cash": tk.StringVar(value="-"),
            "buying_power": tk.StringVar(value="-"),
            "equity": tk.StringVar(value="-"),
            "positions": tk.StringVar(value="0"),
            "orders": tk.StringVar(value="0"),
        }

        self._build_controls()
        self._build_summary()
        self._build_positions()
        self._build_orders()
        self.refresh_status()

    def refresh_status(self) -> None:
        status = self.services.broker.get_status()
        self.feedback_var.set(status.detail)

    def load_snapshot(self) -> None:
        account_id = self.account_var.get().strip()
        self.feedback_var.set("Loading broker snapshot...")
        self.set_status("Loading broker account data...")
        self.run_async(
            lambda: self.services.broker.get_snapshot(account_id or None),
            self._on_snapshot_loaded,
            self._on_snapshot_error,
        )

    def _on_snapshot_loaded(self, snapshot: BrokerSnapshot) -> None:
        account = snapshot.account
        if account is None:
            self.feedback_var.set("Broker did not return an account record.")
            return
        self.summary_vars["account"].set(account.account_id)
        self.summary_vars["cash"].set(f"${account.cash_balance:,.2f}")
        self.summary_vars["buying_power"].set(f"${account.buying_power:,.2f}")
        self.summary_vars["equity"].set(f"${account.equity:,.2f}")
        self.summary_vars["positions"].set(str(len(snapshot.positions)))
        self.summary_vars["orders"].set(str(len(snapshot.orders)))

        for row_id in self.positions_tree.get_children():
            self.positions_tree.delete(row_id)
        for position in snapshot.positions:
            self.positions_tree.insert(
                "",
                "end",
                values=(
                    position.symbol,
                    f"{position.quantity:.2f}",
                    f"${position.average_price:,.2f}",
                    f"${position.market_value:,.2f}",
                ),
            )

        for row_id in self.orders_tree.get_children():
            self.orders_tree.delete(row_id)
        for order in snapshot.orders:
            price = f"${order.price:,.2f}" if order.price is not None else "-"
            self.orders_tree.insert(
                "",
                "end",
                values=(
                    order.order_id,
                    order.symbol,
                    order.side.value,
                    order.order_type.value,
                    order.status.value,
                    f"{order.quantity:.2f}",
                    price,
                ),
            )

        self.feedback_var.set("Broker snapshot loaded.")
        self.set_status("Broker snapshot ready.")

    def _on_snapshot_error(self, exc: Exception) -> None:
        self.feedback_var.set(str(exc))
        self.set_status("Broker request failed.")

    def _build_controls(self) -> None:
        frame = ttk.LabelFrame(self, text="Broker", style="Card.TLabelframe", padding=14)
        frame.grid(row=0, column=0, sticky="ew")
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Account ID", style="Body.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.account_var, width=24).grid(row=0, column=1, sticky="ew", padx=(8, 12))
        ttk.Button(frame, text="Refresh Snapshot", style="Accent.TButton", command=self.load_snapshot).grid(
            row=0, column=2, sticky="e"
        )
        ttk.Label(frame, textvariable=self.feedback_var, style="Muted.TLabel").grid(
            row=1, column=0, columnspan=3, sticky="w", pady=(10, 0)
        )

    def _build_summary(self) -> None:
        frame = ttk.LabelFrame(self, text="Account Summary", style="Card.TLabelframe", padding=14)
        frame.grid(row=1, column=0, sticky="ew", pady=(14, 14))
        for column in range(6):
            frame.columnconfigure(column, weight=1)

        metrics = [
            ("Account", "account"),
            ("Cash", "cash"),
            ("Buying Power", "buying_power"),
            ("Equity", "equity"),
            ("Positions", "positions"),
            ("Orders", "orders"),
        ]
        for index, (label, key) in enumerate(metrics):
            ttk.Label(frame, text=label, style="Muted.TLabel").grid(row=0, column=index, sticky="w")
            ttk.Label(frame, textvariable=self.summary_vars[key], style="Value.TLabel").grid(row=1, column=index, sticky="w", pady=(4, 0))

    def _build_positions(self) -> None:
        frame = ttk.LabelFrame(self, text="Positions", style="Card.TLabelframe", padding=12)
        frame.grid(row=2, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        columns = ("symbol", "quantity", "average", "value")
        self.positions_tree = ttk.Treeview(frame, columns=columns, show="headings", height=7)
        for column, heading, width in (
            ("symbol", "Ticker", 90),
            ("quantity", "Quantity", 90),
            ("average", "Avg Price", 110),
            ("value", "Market Value", 120),
        ):
            self.positions_tree.heading(column, text=heading)
            self.positions_tree.column(column, width=width, anchor="w")
        self.positions_tree.grid(row=0, column=0, sticky="nsew")

    def _build_orders(self) -> None:
        frame = ttk.LabelFrame(self, text="Open Orders", style="Card.TLabelframe", padding=12)
        frame.grid(row=3, column=0, sticky="nsew", pady=(14, 0))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        columns = ("id", "symbol", "side", "type", "status", "quantity", "price")
        self.orders_tree = ttk.Treeview(frame, columns=columns, show="headings", height=7)
        widths = {"id": 90, "symbol": 90, "side": 70, "type": 80, "status": 100, "quantity": 90, "price": 90}
        for column in columns:
            self.orders_tree.heading(column, text=column.title())
            self.orders_tree.column(column, width=widths[column], anchor="w")
        self.orders_tree.grid(row=0, column=0, sticky="nsew")
