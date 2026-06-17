import webbrowser
import customtkinter as ctk
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import queue
from pathlib import Path
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from modules.services import Persistence
from modules.services.persistence import JsonFilePersistence
from .process import DashboardWorker
from .layout import DashboardLayout
from .bases import BaseDashboard
from src.constants import *

class FinancialDashboard(BaseDashboard):
    """
    Main controller for the Financial Analysis and Order Execution Dashboard.
    Manages background thread tasks, coordinates UI presentation layers, 
    and handles state for active tickers, orders, and real-time market news.
    """

    def __init__(self, master, storage:Persistence=None):
        """
        Initializes the dashboard workspace, sets up local storage drivers,
        and initializes structural UI layout components.

        Args:
            master (tk.Tk / ctk.CTk): The parent root window or frame container.
            storage (Persistence, optional): Pluggable data layer for saving/loading transactions.
        """
        super().__init__(master, fg_color="transparent")
        self.master = master
        self.persistent_storage = storage
        self.tickers = []
        self.current_orders = list()
        self.active_news_nodes = dict()
        self.news_nodes = []
        self.active_canvas_widget = None
        self.current_fig = None
        self._resize_timer = None
        self.check_queue()

        self.grid(row=0, column=0, sticky="nsew", padx=PADDING_MAIN_X, pady=PADDING_MAIN_Y)
        
        self._worker = DashboardWorker(self, int(MAX_WORKERS))
        self._layout = DashboardLayout(self)
    

    def search(self):
        """Triggers the active background worker queue to execute a market update sweep."""
        self.worker.update()

    def _draw_matplotlib_canvas(self, ticker, data):
        """
        Updates the active visualization matrix with incoming data series.

        Args:
            ticker (str): Asset equity identifier.
            data (dict/DataFrame): Data payload consisting of time-series records.
        """
        if hasattr(self, "chart"):
            self.chart.update(ticker, data)

    def _build_sentiment_panel(self):
        """Builds and grids the display architecture for real-time market sentiment items."""
        self.sentiment_frame = ctk.CTkFrame(self, width=int(SENTIMENT_PANEL_WIDTH), height=int(SENTIMENT_PANEL_HEIGHT))
        self.sentiment_frame.grid(row=1, column=1, padx=PADDING_SENTIMENT_PANEL_X, pady=PADDING_SENTIMENT_PANEL_Y, sticky="nsew")
        self.sentiment_frame.pack_propagate(False)

        sent_title = ctk.CTkLabel(
            self.sentiment_frame, 
            text="Market Sentiment News", 
            font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold")
        )
        sent_title.pack(anchor="w", padx=PADDING_SENTIMENT_INNER_X, pady=(PADDING_SENTIMENT_OUTER_Y, PADDING_SENTIMENT_INNER_Y))

        self.news_scroll = ctk.CTkScrollableFrame(self.sentiment_frame, fg_color="transparent")
        self.news_scroll.pack(fill="both", expand=True, padx=PADDING_SENTIMENT_PANEL_X, pady=PADDING_SENTIMENT_INNER_Y)

    def _build_order_panel(self):
        """Builds the transaction ledger input interfaces, parameters, and historical logging elements."""
        self.persistent_storage = JsonFilePersistence(Path(JSON_PATH)) 
        data = self.persistent_storage.load_items()
        order_frame = ctk.CTkFrame(self, width=int(ORDER_PANEL_WIDTH), height=int(ORDER_PANEL_HEIGHT))
        order_frame.grid(row=0, column=2, rowspan=2, padx=PADDING_ORDER_PANEL_X, pady=PADDING_ORDER_PANEL_Y, sticky="ns")
        order_frame.pack_propagate(False)

        title = ctk.CTkLabel(order_frame, text="Execute & Track Orders", font=(FONT_FAMILY, FONT_SIZE_MEDIUM, "bold"))
        title.pack(pady=PADDING_ORDER_INNER_X)

        self.order_type = ctk.CTkSegmentedButton(order_frame, values=["BUY", "SELL"])
        self.order_type.set("BUY")
        self.order_type.pack(fill="x", padx=PADDING_ORDER_INNER_X, pady=PADDING_ORDER_INNER_Y)

        self.ticker_input = ctk.CTkEntry(order_frame, placeholder_text="Ticker (e.g. AAPL)")
        self.ticker_input.pack(fill="x", padx=PADDING_ORDER_INNER_X, pady=PADDING_ORDER_INNER_Y)

        self.qty_input = ctk.CTkEntry(order_frame, placeholder_text="Quantity")
        self.qty_input.pack(fill="x", padx=PADDING_ORDER_INNER_X, pady=PADDING_ORDER_INNER_Y)

        self.price_input = ctk.CTkEntry(order_frame, placeholder_text="Price ($)")
        self.price_input.pack(fill="x", padx=PADDING_ORDER_INNER_X, pady=PADDING_ORDER_INNER_Y)

        btn = ctk.CTkButton(
            order_frame, text="Log Order", font=(FONT_FAMILY, FONT_SIZE_BODY, "bold"),
            fg_color=DEEP_BLUE, command=self._log_transaction
        )
        btn.pack(fill="x", padx=PADDING_ORDER_INNER_X, pady=PADDING_ORDER_OUTER_Y)

        btn = ctk.CTkButton(
            order_frame, text="Save Orders", font=(FONT_FAMILY, FONT_SIZE_BODY, "bold"),
            fg_color=DEEP_BLUE, command=self._save_transactions
        )
        btn.pack(fill="x", padx=PADDING_ORDER_INNER_X, pady=PADDING_ORDER_OUTER_Y)

        ledger_title = ctk.CTkLabel(order_frame, text="Order History Log", font=(FONT_FAMILY, FONT_SIZE_SUB, "bold"))
        ledger_title.pack(anchor="w", padx=PADDING_ORDER_INNER_X, pady=(PADDING_ORDER_OUTER_Y, PADDING_LEDGER_LIST_X))

        self.ledger_scroll = ctk.CTkScrollableFrame(order_frame, fg_color="transparent")
        self.ledger_scroll.pack(fill="both", expand=True, padx=PADDING_ORDER_INNER_X, pady=(0, PADDING_ORDER_INNER_X))            

    def _save_transactions(self):
        """Serializes current cache transactions onto disk via active persistent storage engine wrappers."""
        self._update_status_msg("Saving orders to JSON file...", WHITE)

        self.persistent_storage.add_items(self.current_orders)
        result = self.persistent_storage.save()

        if result:
            self._update_status_msg("Orders saved!", GREEN)
        else:
            self._update_status_msg("Error saving orders..", RED)

    def _delete_transaction(self, widget_frame):
        """
        Removes a targeted order transaction record from both memory tables and the UI scrolling container.

        Args:
            widget_frame (ctk.CTkFrame): The structural frame item housing the target item elements.
        """
        target_idx = None
        for idx, order in enumerate(self.current_orders):
            if order["ui_frame"] == widget_frame:
                target_idx = idx
                break

        if target_idx is not None:
            order_to_remove = self.current_orders.pop(target_idx)
            if order_to_remove["ticker"] in self.tickers:
                self.tickers.remove(order_to_remove["ticker"])
            if order_to_remove["ui_frame"] and order_to_remove["ui_frame"].winfo_exists():
                order_to_remove["ui_frame"].destroy()

    def _log_transaction(self, **kwargs):
        """
        Validates, processes, and pushes a newly defined order entry into active display blocks.

        Args:
            **kwargs: Can include explicit 'data' tuples to programmatically execute log entries.
        """
        data = kwargs.get("data", None)
        side = None
        ticker = None
        qty = None
        price = None

        if data is None:
            side = self.order_type.get()
            ticker = self.ticker_input.get().strip().upper()
            qty = self.qty_input.get().strip()
            price = self.price_input.get().strip()
        else:
            side, ticker, qty, price = data

        if not ticker or not qty or not price:
            return

        try:
            qty = float(qty)
            price = float(price)
        except ValueError:
            self._update_status_msg("Invalid entry types", RED)
            return

        log_entry = ctk.CTkFrame(self.ledger_scroll, width=int(LEDGER_ROW_WIDTH), height=int(LEDGER_ROW_HEIGHT), bg_color="transparent")
        log_entry.pack(fill="x", pady=3, padx=PADDING_LEDGER_LIST_X)
        log_entry.pack_propagate(False)

        side_badge = ctk.CTkLabel(
            log_entry, text=side, text_color="white", fg_color=GREEN if side == "BUY" else RED,
            font=(FONT_FAMILY, FONT_SIZE_MINI, "bold"), width=40, corner_radius=3,
        )
        side_badge.pack(side="left", padx=PADDING_ORDER_INNER_Y)

        details_label = ctk.CTkLabel(log_entry, fg_color="transparent", bg_color="transparent", text=f"{ticker} | Qty: {qty} | @ ${price}", font=(FONT_FAMILY, FONT_SIZE_SMALL))
        details_label.pack(side="left", padx=DETAILS_PADDING_X)

        delete_btn = ctk.CTkButton(
            log_entry, text="✕", text_color=DARK_GRAY, fg_color="transparent",
            hover_color=(LIGHT_GRAY, DARK_GRAY), width=20, font=(FONT_FAMILY, FONT_SIZE_SMALL, "bold"),
            command=lambda f=log_entry: self._delete_transaction(f)
        )
        delete_btn.pack(side="right", padx=PADDING_ORDER_INNER_Y)

        order = tuple([ticker, price])

        self.tickers.append(ticker)
        self.current_orders.append(order)
        self.ticker_input.delete(0, "end")
        self.qty_input.delete(0, "end")
        self.price_input.delete(0, "end")

    def _add_news_node(self, news):
        """
        Assembles, binds, and renders a localized interactive element mapping back to external news sources.

        Args:
            news (dict): Structural market news entity carrying headers, index-keys, and links.
        """
        news_content = news.get("content", {})
        news_id = news.get("id") or news_content.get("id")
        title = news_content.get("title", "No Title")
        url = (news_content.get("clickThroughUrl") or news_content.get("canonicalUrl") or {}).get("url", "No Link")

        node = ctk.CTkFrame(self.news_scroll, height=int(NEWS_ROW_HEIGHT), fg_color="transparent")
        node.pack(fill="x", pady=PADDING_NEWS_LIST_Y, padx=PADDING_NEWS_LIST_X)
        node.pack_propagate(False)

        if news_id:
            self.active_news_nodes[news_id] = node
            self.news_nodes.append([news_id,title,url])

        badge = ctk.CTkLabel(
            node, text=title[:4].upper(), fg_color=GREEN,
            text_color="white", width=50, font=(FONT_FAMILY, FONT_SIZE_MINI, "bold"), corner_radius=4
        )
        badge.pack(side="left", padx=PADDING_NEWS_BADGE_X)

        link_btn = ctk.CTkButton(
            node, text=title[:NEWS_CHAR_LIMIT], anchor="w", fg_color="transparent",
            text_color=(DARK_GRAY), hover_color=(LIGHT_GRAY, DARK_GRAY),
            font=(FONT_FAMILY, FONT_SIZE_BODY, "underline"), command=lambda u=url: webbrowser.open(u)
        )
        link_btn.pack(side="left", fill="both", expand=True)

    def _remove_news_node(self, news_id):
        """
        Clears a target individual streaming news item element from memory cache and layout views.

        Args:
            news_id (str): Unique structural layout verification lookup key.
        """
        if news_id in self.active_news_nodes:
            self.active_news_nodes[news_id].destroy()
            del self.active_news_nodes[news_id]

    def clear_all_news(self):
        """Purges every active streaming node mapped inside the news collection cache view."""
        for news_id in list(self.active_news_nodes.keys()):
            self._remove_news_node(news_id)

    def _update_status_msg(self, text, color=WHITE):
        """
        Updates display messages within the visible charting environment tracking panel.

        Args:
            text (str): Display message target string.
            color (str, optional): Target rendering color configuration. Defaults to WHITE.
        """
        if hasattr(self, "layout") and hasattr(self.layout, "chart"):
            self.chart.update_chart_msg(text, color)

    def check_queue(self):
        """
        Continually monitors and drains the application's thread-safe GUI queue.
        Safely dispatches tasks waiting for execution inside the main execution thread.
        """
        try:
            while True:
                task = self.gui_queue.get_nowait()
                task()
                self.gui_queue.task_done()
        except queue.Empty:
            pass
        self.after(QUEUE_POLL, self.check_queue)

    def get_news_context(self):
        return self.news_nodes

    @property
    def chart(self):
        """Provides high-level abstraction validation tracking to historical chart visual arrays."""
        if hasattr(self, "_chart"):
            return self._chart
        else:
            return None

    @chart.setter
    def chart(self, chart):
        self._chart = chart

    @property
    def meter(self):
        """Provides modular interface references tracking to linear performance meters."""
        if hasattr(self, "meter_bar"):
            return self.meter_bar
        return None
    
    @property
    def worker(self):
        """Provides a way to retrieve the worker to run tasks asynchronously"""
        if hasattr(self,"_worker"):
            return self._worker
        return None

    @property
    def price_input_field(self):
        """Encapsulates system layout text references tracking directly to order execution entry items."""
        if hasattr(self, "_price_input"):
            return self._price_input
        return None

    @property
    def queue(self):
        """Exposes the application's thread-safe GUI queue for external worker coordination."""
        return self.gui_queue


def run_gui_app(storage=None):
    """
    Sets application styling defaults and acts as the entry orchestrator to build
    the core app frame and mount the detached AI Copilot panel safely.

    Args:
        storage (Persistence, optional): Pluggable data layer for saving/loading transactions.
    """
    ctk.set_appearance_mode(APPEARANCE_MODE)
    ctk.set_default_color_theme(COLOR_THEME)

    root = ctk.CTk()
    root.title(WINDOW_TITLE)
    root.geometry(WINDOW_GEOMETRY)
    root.resizable(True, True)

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    dashboard = FinancialDashboard(root, storage=storage)
        
    root.mainloop()

def main():
    """Main program entry block."""
    run_gui_app()

if __name__ == "__main__":
    main()