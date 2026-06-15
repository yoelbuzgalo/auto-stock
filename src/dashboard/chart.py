import customtkinter as ctk
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from src.constants import RED, GREEN, WHITE
from .process import DashboardWorker
from .bases import BaseDashboard

class DashboardChart(ctk.CTkFrame):

    def __init__(self, root: BaseDashboard, worker: DashboardWorker):
        super().__init__(root, fg_color="transparent")
        self.root = root
        self.data = worker.download_data()
        self.active_canvas_widget = None
        self._build_chart_panel()
        self.update()

    def update_msg(self, text, color):
        self._update_status_msg(text, color)

    def update(self, ticker="AAPL"):

        self._draw_matplotlib_canvas(ticker, self.data)
        self._update_status_msg(ticker, GREEN)

    def _draw_matplotlib_canvas(self, ticker, data=None):

        if self.data is None:
            self.data = DashboardWorker.download_data(ticker)
        
        if data is None:
            data = self.data

        if self.active_canvas_widget:
            self.active_canvas_widget.get_tk_widget().destroy()

        fig, ax = plt.subplots(figsize=(6, 3.5), facecolor="#2b2b2b")
        ax.set_facecolor("#2b2b2b")
        
        ax.plot(data.index, data['Close'], color="#1f538d", linewidth=2)
        fig.autofmt_xdate(bottom=0.2, rotation=30, ha='right')
        
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

        ax.set_title(f"{ticker} - Last 30 Days", color=WHITE, fontsize=11, fontweight="bold")
        ax.tick_params(colors="white", labelsize=9)
        ax.grid(True, color="#444444", linestyle="--", linewidth=0.5)
        
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.view_canvas_container)
        self.active_canvas_widget = canvas
        
        if hasattr(self.root, 'ticker_input'):
            self.root.ticker_input.delete(0, 'end')
            self.root.ticker_input.insert(0, ticker)
            
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        canvas.draw()
        plt.close(fig)

    def _update_status_msg(self, text, color=WHITE):
        if hasattr(self, 'chart_status_lbl'):
            self.chart_status_lbl.configure(text=text, text_color=color)

    def _build_chart_panel(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        search_container = ctk.CTkFrame(self, fg_color="transparent")
        search_container.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="ew")

        self.chart_search_input = ctk.CTkEntry(
            search_container, placeholder_text="Search Ticker (e.g., NVDA, TSLA)"
        )
        self.chart_search_input.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=(0, 10))
        
        self.chart_search_input.bind("<Return>", command=lambda: self.root.search(self.chart_search_input.get().upper()))

        search_btn = ctk.CTkButton(search_container, text="Search", width=80, command=lambda: self.root.search(self.chart_search_input.get().upper()))
        search_btn.pack(side="right", pady=(0, 10))

        self.chart_status_lbl = ctk.CTkLabel(
            self, text="System Ready", font=("Helvetica", 11, "italic"), text_color="#aaaaaa", fg_color="transparent"
        )
        self.chart_status_lbl.grid(row=1, column=0, padx=18, pady=(0, 5), sticky="w")
        
        self.view_canvas_container = ctk.CTkFrame(self, fg_color="transparent")
        self.view_canvas_container.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.view_canvas_container.grid_rowconfigure(0, weight=1)
        self.view_canvas_container.grid_columnconfigure(0, weight=1)
        
        if hasattr(self.root, '_debounce_canvas_resize'):
            self.view_canvas_container.bind("<Configure>", self.root._debounce_canvas_resize)
        self.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nsew")

    def set_data(self, data):
        self.data = data