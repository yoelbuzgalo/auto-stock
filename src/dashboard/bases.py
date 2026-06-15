from abc import ABC
import customtkinter as ctk


class BaseDashboard(ctk.CTkFrame,ABC):

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