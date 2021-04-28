import os,sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))



from Helper.helpers import divide_chunks

import alpaca_trade_api as Api
import config as Config
import pandas as pd
from functools import wraps,partial
import time

import asyncio

class Alpaca:

    def __init__(self):

        self.key = Config.ALPACA_API_KEY
        self.secret = Config.ALPACA_SECRET_KEY
    
       
        self.url = Config.ALPACA_API_URL
        self.event_loop=asyncio.get_event_loop()
        self._CNX_FLAG=False
        
    


    def async_wrap(self,func):
        @wraps(func)
        async def run(*args, loop=None, executor=None, **kwargs):
            if self.event_loop is None:
                self.event_loop = asyncio.get_event_loop()
            pfunc = partial(func, *args, **kwargs)
            return await self.event_loop.run_in_executor(executor, pfunc)
        return run 












    async def convert_to_async(self):

        self.async_account=self.async_wrap(self._conn.get_account)
        self.async_asset=self.async_wrap(self._conn.list_assets)
        self.async_bars=self.async_wrap(self._conn.get_barset)


    



    

    async def connect(self):

        try:
            self._conn=Api.REST(self.key,self.secret,self.url)
            self._CNX_FLAG=True
            await self.convert_to_async()

            print("Connection Established With Alpaca")


        except Exception as e:

            print("Error Connecting to Alpaca")
            raise e







    




    async def get_security_list(self):

        if not self._CNX_FLAG:

            await self.connect()

        
        account_details=await self.async_account()

        if account_details.status == "ACTIVE":

            assets=await self.async_asset()
            
            return assets






    async def get_prices(self, stock_list:list=[] , timeframe="1D", limit = None, start=None, end=None ):

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

        if not self._CNX_FLAG:

            await self.connect()


        

        if len(stock_list) != 0:

            tasks=[asyncio.create_task(self.request_prices(stock,timeframe,limit,start,end)) for stock in stock_list]


        else:

            
            stocks=await self.get_security_list()


            tickers=[getattr(stock,"symbol") for stock in stocks]


            chun_tickers=divide_chunks(tickers, 200)


            tasks=[asyncio.create_task(self.request_prices(stock,timeframe,limit,start,end)) for stock in chun_tickers]





        try:

            prices=await asyncio.gather(*tasks)

            return prices


 
        except Exception as e:

            raise e





















            


        


        
                    



    async def request_prices(self,stock,timeframe,limit,start,end):

        try:

            price_data=await self.async_bars(stock,timeframe,limit,"2007-01-01",end)
            
            return price_data


        except Exception as e:

            raise e

    


    



    












    async def getTradableAndActiveStocks(self):

        try:
            asset_list=await self.get_security_list()


            

        except Exception as e:

            raise e


        alpaca_dict = [{"ticker":getattr(asset, "symbol"),
                     "exchange":getattr(asset, "exchange"), 
                     "asset":getattr(asset, "name"),
                     "id":getattr(asset ,"id"),} for asset in asset_list if asset.status == 'active' and asset.tradable]






        return alpaca_dict
        


    
    



        















# alpaca =Alpaca()
# start=time.perf_counter()
# detials=alpaca.get_prices(["AAPL","XOM"])
# print(f"time taken{ time.perf_counter()-start}")

# # asset_list =alpaca.getAssetList()
# print(asset_list)
# print(len(asset_list))

