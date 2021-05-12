from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sys,os,pathlib
from fastapi_pagination import LimitOffsetPage, Page, add_pagination
from fastapi.middleware.wsgi import WSGIMiddleware

# we're appending the app directory to our path here so that we can import config easily
sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))


from app.api.Routes.web import router as web_api_router
from app.api.Routes.restapi import router as api_router
from app.core.config import ASSET_DIR

from app.sub_app.dash import dash_app




def get_application():

     #fastapi app decleration

     app = FastAPI(title="Trade-App", version="1.0.0")



    # add Cors middleware to pastapi


     origins = [
          "http://localhost",
          "http://localhost:8080",
          ]

     app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
     )

    
     #munting static fiiels to fastapi
     app.mount("/Trading-final/trading/app/assets", StaticFiles(directory="/Trading-final/trading/app/assets"), name="static")
     
     # add routers to fastapi
     app.include_router(web_api_router,prefix="/app")
     app.include_router(api_router,prefix="/api")

     #add pagination to fastapi


     add_pagination(app)


     #mount dash on fastapi app

     d_app=dash_app()


     app.mount("/app/dash", WSGIMiddleware(d_app.server))
     return app



#call to get app declared 


app = get_application()



