  
from typing import List, Optional
from pydantic import BaseModel
from datetime import date, datetime, time, timedelta


class SymbolIn(BaseModel):

    
    ticker :Optional[str]  
    name :Optional[str]                    
    compositeFigi :Optional[str]
    shareClassFigi : Optional[str]
    exchCode : Optional[str]         
    exSymbol : Optional[str]
    primaryExch : Optional[str]
    securityType: Optional[str]
    securityType2 : Optional[str]
    market : Optional[str]
    type : Optional[str]
    internal_code:Optional[int]
    marketSector :Optional[str]
    currency :Optional[str]
    country:Optional[str]         
    active :Optional[str]
    tags : Optional[List]
    similar :Optional[List]


class SymbolOut(SymbolIn):
    unique_id :Optional[str]
    class Config:
        orm_mode = True


class CompanyIn(BaseModel):
    compositeFigi:str
    name: Optional[str]
    ticker: Optional[str]
    cik : Optional[str]
    sic :Optional[str]
    industry:Optional[str]
    sector:Optional[str]
    url :Optional[str]
    description :Optional[str]
    tags :Optional[List]
    similar :Optional[List]



class CompanyOut(CompanyIn):
    
    updated_at:Optional[datetime]

    class Config:

        orm_mode=True




 