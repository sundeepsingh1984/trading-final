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
from functools import lru_cache

import plotly.graph_objs as go

import plotly.express as px


import dash_bootstrap_components as dbc


def create_app():
    
    app=dash.Dash(requests_pathname_prefix='/app/dash/',external_stylesheets=[dbc.themes.BOOTSTRAP])
    

    controls = dbc.Card([
        dbc.FormGroup([
                dbc.Label("Asset-Type"),
                dcc.RadioItems(
                    id="asset_type",
                    options=[
                        
                        {"label":"Stocks" ,"value":"STOCKS"},
                        {"label":"Indices" ,"value":"INDICES"},

                        {"label":"Forex","value":"FX"},

                        {"label":"Crypto","value":"CRYPTO"},
                        
                        ],
                        value="STOCKS",
                    ),
                ]
            ),

        dbc.FormGroup(
            [
                dbc.Label("Ticker"),
                dcc.Dropdown(
                    id="ticker",
                 
                ),
            ]
        ),

        

        dbc.FormGroup([
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

    body=True,)
    

            
    app.layout = dbc.Container([
        html.H1("Trading"),
        html.Hr(),
        dbc.Row([dcc.Location(id="url",refresh=False)]),
        dbc.Row([
            dbc.Col(controls, md=4),
            dbc.Col([
                html.H3(id="stock_name"), 
                dcc.Graph(id="open-close-graph"),
                dcc.Graph(id="high-low-graph"),], md=8)],)],fluid=True)



    @lru_cache









    @app.callback([ Output("ticker", "value"),Output("ticker", "options")], [Input("asset_type" , "value")] )

    def updateOptions(asset_type):

        tickers=request_ticker(asset_type)
        options=[ {"label":ticker["ticker"], "value": ticker["ticker"]} for ticker in tickers]

        return tickers[0]["ticker"],options




    @app.callback([
        Output("ticker", "options"),
        Output("ticker", "value"),
        Output("open-close-graph","figure"),
        Output("high-low-graph","figure"),
        Output("stock_name","children"),]
        ,
        [
        Input("url", "pathname")
        ],
        )


    def read_tickers(pathname):

        if pathname == "/app/dash/" :
            
            tickers=request_ticker("STOCKS")
            
            options=[ {"label":ticker["ticker"], "value": ticker["ticker"]} for ticker in tickers]
            df=request_prices("AAAP")

            fig1=create_fig(df,"datetime",["open","close","vw_avg_price"],"volume","Closing-Opening Price")
            fig2=create_fig(df,"datetime",["low","high","vw_avg_price"],"volume","Low-High Prices")

            return options,tickers[0]["ticker"],fig1,fig2,tickers[0]["ticker"]





        





    return app




def create_fig(df,x_axis,y_axis,hover_name,title):
    
    fig = px.line(df, x=x_axis,y= y_axis,hover_name=hover_name,title=title)
    return fig

@lru_cache

def request_ticker(market):
    URL="http://127.0.0.1:8000/api/tickers?market={}".format(market)
    data=requests.get(URL)
    return data.json()


def request_prices(ticker,asset_type='stocks',timeframe="minute"):
    URL="http://127.0.0.1:8000/api/prices/{}/{}/{}".format(asset_type,ticker,timeframe)
    data=requests.get(URL)
    return pd.DataFrame.from_dict(data.json())









          








   















# if __name__ == '__main__':
#     app.run_server(debug=True)