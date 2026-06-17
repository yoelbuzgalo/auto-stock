import customtkinter as ctk

from .ai_panel import AIPanel
from .chart import DashboardChart
from .fear import FearMeter
from .bases import BaseDashboard, BaseLayout
from src.constants import *


class DashboardLayout(BaseLayout):

    def __init__(self, root: BaseDashboard):
        self.root = root
        self._configure_grid_layout()
        self._init_dashboard_panels()
    
    def _configure_grid_layout(self):
        self.root.grid_columnconfigure(0, weight=4, uniform=COLS)
        self.root.grid_columnconfigure(1, weight=2, uniform=COLS)
        self.root.grid_columnconfigure(2, weight=2, uniform=COLS)
        self.root.grid_rowconfigure(0, weight=1, uniform=ROWS)
        self.root.grid_rowconfigure(1, weight=1, uniform=ROWS)

    def _init_dashboard_panels(self):
        self.root._chart = DashboardChart(self.root)
        self.root.meter_bar = FearMeter(self.root)
        self.root.copilot = AIPanel(self.root,self.root)
        self.root._build_order_panel()
        self.root._build_sentiment_panel()


