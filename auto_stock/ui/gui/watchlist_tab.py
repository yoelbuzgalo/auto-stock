from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from auto_stock.domain.market import Quote
from auto_stock.domain.watchlist import WatchlistItem


class WatchlistTab(ttk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        *,
        services,
        run_async,
        set_status,
        open_symbol,
        on_change,
    ) -> None:
        super().__init__(master, style="App.TFrame", padding=16)
        self.services = services
        self.run_async = run_async
        self.set_status = set_status
        self.open_symbol = open_symbol
        self.on_change = on_change

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.symbol_var = tk.StringVar()
        self.target_price_var = tk.StringVar()
        self.note_var = tk.StringVar()
        self.feedback_var = tk.StringVar(value="Track symbols to keep them one click away.")
        self.quote_cache: dict[str, Quote] = {}

        self._build_controls()
        self._build_table()
        self.refresh_items()

    def refresh_items(self) -> None:
        items = self.services.watchlist.list_items()
        self._render_items(items)
        self.feedback_var.set("Watchlist updated.")

    def refresh_quotes(self) -> None:
        items = self.services.watchlist.list_items()
        if not items:
            self.feedback_var.set("Add symbols to the watchlist first.")
            return
        self.feedback_var.set("Refreshing tracked quotes...")
        self.set_status("Refreshing watchlist quotes...")

        def load_quotes() -> dict[str, Quote]:
            return {item.symbol: self.services.market.get_quote(item.symbol) for item in items}

        self.run_async(load_quotes, self._on_quotes_loaded, self._on_quotes_error)

    def add_item(self, symbol: str | None = None) -> None:
        input_symbol = symbol or self.symbol_var.get()
        item = self.services.watchlist.add_item(
            input_symbol,
            target_price=self.target_price_var.get() or None,
            note=self.note_var.get(),
        )
        self.symbol_var.set("")
        self.target_price_var.set("")
        self.note_var.set("")
        self.refresh_items()
        self.feedback_var.set(f"Tracking {item.symbol}.")
        self.set_status(f"Tracking {item.symbol}.")
        self.on_change()

    def remove_selected(self) -> None:
        selected = self.tree.selection()
        if not selected:
            self.feedback_var.set("Select a symbol to remove.")
            return
        symbol = selected[0]
        removed = self.services.watchlist.remove_item(symbol)
        if removed:
            self.quote_cache.pop(symbol, None)
            self.refresh_items()
            self.feedback_var.set(f"Removed {symbol}.")
            self.set_status(f"Removed {symbol} from the watchlist.")
            self.on_change()
        else:
            self.feedback_var.set("No matching symbol found.")

    def _on_row_open(self, _event: tk.Event[tk.Misc]) -> None:
        selected = self.tree.selection()
        if selected:
            self.open_symbol(selected[0], auto_load=True)

    def _on_quotes_loaded(self, quote_map: dict[str, Quote]) -> None:
        self.quote_cache = quote_map
        self.refresh_items()
        self.feedback_var.set("Tracked quotes refreshed.")
        self.set_status("Watchlist quotes updated.")

    def _on_quotes_error(self, exc: Exception) -> None:
        self.feedback_var.set(str(exc))
        self.set_status("Watchlist refresh failed.")

    def _render_items(self, items: list[WatchlistItem]) -> None:
        for row_id in self.tree.get_children():
            self.tree.delete(row_id)
        for item in items:
            quote = self.quote_cache.get(item.symbol)
            last_price = f"${quote.last:.2f}" if quote else "-"
            target = f"${item.target_price:.2f}" if item.target_price is not None else "-"
            self.tree.insert(
                "",
                "end",
                iid=item.symbol,
                values=(
                    item.symbol,
                    target,
                    last_price,
                    item.note or "-",
                    item.added_at.astimezone().strftime("%Y-%m-%d"),
                ),
            )

    def _build_controls(self) -> None:
        frame = ttk.LabelFrame(self, text="Watchlist", style="Card.TLabelframe", padding=14)
        frame.grid(row=0, column=0, sticky="ew")
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(3, weight=1)

        ttk.Label(frame, text="Ticker", style="Body.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.symbol_var, width=14).grid(row=0, column=1, sticky="ew", padx=(8, 12))
        ttk.Label(frame, text="Target Price", style="Body.TLabel").grid(row=0, column=2, sticky="w")
        ttk.Entry(frame, textvariable=self.target_price_var, width=12).grid(row=0, column=3, sticky="ew", padx=(8, 12))
        ttk.Label(frame, text="Note", style="Body.TLabel").grid(row=0, column=4, sticky="w")
        ttk.Entry(frame, textvariable=self.note_var, width=24).grid(row=0, column=5, sticky="ew", padx=(8, 12))
        ttk.Button(frame, text="Track Symbol", style="Accent.TButton", command=self.add_item).grid(row=0, column=6, sticky="e")
        ttk.Button(frame, text="Refresh Quotes", command=self.refresh_quotes).grid(row=0, column=7, sticky="e", padx=(8, 0))
        ttk.Button(frame, text="Remove Selected", command=self.remove_selected).grid(row=0, column=8, sticky="e", padx=(8, 0))
        ttk.Label(frame, textvariable=self.feedback_var, style="Muted.TLabel").grid(
            row=1, column=0, columnspan=9, sticky="w", pady=(10, 0)
        )

    def _build_table(self) -> None:
        frame = ttk.LabelFrame(self, text="Tracked Symbols", style="Card.TLabelframe", padding=12)
        frame.grid(row=1, column=0, sticky="nsew", pady=(14, 0))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        columns = ("symbol", "target", "last", "note", "added")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        headings = {
            "symbol": "Ticker",
            "target": "Target",
            "last": "Last",
            "note": "Note",
            "added": "Added",
        }
        widths = {"symbol": 100, "target": 90, "last": 90, "note": 280, "added": 100}
        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=widths[column], anchor="w")
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<Double-1>", self._on_row_open)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
