from app.models.sqa_models import Company
from app.db.tasks import database_session
from fastapi_pagination.ext.sqlalchemy import paginate

from app.helpers.database_helper import bulk_insert
from sqlalchemy.future import select
from sqlalchemy.orm import load_only,Load
from dataclasses import dataclass, asdict



class CompanyController:


    def __init__(self):
        self.session, self.sync_session = database_session()
    



        
        

    async def  bulk_insert_data(self,data_dict) :
        try:
            async with self.session() as session:
                await session.run_sync(bulk_insert,data_dict,Company)
                await session.commit()
        
        except Exception as e:
            print("Error Inserting Data ERROR DETAILS {e}")
            session.rollback()
        finally:
            session.close()

    



    async def get_company(self,cfigi=None,column=None):
        
            
            if cfigi:
                async with self.session() as session:
                    q_res=await session.execute(select(Company).where(Company.compositeFigi == cfigi).order_by(Company.name))
                    companies =q_res.scalars().first()

                    await session.commit()
                   

            else:
                with self.sync_session() as session:
                    if column:
                        companies=session.query(Company).all()
                        session.commit()

                        return [ company.asdict(only=column) for company in companies ]

                    



                    else:
                        companies=session.query(Company).all()
                        session.commit()

            return [ company.asdict(only=column) for company in companies ]

           

                   





            









