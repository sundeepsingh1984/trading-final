import sys,os,pathlib

# we're appending the app directory to our path here so that we can import config easily
sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))




from app.models.sqa_models import Symbol, Vendor, Company, Forex, Indices, VendorSymbol, StockPricesMinuteAdj
from app.helpers.database_helper import processTickerData, bulk_insert

import numpy as np
from sqlalchemy.future import select
import asyncio
from app.db.tasks import database_session
from app.helpers.dataprocessing_helper import processstock,get_file_list


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




    async def populate_symbols(self):

        df = processTickerData()

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

            raise e

            print("there was some error Inserting Data")







    async def populate_price(self,dir_name,data_type,database_relation):

        


        for file in get_file_list(dir_name):

            # processing the data
            df=processstock(dir_path+"/"+file,data_type=data_type)

            
            # abstract ticker
            ticker_name=str(file).split("_")

            symbol=await self.get_symbol_byticker(ticker_name)


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
                with self.session as session():
                        await session.run_sync(bulk_insert,price_dict,database_relation)
                        await session.commit()

            except Exception as e:

                raise e



        async def get_symbol_byticker(self,ticker):

                async with self.session() as session:

                        try:

                                # get symbol details
                                symbol = await session.execute(select(Symbol.unique_id).where(Symbol.ticker == ticker_name[0] ))
                                symbol=symbol.scalars().first()
                                return symbol   

                        except exception as e:

                                raise e


        async def get_vendor_byname(self,vendor_name):



                try:
                                

                        # vendor details
                        vendor = await session.execute(select(Vendor).where(Vendor.name == "Polygon" ))
                        vendor=vendor.scalars().first()
                        return vendor


                except Exception as e:


                        print (f"Error getting the vendor details \t Error Details: {e} ")







       async def populate_splits():

        for file in get_file_list(dir_name):

            # processing the data
            df=processstock(dir_path+"/"+file,data_type=data_type)

            
            # abstract ticker
            ticker_name=str(file).split("_")



          
















    def main_async(self):

        asyncio.run(self.populate_price("Adj_StockPrice_Min","minute",StockPricesMinuteAdj))


obj = DataInsertController()
obj.main_async()



