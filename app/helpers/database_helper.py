import pandas as pd
import json
from ast import literal_eval


def bulk_insert(session,data, relation):
    try:
        session.bulk_insert_mappings(relation, data)


        print(f"Data Inserted into {relation.__tablename__} table")

    except Exception as e:
        raise e


def processTickerData(process="Stocks"):

    df = pd.read_csv("/app/assets/joinedpolygon.csv")

    ticker_details=pd.read_csv("/app/assets/tickerdetails.csv")

    ticker_details.set_index("symbol")

    if process == "Stocks":

        open_figi = pd.read_csv("/app/assets/figi_details.csv")
        stocks = df[df["market"] == "STOCKS"]

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
        df_codes = pd.DataFrame(
            stocks_with_codes.codes.tolist(), index=stocks_with_codes.index)
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



        print(df.info())

        return df









    else:
        assets = df[~df["market"] == "STOCKS"]
        assets.set_index("ticker")
        asset_with_attr = stocks[~stocks["attrs"].isnull()]
        asset_without_attr = stocks[stocks["attrs"].isnull()]
        asset_with_attr.attrs = stocks_with_attr.attrs.apply(literal_eval)
        df_attrs = pd.DataFrame(
            stocks_with_attr.attrs.tolist(), index=stocks_with_attr.index)
        df = stocks_with_attr.join(df_attrs)
        df = pd.concat([df, assets_without_attrs])

        return df

    # df2=pd.DataFrame(lst)

    # print(df2)
