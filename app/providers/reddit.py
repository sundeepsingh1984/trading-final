# import os
# os.environ['PYTHONASYNCIODEBUG'] = '1'
# os.environ['PYTHONTRACEMALLOC'] = '1'

# TO DO
# Make code cleaner - in functions
# Make asyncio functions for all tasks including SQL Queries using asyncpg
# Synchronize rate limit with Semaphores - Check if all data is being Updated
# When we decrease the "connector or semaphore value (~2 - this script picks up most of the url's - otherwise not"

# Make an auto updatable function - make combination of 2 keys unique if required

# https://rareloot.medium.com/using-pushshifts-api-to-extract-reddit-submissions-fb517b286563
import httpx
import datetime, time
import pandas as pd
import json
import asyncio, aiohttp
from aiohttp import ClientSession
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import config
from Models.sqa_models import Symbol, VendorSymbol, Company, Forex, Indices, Crypto, Mention
import re, ssl, requests
from sqlalchemy.exc import SQLAlchemyError


reddit_limit = json.loads((requests.get('https://api.pushshift.io/meta')).text)['server_ratelimit_per_minute']


Session = sessionmaker()
engine = create_engine(config.DB_URL)
Session.configure(bind=engine)
session = Session()
symbols_in_db = session.query(Symbol).all()
dict_symbols_figi = {}
for symbol in symbols_in_db:
    if(":" in symbol.ticker):
            symbol.ticker = symbol.ticker.split(":")[1].strip('"\'')
    dict_symbols_figi['$' + symbol.ticker] = [symbol.uniqueID,symbol.ticker]

unix_start = int(datetime.datetime(2021, 2, 14).timestamp())
unix_last = int(datetime.datetime(2021, 2, 15).timestamp())
increments = 120 #seconds
unix_end = unix_start + increments
periods = int((unix_last - unix_start)/increments)

sub = "wallstreetbets"


subStats = {} #subStats is the dictionary to store data.

def create_urls(unix_start,unix_end):
    list = []
    for p in range(periods):
        list.append('https://api.pushshift.io/reddit/search/submission/?''size=1000&after='+str(unix_start)+'&before='+str(unix_end)+'&subreddit='+str(sub))
        unix_start = unix_end
        unix_end = unix_end + increments
    return list

urls = create_urls(unix_start,unix_end)
num_urls = len(urls)

def collectSubData(subm):
    subData = list()
    title = subm['title']
    url = subm['url']
    try:
        flair = subm['link_flair_text']
    except KeyError:
        flair = "NaN"
    author = subm['author']
    sub_id = subm['id']
    score = subm['score']
    created = datetime.datetime.fromtimestamp(subm['created_utc'])
    numComms = subm['num_comments']
    permalink = subm['permalink']
    subred = subm['subreddit']
    subData.append((author,created,subred,title ,sub_id,url,score,numComms,permalink,flair))
    #Create a dictionary entry of current submission data and store all data related to it
    subStats[sub_id] = subData

async def read_urls(r):
     data = await r.read()
     data1 = json.loads(data)
     hashrate = data1['data']
     for submission in hashrate:
         collectSubData(submission)

async def fetch(url, session):
    async with session.get(url) as response:
        try:
            type = response.headers.get("content-type")
            date = response.headers.get("DATE")
            print("{}:{} with type {}".format(date, response.url, type))
            await read_urls(response)
        except Exception as e:
            print("Problem due to:",e)

async def bound_fetch(sem, url, session):
    # Getter function with semaphore.
    async with sem:
        return await fetch(url, session)

async def run(urls):
    tasks = []
    sem = asyncio.Semaphore(1000)
    connector = aiohttp.TCPConnector(limit=(reddit_limit/60))
    async with ClientSession(connector=connector) as session:
        for url in urls:
            task = asyncio.create_task(bound_fetch(sem, url, session))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)
        return responses

start = time.time()
asyncio.run(run(urls))
end = time.time()
print("Took {} seconds to pull {} url.".format(end-start,num_urls))

# convert it to a asyncio function
headers = ["Author", "PublishDate", "SubReddit", "Title", "Post ID",  "Url", "Score", "TotalComments", "Permalink", "Flair"]
subStats_df = []
for sub in subStats:
    subStats_df.append(subStats[sub][0])
subStats_df = pd.DataFrame(data=subStats_df,columns=headers)


df_mention = pd.DataFrame(columns=["datetime","ticker", "uniqueID", "message", "source", "url"])
uniqueID = []
ud = []
ticker = []

for index,row  in subStats_df.iterrows():
    words = str(row['Title']).split()
    cashtags = list(set(filter(lambda word: word.startswith('$'), words)))
    title = re.sub(r'[\W_]+ ', '', row['Title'])
    ur = row['Url']
    publish_dt = row['PublishDate']
    if len(cashtags) > 0:
        for cashtag in cashtags:
            cashtag = '$' + re.sub(r'[\W_]+', '', cashtag) # Only AlphaNumeric
            try:
                uniqueID.append(dict_symbols_figi[cashtag.upper()][0])
                uid_tick = dict_symbols_figi[cashtag.upper()]
                ud = uid_tick[0]
                tick = uid_tick[1]
            except Exception as e:
                print("Didn't work because",e)

            if len(ud):
                data = [publish_dt, tick, ud, title, "WSB", ur]
                df_mention.loc[-1] = data  # adding a row
                df_mention.index = df_mention.index + 1

print("uniqueID:",uniqueID)
print("Count of uniqueID:",len(uniqueID))
print("Set of uniqueID:",len(set(uniqueID)))

df_mention.dropna()

try:
    session = Session()
    session.bulk_insert_mappings(Mention, df_mention.to_dict(orient='records'))
except SQLAlchemyError as e:
    error = str(e.__dict__['orig'])
    print("SQL ERROR",error)
    session.rollback()

session.commit()


print("df_mention.to_dict",df_mention.to_dict(orient='records'))
