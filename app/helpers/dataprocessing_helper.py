import sys,os
import pathlib
import pandas as pd
import pandas_market_calendars as mcal
import pytz


from app.core.config import ASSET_DIR
from sqlalchemy import inspect




import time



def processstock(filename,paucity_threshold=0.00, data_type="daily"):


    if data_type == "daily":

        freq = "1D"



    elif data_type == "hourly":

        freq = "1H"


    else:


        freq = "1min"





    NY = pytz.timezone("America/New_York")

    # Must be a NY, pandas Timestamp


    print(f"Performing Transforms for path {filename}...")

    process_st=time.perf_counter()

    df: pd.DataFrame =pd.read_csv(filename)


    df=df.sort_values(by = 't')



    start=pd.to_datetime(pd.to_numeric(df.iloc[0]["t"]), unit="ms", utc=True)
    end=pd.to_datetime(pd.to_numeric(df.iloc[-1]["t"]), unit="ms", utc=True)





    nyse: NYSEExchangeCalendar = mcal.get_calendar("NYSE")
    schedule = nyse.schedule(start, end)

    if data_type == "minute":

        valid_minutes: pd.DatetimeIndex = mcal.date_range(schedule, freq) - pd.Timedelta(
            value=1, unit="T"
        )

    else:
        valid_minutes: pd.DatetimeIndex = mcal.date_range(schedule, freq)



    if df is None or df.empty:
        print(f"No results found.")
        return None
    df.t = pd.to_datetime(pd.to_numeric(df.t), unit="ms", utc=True)
    df.set_index("t", inplace=True)

    expected_sessions = schedule.shape[0]

    actual_sessions = df.groupby(df.index.date).count().shape[0]  # type:ignore

    print(
        f"{expected_sessions=}\t{actual_sessions=}\tpct_diff: {(actual_sessions/expected_sessions)-1.:+.2%}"
    )

    expected_minutes = valid_minutes.shape[0]
    actual_minutes = df.loc[~df.isnull().all(axis="columns")].shape[0]

    print(
        f"{expected_minutes=}\t{actual_minutes=}\tpct_diff: {(actual_minutes/expected_minutes)-1.:+.2%}"
    )

    if (duplicated_indice_count := df.index.duplicated().sum()) > 0:
        # print("\n")
        # print(f"Found the following duplicated indexes:")
        # print(df[df.index.duplicated(keep=False)].sort_index()["vw"])  # type: ignore
        print(f"Dropping {duplicated_indice_count} row(s) w/ duplicate Datetimeindex ")
        df = df[~df.index.duplicated()]  # type: ignore






    # print("Reindexing...")
    df = df.reindex(valid_minutes)  # type: ignore






    print("After Reindexing by trading calender:")

    actual_sessions = df.groupby(df.index.date).count().shape[0]  # type:ignore
    actual_minutes = df.loc[~df.isnull().all(axis="columns")].shape[0]

    print(f"{expected_sessions = }\t{actual_sessions = }")
    print(f"{expected_minutes = }\t{actual_minutes = }")

    pct_minutes_not_null = actual_minutes / expected_minutes

    print(f"{pct_minutes_not_null = :.3%}")

    if pct_minutes_not_null < paucity_threshold:
        print(f" below threshold: {paucity_threshold}")
        #return None

    if pct_minutes_not_null > 1.01:
        raise ValueError(f"{pct_minutes_not_null=} Riley messed up, yell at him")

    # Rename polygon json keys to canonical pandas headers
    df = df.rename(
        columns={
            "v": "volume",
            "vw": "volwavg",
            "o": "open",
            "c": "close",
            "h": "high",
            "l": "low",
            "t": "date",
            "n": "trades",
        }
    )


    # Converting UTC-aware timestamps to NY-naive
    if isinstance(df.index, pd.DatetimeIndex):
        df.index = df.index.tz_convert(NY).tz_localize(None)  # type:ignore
    else:
        raise TypeError

    # Reorder columns so that ohlcv comes first
    df = df[["ticker","open", "high", "low", "close", "volume", "volwavg", "trades"]]
    df.index.name = "time"

    first_index = df.index.min()
    last_index = df.index.max()

    print(f"{first_index = } {last_index = }")


    print(f"Time Taken to perform transformation {time.perf_counter()-process_st}")

    if isinstance(df, pd.DataFrame):
        return df








def get_file_list(folder_name):

    """"

    DESCRIPTION
    ------------

    RETURN THE LIST OF FILES FROM ASSET LIST




    PARAMERTERS:
    ------------

    folder_name(str):name of the folder.


    RETURNS:
    -------

    files (list):list of file names in a directory

    """

    # directory path
    dir_path=ASSET_DIR  + folder_name
    
    files=os.listdir(dir_path)

    return files




def object_as_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}














