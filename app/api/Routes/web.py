from typing	import List
from fastapi import APIRouter,Request
import sys,os,pathlib

from typing import Optional
# we're appending the app directory to our path here so that we can import config easily
sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))

from app.controllers import SymbolController,CompanyController,StockPriceController

from fastapi_pagination import LimitOffsetPage, Page, add_pagination
from app.schemas import *
from fastapi.templating import Jinja2Templates



# from app.controllers import SymbolController
router=APIRouter()


#template setting

templates = Jinja2Templates(directory="/Trading-final/trading/app/views")



@router.get("/", response_model=Page[SymbolOut])

async def index(request:Request):
    
    sym_obj=SymbolController()
    
    symbols=await sym_obj.get_symbol_by_market("STOCKS")

    return templates.TemplateResponse("index.html",{"request":request,"symbols":symbols,"data_type":"stock","count":len(symbols)})


    
    








@router.get("/company/{c_id}")

async def company(c_id:str):
    
    obj=CompanyController()
    if id:
        company=await obj.get_company(c_id)
        









@router.get("/companies",response_model=Page[CompanyOut])

async def companies(request:Request):
    obj=CompanyController()

    companies=await obj.get_company(column=["name","ticker"])



 
    return templates.TemplateResponse("index.html",{"request":request,"symbols":companies,"data_type":"company","count":len(companies)})







@router.get("/stocks" ,response_model=Page[SymbolOut])
async def stocks(request:Request):
    obj=SymbolController()
    stocks=await obj.get_symbol_by_market("STOCKS")
    
    return templates.TemplateResponse("index.html",{"request":request,"symbols":stocks,"data_type":"stock","count":len(stocks)})








@router.get("/forex" ,response_model=Page[SymbolOut])
async def forex(request:Request):
    obj=SymbolController()
    forex=await obj.get_symbol_by_market("FX")
    return templates.TemplateResponse("index.html",{"request":request,"symbols":forex,"data_type":"forex","count":len(forex)})


    





@router.get("/indices" ,response_model=Page[SymbolOut])
async def indices(request:Request):
    obj=SymbolController()
    indices=await obj.get_symbol_by_market("INDICES")
    return templates.TemplateResponse("index.html",{"request":request,"symbols":indices,"data_type":"indices","count":len(indices)})








@router.get("/crypto",response_model=Page[SymbolOut])
async def crypto(request:Request):
    obj=SymbolController()
    crypto=await obj.get_symbol_by_market("CRYPTO")
    return templates.TemplateResponse("index.html",{"request":request,"symbols":crypto,"data_type":"crypto","count":len(crypto)})












@router.get("/stockprices/{ticker}")
async def stockprices(request:Request,ticker:str,timeframe:str="minute",adjusted:bool=True,from_date:Optional[str]=None,to_date:Optional[str]=None):

    obj=StockPriceController()

    
    if timeframe == "hourly" and adjusted:

        data=await obj.get_stock_price_hourly_adj(ticker)






    elif timeframe == "hourly"  and  not adjusted:

        data=await obj.get_stock_price_hourly_unadj(ticker)



    elif timeframe == "daily"  and  not adjusted:

        data=await obj.get_stock_price_daily_unadj(ticker)



    elif timeframe == "daily"  and  adjusted:

        data=await obj.get_stock_price_daily_adj(tciker)



    elif timeframe == "minute"  and   adjusted:

        data=await obj.get_stock_price_minute_adj(ticker)
    


    else:

        data=await obj.get_stock_price_daily_unadj(ticker)



    return templates.TemplateResponse("stock_details.html",{"request":request,"symbol":ticker,"adjusted":adjusted,"timeframe":timeframe,"prices":data})




























