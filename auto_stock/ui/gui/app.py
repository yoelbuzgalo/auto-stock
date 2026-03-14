from __future__ import annotations

import threading
import tkinter as tk
from tkinter import ttk

from auto_stock.bootstrap import AppServices
from auto_stock.ui.gui.broker_tab import BrokerTab
from auto_stock.ui.gui.market_tab import MarketTab
from auto_stock.ui.gui.notifications_tab import NotificationsTab
from auto_stock.ui.gui.orders_tab import OrdersTab
from auto_stock.ui.gui.system_tab import SystemTab
from auto_stock.ui.gui.theme import configure_theme
from auto_stock.ui.gui.watchlist_tab import WatchlistTab


class AutoStockDesktop(tk.Tk):
    services: AppServices
    status_var: tk.StringVar
    notebook: ttk.Notebook
    market_tab: MarketTab
    watchlist_tab: WatchlistTab
    orders_tab: OrdersTab
    broker_tab: BrokerTab
    notifications_tab: NotificationsTab
    system_tab: SystemTab

    def __init__(self, services: AppServices) -> None:
        super().__init__()
        self.services = services
        self.status_var = tk.StringVar(value="Ready.")

        configure_theme(self)
        self.title("Auto Stock")
        self.geometry("1120x780")
        self.minsize(980, 700)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_header()
        self._build_tabs()
        self._build_status_bar()

        self.watchlist_tab.refresh_items()
        self.orders_tab.refresh_orders()
        self._refresh_system_status()

    def run_async(self, work, on_success, on_error=None) -> None:
        def worker() -> None:
            try:
                result = work()
            except Exception as exc:  # noqa: BLE001 - UI needs to surface all user-facing failures.
                callback = on_error or self._default_error_handler
                def run_err(e: Exception = exc) -> None:
                    callback(e)
                self.after(0, run_err)
                return

            def run_ok(r: object = result) -> None:
                on_success(r)
            self.after(0, run_ok)

        threading.Thread(target=worker, daemon=True).start()

    def set_status(self, message: str) -> None:
        self.status_var.set(message)

    def add_watchlist_symbol(self, symbol: str) -> None:
        self.watchlist_tab.add_item(symbol)
        self._refresh_system_status()

    def open_symbol(self, symbol: str, *, auto_load: bool = False) -> None:
        self.notebook.select(self.market_tab)
        self.market_tab.set_symbol(symbol, auto_load=auto_load)

    def _default_error_handler(self, exc: Exception) -> None:
        self.status_var.set(str(exc))

    def _refresh_system_status(self) -> None:
        system_tab = self.__dict__.get("system_tab")
        if system_tab is not None:
            system_tab.refresh()

    def _build_header(self) -> None:
        header = ttk.Frame(self, style="App.TFrame", padding=(18, 18, 18, 8))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="Auto Stock", style="Header.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text="A lightweight desktop workspace for quotes, history, watchlists, order plans, and broker visibility.",
            style="Subheader.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

    def _build_tabs(self) -> None:
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 12))

        self.market_tab = MarketTab(
            self.notebook,
            services=self.services,
            run_async=self.run_async,
            set_status=self.set_status,
            add_watchlist_callback=self.add_watchlist_symbol,
        )
        self.system_tab = SystemTab(self.notebook, services=self.services, set_status=self.set_status)
        self.watchlist_tab = WatchlistTab(
            self.notebook,
            services=self.services,
            run_async=self.run_async,
            set_status=self.set_status,
            open_symbol=self.open_symbol,
            on_change=self._refresh_system_status,
        )
        self.orders_tab = OrdersTab(
            self.notebook,
            services=self.services,
            set_status=self.set_status,
            on_change=self._refresh_system_status,
        )
        self.broker_tab = BrokerTab(
            self.notebook,
            services=self.services,
            run_async=self.run_async,
            set_status=self.set_status,
            default_account_id=self.services.config.broker.account_id,
        )
        self.notifications_tab = NotificationsTab(
            self.notebook,
            services=self.services,
            run_async=self.run_async,
            set_status=self.set_status,
        )

        self.notebook.add(self.market_tab, text="Market")
        self.notebook.add(self.watchlist_tab, text="Watchlist")
        self.notebook.add(self.orders_tab, text="Order Plans")
        self.notebook.add(self.broker_tab, text="Broker")
        self.notebook.add(self.notifications_tab, text="Notifications")
        self.notebook.add(self.system_tab, text="System")

    def _build_status_bar(self) -> None:
        frame = ttk.Frame(self, style="App.TFrame", padding=(18, 0, 18, 18))
        frame.grid(row=2, column=0, sticky="ew")
        frame.columnconfigure(0, weight=1)
        ttk.Separator(frame, orient="horizontal").grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ttk.Label(frame, textvariable=self.status_var, style="Status.TLabel").grid(row=1, column=0, sticky="w")


def launch_gui(services: AppServices) -> None:
    app = AutoStockDesktop(services)
    app.mainloop()
