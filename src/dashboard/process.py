import threading
import yfinance as yf
import pandas as pd
from .bases import BaseDashboard

class DashboardWorker:

    def __init__(self, root: BaseDashboard):
        self.root = root
        self.stock_data = None

    def update(self, ticker="AAPL"):
        self._trigger_chart_update(ticker)

    def _trigger_chart_update(self, ticker):
        threading.Thread(target=lambda: self._fetch_and_render_worker(ticker), daemon=True).start()

    @classmethod
    def download_data(self, ticker="AAPL"):
        try:
            df = yf.download(ticker, period="1mo", interval="1d", progress=False)
            self.stock_data = df
            return df
        except Exception:
            return pd.DataFrame()

    def _fetch_and_render_worker(self, ticker):
        try:
            stock_data = self.download_data(ticker)
            
            if stock_data.empty or 'Close' not in stock_data.columns:
                raise ValueError("Matrix empty")

            # Extract final scalar value
            last_price = float(stock_data['Close'].iloc[-1])
            price_str = f"{last_price:.2f}"
            
            try:
                vix_df = yf.download("^VIX", period="1d", progress=False)
                if isinstance(vix_df.columns, pd.MultiIndex):
                    vix_df.columns = vix_df.columns.droplevel(1)
                vi = float(vix_df['Close'].iloc[-1])
            except Exception:
                vi = 20.0

            try:
                ticker_obj = yf.Ticker(ticker)
                articles = ticker_obj.news[:5]
            except Exception:
                articles = []

            self.root.master.after(0, lambda: self._apply_downloaded_payload(
                ticker, stock_data, vi, articles, price_str
            ))
        except Exception as e:
            self.root.master.after(0, lambda: self.root.get_chart().update_msg(
                "Error lookup failed", color="#ff4d4d"
            ))

    def _apply_downloaded_payload(self, ticker, stock_data, vix_val, articles, price_str):
        # Update inputs safely
        if hasattr(self.root, 'price_input'):
            self.root.price_input.delete(0, "end")
            self.root.price_input.insert(0, price_str)

        chart = self.root.get_chart()
        meter = self.root.get_meter()

        if chart:
            chart.update(ticker, stock_data)
        
        if meter:
            meter.update(vix_val)

        self.root.clear_all_news()
        for news in articles:
            self.root._add_news_node(news)