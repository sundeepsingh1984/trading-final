from app.models.sqa_models import *
from app.db.tasks import database_session
from app.helpers.database_helper import bulk_insert
from sqlalchemy.future import select
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import lazyload
from datetime import date,datetime


class ForexController:


    def __init__(self):
         self.session, self.sync_session = database_session()


    async def query_data(self,r_obj,relation,parameter_val=None,start=None,end=None,limit=50000,parameter="ticker"):

        session=self.sync_session()
        q_res=session.query(Forex).filter( getattr(Forex,parameter) ==  parameter_val).one()


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



        

    
    async def get_forex_price_daily_adj(self,ticker=None,start=None,end=None):
        prices=await self.query_data(ForexPricesDailyAdj,"price_daily_adjusted",ticker,start,end)
        return prices

        
    
    
    async def get_forex_price_daily_unadj(self,ticker=None,start=None,end=None):

        prices=await self.query_data(ForexPricesDailyUnadj,"price_daily_unadjusted",ticker,start,end)
        return prices

    
   

    async def get_forex_price_minute_adj(self,ticker=None,start=None,end=None):
        
        prices=await self.query_data(ForexPricesMinAdj,"prices_min_adjusted",ticker,start,end)
        return prices 


    
    async def get_forex_price_minute_unadj(self,ticker=None,start=None,end=None):
        
        prices=await self.query_data(ForexPricesMinUnadj,"price_min_unadjusted",ticker,start,end)
        return prices 

    

    async def get_forex_price_hourly_unadj(self,ticker=None,start=None,end=None):
        prices=await self.query_data(ForexPricesHourlyAdj,"prices_hourly_unadjusted",ticker,start,end)
        return prices

    
    async def get_forex_price_hourly_adj(self,ticker=None,start=None,end=None):
        prices=await self.query_data(ForexPricesHourlyUnadj,"prices_hourly_adjusted",ticker,start,end)
        return prices 





