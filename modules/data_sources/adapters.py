import yfinance as yf

class yFinanceAdapter:

    def __init__(self,data:yf.Ticker):
        self.data = data.options2df().__dict__

    @classmethod
    def get_dict(self,yf_data:yf.Ticker=None):
        if not yf_data:
            yf_data = self.data
            return data_dict
        yf_data = yf_data._options2df()
        data_dict = yf_data.__dict__
        return data_dict
    
    def get_value(self,value):
        '''
        
        For retrieving a specific value without needing the entire dictionary
        
        
        '''

        return self.data.get(value,"NULL")
        
        
    






        
        