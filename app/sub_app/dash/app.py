import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
from ast import literal_eval
import requests
import dash_tabulator
import dash_table
import dash_labs as dl 


import dash_bootstrap_components as dbc


def create_app():


    app=dash.Dash(requests_pathname_prefix='/app/dash/',external_stylesheets=[dbc.themes.COSMO])


    controls = dbc.Card(
    [
        dbc.FormGroup(
            [
                dbc.Label("Ticker"),
                dcc.Dropdown(
                    id="ticker",
                 
                ),
            ]
        ),






    dbc.FormGroup(
        [
            dbc.Label("Type"),
            dcc.RadioItems(
                id="type",
                options=[
                    
                    {"label":"Adjusted" ,"value":"adjusted"},
                    {"label":"Unadjusted" ,"value":"unadjusted"},
                    
                    ],
                    value="adjusted",
                ),
            ]
        ),








    dbc.FormGroup([
        dbc.Label("Time-Frame"),
        dcc.RadioItems(
        id="tf",
        options=[
        
        {"label":"Daily" ,"value":"day"},
        {"label":"Minute" ,"value":"minute"},
        {"label":"Hourly" ,"value":"hourly"}
         ],
        value="day",),]),
    

 

            

            ],
            body=True,
        )
    

            
    app.layout = dbc.Container(
        [
        html.H1("Trading"),
        html.Hr(),
        dbc.Row([dcc.Location(id="url",refresh=False)]),

        dbc.Row(
            [
                dbc.Col(controls, md=4),
                dbc.Col(dcc.Graph(id="cluster-graph"), md=8),
            ],
            align="center",
            ),
        ],
        fluid=True,
        )

    @app.callback([
        Output("ticker", "options"),
        Output("cluster-graph","figure")

        ],
        
        [
        Input("url", "pathname"),
        ],
    )


    def read_tickers(pathname):
        
        if pathname == "/app/dash/" :
            PRICE_URL= "http://127.0.0.1:8000/api/prices/stocks/{}/minute"

            data=requests.get("http://127.0.0.1:8000/api/tickers")

            data=data.json()


            options=[ {"label":ticker["ticker"], "value": ticker["ticker"]} for ticker in data]
            print(data[0]["ticker"])
            
            prices=requests.get(PRICE_URL.format("AAAP"))

            print(prices.json())

            figure=[1,2,3,4,5,6]
            
            return options,figure





    











    





        



























    # @app.callback(inputs=dict( pathname=dl.Input(location,component_property="pathname")),output=dict(dropdown=dl.Output(drpdown,component_property="options")))

    # 

    
    return app

          








   















# if __name__ == '__main__':
#     app.run_server(debug=True)