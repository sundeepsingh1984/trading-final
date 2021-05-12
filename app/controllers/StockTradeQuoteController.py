from app.models.sqa_models import *
from app.db.tasks import database_session
from app.helpers.database_helper import bulk_insert
from sqlalchemy.future import select
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import lazyload
from datetime import date,datetime


class StockTradeQuoteController:


    def __init__(self):
         self.session, self.sync_session = database_session()


    async def query_data(self,r_obj,relation,parameter_val=None,start=None,end=None,limit=50000,parameter="ticker"):
        session=self.sync_session()
        q_res=session.query(Indices).filter( getattr(Indices,parameter) ==  parameter_val).one()


        if parameter:
            if start and end:
                my_time = datetime.min.time()
                start = datetime.combine(start, my_time)
                end=datetime.combine(end,my_time)
                data=getattr(q_res,relation).filter(r_obj.datetime.between(start,end)).limit(limit).all()
            else:
                data=getattr(q_res,relation).limit(limit).all()

        else:
            if start and end:
                my_time = datetime.min.time()
                start = datetime.combine(start, my_time)
                end=datetime.combine(end,my_time)
                data=getattr(q_res,relation).filter(r_obj.datetime.between(start,end)).limit(limit).all()

                        
            else:
                data=getattr(q_res,relation).limit(limit).all()


        data=[dict(d) for d in data]
        return data 



        

    
    async def get_indices_prices_daily(self,ticker=None,start=None,end=None):
        prices=await self.query_data(IndicesPriceDaily,"price_daily",ticker,start,end)
        return prices

        
    
    
    async def get_forex_price_hourly(self,ticker=None,start=None,end=None):

        prices=await self.query_data(IndicesPriceHourly,"price_hourly",ticker,start,end)
        return prices

    
   

    async def get_indices_price_min(self,ticker=None,start=None,end=None):
        
        prices=await self.query_data(IndicesPriceMin,"prices_min",ticker,start,end)
        return prices 


    
    



