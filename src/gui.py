import threading
import webbrowser
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import yfinance as yf


class FinancialDashboard(ctk.CTkFrame):

    def __init__(self, master, storage=None):
        super().__init__(master, fg_color="transparent")
        self.master = master
        self.pack(fill="both", expand=True, padx=20, pady=20)

        if storage is not None:
            self.persistent_storage = storage

        self._configure_grid_layout()
        self._init_dashboard_panels()
        
        # Asynchronously fetch default ticker to prevent startup lag
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
        self._build_heatmap_panel()
        self._build_sentiment_panel()
        self._build_order_panel()

    def _build_chart_panel(self):
        self.chart_frame = ctk.CTkFrame(self)
        self.chart_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Engine Control Sub-panel
        search_container = ctk.CTkFrame(self.chart_frame, fg_color="transparent")
        search_container.pack(fill="x", padx=15, pady=(15, 5))

        self.chart_search_input = ctk.CTkEntry(
            search_container, placeholder_text="Search Ticker (e.g., NVDA, TSLA)"
        )
        self.chart_search_input.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.chart_search_input.bind("<Return>", lambda event: self._on_search_submit())

        search_btn = ctk.CTkButton(
            search_container, text="Search", width=80, command=self._on_search_submit
        )
        search_btn.pack(side="right")

        # Status Messenger Line
        self.status_lbl = ctk.CTkLabel(
            self.chart_frame, text="System Ready", font=("Helvetica", 11, "italic"), text_color="#aaaaaa"
        )
        self.status_lbl.pack(anchor="w", padx=18)

        # Dynamic Content Viewport Area
        self.view_canvas_container = ctk.CTkFrame(self.chart_frame, fg_color="transparent")
        self.view_canvas_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.active_canvas_widget = None

    def _on_search_submit(self):
        ticker = self.chart_search_input.get().strip().upper()
        if not ticker:
            self._update_status_msg("Error: Input query empty", "#ff4d4d")
            return
        self._trigger_chart_update(ticker)

    def _update_status_msg(self, text, color="#aaaaaa"):
        self.status_lbl.configure(text=text, text_color=color)

    def _update_fear_meter(self, value):
        self.meter_bar.set(value)

    def _trigger_chart_update(self, ticker):
        self._update_status_msg(f"Fetching {ticker} market matrix asynchronously...", "#3b8ed0")
        
        # Multithreading worker isolates external network delays
        worker = threading.Thread(target=self._fetch_and_render_worker, args=(ticker,), daemon=True)
        worker.start()

    def _fetch_and_render_worker(self, ticker):
        try:
            stock_data = yf.download(ticker, period="1mo", interval="1d", progress=False)
            vi = yf.Ticker("^VIX").history(period="1d")["Close"].iloc[-1]
            vi = round(vi, 2)
            
            if stock_data.empty or len(stock_data) < 2:
                raise ValueError("Invalid symbol matrices returned")

            # Safely push visual updates back onto the main loop thread execution framework
            self.master.after(0, lambda: self._draw_matplotlib_canvas(ticker, stock_data))
            self.master.after(0, lambda: self._update_fear_meter(vi))
        except Exception as e:
            self.master.after(0, lambda: self._update_status_msg(f"Error lookup failed: {str(e)}", "#ff4d4d"))

    def _draw_matplotlib_canvas(self, ticker, data):
        # Clean down any residual historical rendering canvas contexts
        if self.active_canvas_widget:
            self.active_canvas_widget.destroy()

        self._update_status_msg(f"Displaying {ticker} performance data cleanly.", "#107c41")

        fig, ax = plt.subplots(figsize=(5, 3), facecolor="#2b2b2b")
        ax.set_facecolor("#2b2b2b")
        
        # Draw clean Close price vector lines
        ax.plot(data.index, data['Close'], color="#1f538d", linewidth=2)
        
        ax.set_title(f"{ticker} - Last 30 Days", color="white", fontsize=12, fontweight="bold")
        ax.tick_params(colors="white", labelsize=8)
        ax.grid(True, color="#444444", linestyle="--", linewidth=0.5)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.view_canvas_container)
        self.active_canvas_widget = canvas.get_tk_widget()
        self.active_canvas_widget.pack(fill="both", expand=True)
        canvas.draw()
        
        # Cleanup memory structures behind closed figures explicitly
        plt.close(fig)

    def _build_fear_panel(self):
        self.fear_frame = ctk.CTkFrame(self)
        self.fear_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        fear_title = ctk.CTkLabel(
            self.fear_frame, text="Fear & Greed Index", font=("Helvetica", 16, "bold")
        )
        fear_title.pack(pady=(15, 5))

        vi = yf.Ticker("^VIX").history(period="1d")["Close"].iloc[-1]
        vi = round(vi, 2)

        self.meter_bar = ctk.CTkProgressBar(self.fear_frame, orientation="horizontal", height=25)
        self.meter_bar.set(0.32)
        self.meter_bar.pack(fill="x", padx=30, pady=20)

        self.meter_label = ctk.CTkLabel(
            self.fear_frame, text=vi, font=("Helvetica", 24, "bold"), text_color="#ff4d4d"
        )
        self.meter_label.pack()

    def _build_heatmap_panel(self):
        self.heatmap_frame = ctk.CTkFrame(self)
        self.heatmap_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        heatmap_title = ctk.CTkLabel(
            self.heatmap_frame, text="Sector Performance", font=("Helvetica", 14, "bold")
        )
        heatmap_title.pack(anchor="w", padx=15, pady=(10, 5))

        self.matrix_container = ctk.CTkFrame(self.heatmap_frame, fg_color="transparent")
        self.matrix_container.pack(fill="both", expand=True, padx=15, pady=10)
        self.matrix_container.grid_columnconfigure((0, 1, 2), weight=1, uniform="sub")
        self.matrix_container.grid_rowconfigure((0, 1), weight=1, uniform="sub")

        sectors = [
            ("TECH\n+2.4%", "#107c41", 0, 0), ("FIN\n-0.8%", "#a80000", 0, 1), ("HLTH\n+0.1%", "#1b5e20", 0, 2),
            ("CONS\n-1.4%", "#7f0000", 1, 0), ("ENRG\n+3.1%", "#0b5127", 1, 1), ("UTIL\n0.0%", "#4a4a4a", 1, 2)
        ]
        for text, color, r, c in sectors:
            tile = ctk.CTkButton(
                self.matrix_container, text=text, fg_color=color, hover_color=color,
                font=("Helvetica", 12, "bold"), corner_radius=6
            )
            tile.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")

    def _build_sentiment_panel(self):
        self.sentiment_frame = ctk.CTkFrame(self)
        self.sentiment_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        sent_title = ctk.CTkLabel(
            self.sentiment_frame, text="Market Sentiment News", font=("Helvetica", 14, "bold")
        )
        sent_title.pack(anchor="w", padx=15, pady=(10, 5))

        self.news_scroll = ctk.CTkScrollableFrame(self.sentiment_frame, fg_color="transparent")
        self.news_scroll.pack(fill="both", expand=True, padx=10, pady=5)

        articles = [
            ("Bullish", "Fed hints at cutting baseline rates early next quarter", "https://news.google.com"),
            ("Bearish", "Tech margins squeeze as hardware costs reach macro high", "https://news.google.com"),
            ("Neutral", "Retail volume plateaus following seasonal push", "https://news.google.com")
        ]
        for sentiment, headline, url in articles:
            self._add_news_node(sentiment, headline, url)

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

        submit_order_btn = ctk.CTkButton(
            order_frame, text="Log Order", font=("Helvetica", 12, "bold"),
            fg_color="#1f538d", command=self._log_transaction
        )
        submit_order_btn.pack(fill="x", padx=15, pady=15)

        save_order_btn = ctk.CTkButton(
            order_frame, text="Save Orders", font=("Helvetica", 12, "bold"),
            fg_color="#1f538d", command=self._log_transaction
        )
        save_order_btn.pack(fill="x", padx=15, pady=15)

        ledger_title = ctk.CTkLabel(order_frame, text="Order History Log", font=("Helvetica", 13, "bold"))
        ledger_title.pack(anchor="w", padx=15, pady=(10, 2))

        self.ledger_scroll = ctk.CTkScrollableFrame(order_frame, fg_color=("#D1D1D1", "#1E1E1E"))
        self.ledger_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def _log_transaction(self):
        side = self.order_type.get()
        ticker = self.ticker_input.get().strip().upper()
        qty = self.qty_input.get().strip()
        price = self.price_input.get().strip()

        if not ticker or not qty or not price:
            return

        log_entry = ctk.CTkFrame(self.ledger_scroll, height=35, fg_color=("#EAEAEA", "#2B2B2B"))
        log_entry.pack(fill="x", pady=3, padx=2)
        log_entry.pack_propagate(False)

        side_color = "#107c41" if side == "BUY" else "#a80000"
        side_badge = ctk.CTkLabel(
            log_entry, text=side, text_color="white", fg_color=side_color,
            font=("Helvetica", 9, "bold"), width=40, corner_radius=3
        )
        side_badge.pack(side="left", padx=5)

        details_label = ctk.CTkLabel(log_entry, text=f"{ticker} | Qty: {qty} | @ ${price}", font=("Helvetica", 11))
        details_label.pack(side="left", padx=5)

        delete_btn = ctk.CTkButton(
            log_entry, text="✕", text_color=("#555555", "#aaaaaa"),
            fg_color="transparent", hover_color=("#DCDCDC", "#3A3A3A"),
            width=20, font=("Helvetica", 11, "bold"),
            command=log_entry.destroy
        )
        delete_btn.pack(side="right", padx=5)

        self.ticker_input.delete(0, "end")
        self.qty_input.delete(0, "end")
        self.price_input.delete(0, "end")

    def _add_news_node(self, sentiment, headline, url):
        node = ctk.CTkFrame(self.news_scroll, height=45, fg_color=("#EAEAEA", "#2B2B2B"))
        node.pack(fill="x", pady=4, padx=2)
        node.pack_propagate(False)

        badge_color = "#107c41" if sentiment == "Bullish" else "#a80000" if sentiment == "Bearish" else "#666666"
        badge = ctk.CTkLabel(
            node, text=sentiment[:4].upper(), fg_color=badge_color,
            text_color="white", width=50, font=("Helvetica", 10, "bold"), corner_radius=4
        )
        badge.pack(side="left", padx=8)

        link_btn = ctk.CTkButton(
            node, text=headline, anchor="w", fg_color="transparent",
            text_color=("black", "#A3D8FF"), hover_color=("#DCDCDC", "#3A3A3A"),
            font=("Helvetica", 12, "underline"), command=lambda u=url: webbrowser.open(u)
        )
        link_btn.pack(side="left", fill="both", expand=True)


def main():
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Institutional Financial Analytics Dashboard")
    root.geometry("1300x750")
    root.resizable(True, True)

    FinancialDashboard(root)
    root.mainloop()


if __name__ == "__main__":
    main()