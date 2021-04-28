import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))
from app.core.config import OPENFIGI_URL, OPENFIGI_KEY
import asyncio
import aiohttp
import orjson
from time import perf_counter
from app.helpers.datatype_helpers import divide_chunks,unwrap
import pandas as pd

class OpenFigi:

    def __init__(self):
        self. url = OPENFIGI_URL
        self. key = OPENFIGI_KEY



    async def consume_openfigi(self,job, queue, client):

        openfigi_headers = {'Content-Type': 'text/json'}
        if self . key:
            openfigi_headers['X-OPENFIGI-APIKEY'] = self . key





        res = await client.post(self.url, json=job, headers=openfigi_headers)



        if res.status != 200:


            raise ValueError(f"Bad statuscode {res.status=};expected 200")

        await queue.put(await res.json(loads=orjson.loads))

    async def dispatch_consume_openfigi(self,symbols: list):
        queue: asyncio.Queue[bytes] = asyncio . Queue()

        client = aiohttp. ClientSession()

        jobs = [[{" idType ": " TICKER ", " idValue ": symbol}
                for symbol in symbols]]




        if len(jobs) > 100:

            jobs = list(divide_chunks(jobs, 100))

        async with client:

            await asyncio.gather(

                *(

                    self.consume_openfigi(jobs, queue, client)

                    for job in jobs

                )
            )

        results: List[bytes] = []
        while not queue.empty():
            results.append(await queue.get())
            queue.task_done()

        print(results)

        return results

    def get_figi(self, tickers):

        network_io_start = perf_counter()

        raw_results = unwrap(
            asyncio.run(
                self.dispatch_consume_openfigi(tickers)
            )
        )
        network_io_stop = perf_counter()
        print(f"Data retrieved in {network_io_stop-network_io_start:.2f} seconds.")
        print("Performing Transforms...")
        df = pd.concat(
            (pd.DataFrame(result_chunk.get("results", None))
             for result_chunk in raw_results),
            ignore_index=True,
        )

        print(df.info())


obj = OpenFigi()
obj.get_figi(["MSFT"])
