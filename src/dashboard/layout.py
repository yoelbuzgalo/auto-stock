from .bases import BaseDashboard

class DashboardLayout:

    def __init__(self,root:BaseDashboard):
        self.root = root
    
    def _configure_grid_layout(self):
        self.root.grid_columnconfigure(0, weight=3, uniform="main_cols")
        self.root.grid_columnconfigure(1, weight=2, uniform="main_cols")
        self.root.grid_columnconfigure(2, weight=2, uniform="main_cols")
        self.root.grid_rowconfigure(0, weight=1, uniform="rows")
        self.root.grid_rowconfigure(1, weight=1, uniform="rows")

    def _init_dashboard_panels(self):
        self.root._build_chart_panel()
        self.root._build_fear_panel()
        self.root._build_sentiment_panel()
        self.root._build_order_panel()
