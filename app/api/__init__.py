from fastapi import APIRouter
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from api.Routes.trading import router as trading_router



router=APIRouter()

router.include_router(trading_router,prefix="/trading",tags=["trading"])
