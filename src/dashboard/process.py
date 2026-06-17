import threading
import yfinance as yf
import re
import pandas as pd
import queue as q
import traceback
from modules.data_sources import yFinanceAdapter
from .bases import BaseDashboard, BaseThread, BaseWorker
from concurrent.futures import ThreadPoolExecutor, Future
from src.constants import *

# class DashboardThread(BaseThread, threading.Thread):

#     def __init__(self, root: BaseDashboard, queue: q.Queue, target, args=()):
#         threading.Thread.__init__(self)
#         self.root = root
#         self.target = target
#         self.args = args
#         self.result = None

#     def run(self):
#         if self.target:
#             self.result = self.target(*self.args)
        
#     def join(self, timeout=None, *args, **kwargs):
#         super().join(timeout)
#         return self.result


class DashboardWorker(BaseWorker, ThreadPoolExecutor):

    def __init__(self, root: BaseDashboard, max_workers=None, thread_name_prefix='', *args, **kwargs):
        self.root = root
        self.yf_cache = None
        self.vix_cache = None
        ThreadPoolExecutor.__init__(self, max_workers=max_workers, thread_name_prefix=thread_name_prefix, *args, **kwargs)

    def submit(self, target, *args, **kwargs):
        return super().submit(target, *args, **kwargs)

    def shutdown(self, wait=True, cancel_futures=False):
        super().shutdown(wait=wait, cancel_futures=cancel_futures)

    def update(self):
        chart = self.root.chart
        input_widget = self.root.price_input
       
        ticker_input = "AAPL"
        if chart and hasattr(chart, "ticker"):
            ticker_input = chart.ticker
        elif input_widget:
            ticker_input = input_widget.get().strip().upper()

        if not ticker_input:
            return

        super().submit(self._async_update_pipeline, ticker_input, input_widget)

    def _async_update_pipeline(self, ticker_input, input_widget):
        gui_queue = self.root.queue
        chart = self.root.chart

        try:
            gui_queue.put(lambda: chart.update_chart_msg(
                f"Fetching data for {ticker_input}...", color=GREEN
            ))

            ticker_obj = yf.Ticker(ticker_input)
            vix_obj = yf.Ticker("^VIX")

            stock_data = ticker_obj.history(period="30d", interval="1d")
            vix_data = vix_obj.history(period="1d")

            if stock_data.empty:
                raise ValueError(f"No historical market data found for symbol: {ticker_input}")

            latest_vix = vix_data['Close'].iloc[-1] if not vix_data.empty else 20.0
            latest_price = stock_data['Close'].iloc[-1]

            self.yf_cache = stock_data
            self.vix_cache = vix_data

           
            articles = getattr(ticker_obj, "news", None)

            gui_queue.put(lambda: apply_downloaded_payload(
                price_input=input_widget,
                ticker=ticker_input,
                stock_data=stock_data,
                vix_val=latest_vix,
                latest_price=latest_price,
                chart=chart,
                meter=self.root.meter,
                articles=articles
            ))

            gui_queue.put(lambda: chart.update_chart_msg(
                f"Fetching data for {ticker_input}...", color=GREEN
            ))

        except Exception as e:
            print(traceback.format_exc())
            error_msg = str(e)
            if chart:
                gui_queue.put(lambda: chart.update_chart_msg(error_msg, color=RED))


def apply_downloaded_payload(price_input, ticker, stock_data: pd.DataFrame, vix_val, latest_price, chart, meter, **kwargs):
    if price_input and hasattr(price_input, "winfo_exists") and price_input.winfo_exists():
        price_input.delete(0, "end")
        price_input.insert(0, f"{latest_price:.2f}")

    if chart:
        articles = kwargs.get("articles")
        try:
            chart.update(ticker, stock_data, articles=articles)
        except TypeError:
            chart.update(ticker, stock_data)
        
    if meter:
        try:
            meter.update(vix_val)
        except Exception:
            pass