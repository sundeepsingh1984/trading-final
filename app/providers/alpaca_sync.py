import os,sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import alpaca_trade_api as Api
import config as Config
import pandas as pd
import time

import asyncio

class Alpaca:

    def __init__(self):

        self.key = Config.ALPACA_API_KEY
        self.secret = Config.ALPACA_SECRET_KEY
        self.url = Config.ALPACA_API_URL

        self._CNX_FLAG=False



    



    def connect(self):
        try:
            self.connection = Api.REST(self.key, self.secret, self.url)
            print("Connection established With Alpaca")
            self._CNX_FLAG=True
            self.event_loop=asyncio.get_event_loop()
        


        except Exception as e:
            print("Error Connecting to Alpaca")
            raise e

    


    def getAssetList(self):

        try:
            account_info = self.connection.get_account()
            if account_info.status == "ACTIVE":
                self.assetList = self.connection.list_assets()
                return self.assetList

        except Exception as e:
            raise e

    







    def getStockPrices(self, symbols=None, timeframe='1D', start=None, end=None, limit=None, output_as=None):
        '''
            Send an collection of stock symbols to the API in order to obtain theassociated prices.
            ----------
            Parameters
            symbol : list() - A list of stock symbols that conform to the Alpaca API request structure.
            timeframe:str - Possible values are 1D,1Min,5Min,15Min,day
            start :ISO Format datetime str()
            end :ISO Format datetime str()
            output_as:str allowed value=dataframe
            limit:Int
            timeframe:str
            Returns: DATAFRAME of stockprices
        '''

        if symbols == None:
            import Helper.helpers as Helper
            self.getAssetList()
            symbol_list = [getattr(asset, "symbol") for asset in self.assetList]

            stock_list = list(Helper.divide_chunks(symbol_list, 50))
        
        else:

            stock_list = symbols

        try:
            if output_as == None:
                stock_prices = [
                    self.connection.get_barset(symbols, timeframe=timeframe, limit=limit, start=start, end=end) for
                    symbols in stock_list]
            else:
                stock_prices = [
                    self.connection.get_barset(symbols, timeframe=timeframe, limit=limit, start=start, end=end).df for
                    symbols in stock_list]

            return stock_prices

        except Exception as e:
            raise e






    







alpaca =Alpaca()

alpaca.connect()

 

st=time.perf_counter()

data=alpaca.getStockPrices(output_as="dataframe")

print(f"time taken {time.perf_counter()-st}")


dataframe=pd.concat(data)


print(dataframe.tail())

print(dataframe.info())


