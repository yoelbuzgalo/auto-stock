import threading
import webbrowser
import customtkinter as ctk
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import yfinance as yf
import re

GREEN = "#107c41"
RED = "#a80000"
WHITE = "#D1D1D1"
PRICE_PATTERN=r"\s+(\d+\.\d+)"

class FinancialDashboard(ctk.CTkFrame):

    def __init__(self, master, storage=None):
        super().__init__(master, fg_color="transparent")
        self.master = master
        self.pack(fill="both", expand=True, padx=20, pady=20)

        if storage is not None:
            self.persistent_storage = storage

        # State management parameters
        self.active_news_nodes = dict()
        self.active_canvas_widget = None
        self.current_fig = None
        self._resize_timer = None  # Crucial for debouncing resize lag

        self._configure_grid_layout()
        self._init_dashboard_panels()

        # Initial asynchronous application population
        self._trigger_chart_update("AAPL")

    def _configure_grid_layout(self):
        self.grid_columnconfigure(0, weight=3, uniform="main_cols")
        self.grid_columnconfigure(1, weight=2, uniform="main_cols")
        self.grid_columnconfigure(2, weight=2, uniform="main_cols")
        self.grid_rowconfigure(0, weight=1, uniform="rows")
        self.grid_rowconfigure(1, weight=1, uniform="rows")

    def _init_dashboard_panels(self):
        self._build_chart_panel()
        self._build_fear_panel()
        self._build_sentiment_panel()
        self._build_order_panel()

    def _build_chart_panel(self):
        self.chart_frame = ctk.CTkFrame(self)
        self.chart_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.chart_frame.grid_columnconfigure(0, weight=1)
        self.chart_frame.grid_rowconfigure(2, weight=1)

        # Engine Control Sub-panel
        search_container = ctk.CTkFrame(self.chart_frame, fg_color="transparent")
        search_container.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="ew")

        self.chart_search_input = ctk.CTkEntry(
            search_container, placeholder_text="Search Ticker (e.g., NVDA, TSLA)"
        )
        self.chart_search_input.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.chart_search_input.bind("<Return>", lambda e: self._on_search_submit())

        search_btn = ctk.CTkButton(search_container, text="Search", width=80, command=self._on_search_submit)
        search_btn.pack(side="right")

        # Status Messenger Line
        self.status_lbl = ctk.CTkLabel(
            self.chart_frame, text="System Ready", font=("Helvetica", 11, "italic"), text_color="#aaaaaa"
        )
        self.status_lbl.grid(row=1, column=0, padx=18, sticky="w")

        # Dynamic Content Viewport Area
        self.view_canvas_container = ctk.CTkFrame(self.chart_frame, fg_color="transparent")
        self.view_canvas_container.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.view_canvas_container.grid_rowconfigure(0, weight=1)
        self.view_canvas_container.grid_columnconfigure(0, weight=1)
        
        # Debounced Event Binding - Smooths resizing down completely
        self.view_canvas_container.bind("<Configure>", self._debounce_canvas_resize)

    def _debounce_canvas_resize(self, event):
        """Cancels past sizing queues to ensure drawing executes only when drag stops."""
        if self._resize_timer is not None:
            self.master.after_cancel(self._resize_timer)
        
        # Wait 150ms before committing to redrawing core components
        self._resize_timer = self.master.after(150, lambda: self._execute_deferred_resize(event.width, event.height))

    def _execute_deferred_resize(self, w, h):
        """Runs single layout calculations cleanly without lagging out layout managers."""
        if self.current_fig and self.active_canvas_widget and w > 10 and h > 10:
            dpi = self.current_fig.get_dpi()
            self.current_fig.set_size_inches(w / dpi, h / dpi)
            self.active_canvas_widget.draw_idle()

    def _on_search_submit(self):
        ticker = self.chart_search_input.get().strip().upper()
        if not ticker:
            self._update_status_msg("Error: Input query empty", RED)
            return
        self._trigger_chart_update(ticker)

    def _update_status_msg(self, text, color="#aaaaaa"):
        self.status_lbl.configure(text=text, text_color=color)

    def _update_fear_meter(self, value):
        self.meter_bar.set(round(value, 2) / 100)
        self.meter_label.configure(text=value)

    def _trigger_chart_update(self, ticker):
        self._update_status_msg(f"Fetching market data for {ticker}...", "#3b8ed0")
        self.ticker_input.delete(0,"end")
        self.ticker_input.insert(0,ticker)
        stock_data = yf.download(ticker, period="1mo", interval="1d", progress=False)
        threading.Thread(target=self._fetch_and_render_worker, args=(ticker,stock_data), daemon=True).start()

    def _fetch_and_render_worker(self, ticker, stock_data):
        try:
            # After retrieving the data, get the most recently available price

            prices = stock_data[("Close",ticker)]
            data = prices.head(1).to_string()
            price = re.search(PRICE_PATTERN,data).group(1)

            # Insert it into the order panel for convenience
            self.price_input.delete(0,"end")
            self.price_input.insert(0,price)
            
            vi = yf.Ticker("^VIX").history(period="1d")["Close"].iloc[-1]
            vi = round(vi, 2)
            ticker_obj = yf.Ticker(ticker)
            articles = ticker_obj.news[:5]
            
            if stock_data.empty or len(stock_data) < 2:
                raise ValueError("Invalid symbol matrices returned")

            # Consolidated singular execution block pushed to main event loop
            self.master.after(0, lambda: self._apply_downloaded_payload(ticker, stock_data, vi, articles))
        except Exception as e:
            self.master.after(0, lambda: self._update_status_msg(f"Error lookup failed: ", "#ff4d4d"))

    def _apply_downloaded_payload(self, ticker, stock_data, vix_val, articles):
        """Unified UI updates executed purely inside the safe main process thread."""
        self._draw_matplotlib_canvas(ticker, stock_data)
        self._update_fear_meter(vix_val)
        self.clear_all_news()
        for news in articles:
            self._add_news_node(news)

    def _draw_matplotlib_canvas(self, ticker, data):
        if self.active_canvas_widget:
            self.active_canvas_widget.get_tk_widget().destroy()

        self._update_status_msg(f"Displaying {ticker} performance data cleanly.", GREEN)

        # Expand the baseline figure layout proportion slightly
        fig, ax = plt.subplots(figsize=(6, 3.5), facecolor="#2b2b2b")
        ax.set_facecolor("#2b2b2b")
        
        # Draw Close price lines
        ax.plot(data.index, data['Close'], color="#1f538d", linewidth=2)
        
        
        # Rotate date labels automatically so they don't crash into each other
        fig.autofmt_xdate(bottom=0.2, rotation=30, ha='right')
        
        # Only show a tick mark every 5 days instead of all 30 days
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
        # Format dates as 'Year-Month-Day'
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

        # Styling adjustments
        ax.set_title(f"{ticker} - Last 30 Days", color=WHITE, fontsize=12, fontweight="bold")
        ax.tick_params(colors="white", labelsize=9)
        ax.grid(True, color="#444444", linestyle="--", linewidth=0.5)
        
        # Using tight_layout safely keeps labels inside the image borders
        fig.tight_layout()

        # Mount everything to your Tkinter grid viewport
        self.current_fig = fig
        canvas = FigureCanvasTkAgg(fig, master=self.view_canvas_container)
        self.active_canvas_widget = canvas
        
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        canvas.draw()
        plt.close(fig)

    def _build_fear_panel(self):
        self.fear_frame = ctk.CTkFrame(self)
        self.fear_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        fear_title = ctk.CTkLabel(self.fear_frame, text="Fear & Greed Index", font=("Helvetica", 16, "bold"))
        fear_title.pack(pady=(15, 5))

        self.meter_bar = ctk.CTkProgressBar(self.fear_frame, orientation="horizontal", height=25)
        self.meter_bar.set(0.32)
        self.meter_bar.pack(fill="x", padx=30, pady=20)

        self.meter_label = ctk.CTkLabel(self.fear_frame, text="0.0", font=("Helvetica", 24, "bold"), text_color=GREEN)
        self.meter_label.pack()

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

        # Log orders button

        btn = ctk.CTkButton(
            order_frame, text="Log Order", font=("Helvetica", 12, "bold"),
            fg_color="#1f538d", command=self._log_transaction
        )
        btn.pack(fill="x", padx=15, pady=10)

        # Save orders

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
        self._update_status_msg("Saving orders to JSON file...",WHITE)
        result = self.persistent_storage.save()
        if result:
            self._update_status_msg("Orders saved!",GREEN)
        else:
            self._update_status_msg("Error saving orders..",RED)

    def _delete_transaction(self,log_entry:ctk.CTkFrame):
        log_entry.destroy()

    def _log_transaction(self):
        side = self.order_type.get()
        ticker = self.ticker_input.get().strip().upper()
        qty = self.qty_input.get().strip()
        price = self.price_input.get().strip()

        self.persistent_storage.add_item((ticker,qty,price))

        if not ticker or not qty or not price:
            return

        log_entry = ctk.CTkFrame(self.ledger_scroll, height=35, fg_color=("#EAEAEA", "#2B2B2B"))
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
            command=lambda:self._delete_transaction(log_entry)
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

        node = ctk.CTkFrame(self.news_scroll, height=45, fg_color=("#EAEAEA", "#2B2B2B"))
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

        

def run_gui_app(storage):
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Financial Analytics Dashboard")
    root.geometry("1300x750")
    root.resizable(True, True)

    FinancialDashboard(root,storage=storage)
    root.mainloop()

def main():
    run_gui_app()


if __name__ == "__main__":
    main()