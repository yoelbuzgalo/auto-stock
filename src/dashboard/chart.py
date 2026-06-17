import customtkinter as ctk
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import tkinter as tk

from .bases import BaseDashboard
from src.constants import *


class DashboardChart(ctk.CTkFrame):
    """
    Manages the visualization panel displaying market chart tracking metrics
    and handles responsive canvas layout updates.
    """

    def __init__(self, root: BaseDashboard):
        """
        Initializes the chart dashboard frame, internal chart state, and resize debounce state.

        Args:
            root (BaseDashboard): Parent dashboard controller instance.
        """
        super().__init__(root, fg_color="transparent")

        self.root = root
        self.active_canvas_widget = None
        self._data = None

        self._resize_timer = None
        self._last_canvas_size = None
        self._pending_canvas_size = None

        self._init()

    def _init(self):
        """
        Builds the chart search controls, status label, and responsive Matplotlib canvas container.
        """
        self.grid_columnconfigure(0, weight=1)

        search_container = ctk.CTkFrame(self, fg_color="transparent")
        search_container.grid(
            row=0,
            column=0,
            padx=PADDING_CHART_INNER_X,
            pady=(PADDING_CHART_PANEL_X * 2, PADDING_CHART_INNER_Y),
            sticky="ew"
        )

        self._chart_search_input = ctk.CTkEntry(
            search_container,
            placeholder_text="Search Ticker (e.g., NVDA, TSLA)"
        )
        self._chart_search_input.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, PADDING_CHART_PANEL_X),
            pady=(0, PADDING_CHART_PANEL_X)
        )
        
        self._chart_search_input.bind("<Return>", lambda event: self.root.search())

        search_btn = ctk.CTkButton(
            search_container,
            text="Search",
            command=lambda: self.root.search()
        )
        search_btn.pack(side="right", pady=(0, PADDING_CHART_PANEL_X))

        self.chart_status_lbl = ctk.CTkLabel(
            self,
            text="System Ready",
            font=(FONT_FAMILY, int(FONT_SIZE_SMALL), "italic"),
            text_color="#aaaaaa",
            fg_color="transparent"
        )
        self.chart_status_lbl.grid(
            row=1,
            column=0,
            padx=PADDING_CHART_INNER_X,
            pady=(0, PADDING_CHART_INNER_Y),
            sticky="ew"
        )

        self.view_canvas_container = ctk.CTkFrame(self, fg_color="transparent")
        self.view_canvas_container.grid(
            row=2,
            column=0,
            padx=PADDING_CHART_PANEL_X,
            pady=PADDING_CHART_PANEL_Y,
            sticky="nsew"
        )

        self.view_canvas_container.grid_rowconfigure(0, weight=1)
        self.view_canvas_container.grid_columnconfigure(0, weight=1)
        self.view_canvas_container.bind("<Configure>", self._debounce_canvas_resize)

        self.grid(
            row=0,
            column=0,
            rowspan=2,
            padx=PADDING_CHART_PANEL_X,
            pady=PADDING_CHART_PANEL_Y,
            sticky="nsew"
        )

    def _debounce_canvas_resize(self, event):
        """
        Defers chart resizing until the canvas container stops changing size.

        Args:
            event (tk.Event): Tkinter configure event containing the latest widget width and height.
        """
        if self.active_canvas_widget is None:
            return

        w, h = event.width, event.height

        if w < int(CHART_MIN_WIDTH) or h < int(CHART_MIN_HEIGHT):
            return

        last_size = self._last_canvas_size
        if last_size is not None:
            last_w, last_h = last_size
            if abs(w - last_w) < 4 and abs(h - last_h) < 4:
                return

        self._pending_canvas_size = (w, h)

        if self._resize_timer is not None:
            try:
                self.after_cancel(self._resize_timer)
            except tk.TclError:
                pass

        self._resize_timer = self.after(
            int(DEBOUNCE_RESIZE_MS),
            self._run_deferred_resize
        )


    def _run_deferred_resize(self):
        """
        Executes the latest pending resize request after the debounce delay.
        """
        self._resize_timer = None

        if self.active_canvas_widget is None:
            return

        if self._pending_canvas_size is None:
            return

        w, h = self._pending_canvas_size
        self._last_canvas_size = (w, h)

        self.execute_deferred_resize(w, h)


    def execute_deferred_resize(self, w, h):
        """
        Resizes the Matplotlib figure and Tk canvas using configured chart constants.

        Args:
            w (int): Available container width in pixels.
            h (int): Available container height in pixels.
        """
        fig = getattr(self.root, "current_fig", None)

        if fig is None or self.active_canvas_widget is None:
            return

        chart_w = int(w * float(CHART_WIDTH_RATIO))
        chart_h = int(h * float(CHART_HEIGHT_RATIO))

        chart_w = min(chart_w, int(CHART_MAX_WIDTH))
        chart_h = min(chart_h, int(CHART_MAX_HEIGHT))

        if chart_w < int(CHART_MIN_WIDTH) or chart_h < int(CHART_MIN_HEIGHT):
            return

        dpi = fig.get_dpi()

        fig.set_size_inches(chart_w / dpi, chart_h / dpi, forward=True)

        fig.subplots_adjust(
            left=float(CHART_MARGIN_LEFT),
            right=float(CHART_MARGIN_RIGHT),
            top=float(CHART_MARGIN_TOP),
            bottom=float(CHART_MARGIN_BOTTOM)
        )

        canvas_widget = self.active_canvas_widget.get_tk_widget()
        canvas_widget.configure(width=chart_w, height=chart_h)
        self.active_canvas_widget.draw_idle()

    def update_chart_msg(self, text, color):
        """
        Updates the chart status label text and color.

        Args:
            text (str): Message to display.
            color (str): Text color value.
        """
        self._update_status_msg(text, color)

    def draw_matplotlib_canvas(self, ticker, data):
        """
        Creates and displays a responsive Matplotlib line chart for the provided ticker data.

        Args:
            ticker (str): Stock ticker symbol shown in the chart title.
            data (pd.Series): Historical price series plotted on the chart.
        """
        if self.active_canvas_widget:
            self.active_canvas_widget.get_tk_widget().destroy()
            self.active_canvas_widget = None

        fig, ax = plt.subplots(
            figsize=(float(MATPLOTLIB_FIG_W), float(MATPLOTLIB_FIG_H)),
            dpi=int(CANVAS_DEFAULT_DPI_MIN),
            facecolor="#2b2b2b",
            constrained_layout=False
        )

        ax.set_facecolor("#2b2b2b")
        ax.plot(data, color="#1f538d", linewidth=int(MATPLOTLIB_LINEWIDTH))

        ax.xaxis.set_major_locator(
            mdates.DayLocator(interval=int(MATPLOTLIB_INTERVAL_DAYS))
        )
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))

        ax.set_title(
            f"{ticker} - Last 30 Days",
            color=WHITE,
            fontsize=int(FONT_SIZE_NORMAL),
            fontweight="bold"
        )

        ax.tick_params(colors="white", labelsize=int(MATPLOTLIB_LABELSIZE))
        ax.grid(True, color="#444444", linestyle="--", linewidth=0.5)

        for label in ax.get_xticklabels():
            label.set_rotation(30)
            label.set_ha("right")

        canvas = FigureCanvasTkAgg(fig, master=self.view_canvas_container)

        self.active_canvas_widget = canvas
        self.root.active_canvas_widget = canvas
        self.root.current_fig = fig

        if hasattr(self.root, "ticker_input"):
            self.root.ticker_input.delete(0, "end")
            self.root.ticker_input.insert(0, ticker)

        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=0, column=0)

        self.view_canvas_container.grid_rowconfigure(0, weight=1)
        self.view_canvas_container.grid_columnconfigure(0, weight=0)

        self.update_idletasks()

        w = self.view_canvas_container.winfo_width()
        h = self.view_canvas_container.winfo_height()

        if w > 100 and h > 100:
            self.execute_deferred_resize(w, h)
        else:
            canvas.draw_idle()

        plt.close(fig)

    def update(self, ticker, data, articles=None):
        """
        Normalizes chart data, redraws the price chart, and refreshes news article nodes.

        Args:
            ticker (str): Stock ticker symbol.
            data (pd.DataFrame | pd.Series): Market price data.
            articles (list | None): Optional news article collection.
        """
        if (
            hasattr(data, "columns")
            and hasattr(data.columns, "levels")
            and len(data.columns.levels) > 1
        ):
            data.columns = data.columns.droplevel(1)

        chart_series = (
            data["Close"]
            if hasattr(data, "columns") and "Close" in data.columns
            else data
        )

        self.draw_matplotlib_canvas(ticker, chart_series)

        if hasattr(self.root, "clear_all_news"):
            self.root.clear_all_news()

        if articles:
            for news in articles:
                if hasattr(self.root, "_add_news_node"):
                    self.root._add_news_node(news)

    def _update_status_msg(self, text, color=WHITE):
        """
        Applies status text and color updates to the chart status label.

        Args:
            text (str): Status message.
            color (str): Label text color.
        """
        if hasattr(self, "chart_status_lbl"):
            self.chart_status_lbl.configure(text=text, text_color=color)

    @property
    def ticker(self):
        """
        Retrieves the current ticker query from the chart search field.

        Returns:
            str: Uppercase ticker symbol.
        """
        return self._chart_search_input.get().strip().upper()

    @property
    def data(self):
        """
        Retrieves the chart data currently stored by the dashboard chart.

        Returns:
            Any: Current chart data object.
        """
        return self._data
    
    @property
    def input(self):
        """
        
        Retrieves the search input
        
        
        """

        return self._chart_search_input.get()
    
    @property
    @input.setter
    def set_input(self,value):
        
        self._chart_search_input.delete(0,"end")
        self._chart_search_input.insert(0,value)

    
