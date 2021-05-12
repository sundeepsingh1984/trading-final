from app.models.sqa_models import Symbol
from app.db.tasks import database_session

from app.helpers.database_helper import bulk_insert
from app.helpers.dataprocessing_helper import object_as_dict
from sqlalchemy.future import select
from fastapi_pagination.ext.sqlalchemy import paginate
from app.schemas import SymbolOut
import json


class SymbolController:


    def __init__(self):
        self.session, self.sync_session = database_session()
        
        

    async def  bulk_insert_data(self,data_dict) :
        try:
            async with self.session() as session:
                await session.run_sync(bulk_insert,data_dict,Symbol)
                await session.commit()
        
        except Exception as e:
            print("Error Inserting Data ERROR DETAILS {e}")
            session.rollback()
        finally:
            session.close()






    async def get_tickers(self,parm=None,parm_value=None):

        try:


            with self.sync_session() as session:
                if parm :
                    tickers=session.query(Symbol.ticker).where(getattr(Symbol,parm) == parm_value).all()
                else :
                    tickers=session.query(Symbol.ticker).all()
                
                tickers=[dict(tick) for tick in tickers]
                return tickers

        except Exception as e:

            raise e


    



    async def get_symbols(self,parm=None,parm_val=None,paginate=True):
        with self.sync_session() as session:
            if parm :
                if paginate:
                    symbols=paginate(session.query(Symbol).filter(getattr(Symbol,parm) == parm_val))
                    return symbols

                else:
                    symbols=session.query(Symbol).filter(getattr(Symbol,parm) == parm_val).all()
                    return [dict(symbol) for symbol in symbols ]


            else:
                if paginate:
                    symbols=paginate(session.query(Symbol))
                    return symbols

                else:
                    symbols=session.query(Symbol).all()
                    return [ dict(symbol) for symbol in symbols ]


       
                
            
                



    











            









