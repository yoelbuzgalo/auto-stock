from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from auto_stock.domain.market import Candle, Quote
from auto_stock.ui.gui.charts import (
    CHART_MODE_DESCRIPTIONS,
    CHART_MODES,
    DEFAULT_CHART_MODE,
    HistoryChart,
)


class MarketTab(ttk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        *,
        services,
        run_async,
        set_status,
        add_watchlist_callback,
    ) -> None:
        super().__init__(master, style="App.TFrame", padding=16)
        self.services = services
        self.run_async = run_async
        self.set_status = set_status
        self.add_watchlist_callback = add_watchlist_callback

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self.symbol_var = tk.StringVar(value="AAPL")
        self.timeframe_var = tk.StringVar(value="1Day")
        self.chart_mode_var = tk.StringVar(value=DEFAULT_CHART_MODE)
        self.chart_hint_var = tk.StringVar(value=CHART_MODE_DESCRIPTIONS[DEFAULT_CHART_MODE])
        self.feedback_var = tk.StringVar(value="Enter a ticker to load quote and history data.")
        self.quote_vars = {
            "last": tk.StringVar(value="-"),
            "bid": tk.StringVar(value="-"),
            "ask": tk.StringVar(value="-"),
            "spread": tk.StringVar(value="-"),
            "volume": tk.StringVar(value="-"),
            "source": tk.StringVar(value="-"),
            "time": tk.StringVar(value="-"),
        }

        self._build_controls()
        self._build_quote_card()
        self._build_chart_card()

    def set_symbol(self, symbol: str, *, auto_load: bool = False) -> None:
        self.symbol_var.set(symbol)
        if auto_load:
            self.load_market_view()

    def load_market_view(self) -> None:
        symbol = self.symbol_var.get().strip()
        timeframe = self.timeframe_var.get().strip()
        self.feedback_var.set(f"Loading {symbol or 'symbol'}...")
        self.chart.set_loading()
        self.set_status("Loading market data...")
        self.run_async(
            lambda: (
                self.services.market.get_quote(symbol),
                self.services.market.get_history(symbol, timeframe=timeframe),
            ),
            self._on_market_loaded,
            self._on_market_error,
        )

    def _add_to_watchlist(self) -> None:
        symbol = self.symbol_var.get().strip()
        try:
            self.add_watchlist_callback(symbol)
        except Exception as exc:
            messagebox.showerror("Watchlist", str(exc), parent=self)

    def _on_market_loaded(self, result: tuple[Quote, list[Candle]]) -> None:
        quote, candles = result
        self._apply_quote(quote)
        self.chart.set_series(candles)
        self.feedback_var.set(f"Loaded {quote.symbol} with {len(candles)} candles.")
        self.set_status(f"Loaded {quote.symbol} from {quote.source}.")

    def _on_market_error(self, exc: Exception) -> None:
        self.chart.set_error(str(exc))
        self.feedback_var.set(str(exc))
        self.set_status("Market request failed.")

    def _on_chart_mode_changed(self, _event: tk.Event[tk.Misc] | None = None) -> None:
        mode = self.chart_mode_var.get()
        self.chart.set_mode(mode)
        self.chart_hint_var.set(CHART_MODE_DESCRIPTIONS.get(mode, CHART_MODE_DESCRIPTIONS[DEFAULT_CHART_MODE]))
        self.set_status(f"Chart view set to {self.chart_mode_var.get().lower()}.")

    def _apply_quote(self, quote: Quote) -> None:
        self.quote_vars["last"].set(f"${quote.last:.2f}")
        self.quote_vars["bid"].set(f"${quote.bid:.2f}")
        self.quote_vars["ask"].set(f"${quote.ask:.2f}")
        self.quote_vars["spread"].set(f"${quote.spread:.2f}")
        self.quote_vars["volume"].set(f"{quote.volume:,}")
        self.quote_vars["source"].set(quote.source)
        self.quote_vars["time"].set(quote.timestamp.astimezone().strftime("%Y-%m-%d %H:%M:%S"))

    def _build_controls(self) -> None:
        frame = ttk.LabelFrame(self, text="Market Lookup", style="Card.TLabelframe", padding=14)
        frame.grid(row=0, column=0, sticky="ew")
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Ticker", style="Body.TLabel").grid(row=0, column=0, sticky="w")
        symbol_entry = ttk.Entry(frame, textvariable=self.symbol_var, width=14)
        symbol_entry.grid(row=0, column=1, sticky="ew", padx=(8, 12))
        symbol_entry.bind("<Return>", lambda _event: self.load_market_view())

        ttk.Label(frame, text="Timeframe", style="Body.TLabel").grid(row=0, column=2, sticky="w")
        timeframe_combo = ttk.Combobox(
            frame,
            textvariable=self.timeframe_var,
            state="readonly",
            values=("1Min", "5Min", "15Min", "1Hour", "1Day"),
            width=10,
        )
        timeframe_combo.grid(row=0, column=3, sticky="w", padx=(8, 12))

        ttk.Label(frame, text="Chart View", style="Body.TLabel").grid(row=0, column=4, sticky="w")
        chart_mode_combo = ttk.Combobox(
            frame,
            textvariable=self.chart_mode_var,
            state="readonly",
            values=CHART_MODES,
            width=14,
        )
        chart_mode_combo.grid(row=0, column=5, sticky="w", padx=(8, 12))
        chart_mode_combo.bind("<<ComboboxSelected>>", self._on_chart_mode_changed)

        ttk.Button(frame, text="Load Market View", style="Accent.TButton", command=self.load_market_view).grid(
            row=0, column=6, sticky="e"
        )
        ttk.Button(frame, text="Track Symbol", command=self._add_to_watchlist).grid(row=0, column=7, sticky="e", padx=(8, 0))
        ttk.Label(frame, textvariable=self.feedback_var, style="Muted.TLabel").grid(
            row=1, column=0, columnspan=8, sticky="w", pady=(10, 0)
        )
        ttk.Label(frame, textvariable=self.chart_hint_var, style="Muted.TLabel").grid(
            row=2, column=0, columnspan=8, sticky="w", pady=(6, 0)
        )

    def _build_quote_card(self) -> None:
        frame = ttk.LabelFrame(self, text="Quote Snapshot", style="Card.TLabelframe", padding=14)
        frame.grid(row=1, column=0, sticky="ew", pady=(14, 14))
        for column in range(4):
            frame.columnconfigure(column, weight=1)

        metrics = [
            ("Last", "last"),
            ("Bid", "bid"),
            ("Ask", "ask"),
            ("Spread", "spread"),
            ("Volume", "volume"),
            ("Source", "source"),
            ("As Of", "time"),
        ]
        for index, (label, key) in enumerate(metrics):
            row = index // 4
            column = index % 4
            container = ttk.Frame(frame, style="Surface.TFrame", padding=(0, 0, 8, 6))
            container.grid(row=row * 2, column=column, sticky="ew")
            ttk.Label(container, text=label, style="Muted.TLabel").grid(row=0, column=0, sticky="w")
            ttk.Label(container, textvariable=self.quote_vars[key], style="Value.TLabel").grid(row=1, column=0, sticky="w")

    def _build_chart_card(self) -> None:
        frame = ttk.LabelFrame(self, text="History", style="Card.TLabelframe", padding=12)
        frame.grid(row=2, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        self.chart = HistoryChart(frame, initial_mode=self.chart_mode_var.get())
        self.chart.grid(row=0, column=0, sticky="nsew")
