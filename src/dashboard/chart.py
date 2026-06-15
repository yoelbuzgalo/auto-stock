from .bases import BaseDashboard
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from src.constants import RED, GREEN, WHITE

class DashboardChart:

    def __init__(self,root:BaseDashboard):
        self.root = root
        self._build_chart_panel()


    def update(self,ticker,data):
        self._draw_matplotlib_canvas(ticker,data)
        self._update_status_msg(ticker)

    def _draw_matplotlib_canvas(self, ticker, data):
        if self.root.active_canvas_widget:
            self.root.active_canvas_widget.get_tk_widget().destroy()

        self.root._update_status_msg(f"Displaying {ticker} performance data cleanly.", GREEN)

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
        ax.set_title(f"{ticker} - Last 30 Days", color=WHITE, fontsize=11, fontweight="bold")
        ax.tick_params(colors="white", labelsize=9)
        ax.grid(True, color="#444444", linestyle="--", linewidth=0.5)
        
        # Using tight_layout safely keeps labels inside the image borders
        fig.tight_layout()

        # Mount everything to your Tkinter grid viewport
        self.root.current_fig = fig
        canvas = FigureCanvasTkAgg(fig, master=self.view_canvas_container)
        self.root.active_canvas_widget = canvas
        self.root.ticker_input.insert(0,ticker)
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        canvas.draw()
        plt.close(fig)

    def _update_status_msg(self, text, color=WHITE, coords=(5,40)):
        self.root.chart_status_lbl.configure(text=text,fg_color="transparent",text_color=color)
        x,y = coords
        self.root.chart_status_lbl.place(x=x,y=y)

    def _build_chart_panel(self):
        self.root.chart_frame = ctk.CTkFrame(self.root)
        self.root.chart_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.root.chart_frame.grid_columnconfigure(0, weight=1)
        self.root.chart_frame.grid_rowconfigure(2, weight=1)

        # Engine Control Sub-panel
        search_container = ctk.CTkFrame(self.root.chart_frame, fg_color="transparent")
        search_container.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="ew")

        self.root.chart_search_input = ctk.CTkEntry(
            search_container, placeholder_text="Search Ticker (e.g., NVDA, TSLA)"
        )
        self.root.chart_search_input.pack(side="left", fill="x", expand=True, padx=(0, 30),pady=(0,50))
        self.root.chart_search_input.bind("<Return>", lambda e: self._on_search_submit())

        search_btn = ctk.CTkButton(search_container, text="Search", width=80, command=self._on_search_submit)
        search_btn.pack(side="right")

        # Status Messenger Line
        self.root.chart_status_lbl = ctk.CTkLabel(
            self.root.chart_frame, text="System Ready", font=("Helvetica", 11, "italic"), text_color="#aaaaaa",fg_color="transparent"
        )
        self.root.chart_status_lbl.grid(row=1, column=0, padx=18, sticky="w")
        
        # Dynamic Content Viewport Area
        self.view_canvas_container = ctk.CTkFrame(self.root.chart_frame, fg_color="transparent")
        self.view_canvas_container.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.view_canvas_container.grid_rowconfigure(0, weight=1)
        self.view_canvas_container.grid_columnconfigure(0, weight=1)
        
        # Debounced Event Binding - Smooths resizing down completely
        self.view_canvas_container.bind("<Configure>", self._debounce_canvas_resize)
