from typing	import List
from fastapi import APIRouter,Request
import sys,os,pathlib

from typing import Optional
# we're appending the app directory to our path here so that we can import config easily
sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))

from app.controllers import *

from fastapi_pagination import LimitOffsetPage, Page, add_pagination
from app.schemas import *
from fastapi.templating import Jinja2Templates
from fastapi_pagination import LimitOffsetPage, Page, add_pagination
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from datetime import datetime,date
from typing import Optional



# from app.controllers import SymbolController
router=APIRouter()






@router.get("/tickers")


async def symbols(request:Request,market:Optional[str]=None):

    sym_obj=SymbolController()
    
    symbols=await sym_obj.get_tickers("market",market)

    sym_json = jsonable_encoder(symbols)
    return JSONResponse(content=sym_json)




#stockprices router


@router.get("/prices/stocks/{ticker}/{timeframe}")

async def getprices(request:Request,ticker:str,timeframe:str,start:Optional[date]=None,end:Optional[date]=None,adjusted:Optional[bool]=True):

    obj=StockPriceController()

    if timeframe == "hourly" and adjusted:

        data=await obj.get_stock_price_hourly_adj(ticker,ticker,start,end)

    elif timeframe == "hourly"  and  not adjusted:

        data=await obj.get_stock_price_hourly_unadj(ticker,start,end)
    
    elif timeframe == "daily"  and  not adjusted:

        data=await obj.get_stock_price_daily_unadj(ticker,start,end)

    elif timeframe == "daily"  and  adjusted:

        data=await obj.get_stock_price_daily_adj(ticker,start,end)

    elif timeframe == "minute"  and   adjusted:

        data=await obj.get_stock_price_minute_adj(ticker,start,end)
    


    else:

        data=await obj.get_stock_price_daily_unadj(ticker,start,ends)


    data_json = jsonable_encoder(data)
    return JSONResponse(content=data_json)



#forex router



@router.get("/prices/forex/{ticker}/{timeframe}")

async def getprices(request:Request,ticker:str,timeframe:str,start:Optional[date]=None,end:Optional[date]=None,adjusted:Optional[bool]=True):

    obj=ForexController()

    if timeframe == "hourly" and adjusted:

        data=await obj.get_forex_price_hourly_adj(ticker,ticker,start,end)

    elif timeframe == "hourly"  and  not adjusted:

        data=await obj.get_forex_price_hourly_unadj(ticker,start,end)
    
    elif timeframe == "daily"  and  not adjusted:

        data=await obj.get_forex_price_daily_unadj(ticker,start,end)

    elif timeframe == "daily"  and  adjusted:

        data=await obj.get_forex_price_daily_adj(ticker,start,end)

    elif timeframe == "minute"  and   adjusted:

        data=await obj.get_forex_price_minute_adj(ticker,start,end)
    else:
        data=await obj.get_forex_price_daily_unadj(ticker,start,ends)


    data_json = jsonable_encoder(data)
    return JSONResponse(content=data_json)



#crypto router



@router.get("/prices/crypto/{ticker}/{timeframe}")

async def getprices(request:Request,ticker:str,timeframe:str,start:Optional[date]=None,end:Optional[date]=None,adjusted:Optional[bool]=True):

    obj=CryptoPriceController()

    if timeframe == "hourly" and adjusted:

        data=await obj.get_crypto_price_hourly_adj(ticker,ticker,start,end)

    elif timeframe == "hourly"  and  not adjusted:

        data=await obj.get_crypto_price_hourly_unadj(ticker,start,end)
    
    elif timeframe == "daily"  and  not adjusted:

        data=await obj.get_crypto_price_daily_unadj(ticker,start,end)

    elif timeframe == "daily"  and  adjusted:

        data=await obj.get_crypto_price_daily_adj(ticker,start,end)

    elif timeframe == "minute"  and   adjusted:

        data=await obj.get_crypto_price_minute_adj(ticker,start,end)
    else:
        data=await obj.get_crypto_price_daily_unadj(ticker,start,ends)


    data_json = jsonable_encoder(data)
    return JSONResponse(content=data_json)





@router.get("/prices/indices/{ticker}/{timeframe}")


async def getprices(request:Request,ticker:str,timeframe:str,start:Optional[date]=None,end:Optional[date]=None):

    obj=IndicesPriceController()


    if timeframe == "daily":

        data=await obj.get_indices_prices_daily(ticker,start,end)

    elif timeframe == "minute":

        data=await obj.get_indices_price_min(ticker,start,end)

    else:
        data=await obj.get_indices_price_hourly(ticker,start,end)



   



    
     
    