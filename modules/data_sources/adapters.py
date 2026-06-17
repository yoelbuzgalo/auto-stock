import yfinance as yf
import pandas as pd
import re
from .market_models import Ohlcv
from src.constants import PRICE_PATTERN,TICKER_PATTERN,NEWS_ARTICLE_LIMIT

class yFinanceAdapter:

    def __init__(self,data:yf.Ticker,period:str,interval:str):
        ohlcv = get_ohlcv(data)
        self._chart_data = get_chart_data(data)
        self._period = period
        self._interval = interval

        
    """
    
    Getters

    
    """

    @property
    def ticker(self):
        return self.ticker
    
    @property
    def price(self):
        return self.price
    
    @property
    def articles(self):
        return self.articles
    
    @property
    def chart_data(self):
        return self.chart_data
    
    @property
    def period(self):
        return self.period
    
    @property
    def interval(self):
        return self.interval
    
    def get_value(self,value):
        '''
        
        For retrieving a specific value without needing the entire dictionary
        
        
        '''

        return self.data.get(value,"NULL")


    """
    
    Setters
    
    
    """

    @ticker.setter
    def set_ticker(self,ticker):
        self.ticker = ticker

    @price.setter
    def set_price(self,price):
        self.price = price

    @articles.setter
    def set_articles(self,news):
        self.articles = news

    @period.setter
    def set_articles(self,period):
        self.period = period

    @interval.setter
    def set_interval(self,interval):
        self.interval = interval

    @chart_data.setter
    def set_chart_data(self,data):
        self.chart_data = data


'''

    Helper method to turn pandas data into a Ohlcv object


'''

def get_ohlcv(data:yf.Ticker):
    
    open = data["Open"].sort_values(by="Date",ascending=False).min()
    high = data["High"].sort_values(by="Date",ascending=False).min()
    low = data["Low"].sort_values(by="Date",ascending=False).min()
    close = data["Close"].sort_values(by="Date",ascending=False).min()
    volume = data["Volume"].sort_values(by="Date",ascending=False).min()

    return Ohlcv(open,high,low,close,volume)

'''

    Helper method to turn a Ticker object into usable chart data


'''

def get_chart_data(data:yf.Ticker):
    df = data.history()
    return df

        

        
        
        
    






        
        