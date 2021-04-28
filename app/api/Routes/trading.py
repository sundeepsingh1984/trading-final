from typing	import List
from fastapi import APIRouter

router=APIRouter()



@router.get("/")

def index():
    print("Hello World")
    return [1,2,3,4,5,]