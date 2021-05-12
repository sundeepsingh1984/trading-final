from databases import DatabaseURL
from starlette.config import Config
from starlette.datastructures import Secret
import pathlib
import sys

# we're appending the app directory to our path here so that we can import config easily
sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))


"""
--------------------------------------------------------------------------------------------------------------------------------------

                                                         APP CONFIG

-------------------------------------------------------------------------------------------------------------------------------------

"""
config = Config(".env")
PROJECT_NAME = "Trading-app"
VERSION = "1.0.0"
API_PREFIX = "/api"
SECRET_KEY = config("SECRET_KEY", cast=Secret, default="CHANGEME")
ROOT_DIR="/app/"
ASSET_DIR=config("ASSET_DIR", cast=str, default=str(pathlib.Path(__file__).resolve().parents[2])+ROOT_DIR+"assets/")
sys.path.append(str(pathlib.Path(__file__).resolve().parents[2])+ROOT_DIR)
sys.path.append(str(pathlib.Path(__file__).resolve().parents[2])+ASSET_DIR)
"""
----------------------------------------------------------------------------------------------------------------------------

                                                      DATABASE CONFIG DETAILS

---------------------------------------------------------------------------------------------------------------------------------
"""
POSTGRES_USER = config("POSTGRES_USER", cast=str,default="postgres")
POSTGRES_PASSWORD = config("POSTGRES_PASSWORD", cast=Secret,default="Sunny@123")
POSTGRES_SERVER = config("POSTGRES_SERVER", cast=str, default="localhost")
POSTGRES_PORT = config("POSTGRES_PORT", cast=str, default="5432")
POSTGRES_DB = config("POSTGRES_DB", cast=str, default="tradingnew")
DATABASE_URL_ASYNC = config(
    "DB_URL",
    cast=DatabaseURL,
    default=f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
)
DATABASE_URL = config(
    "DB_URL",
    cast=DatabaseURL,
    default=f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
)


"""
--------------------------------------------------------------------------------------------------------------------------------------------------
                                                       OPENFIGI CONFIG DETAILS
--------------------------------------------------------------------------------------------------------------------------------------------------

"""
OPENFIGI_URL = config("OPEN_FIGI_URL", cast=str,default="")
OPENFIGI_KEY = config("OPEN_FIGI_KEY", cast=str,default="")
