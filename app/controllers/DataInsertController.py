import sys,os,pathlib
# we're appending the app directory to our path here so that we can import config easily
sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))
from app.models.sqa_models import *
from app.helpers.database_helper import processTickerData, bulk_insert
import numpy as np
import pandas as pd
from sqlalchemy.future import select
import asyncio
from app.db.tasks import database_session
from app.helpers.dataprocessing_helper import processstock,get_file_list
from app.core.config import ASSET_DIR






class DataInsertController:

    def __init__(self):

        self.session, self.sync_session = database_session()

    

    async def populate_vendors(self):

        vendors = [Vendor(name='Alpaca'), Vendor(name='Polygon'), Vendor(name='InteractiveBrokers'), Vendor(
            name='SimFin'), Vendor(name='AlphaVantage'), Vendor(name='Quandl'), Vendor(name='Internal')]

        try:

            async with self.session() as session:

                session.add_all(vendors)

                await session.commit()

                print("-----Vendor's Added-----")

        except Exception as e:

            raise e






    async def populate_stock_symbols(self):

        df = await processTickerData()

        # remove null
        not_present = ['', np.nan, None]

        df = df.loc[~(df['unique_id'].isin(not_present))]
        df = df.loc[~(df['figi'].isin(not_present))]

        # duplicate dataframes

        df = df.drop_duplicates(subset=['unique_id'])

        # rename Columns

        df.rename(columns={"exchangeSymbol": "exSymbol", "cfigi": "compositeFigi",
                  "shareClassFIGI": "shareClassFigi", "marketSector": 'sector', "sector": "marketSector"}, inplace=True)

        # create dictionaries

        dict_sym = [{
                'unique_id': str(row['unique_id']), 'ticker': str(row['ticker']), 'name': str(row['name']),
                'compositeFigi': str(row['compositeFigi']),
                'shareClassFigi': str(row['shareClassFigi']),
                'exchCode': str(row["exchCode"]), 'exSymbol': str(row['exSymbol']), 'primaryExch': str(row['primaryExch']),
                'securityType': str(row['securityType']), 'securityType2':str(row['securityType2']),

                'market': str(row['market']), 'type': str(row['type']), 'marketSector':str(row['marketSector']),
                'currency': str(row['currency']), 'country':str(row['country']), 'active':str(row['active']),
                'internal_code': int(row["internal_code"]),  "tags":[] if row["tags"] in not_present else row["tags"], "similar":[] if row["similar"] in not_present else row["similar"]}for index, row in df.iterrows()]

        dict_comp = [{'compositeFigi': str(row['unique_id']), 'name': str(row['name']), 'ticker': str(row['ticker']),
                            'sector': str(row['marketSector']),
                            'description': str(row['securityDescription']),
                             "cik":str(row["cik"]), "sic":str(row["sic"]), "industry":str(row["industry"]), "url":str(row["url"]),

                             "tags":[] if row["tags"] in not_present else row["tags"],

                             "similar":[] if row["similar"] in not_present else row["similar"]
                                }for index, row in df.iterrows()]

        # Fetch Vendor Details

        try:

            async with self.session() as session:

                vendor = await session.execute(select(Vendor).where(Vendor.name == "Polygon"))

                vendor = vendor.scalars().first()

                await session.commit()

        except Exception as e:


            print("There was some error fetching data from database")

            # raise e


        # vendor symbol dictionary creattion


        dict_vendorsymbol = [{"unique_id": row['unique_id'],"vendor_symbol": row['ticker'],"vendor_id": vendor.id
                }for index, row in df.iterrows()]


        # Insert Into Table


        try:
            async with self.session() as session:

                await session.run_sync(bulk_insert,dict_sym,Symbol)
                await session.run_sync(bulk_insert,dict_vendorsymbol,VendorSymbol)
                await session.run_sync(bulk_insert,dict_comp,Company)


                await session.commit()


        except Exception as e:

            await session.rollback()

            raise e

            print("there was some error Inserting Data")



    






    async def populate_forex_indices_symbols(self,provider_name):

        try:

            async with self.session() as session:

                vendor = await session.execute(select(Vendor).where(Vendor.name == provider_name))

                vendor = vendor.scalars().first()

                await session.commit()

        except Exception as e:


            print("There was some error fetching data from database")

            # raise e

        try:
            async with self.session() as session:

                # insert into symbol,forex
                # df_sym,df_forex,d_vs=await processTickerData("Forex",vendor.id)

                # await session.run_sync(bulk_insert,df_sym,Symbol)
                # await session.run_sync(bulk_insert,df_forex,Forex)
                # await session.run_sync(bulk_insert,d_vs,VendorSymbol)

                # # insert into symbol,indices
                # df_sy,df_indices,df_vesy=await processTickerData("Indices",vendor.id)
                # await session.run_sync(bulk_insert,df_sy,Symbol)
                # await session.run_sync(bulk_insert,df_indices,Indices)
                # await session.run_sync(bulk_insert,df_vesy,VendorSymbol)

                # insert into symbol,crypto
                df_s,df_crypto,df_vensym=await processTickerData("Crypto",vendor.id)
                await session.run_sync(bulk_insert,df_s,Symbol)
                await session.run_sync(bulk_insert,df_crypto,Crypto)
                await session.run_sync(bulk_insert,df_vensym,VendorSymbol)

                await session.commit()


        except Exception as e:

            await session.rollback()

            raise e

            print("there was some error Inserting Data")







    async def populate_price(self,dir_name,data_type,database_relation,provider_name):


        for file in get_file_list(dir_name):

            # processing the data
            df=processstock(ASSET_DIR+dir_name+"/"+file,data_type=data_type)

            
            # abstract ticker
            ticker_name=str(file).split("_")

            symbol=await self.get_symbol_byticker(ticker_name[0])

            vendor=await self.get_vendor_byname(provider_name)


            if not symbol:

                continue
                


            # set dataframe columns
            df["unique_id"]=symbol.unique_id
            df["company_id"]=symbol.unique_id
            df["vendor_id"]=vendor.id


            # drop reset rename dataframe
            df.drop(["ticker","trades"],axis=1,inplace=True)
            df.reset_index(inplace=True)
            df.rename(columns={"volwavg":"vw_avg_price","time":"datetime"},inplace=True)
            df.dropna(inplace=True)


            # conver to dictionary
            price_dict=df.to_dict(orient="records")

 

            #insert into table
            try:
               async with self.session() as session:
                        await session.run_sync(bulk_insert,price_dict,database_relation)
                        await session.commit()

            except Exception as e:

                raise e





    async def get_symbol_byticker(self,ticker):

        async with self.session() as session:


            try:
                # get symbol details
                symbol = await session.execute(select(Symbol).where(Symbol.ticker == ticker))
                symbol=symbol.scalars().first()

                return symbol   
            


            except Exception as e:
                raise e





    async def get_vendor_byname(self,vendor_name):

        try:

            async with self.session() as session:

                vendor = await session.execute(select(Vendor).where(Vendor.name == vendor_name ))
                vendor=vendor.scalars().first()



                return vendor


        except Exception as e:
            print (f"Error getting the vendor details \t Error Details: {e} ")






    async def populate_splits_dividents(self,dir_name,relation,from_vendor="Polygon"):

        for file in get_file_list(dir_name):






            # processing the data
            df=pd.read_csv(ASSET_DIR+dir_name+file)


            
            
            # abstract ticker
            ticker_name=str(file).split("_")


            #symbol vendor details
            symbol=await self.get_symbol_byticker(ticker_name[0])
            vendor=await self.get_vendor_byname(from_vendor)


            if not symbol:

                continue


            # set dataframe columns
            df["unique_id"]=symbol.unique_id
            df["company_id"]=symbol.unique_id
            df["vendor_id"]=vendor.id

            

            # conver to dictionary
            split_dict=df.to_dict(orient="records")


            try:

                async with self.session() as session:

                    await session.run_sync(bulk_insert,split_dict,relation)
                    await session.commit()


            except Exception as e:

                print(f"Some Error Inserting Data iInto the table error details {e}")




  



    async def populate_news(self,dir_name,relation,provider_name):

        for file in get_file_list(dir_name):
            df=pd.read_csv(ASSET_DIR+dir_name+file)

            
            vendor=await self.get_vendor_byname(provider_name)


           
            df["vendor_id"]=vendor.id

            df.rename(columns={"timestamp":"datetime"},inplace=True)


            df.dropna(inplace=True)

            

            # conver to dictionary
            news_dict=df.to_dict(orient="records")

            try:
                async with self.session() as session:
                    await session.run_sync(bulk_insert,news_dict,relation)
                    await session.commit()


            except Exception as e:


                await session.rollback()

                raise e













    async def populate_financials(self,dir_name,adjusted=True):


        for  file in get_file_list(dir_name):

            df=pd.read_csv(file)


            # abstract ticker
            ticker_name=str(file).split("_")


            #symbol vendor details
            symbol=await self.get_symbol_byticker(ticker_name)
            vendor=await self.get_vendor_byname(ticker_name)


            # set dataframe columns
            df["unique_id"]=symbol.unique_id
            df["company_id"]=symbol.unique_id
            df["vendor_id"]=vendor.id


            df["adjusted"]=adjusted

            df.drop("ticker",index=1,inplace=True)


            # conver to dictionary
            split_dict=df.to_dict(orient="records")

            


            try:
                await session.bulk_insert_mappings(bulk_insert,split_dict,Financials)
                await session.commit()


            

            except Exception as e:

                await session.rollback()

                print(f"Some Error Inserting Data iInto the table error details {e}")








































          
















    def main_async(self):

        # asyncio.run(self.populate_price("price_data/adjusted_stock_price_min","Stocks",StockPricesMinuteAdj,"Polygon"))

        #asyncio.run(self.populate_vendors())
        
        # asyncio.run(self.populate_splits_dividents("SPLITS/Stocks/",StockSplits))

        asyncio.run(self.populate_forex_indices_symbols("Polygon"))




obj = DataInsertController()
obj.main_async()



