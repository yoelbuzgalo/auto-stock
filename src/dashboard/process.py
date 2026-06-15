import threading
from .bases import BaseDashboard
import yfinance as yf
import re

PRICE_PATTERN=r"\s+(\d+\.\d+)"

class DashboardWorker:

    def __init__(self,root:BaseDashboard):
        self.root = root
        self.update()

    def update(self,ticker="AAPL"):
        self._trigger_chart_update(ticker)
        self._fetch_and_render_worker(ticker)

    def _trigger_chart_update(self, ticker):
        self.root.get_chart().update(ticker)
        threading.Thread(target=lambda: self._fetch_and_render_worker(self.root,ticker), args=(ticker), daemon=True).start()

    
    def _fetch_and_render_worker(self, ticker):
        try:
            # After retrieving the data, get the most recently available price
            stock_data = yf.download(ticker, period="1mo", interval="1d", progress=False)
            prices = stock_data[("Close",ticker)]
            data = prices.head(1).to_string()
            price = re.search(PRICE_PATTERN,data).group(1)

            # Insert it into the order panel for convenience
            self.root.price_input.delete(0,"end")
            self.root.price_input.insert(0,price)
            
            vi = yf.Ticker("^VIX").history(period="1d")["Close"].iloc[-1]
            vi = round(vi, 2)
            ticker_obj = yf.Ticker(ticker)
            articles = ticker_obj.news[:5]
            
            if stock_data.empty or len(stock_data) < 2:
                raise ValueError("Invalid symbol matrices returned")

            # Consolidated singular execution block pushed to main event loop
            self.root.master.after(0, lambda: self._apply_downloaded_payload(ticker, stock_data, vi, articles))
        except Exception as e:
            self.root.master.after(0, lambda: self.root._update_status_msg(f"Error lookup failed: ", "#ff4d4d"))

    def _apply_downloaded_payload(self, ticker, stock_data, vix_val, articles):
        """Unified UI updates executed purely inside the safe main process thread."""
        self.root._draw_matplotlib_canvas(ticker, stock_data)
        self.root._update_fear_meter(vix_val)
        self.root.clear_all_news()
        for news in articles:
            self.root._add_news_node(news)
