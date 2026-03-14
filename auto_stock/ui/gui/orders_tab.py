from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class OrdersTab(ttk.Frame):
    def __init__(self, master: tk.Misc, *, services, set_status, on_change) -> None:
        super().__init__(master, style="App.TFrame", padding=16)
        self.services = services
        self.set_status = set_status
        self.on_change = on_change

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.symbol_var = tk.StringVar()
        self.side_var = tk.StringVar(value="BUY")
        self.quantity_var = tk.StringVar(value="1")
        self.target_price_var = tk.StringVar()
        self.note_var = tk.StringVar()
        self.feedback_var = tk.StringVar(value="Create local plans before wiring live execution.")

        self._build_controls()
        self._build_table()
        self.refresh_orders()

    def refresh_orders(self) -> None:
        orders = self.services.order_plans.list_orders()
        for row_id in self.tree.get_children():
            self.tree.delete(row_id)
        for order in orders:
            target = f"${order.target_price:.2f}" if order.target_price is not None else "-"
            self.tree.insert(
                "",
                "end",
                iid=order.order_id,
                values=(
                    order.order_id,
                    order.symbol,
                    order.side.value,
                    f"{order.quantity:.2f}",
                    target,
                    order.note or "-",
                    order.created_at.astimezone().strftime("%Y-%m-%d %H:%M"),
                ),
            )

    def add_order(self) -> None:
        order = self.services.order_plans.add_order(
            self.symbol_var.get(),
            side=self.side_var.get(),
            quantity=self.quantity_var.get(),
            target_price=self.target_price_var.get() or None,
            note=self.note_var.get(),
        )
        self.symbol_var.set("")
        self.quantity_var.set("1")
        self.target_price_var.set("")
        self.note_var.set("")
        self.refresh_orders()
        self.feedback_var.set(f"Saved local order plan {order.order_id}.")
        self.set_status(f"Saved order plan for {order.symbol}.")
        self.on_change()

    def remove_selected(self) -> None:
        selected = self.tree.selection()
        if not selected:
            self.feedback_var.set("Select an order plan to remove.")
            return
        removed = self.services.order_plans.remove_order(selected[0])
        if removed:
            self.refresh_orders()
            self.feedback_var.set("Removed local order plan.")
            self.set_status("Order plan removed.")
            self.on_change()
        else:
            self.feedback_var.set("No matching order plan found.")

    def _build_controls(self) -> None:
        frame = ttk.LabelFrame(self, text="Local Order Plans", style="Card.TLabelframe", padding=14)
        frame.grid(row=0, column=0, sticky="ew")
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(7, weight=1)

        ttk.Label(frame, text="Ticker", style="Body.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.symbol_var, width=12).grid(row=0, column=1, sticky="ew", padx=(8, 12))
        ttk.Label(frame, text="Side", style="Body.TLabel").grid(row=0, column=2, sticky="w")
        ttk.Combobox(frame, textvariable=self.side_var, state="readonly", values=("BUY", "SELL"), width=8).grid(
            row=0, column=3, sticky="w", padx=(8, 12)
        )
        ttk.Label(frame, text="Quantity", style="Body.TLabel").grid(row=0, column=4, sticky="w")
        ttk.Entry(frame, textvariable=self.quantity_var, width=10).grid(row=0, column=5, sticky="w", padx=(8, 12))
        ttk.Label(frame, text="Target Price", style="Body.TLabel").grid(row=0, column=6, sticky="w")
        ttk.Entry(frame, textvariable=self.target_price_var, width=10).grid(row=0, column=7, sticky="ew", padx=(8, 12))
        ttk.Label(frame, text="Note", style="Body.TLabel").grid(row=0, column=8, sticky="w")
        ttk.Entry(frame, textvariable=self.note_var, width=24).grid(row=0, column=9, sticky="ew", padx=(8, 12))
        ttk.Button(frame, text="Save Plan", style="Accent.TButton", command=self.add_order).grid(row=0, column=10, sticky="e")
        ttk.Button(frame, text="Remove Selected", command=self.remove_selected).grid(row=0, column=11, sticky="e", padx=(8, 0))
        ttk.Label(frame, textvariable=self.feedback_var, style="Muted.TLabel").grid(
            row=1, column=0, columnspan=12, sticky="w", pady=(10, 0)
        )

    def _build_table(self) -> None:
        frame = ttk.LabelFrame(self, text="Saved Plans", style="Card.TLabelframe", padding=12)
        frame.grid(row=1, column=0, sticky="nsew", pady=(14, 0))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        columns = ("id", "symbol", "side", "quantity", "target", "note", "created")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        headings = {
            "id": "Plan ID",
            "symbol": "Ticker",
            "side": "Side",
            "quantity": "Quantity",
            "target": "Target",
            "note": "Note",
            "created": "Created",
        }
        widths = {"id": 90, "symbol": 80, "side": 70, "quantity": 90, "target": 90, "note": 260, "created": 150}
        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=widths[column], anchor="w")
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
