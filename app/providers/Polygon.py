import alpaca_trade_api as Api
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config as Config
import pandas as pd
import requests, time, math
import asyncio,aiohttp
import typing
import datetime

import threading 


class Polygon:

   



    def __init__(self):

        self.key = Config.API_KEY_POLY

        self.secret = Config.ALPACA_SECRET_KEY
        self.url = Config.API_URL_SETH
        self.DATA = []
        self.TICKER_LIST = []
        self.PriceData=[]
        self.event_loop=asyncio.get_event_loop()

        try:

            self.event_loop.run_until_complete(self.fetch_tickers_async())

        except Exception as e:

            raise e





    


    # function generates the list of url's
    async def generate_url(self, symbolList,url_format):
        """ This function creates a list of urls Parameters:
        symbolList(list): list of tickers
        Returns: url(list) a list of url's """
        return [url_format.format(symbol, self.key) for symbol in symbolList]


   

    # function takes urls as an argument requests the data
   

    async  def request_data(self, url,data_type="tickers",timeframe=None,unadjusted=None):

        """ 
        This function retrieves ticker details and adds them to global variable DATA
        Parameters: urls (list): list of url strings
        Returns: None 

        """

        print(url)
        async with aiohttp.ClientSession(trust_env=True,) as session:
            
            try:
                async with session.get(url) as resp:
                    

                    rs=await resp.json()

                    if resp.status == 200:

                        data=await resp.json()
                        
                   

                        if data_type == "tickers":
                            
                            self.TICKER_LIST.append(pd.DataFrame.from_dict(data["tickers"]))
                            
                            
                            
                            
                        elif data_type == "priceHist":
                            
                            
                            
                            
                          
                            df=pd.DataFrame.from_dict(data["results"])
                            df["ticker"]=data["ticker"]
                            
                            
                            
                            lst_rec=df.tail(1)
                          
                            
                           
                           
                            
                            
                            
                            
                            
                          

                           






                       
                            ts=lst_rec['t'].values[0]
                        
                            
                            
                        
                        
                            dt=datetime.datetime.utcfromtimestamp(int(ts/1000.0)).strftime('%Y-%m-%d')

                            
                      
                            
                            
                            
                         

                            today=datetime.datetime.today().strftime('%Y-%m-%d')
                            
                            self.PriceData.append(df)
                            
                             

                            if str(today) > str(dt):
                                
                               
                                
                                print(dt)
                                
                                
                                
                                print(today)


                                url_new=await self.create_aggregate_url(data["ticker"],str(dt) ,str(today), timeframe, unadjusted)
                                
                                await self.request_data(url_new,"priceHist",timeframe,unadjusted)





                            
                            
                        
                            
                            
                        elif data_type=="tickers_vx":
                            if 'next_page_path' in data:
                                
                                
                                base_url="https://api.polygon.io"
                                
                                url=base_url+data["next_page_path"]+"&apiKey={}"
                                
                                
                                url=url.format(self.key)
                                
                                
                                await self.request_data(url,"tickers_vx")
                                
                                
                                self.DATA.append(data["results"])
                                
                                
                                
                            else:
                                
                             
                                
                                return[data["results"]]
                            
                            
                            
                            
                                
                           
                                
                                
                           
                                
                            
                                
                         
                                
                               
                            
                            
                           
                            
                        else :

                            return data

                    else:
                        print(f"There was some error getting data responded with status code {resp.status}")
            

            except Exception as  e:

                if e.__class__==aiohttp.client_exceptions.ClientConnectionError:

                    pass


        

    # this is a async function that  acqures the ticker details  usinng asyncio taska
    async def ticker_details(self, symbols):
        """
        This function implements   retrieves the details of the ticker using the function request_data
        Parameters:symbols(list): list of tickers
        Returns:None

        """

        urls = await self.generate_url(symbols,Config.POLYGON_TICKER_DETAILS)
        tasks=[asyncio.create_task(self.request_data(url,"other")) for url in urls]


        try:
            data=await asyncio.gather(*tasks)


            data=list(filter(None, data)) 
  



            return data

        except Exception as e:

            print(f"error accured while fetching ticker_details")

            raise e
















    # This function retreives the tickers 


    async  def fetch_tickers_async(self):

        """

        DESCRIPTION
        -----------
        ASync function that uses asyncio tasks to fetch the tickers in asynch manner.


         Parameters
        ----------
        None

        Returns
        -------
        NOne

        """

        int_url = Config.POLYGON_TICKERS_URL.format(1, self.key)
        



        async with aiohttp.ClientSession(trust_env=True) as session:
            try:
                data= await session.get(int_url)
                rs=await data.json()
                

                if data.status==200:




                    data=await data.json()


                    

                    self.TICKER_LIST.append(pd.DataFrame.from_dict(data["tickers"]))

                    pages=math.ceil(int(data["count"]))/int(data["perPage"])


                    urls=[Config.POLYGON_TICKERS_URL.format(page,self.key) for page in range(2, int(pages))]

                    tasks=[asyncio.create_task(self.request_data(url)) for url in urls]
                    



                    try:
            
                        await asyncio.gather(*tasks)

                    
                    except Exception as e:

                        if e.__class__ == "ClientConnectorError":

                            pass



                        else:

                            raise e


                else:


                    print(f"error connecting to provider error code {data.status}")



                    raise Exception





            except Exception as e:

                raise e



        
       


        
        



    async def get_tickers(self):
        """
        DESCRIPTION
        -----------
        Function Fetches the list of ticker from polygon

        PARAMETERS
        -----------------------------------------

        None
        
        RETURNS
        ----------------------------------------------------------


        df:  list of tickers from alpaca 

        """



        try:

            await self.fetch_tickers_async()
            
            df=pd.concat(self.TICKER_LIST,sort=True)
            
            return df



        except Exception as e:



            raise e




    










        #function to create the aff


    async def create_aggregate_url(self,ticker,from_date,to_date,timespan,unadjusted,limit=50000):
        """


        
        ticker(str):ticker list

        
        from_data (Date str):date string in ISO format yyyy-mm-dd.date form which agreegated data is required 

        
        to_date (Date str):date string in ISO format yyyy-mm-dd date upto which aggregated data is required 


        timespan(str): possible values are as in list ["day","minute","hour","week","month","quarter","year"]


        unadjusted(str Boolean):True for unadjusted data False for adjusted 



        limit(number):no of aggregates








        """


        return Config.POLYGON_AGGS_URL.format(ticker,timespan,from_date,to_date,unadjusted,limit,self.key)







    











    async def getPrices(self,tickers,date_from=pd.datetime.now().date(),to_date=pd.datetime.now().date(),timespan="minute",unadjusted=True):


        """

        ----------------------------------------
        PARAMETERS
        -----------------------------------------

        ticker(str ):ticker list

        
        from_data (Date str):date string in ISO format yyyy-mm-dd.date form which agreegated data is required 

        
        to_date (Date str):date string in ISO format yyyy-mm-dd date upto which aggregated data is required 


        timespan(str): possible values are as in list ["day","minute","hour","week","month","quarter","year"]


        unadjusted(str Boolean):True for unadjusted data False for adjusted 


        -----------------------------------------------------------
        RETURNS
        ----------------------------------------------------------


        data (json list): json list of bars 


        """


        if len(tickers)>1 and type(tickers) == "List":


            urls=[await self.create_aggregate_url(ticker, date_from, to_date, timespan, unadjusted) for ticker in tickers ]


            try:


                tasks=[asyncio.create_task(self.request_data(url,"other") for url in urls)]



                data=await asyncio.gather(*tasks)




            except Exception as e:


                raise e




        else:



            url=await self.create_aggregate_url(tickers, date_from, to_date, timespan, unadjusted)

            try:

                data=await self.request_data(url,"other")


            except Exception as e:


                raise e 



        return data


    async def getPrices(self,tickers,date_from=pd.datetime.now().date(),to_date=pd.datetime.now().date(),timespan="minute",unadjusted=True):


