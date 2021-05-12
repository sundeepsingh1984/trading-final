import pandas as pd
import json
from ast import literal_eval
from app.core.config import ASSET_DIR


def bulk_insert(session,data, relation):
    
    try:
        session.bulk_insert_mappings(relation, data)


        print(f"Data Inserted into {relation.__tablename__} table")

    except Exception as e:
        raise e











async def processTickerData(process,provider_id):

    df = pd.read_csv(ASSET_DIR+"joinedpolygon.csv")
   
    df.drop_duplicates(subset=["ticker"],inplace=True)

    



    if process == "Stocks":
        
        stock_data = await process_stocks(df[df["market"] == "STOCKS"])
        return stock_data

        
    


    elif process == "Forex":
        forex=await process_fx_idx_cryp(df[(df["market"] == "FX")])

        
        dict_sym = [{'unique_id': str(row['ticker']), 'ticker': str(row['ticker']), 'name': str(row['name']),'primaryExch': str(row['primaryExch']),
                'market': str(row['market']), 'type': str(row['type']), 
                'currency': str(row['currency']),  'active':str(row['active']),
                'internal_code':0 } for index, row in forex.iterrows()]

        dict_forex=[{"vendor_id":provider_id,"ticker":str(row['ticker']),"name":str(row['name']),"currencyName":str(row['currencyName']),"currency":str(row['currency']),"baseName":str(row['baseName']),"base":str(row['base'])} for index,row in forex.iterrows()]

        dict_vendorsymbol = [{"unique_id": row['ticker'],"vendor_symbol": row['ticker'],"vendor_id": provider_id
                }for index, row in forex.iterrows()]

        return dict_sym,dict_forex,dict_vendorsymbol




        
    
    
    elif process == "Indices":   
        indices=await process_fx_idx_cryp(df[ (df["market"] == "INDICES")])

        indices.dropna(inplace=True)
        


        dict_sym = [{'unique_id': str(row['ticker']), 'ticker': str(row['ticker']), 'name': str(row['name']),'primaryExch': str(row['primaryExch']),
                'market': str(row['market']), 'type': str(row['type']), 
                'currency': str(row['currency']),  'active':str(row['active']),
                'internal_code':0 } for index, row in indices.iterrows()]

        dict_indices=[{"vendor_id":provider_id,"name":str(row["name"]),"holiday":str(row["holiday"]),"assettype":str(row["assettype"]),"entitlement":str(row["entitlement"]),"disseminationfreq":str(row["disseminationfreq"]),"dataset":str(row["dataset"]),"schedule":str(row["schedule"]),"brand":str(row["brand"]),"series":str(row["series"])} for index,row in indices.iterrows()]


        dict_vendorsymbol = [{"unique_id": row['ticker'],"vendor_symbol": row['ticker'],"vendor_id": provider_id
                }for index, row in indices.iterrows()]


        return dict_sym,dict_indices,dict_vendorsymbol





    

    
    else:
        crypto=await process_fx_idx_cryp(df[ (df["market"] == "CRYPTO")])




        
        dict_sym = [{'unique_id': str(row['ticker']), 'ticker': str(row['ticker']), 'name': str(row['name']),'primaryExch': str(row['primaryExch']),
                'market': str(row['market']), 'type': str(row['type']), 
                'currency': str(row['currency']),  'active':str(row['active']),
                'internal_code':0 } for index, row in crypto.iterrows()]

        dict_crypto=[{"vendor_id":provider_id,"ticker":str(row['ticker']),"name":str(row['name']),"currencyName":str(row['currencyName']),"currency":str(row['currency']),"baseName":str(row['baseName']),"base":str(row['base'])} for index,row in crypto.iterrows()]
        dict_vendorsymbol = [{"unique_id": row['ticker'],"vendor_symbol": row['ticker'],"vendor_id": provider_id
                }for index, row in crypto.iterrows()]



        return dict_sym,dict_crypto,dict_vendorsymbol







   


