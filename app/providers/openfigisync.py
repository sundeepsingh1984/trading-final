import os,sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


import config, requests
import pandas as pd
from Helper.helpers import divide_chunks
import threading
class OpenFigi:

    def __init__(self):
        self.api_url = config.OPEN_FIGI_URL
        self.openfigi_key = config.OPEN_FIGI_KEY
        self.openfigi_headers = {'Content-Type': 'text/json'}

        self.FIGI=[]

    def map_jobs(self, jobs):

        if self.openfigi_key:
            self.openfigi_headers['X-OPENFIGI-APIKEY'] = self.openfigi_key
        response = requests.post(url=self.api_url, headers=self.openfigi_headers,json=jobs)
        
        if response.status_code != 200:

            pass
            # print('Bad response code: {}'.format(str(response.status_code)))
        
        try:
            
            rs=response.json()

            for item in rs:
                self.FIGI.append(item.get("data"))
         

        
        except Exception as e:
            
            pass

        


       



        





    def get_figi_info(self,jobs):

       
        

        #threading applied


        [self.map_jobs(job) for job in jobs]



        # processes = [threading.Thread(target=self.map_jobs, args=(job,), daemon=True) for job in jobs_chunked]
        # start = [process.start() for process in processes]
        # for q in processes:
        #     try:
        #      q.join()
        #     except Exception as e:

        #       raise e


        self.FIGI= list(filter(None, self.FIGI)) 


        return self.FIGI



    def _create_job_mapping(self,stock_tickers):

        jobs = [{'idType': 'TICKER', 'idValue': ticker } for ticker in stock_tickers]


        if len (jobs) > 100:

            jobs= list(divide_chunks(jobs, 50))



        return jobs







        







    def get_figis(self,tickers):
        
        jobs= self._create_job_mapping(tickers)

        self.get_figi_info(jobs)



        dfs=[pd.DataFrame.from_dict(figi) for figi in self.FIGI]




      





        return pd.concat(dfs)








        
        






    # # Returns dataframe where compositeFigi = Figi and exchCode == 'US' when only a Ticker is Passed
    # def get_figi_eq_cfigi(self, jobs):
    #     job_results = self.map_jobs(jobs)
    #     just_dictionaries = [d['data'][i] for d in job_results for i in range(len(job_results[0]['data']))]
    #     df_figi = pd.DataFrame.from_dict(just_dictionaries)
    #     df_figi = df_figi.loc[(df_figi['compositeFIGI'] == df_figi['figi']) & (df_figi['exchCode'] == 'US')]
    #     return (df_figi)