#     ----------------------------------------
#     PARAMETERS
#     -----------------------------------------

#     ticker(str ):ticker list
#     from_data (Date str):date string in ISO format yyyy-mm-dd.date form which agreegated data is required 
#     to_date (Date str):date string in ISO format yyyy-mm-dd date upto which aggregated data is required 
#     timespan(str): possible values are as in list ["day","minute","hour","week","month","quarter","year"]
#     unadjusted(str Boolean):True for unadjusted data False for adjusted 
#     -----------------------------------------------------------
#     RETURNS
#     ----------------------------------------------------------
#     data (json list): json list of bars 




    
        if isinstance(tickers , typing.List):
        
          
        
            details=await self.ticker_details(tickers)
            df=pd.DataFrame(details)
            urls=[]
            if not df.empty:
                url_det=[await self.create_aggregate_url(row["symbol"], row["listdate"], to_date, timespan, unadjusted) for index,row in df.iterrows()]
                [urls.append(url) for url in url_det]


            with_det_lst=df["symbol"].to_list()


            print("tickers with detaisl")


            print(with_det_lst)

            no_det=[ticker for ticker in tickers if ticker not in with_det_lst]




            print(no_det)








            if len(no_det) > 0:
                
                no_det_url=[await self.create_aggregate_url(sym, "2004-01-01", to_date, timespan, unadjusted) for sym in no_det]
                [urls.append(url) for url in no_det_url]
            

            





            try:
                tasks=[asyncio.create_task(self.request_data(url,"priceHist",timespan,unadjusted)) for url in urls]
                
                
                
            
                
                
                
                data=await asyncio.gather(*tasks)

            except Exception as e:

                raise e

        else:
           
            
            
            
            
            details=await self.ticker_details([tickers])
            
            
            
            
            
            
            
            
            

            url=await self.create_aggregate_url(tickers,details[0]["listdate"], to_date, timespan, unadjusted)

            try:

                data=await self.request_data(url,"prices")


            except Exception as e:


                raise e 

        return data
    
    
    
    async def getTickerVX(self,symbol=None):
        
        """
        DESCRIPTION
        -----------
        
        this function gathers the Tickers using VX endpoints.
        
        ----------------------------------------
        PARAMETERS
        -----------------------------------------

        symbol(str ):ticker list
        
        -----------------------------------------------------------
        RETURNS
        ----------------------------------------------------------
        data (dict): json list of bars 

        """
        
        if symbol:
            
            
            
            url=Config.POLYGON_VX_TICKERS.format(symbol,self.key)
            
            data = await self.request_data(url,data_type="tickers_vx")
            
            
            return data
            
            
            
            
           
            
        else:
            
            
            url=Config.POLYGON_VX_TICKERS_FULL.format(self.key)
            
            data=await self.request_data(url,data_type="tickers_vx")
            
            
            
            
    async def getSplits(self,symbol=None):
        
        
        
            
        """
        DESCRIPTION
        -----------
        
        this function gathers the split data from poly gon if parameter is provided it gathers the data for a particular symbols 
        otherwise, gathers the historical split for all stocks.
        
        ----------------------------------------
        PARAMETERS
        -----------------------------------------

        symbol(str ):ticker list
        
        -----------------------------------------------------------
        RETURNS
        ----------------------------------------------------------
        data (dict): json list of bars 

        """
        
        
        if symbol:
            
            
            url=Config.POLYGON_SPLIT_URL.format(symbol,self.key)
            data=await self.request_data(url,data_type="other")
            
            return(data)
        
        
        else:
            self.TICKER_LIST.clear()
            
            tickers=await self.get_tickers()
            
            
            df=pd.concat(self.TICKER_LIST)
            
            
            df=df[df["market"].isin(["STOCKS"])]
            
            
            sym_list=df["ticker"].to_list()
            
            
            
            urls=[Config.POLYGON_SPLIT_URL.format(symbol,self.key) for symbol in sym_list]
            
            
            
            task_list=[asyncio.create_task(self.request_data(url,"splits")) for url in urls]
            
            
            
            
            try:
                
                data= await asyncio.gather(*task_list)
                
                
                return data
                
                
            except Exception as e:
                
                
                raise e
                
                
                
    async def getTrades(self,date_from,symbol=None):
        
        
            
        """
        DESCRIPTION
        -----------
        
        this function gathers the Trade data from Polygon.if no symbol provides gathers the trades for all stocks provided by polygon 
        
        ----------------------------------------
        PARAMETERS
        -----------------------------------------

        date_form (str):iso date string .start of date form where onwards we need trades 
        symbol(str ):ticker list
        
        
        -----------------------------------------------------------
        RETURNS
        ----------------------------------------------------------
        data (dict): json list of bars 

        """
        
        
        if symbol:
            
            
            tickerDetail=await self.ticker_details(symbol)
            url=Config.POLYGON_TRADES_URL.format(symbol,date_from,self.key)
            data=await self.request_data(url,"others")
            return data
        
        
        
        
        else:
            
            tickers=await self.get_tickers()
            df=pd.concat(self.TICKER_LIST)
            df=df[df["market"].isin(["STOCKS"])]
            sym_list=df["ticker"].to_list()
            urls=[Config.POLYGON_TRADES_URL.format(symbol,date_from,self.key) for symbol in sym_list]
            task_list=[asyncio.create_task(self.request_data(url,"splits")) for url in urls]
            try:
                data= await asyncio.gather(*task_list)
                return data
            
            except Exception as e:
                raise e
                
                
    async def getQuotes(self,from_date="2007-03-01",symbol=None):
        
        
                    
        """
        DESCRIPTION
        -----------
        
        this function gathers the Quotes data from Polygon.if no symbol provides gathers the Quotes for all stocks provided by polygon 
        
        ----------------------------------------
        PARAMETERS
        -----------------------------------------

        from_date (str):iso date string .start of date form where onwards we need trades 
        symbol(str ):ticker list
        
        
        -----------------------------------------------------------
        RETURNS
        ----------------------------------------------------------
        data (dict): json list of bars 

        """
        
        
        if symbol:
            
            url=Config.POLYGON_QUOTES_URL.format(symbol,from_date,self.key)
            data=await self.request_data(url,"others")
            return data
        
        
        else:
            
            if not self.TICKER_LIST:
                
                tickers=await self.get_tickers()
            
            
            df=pd.concat(self.TICKER_LIST)
            
            df=df[df["market"].isin(["STOCKS"])]
            
            sym_list=df["ticker"].to_list()
            
            urls=[POLYGON_QUOTES_URL.format(symbol,from_date,self.key) for symbol in sym_list]
            
            task_list=[asyncio.create_task(self.request_data(url,"splits")) for url in urls]
            
            
            
            try:
                data= await asyncio.gather(*task_list)
                return data
                
                
            except Exception as e:
                raise e
                


    def get_bulk_prices(self):


        symbols=self.TICKER_LIST

        df=pd.concat(symbols)



        

            
            
                
                
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
          
            
            
            
            
            
            
            
            
            
            
            
            
            
            


















obj=Polygon()



df=pd.concat(obj.TICKER_LIST)




tickers=df["ticker"].to_list()




loop=asyncio.get_event_loop()
st=time.perf_counter()
data=loop.run_until_complete(obj.getPrices(["BKE"]))
df=pd.concat(obj.PriceData)
df.to_csv("bke.csv.gz", compression='gzip')

print(f"time taken is{time.perf_counter()-st}")


        


       



      






        
        