async def  process_fx_idx_cryp(assets):


    assets.set_index("ticker")
    asset_with_attr = assets[~assets["attrs"].isnull()]
    asset_without_attr = assets[assets["attrs"].isnull()]
    asset_with_attr["attrs"] = asset_with_attr['attrs'].apply(literal_eval)
    df_attrs = pd.DataFrame(asset_with_attr['attrs'].tolist(), index=asset_with_attr.index)
    df = asset_with_attr.join(df_attrs,rsuffix="y_")
    df = pd.concat([df, asset_without_attr])

    df = df[~df.index.duplicated(keep='first')]



    


    return df










async def process_stocks(stocks):

        ticker_details=pd.read_csv(ASSET_DIR+"tickerdetails.csv")
        ticker_details.set_index("symbol")


        open_figi = pd.read_csv(ASSET_DIR+"figi_details.csv")


        # Column list

        column_list = ["ticker", "active", "currency", "locale", "market", "name", "primaryExch", "type", "updated", "url", "cik", "internal_code",
                       "cfigi", "figi", "exchCode", "uniqueID", "securityType", "marketSector",
                       "shareClassFIGI", "uniqueIDFutOpt", "securityType2", "securityDescription"]

        open_figi = open_figi[open_figi["figi"] == open_figi["compositeFIGI"]]
        open_figi.set_index('ticker')

        # convert codes to columns

        stocks.set_index("ticker")
        stocks_with_codes = stocks[~stocks["codes"].isnull()]
        stocks_with_codes.codes = stocks_with_codes.codes.apply(literal_eval)
        df_codes = pd.DataFrame(stocks_with_codes.codes.tolist(), index=stocks_with_codes.index)
        df = stocks_with_codes.join(df_codes)

        # seperate data with and without figi

        df_wo_figi = df[pd.isnull(df["figi"])]
        df_wth_figi = df[~pd.isnull(df["figi"])]



        # processing with figi data:

        df_wo_figi = df[pd.isnull(df["figi"])]
        df_wo_figi = pd.merge(df_wo_figi , open_figi , how="inner", on="ticker")
        df_wo_figi.drop(['cfigi'],axis=1,inplace=True)
        df_wo_figi.rename(columns={"name_x": "name", "figi_y": "figi","compositeFIGI":"cfigi"}, inplace=True)
        df_wo_figi['internal_code'] = 1
        df_wo_figi = df_wo_figi[column_list]



        # add interal code to df_with_figi
        df_wth_figi['internal_code'] = [
            1 if (row['figi'] == row['cfigi']) else 0 for index, row in
            df_wth_figi.iterrows()]

        # get data frame with figi having internal_code 1 and add row to with equal cfigi and figi from open_figi

        df_wth_zero = df_wth_figi[df_wth_figi['internal_code'] == 0]
        df_wth_not_zero = df_wth_figi[~df_wth_figi['internal_code'] == 0]
        open_figi.rename(columns={"compositeFIGI":"cfigi"})
        df = pd.merge(df_wth_zero, open_figi, how="inner", on="ticker")
        df['internal_code'] = 2
        df.rename(columns={"name_x": "name", "figi_y": "figi",}, inplace=True)
        column_list = ["ticker", "active", "currency", "locale", "market", "name", "primaryExch", "type", "updated", "url", "cik", "internal_code",
                       "cfigi", "figi", "exchCode", "uniqueID", "securityType", "marketSector",
                       "shareClassFIGI", "uniqueIDFutOpt", "securityType2", "securityDescription"]
        


        df = df[column_list]
        df_wo_figi=df_wo_figi[column_list]


        # remane without figi dataframe

        df_wo_figi.rename(columns={"name_x": "name", "figi_y": "figi",}, inplace=True)
        df_wo_figi= pd.merge(df_wo_figi, open_figi, how="inner", on="ticker")
        df = pd.concat([df_wth_zero, df,df_wth_not_zero,df_wo_figi])
        df=pd.merge(df,ticker_details,how="outer",left_on='ticker',right_on="symbol",suffixes=(None, '_y'))
        df["unique_id"]=df["cfigi"]
        return df
