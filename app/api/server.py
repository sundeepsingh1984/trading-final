from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from api.Routes.trading import router as api_router


def get_application():
    app = FastAPI(title="Trade-App", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


    app.include_router(api_router,prefix="/api")

    return app


app = get_application()



