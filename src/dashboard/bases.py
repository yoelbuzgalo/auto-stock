from abc import ABC
import customtkinter as ctk


class BaseDashboard(ctk.CTkFrame,ABC):

    __slots__ = [
        "layout",  # Match property name
        "worker",
        "chart",
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

    def __init__(self,master,fg_color):
        super().__init__(master=master,fg_color=fg_color)

    # Build Chart Panel Components
    def _trigger_chart_update(self, ticker):
        pass
    def _build_chart_panel(self):
        pass
    def _on_search_submit(self):
        pass

    # Update Chart Status
    def update_status_msg(self, text, color="#aaaaaa"):
        pass
    def updates_fear_meter(self, value):
        pass
    def draw_matplotlib_canvas(self, ticker, data):
        pass

    # Build Fear Index Panels
    def _build_fear_panel(self):
        pass

    # Build Sentiment News Panels
    def _build_sentiment_panel(self):
        pass

    # Build Order Execute Panels
    def _build_order_panel(self):
        pass

    # Log transactions
    def log_transaction(self):
        pass
    def delete_transaction(self,log_entry: ctk.CTkFrame):
        pass
    def save_transactions(self):
        pass

    def search(self):
        pass

    # Add news nodes to list
    def add_news_node(self, news):
        pass

    # Remove single items from the list
    def remove_news_node(self, news_id):
        pass

    # Clear all items in a list
    def clear_all_news(self):
        pass

    # Retrieves the associated chart portion
    def get_chart(self):
        pass

    # Retrieves the fear meter
    def get_meter(self):
        pass

    def set_chart(self):
        pass