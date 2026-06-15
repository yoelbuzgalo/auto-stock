import webbrowser
import customtkinter as ctk
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from .process import DashboardWorker
from .layout import DashboardLayout
from .bases import BaseDashboard
from .chart import DashboardChart
from .fear import FearMeter
from src.constants import RED, GREEN, WHITE, BLACK

class FinancialDashboard(BaseDashboard):

    __slots__ = [
        "layout",  
        "worker",
        "chart",
        "fear_meter",
        "persistent_storage",
        "active_news_nodes",
        "active_canvas_widget",
        "current_fig",
        "_resize_timer",
        "master",
        "fear_frame",       
        "sentiment_frame",  
        "meter_bar",        
        "meter_label",      
        "news_scroll",      
        "order_type",       
        "ticker_input",     
        "qty_input",        
        "price_input",      
        "ledger_scroll"     
    ]

    def __init__(self, master, storage=None):
        super().__init__(master, fg_color="transparent")
        self.master = master
        self.persistent_storage = storage

        self.active_news_nodes = dict()
        self.active_canvas_widget = None
        self.current_fig = None
        self._resize_timer = None

        # Build local modular frame components
        self._build_sentiment_panel()
        self._build_order_panel()

        self.layout = DashboardLayout(self)
        self.pack(fill="both", padx=0, pady=0)
        # Mount subframes locally to layout
        self.worker = DashboardWorker(self)
        self.chart = DashboardChart(self,self.worker)
        self.fear_meter = FearMeter(self)
        

        self.worker.update("AAPL")

    def execute_deferred_resize(self, w, h):
        if self.current_fig and self.active_canvas_widget and w > 10 and h > 10:
            dpi = self.current_fig.get_dpi()
            self.current_fig.set_size_inches(w / dpi, h / dpi)
            self.active_canvas_widget.draw_idle()

    def _debounce_canvas_resize(self, event):
        if self._resize_timer is not None:
            self.master.after_cancel(self._resize_timer)
        self._resize_timer = self.master.after(150, lambda: self._execute_deferred_resize(event.width, event.height))

    def search(self,ticker):
        self.worker.update(ticker)

    def _draw_matplotlib_canvas(self, ticker, data):
        self.chart.update(ticker, data)

    def _build_sentiment_panel(self):
        self.sentiment_frame = ctk.CTkFrame(self)
        self.sentiment_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        sent_title = ctk.CTkLabel(self.sentiment_frame, text="Market Sentiment News", font=("Helvetica", 14, "bold"))
        sent_title.pack(anchor="w", padx=15, pady=(10, 5))

        self.news_scroll = ctk.CTkScrollableFrame(self.sentiment_frame, fg_color="transparent")
        self.news_scroll.pack(fill="both", expand=True, padx=10, pady=5)

    def _build_order_panel(self):
        order_frame = ctk.CTkFrame(self)
        order_frame.grid(row=0, column=2, rowspan=2, padx=10, pady=10, sticky="nsew")

        title = ctk.CTkLabel(order_frame, text="Execute & Track Orders", font=("Helvetica", 16, "bold"))
        title.pack(pady=15)

        self.order_type = ctk.CTkSegmentedButton(order_frame, values=["BUY", "SELL"])
        self.order_type.set("BUY")
        self.order_type.pack(fill="x", padx=15, pady=5)

        self.ticker_input = ctk.CTkEntry(order_frame, placeholder_text="Ticker (e.g. AAPL)")
        self.ticker_input.pack(fill="x", padx=15, pady=5)

        self.qty_input = ctk.CTkEntry(order_frame, placeholder_text="Quantity")
        self.qty_input.pack(fill="x", padx=15, pady=5)

        self.price_input = ctk.CTkEntry(order_frame, placeholder_text="Price ($)")
        self.price_input.pack(fill="x", padx=15, pady=5)

        btn = ctk.CTkButton(
            order_frame, text="Log Order", font=("Helvetica", 12, "bold"),
            fg_color="#1f538d", command=self._log_transaction
        )
        btn.pack(fill="x", padx=15, pady=10)

        btn = ctk.CTkButton(
            order_frame, text="Save Orders", font=("Helvetica", 12, "bold"),
            fg_color="#1f538d", command=self._save_transactions
        )
        btn.pack(fill="x", padx=15, pady=10)

        ledger_title = ctk.CTkLabel(order_frame, text="Order History Log", font=("Helvetica", 13, "bold"))
        ledger_title.pack(anchor="w", padx=15, pady=(10, 2))

        self.ledger_scroll = ctk.CTkScrollableFrame(order_frame, fg_color=(WHITE, "#1E1E1E"))
        self.ledger_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def _save_transactions(self):
        self._update_status_msg("Saving orders to JSON file...", WHITE)
        if not self.persistent_storage:
            return
        result = self.persistent_storage.save()
        if result:
            self._update_status_msg("Orders saved!", GREEN)
        else:
            self._update_status_msg("Error saving orders..", RED)

    def _delete_transaction(self, log_entry: ctk.CTkFrame):
        log_entry.destroy()

    def _log_transaction(self):
        side = self.order_type.get()
        ticker = self.ticker_input.get().strip().upper()
        qty = self.qty_input.get().strip()
        price = self.price_input.get().strip()

        if not ticker or not qty or not price:
            return

        if self.persistent_storage:
            self.persistent_storage.add_item((ticker, qty, price))

        log_entry = ctk.CTkFrame(self.ledger_scroll, height=35, fg_color=(WHITE, BLACK))
        log_entry.pack(fill="x", pady=3, padx=2)
        log_entry.pack_propagate(False)

        side_badge = ctk.CTkLabel(
            log_entry, text=side, text_color="white", fg_color=GREEN if side == "BUY" else "#a80000",
            font=("Helvetica", 9, "bold"), width=40, corner_radius=3
        )
        side_badge.pack(side="left", padx=5)

        details_label = ctk.CTkLabel(log_entry, text=f"{ticker} | Qty: {qty} | @ ${price}", font=("Helvetica", 11))
        details_label.pack(side="left", padx=5)

        delete_btn = ctk.CTkButton(
            log_entry, text="✕", text_color=("#555555", "#aaaaaa"), fg_color="transparent",
            hover_color=("#DCDCDC", "#3A3A3A"), width=20, font=("Helvetica", 11, "bold"),
            command=lambda: self._delete_transaction(log_entry)
        )
        delete_btn.pack(side="right", padx=5)

        self.ticker_input.delete(0, "end")
        self.qty_input.delete(0, "end")
        self.price_input.delete(0, "end")

    def _add_news_node(self, news):
        news_content = news.get("content", {})
        news_id = news.get("id") or news_content.get("id")
        title = news_content.get('title', 'No Title')
        url = (news_content.get('clickThroughUrl') or news_content.get('canonicalUrl') or {}).get('url', 'No Link')

        node = ctk.CTkFrame(self.news_scroll, height=45, fg_color=(WHITE, BLACK))
        node.pack(fill="x", pady=4, padx=2)
        node.pack_propagate(False)

        if news_id:
            self.active_news_nodes[news_id] = node

        badge = ctk.CTkLabel(
            node, text=title[:4].upper(), fg_color=GREEN,
            text_color="white", width=50, font=("Helvetica", 10, "bold"), corner_radius=4
        )
        badge.pack(side="left", padx=8)

        link_btn = ctk.CTkButton(
            node, text=title, anchor="w", fg_color="transparent",
            text_color=("black", "#A3D8FF"), hover_color=("#DCDCDC", "#3A3A3A"),
            font=("Helvetica", 12, "underline"), command=lambda u=url: webbrowser.open(u)
        )
        link_btn.pack(side="left", fill="both", expand=True)

    def _remove_news_node(self, news_id):
        if news_id in self.active_news_nodes:
            self.active_news_nodes[news_id].destroy()
            del self.active_news_nodes[news_id]

    def clear_all_news(self):
        for news_id in list(self.active_news_nodes.keys()):
            self._remove_news_node(news_id)


    """
    
    Getters
    
    """

    def get_chart(self):
        return self.chart
    
    def get_worker(self):
        return self.worker
    
    def get_meter(self):
        return self.meter_bar

    """
    
    Setters

    
    """

    def set_chart(self, chart):
        self.chart = chart

def run_gui_app(storage=None):
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Financial Analytics Dashboard")
    root.geometry("1300x750")
    root.resizable(True, True)

    FinancialDashboard(root, storage=storage)
    root.mainloop()

def main():
    run_gui_app()

if __name__ == "__main__":
    main()