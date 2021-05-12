import sys,os,pathlib

# we're appending the app directory to our path here so that we can import config easily
sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date,DateTime,UniqueConstraint, ForeignKey, Sequence, Text, Boolean, Float, Enum, BigInteger,TIMESTAMP

from sqlalchemy.dialects.postgresql import ARRAY

from sqlalchemy.dialects import postgresql

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.event import listens_for
import enum

import app.core.config as config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dictalchemy import DictableModel,make_class_dictable



Base = declarative_base()

make_class_dictable(Base)







class User(Base):
    #table name

    __tablename__="users"

    #primary key

    id=Column("id",Integer,primary_key=True,index=True)

    #columns
    name=Column("name",String,nullable=False,index=True)
    email = Column("email", String,index=True)
    password = Column("password",String,index=True)
    created_at=Column("created_at",DateTime(timezone=True),server_default=func.now())
    updated_at=Column("updated_at",DateTime(timezone=True),server_default=func.now())


    #relations

    vendor_details=relationship("UsersVendorDetails",backref="users")
    strategies=relationship("Strategies",backref="users")






    def __repr__(self):
        return "<User(name='{}',email='{}', password='{}', alpaca_secret='{}', alpaca_key='{}', created_at={}, updated_at={})>" \
            .format(self.name,self.email,self.password, self.alpaca_secret, self.alpaca_key, self.created_at, self.updated_at)









#table for vendor details of all users
class UsersVendorDetails(Base):

    # tablename

    __tablename__="user_vendors_details"

    # primary key
    id=Column(Integer,primary_key=True,index=True)

    #columns
    user_id=Column(Integer,ForeignKey("users.id",onupdate="CASCADE",ondelete="CASCADE"))
    vendor_id=Column(Integer,ForeignKey('vendor.id',onupdate='CASCADE',ondelete='CASCADE'))
    secret_key=Column(String,nullable=True)
    secret_id=Column(String,nullable=True)







class Strategies(Base):

    #table name

    __tablename__="user_strategies"

    #primary key

    id=Column(Integer,primary_key=True,index=True,autoincrement=True)

    # foreign keys
    created_by=Column(Integer,ForeignKey("users.id"))


    # columns
    strategy_name=Column(String,nullable=False)
    backtested=Column(Boolean,default=False)
    backtest_id=Column(ARRAY(Integer))
    created_at=Column(DateTime(timezone=True),server_default=func.now())

    #relations

    backtest_details=relationship("Backtests",backref="user_strategies")







class Backtests(Base):

    #table name

    __tablename__="backtests"

    #primary key

    backtest_id=Column(Integer,primary_key=True,index=True,autoincrement=True)

    #foreign key
    strategy_id=Column(Integer,ForeignKey("user_strategies.id"))

    #columns

    avg_return_mon=Column(Float, nullable=True)
    sd_monthly=Column(Float,nullable=True)
    avg_return_annual=Column(Float,nullable=True)
    avg_std=Column(Float,nullable=True)
    sharpe_ratio=Column(Float,nullable=True)
    colmar_ratio=Column(Float,nullable=True)
    worst_monthly_drw_dwn=Column(Float,nullable=True)
    best_month_performance=Column(Float,nullable=True)
    worst_drw_down=Column(Float,nullable=True)







class Symbol(Base):

    #table name

    __tablename__="symbol"


    #primary key

    unique_id = Column("unique_id", String, primary_key=True) #Internal


    #columns

    ticker = Column("ticker", String)               # from Polygons and Alpaca
    name =Column("name",String)                     # from Openfigi, Polygons and Alpaca
    compositeFigi = Column("compositeFigi",String)  #OpenFigi
    shareClassFigi = Column("shareClassFigi", String)#OpenFigi
    exchCode = Column("exchCode", String)           #OpenFigi
    exSymbol = Column("exSymbol", String)        #from Polygon
    primaryExch = Column("primaryExch", String)  #from Polygon
    securityType= Column("securityType",String)     #OpenFigi
    securityType2 = Column("securityType2",String)  #OpenFigi
    market = Column("market", String)            #from Polygon
    type = Column("type", String)                #from Polygon
    internal_code = Column("internal_code", Integer)   #Internal
    marketSector = Column("marketSector", String)    #OPENFIGI & 'sector' from Polygon Ticker Details
    currency = Column("currency", String)        #from Polygon
    country = Column("country", String)          #from Polygon
    active = Column("active", String)            #from Polygon
    tags = Column("tags",postgresql.ARRAY(String))
    similar = Column("similar",postgresql.ARRAY(String))
    created_at=Column("created_at",DateTime(timezone=True),server_default=func.now())
    updated_at=Column("updated_at",DateTime(timezone=True) , onupdate=func.now())

    # relations


    company=relationship("Company",backref="symbol")
    forex=relationship('Forex',backref="symbol")
    indices=relationship("Indices",backref="symbol")
    crypto=relationship("Crypto",backref="symbol")





class Company(Base):

    #table name
    __tablename__="company"






    #primary key

    compositeFigi = Column(String, ForeignKey('symbol.unique_id',onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)



    #columns
    name = Column("name", String)
    ticker = Column("ticker", String)
    cik = Column("cik", String)
    sic = Column("sic", String)  #for Industry classification
    industry = Column("industry", String)
    sector = Column("sector", String)
    url = Column("url", String)
    description = Column("description", String)
    tags = Column("tags",ARRAY(String))
    similar = Column("similar",ARRAY(String))
    created_at=Column("created_at",DateTime(timezone=True),server_default=func.now())
    updated_at=Column("updated_at",DateTime(timezone=True) , onupdate=func.now())



    #relations

    splits=relationship("StockSplits",backref="company",order_by='desc(StockSplits.exDate)', lazy='dynamic')
    dividents=relationship("StockDividents",backref="company",order_by='desc(StockDividents.exDate)', lazy='dynamic')

    price_daily_adjusted=relationship("StockPricesDailyAdj",backref="company",order_by='desc(StockPricesDailyAdj.datetime)', lazy='dynamic')
    price_daily_unadjusted=relationship("StockPricesDailyUnadj",backref="company",order_by='desc(StockPricesDailyUnadj.datetime)', lazy='dynamic')

    prices_hourly_adjusted=relationship("StockPricesHourlyAdj",backref="company",order_by='desc(StockPricesHourlyAdj.datetime)', lazy='dynamic')
    prices_hourly_unadjusted=relationship("StockPricesHourlyUnadj",backref="company",order_by='desc(StockPricesHourlyUnadj.datetime)', lazy='dynamic')

    prices_min_adjusted=relationship("StockPricesMinuteAdj",backref="company",order_by='desc(StockPricesMinuteAdj.datetime)', lazy='dynamic')
    prices_min_unadjusted=relationship("StockPricesMinUnadj",backref="company",order_by='desc(StockPricesMinUnadj.datetime)', lazy='dynamic')

    quotes=relationship("Quotes",backref="company",order_by='desc(Quotes.sip_timestamp)', lazy='dynamic')
    trades=relationship("Trades",backref="company",order_by='desc(Trades.sip_timestamp)', lazy='dynamic')


    financials=relationship("Financials",backref="company",order_by='desc(Financials.calender_date)', lazy='dynamic')


class Forex(Base):

    #table name
    __tablename__="forex"

    #primary key






    ticker = Column("ticker",String, ForeignKey('symbol.unique_id',onupdate='CASCADE',ondelete='CASCADE'), primary_key=True)
    vendor_id=Column(Integer,ForeignKey("vendor.id"))


    #columns

    name =Column("name",String)
    currencyName = Column("currencyName", String)
    currency = Column("currency", String)
    baseName = Column("baseName", String)
    base = Column("base", String)

    #relations
    price_daily_adjusted=relationship("ForexPricesDailyAdj",backref="forex",order_by='desc(ForexPricesDailyAdj.datetime)', lazy='dynamic')
    price_daily_unadjusted=relationship("ForexPricesDailyUnadj",backref="forex",order_by='desc(ForexPricesDailyUnadj.datetime)', lazy='dynamic')

    prices_hourly_adjusted=relationship("ForexPricesHourlyAdj",backref="forex",order_by='desc(ForexPricesHourlyAdj.datetime)', lazy='dynamic')
    prices_hourly_unadjusted=relationship("ForexPricesHourlyUnadj",backref="forex",order_by='desc(ForexPricesHourlyUnadj.datetime)', lazy='dynamic')

    prices_min_adjusted=relationship("ForexPricesMinAdj",backref="forex",order_by='desc(ForexPricesMinAdj.datetime)', lazy='dynamic')
    prices_min_unadjusted=relationship("ForexPricesMinUnadj",backref="forex",order_by='desc(ForexPricesMinUnadj.datetime)', lazy='dynamic')




class ForexPricesMinAdj(Base):

    #table name

    __tablename__="forex_prices_min_adj"


    #tableAttr

    __table_args__ = tuple([UniqueConstraint('vendor_id', 'forex_id', "datetime")])






    #primary key

    id=Column(Integer,index=True,primary_key=True,autoincrement=True)


    #foreign keys

    unique_id=Column(String,ForeignKey("symbol.unique_id"))
    vendor_id=Column(Integer,ForeignKey("vendor.id"))
    forex_id=Column(String,ForeignKey("forex.ticker"))


    #columns


    datetime=Column(TIMESTAMP,nullable=False)
    open=Column(Float,nullable=False)
    high=Column(Float,nullable=False)
    low=Column(Float,nullable=False)
    close=Column(Float,nullable=False)
    volume=Column(BigInteger,nullable=False)
    vw_avg_price=Column(Float,nullable=True)









class Indices(Base):

    #table name
    __tablename__="indices"

    #primary key

    ticker = Column("ticker",String, ForeignKey('symbol.unique_id',onupdate='CASCADE',ondelete='CASCADE'), primary_key=True)
    vendor_id=Column(Integer,ForeignKey("vendor.id"))
    #columns

    name =Column("name",String)
    holiday = Column("holiday ", String)
    assettype = Column("assettype ", String)
    entitlement = Column("entitlement ", String)
    disseminationfreq = Column("disseminationfreq ", String)
    dataset = Column("dataset ", String)
    schedule = Column("schedule ", String)
    brand = Column("brand ", String)
    series = Column("series ", String)

    #relations

    price_daily=relationship("IndicesPriceDaily",backref="indices",order_by='desc(IndicesPriceDaily.datetime)', lazy='dynamic')

    prices_hourly=relationship("IndicesPriceHourly",backref="indices",order_by='desc(IndicesPriceHourly.datetime)', lazy='dynamic')

    prices_min=relationship("IndicesPriceMin",backref="indices",order_by='desc(IndicesPriceMin.datetime)', lazy='dynamic')









class Crypto(Base):

    #table name
    __tablename__="crypto"

    #primary key

    ticker = Column("ticker",String, ForeignKey('symbol.unique_id',onupdate='CASCADE',ondelete='CASCADE'), primary_key=True)
    vendor_id=Column(Integer,ForeignKey("vendor.id"))
    #columns

    name =Column("name",String)
    currencyName = Column("currencyName", String)
    currency = Column("currency", String)
    baseName = Column("baseName", String)
    base = Column("base", String)


    #relations

    price_daily_adjusted=relationship("CryptoPricesDailyAdj",backref="crypto",order_by='desc(CryptoPricesDailyAdj.datetime)', lazy='dynamic')
    price_daily_unadjusted=relationship("CryptoPricesDailyUnadj",backref="crypto",order_by='desc(CryptoPricesDailyUnadj.datetime)', lazy='dynamic')

    prices_hourly_adjusted=relationship("CryptoPricesHourlyAdj",backref="crypto",order_by='desc(CryptoPricesHourlyAdj.datetime)', lazy='dynamic')
    prices_hourly_unadjusted=relationship("CryptoPricesHourlyUnadj",backref="crypto",order_by='desc(CryptoPricesHourlyUnadj.datetime)', lazy='dynamic')

    prices_min_adjusted=relationship("CryptoPricesMinAdj",backref="crypto",order_by='desc(CryptoPricesMinAdj.datetime)', lazy='dynamic')
    prices_min_unadjusted=relationship("CryptoPricesMinUnadj",backref="crypto",order_by='desc(CryptoPricesMinUnadj.datetime)', lazy='dynamic')













class Vendor(Base):
    #table name
    __tablename__="vendor"

    #table arguments
    __table_args__ = tuple([UniqueConstraint('id')])

    #primary key

    id=Column("id",Integer,primary_key=True,autoincrement=True)


    #columns

    name =Column("name",String,nullable=False)
    created_at=Column("created_at",DateTime(timezone=True),server_default=func.now())
    updated_at=Column("updated_at",DateTime(timezone=True) , onupdate=func.now())







class StockPricesDailyAdj(Base):

    #table name

    __tablename__="stock_prices_daily_adj"


    #tableAttr

    __table_args__ = tuple([UniqueConstraint('vendor_id', 'company_id', "datetime")])




    #primary key

    id=Column(Integer,index=True,primary_key=True,autoincrement=True)


    #foreign keys

    unique_id=Column(String,ForeignKey("symbol.unique_id"))
    vendor_id=Column(Integer,ForeignKey("vendor.id"))
    company_id=Column(String,ForeignKey("company.compositeFigi"))


    #columns


    datetime=Column(TIMESTAMP,nullable=False)
    open=Column(Float,nullable=False)
    high=Column(Float,nullable=False)
    low=Column(Float,nullable=False)
    close=Column(Float,nullable=False)
    volume=Column(BigInteger,nullable=False)
    vw_avg_price=Column(Float,nullable=True)





class StockPricesDailyUnadj(Base):

    #table name

    __tablename__="stock_prices_daily_unadj"



    #tableAttr

    __table_args__ = tuple([UniqueConstraint('vendor_id', 'company_id', "datetime")])




    #primary key

    id=Column(Integer,index=True,primary_key=True,autoincrement=True)


    #foreign keys

    unique_id=Column(String,ForeignKey("symbol.unique_id"))
    vendor_id=Column(Integer,ForeignKey("vendor.id"))
    company_id=Column(String,ForeignKey("company.compositeFigi"))


    #columns


    datetime=Column(TIMESTAMP,nullable=False)
    open=Column(Float,nullable=False)
    high=Column(Float,nullable=False)
    low=Column(Float,nullable=False)
    close=Column(Float,nullable=False)
    volume=Column(BigInteger,nullable=False)
    vw_avg_price=Column(Float,nullable=True)








class StockPricesHourlyAdj(Base):

    #table name

    __tablename__="stock_prices_hourly_adj"



    #tableAttr

    __table_args__ = tuple([UniqueConstraint('vendor_id', 'company_id', "datetime")])




    #primary key

    id=Column(Integer,index=True,primary_key=True,autoincrement=True)


    #foreign keys

    unique_id=Column(String,ForeignKey("symbol.unique_id"))
    vendor_id=Column(Integer,ForeignKey("vendor.id"))
    company_id=Column(String,ForeignKey("company.compositeFigi"))


    #columns


    datetime=Column(TIMESTAMP,nullable=False)
    open=Column(Float,nullable=False)
    high=Column(Float,nullable=False)
    low=Column(Float,nullable=False)
    close=Column(Float,nullable=False)
    volume=Column(BigInteger,nullable=False)
    vw_avg_price=Column(Float,nullable=True)






class StockPricesHourlyUnadj(Base):

    #table name

    __tablename__="stock_prices_hourly_unadj"


    #tableAttr

    __table_args__ = tuple([UniqueConstraint('vendor_id', 'company_id', "datetime")])




    #primary key

    id=Column(Integer,index=True,primary_key=True,autoincrement=True)


    #foreign keys

    unique_id=Column(String,ForeignKey("symbol.unique_id"))
    vendor_id=Column(Integer,ForeignKey("vendor.id"))
    company_id=Column(String,ForeignKey("company.compositeFigi"))


    #columns


    datetime=Column(TIMESTAMP,nullable=False)
    open=Column(Float,nullable=False)
    high=Column(Float,nullable=False)
    low=Column(Float,nullable=False)
    close=Column(Float,nullable=False)
    volume=Column(BigInteger,nullable=False)
    vw_avg_price=Column(Float,nullable=True)










class StockPricesMinuteAdj(Base):

    #table name

    __tablename__="stock_prices_min_adj"



    #tableAttr

    __table_args__ = tuple([UniqueConstraint('vendor_id', 'company_id', "datetime")])




    #primary key

    id=Column(Integer,index=True,primary_key=True,autoincrement=True)


    #foreign keys

    unique_id=Column(String,ForeignKey("symbol.unique_id"))
    vendor_id=Column(Integer,ForeignKey("vendor.id"))
    company_id=Column(String,ForeignKey("company.compositeFigi"))


    #columns


    datetime=Column(TIMESTAMP,nullable=False)
    open=Column(Float,nullable=False)
    high=Column(Float,nullable=False)
    low=Column(Float,nullable=False)
    close=Column(Float,nullable=False)
    volume=Column(BigInteger,nullable=False)
    vw_avg_price=Column(Float,nullable=True)






class StockPricesMinUnadj(Base):

    #table name

    __tablename__="stock_prices_min_unadj"


    #tableAttr

    __table_args__ = tuple([UniqueConstraint('vendor_id', 'company_id', "datetime")])





    #primary key

    id=Column(Integer,index=True,primary_key=True,autoincrement=True)


    #foreign keys

    unique_id=Column(String,ForeignKey("symbol.unique_id"))
    vendor_id=Column(Integer,ForeignKey("vendor.id"))
    company_id=Column(String,ForeignKey("company.compositeFigi"))


    #columns


    datetime=Column(TIMESTAMP,nullable=False)
    open=Column(Float,nullable=False)
    high=Column(Float,nullable=False)
    low=Column(Float,nullable=False)
    close=Column(Float,nullable=False)
    volume=Column(BigInteger,nullable=False)
    vw_avg_price=Column(Float,nullable=True)








class StockSplits(Base):

    #table name

    __tablename__='stock_splits'

    #primary key

    id=Column(Integer,index=True,primary_key=True,autoincrement=True)


    #foreign key

    unique_id=Column(String,ForeignKey("symbol.unique_id"))
    company_id=Column(String,ForeignKey("company.compositeFigi"))
    vendor_id=Column(Integer,ForeignKey("vendor.id"))

    #columns


    ticker=Column(String,nullable=False)
    exDate=Column(String,nullable=True)
    paymentDate=Column(String,nullable=True)
    declaredDate=Column(String,nullable=True)
    ratio=Column(Float,nullable=True)
    tofactor=Column(Integer,nullable=True)








class StockDividents(Base):

    #table name

    __tablename__='stock_dividents'

    #primary key

    id=Column(Integer,index=True,primary_key=True,autoincrement=True)


    #foreign key

    unique_id=Column(String,ForeignKey("symbol.unique_id"))
    company_id=Column(String,ForeignKey("company.compositeFigi"))
    vendor_id=Column(Integer,ForeignKey("vendor.id"))

    #columns


    ticker=Column(String,nullable=False)
    exDate=Column(String,nullable=True)
    paymentDate=Column(String,nullable=True)
    recordDate=Column(String,nullable=True)
    amount=Column(Float,nullable=False)












class VendorSymbol(Base):
    __tablename__="vendorsymbol"
    __table_args__ = tuple([UniqueConstraint('vendor_id', 'unique_id')])

    id=Column("id",Integer,primary_key=True,autoincrement=True)
    vendor_symbol = Column("vendor_symbol", String)

    unique_id = Column(String, ForeignKey('symbol.unique_id'))
    vendor_id = Column(Integer, ForeignKey('vendor.id'))

    symbol = relationship("Symbol", backref="vendorsymbol")
    vendor = relationship("Vendor", backref="vendorsymbol")

    created_at=Column("created_at",DateTime(timezone=True),server_default=func.now())
    updated_at=Column("updated_at",DateTime(timezone=True) , onupdate=func.now())








class Quotes(Base):

    #table name

    __tablename__="quotes"


    #primary key

    id=Column(Integer,index=True,primary_key=True,autoincrement=True)

    #foreign key


    vendor_id=Column(Integer,ForeignKey("vendor.id"))
    company_id=Column(String,ForeignKey("company.compositeFigi"))
    symbol_id=Column(String,ForeignKey("symbol.unique_id"))


    #columns


    sip_timestamp=Column(TIMESTAMP,nullable=False)
    participants_timestamp=Column(TIMESTAMP,nullable=False)
    indicator=Column(ARRAY(Integer),nullable=True)
    ask_price=Column(Float,nullable=False)
    ask_exchange=Column(Integer,nullable=False)
    trf_timestamp=Column(TIMESTAMP,nullable=False)
    sequence_no=Column(Integer,nullable=False)
    conditions=Column(ARRAY(Integer),nullable=True)
    bid_price=Column(Float,nullable=False)
    bid_size=Column(BigInteger,nullable=False)
    bid_exchange=Column(Integer,nullable=True)
    ask_size=Column(BigInteger,nullable=False)
    listed_on=Column(String,nullable=False)



class Trades(Base):


    #table name

    __tablename__ = "trades"

    #primary key

    id=Column(Integer,primary_key=True,autoincrement=True,index=True)

    #foreign key

    vendor_id=Column(Integer,ForeignKey("vendor.id"))
    company_id=Column(String,ForeignKey("company.compositeFigi"))
    symbol_id=Column(String,ForeignKey("symbol.unique_id"))

    #columns

    exchange=Column(Integer,nullable=False)
    price=Column(Float,nullable=False)
    trade_id=Column(String,nullable=False)
    correction=Column(Integer,nullable=False)
    trf_id=Column(Integer,nullable=False)
    sip_timestamp=Column(TIMESTAMP,nullable=False)
    participants_timestamp=Column(TIMESTAMP,nullable=False)
    trf_timestamp=Column(TIMESTAMP,nullable=False)
    sequence_no=Column(BigInteger,nullable=False)
    conditions=Column(ARRAY(Integer),nullable=True)
    size=Column(BigInteger,nullable=False)
    listed_on=Column(String,nullable=False)






class News(Base):

    #table name

    __tablename__="news"


    #primary key

    id=Column(Integer,primary_key=True,index=True,autoincrement=True)


    #foreign key


    vendor_id=Column(Integer,ForeignKey("vendor.id"))
    # company_id=Column(ARRAY(String),ForeignKey("company.compositeFigi"))
    # symbol_id=Column(ARRAY(String),ForeignKey("symbol.unique_id"))



    #columns

    datetime=Column(String,nullable=True)
    symbols=Column(ARRAY(String),nullable=True)
    title=Column(String,nullable=True)
    url=Column(String,nullable=True)
    source=Column(String,nullable=True)
    summary=Column(String,nullable=True)
    image=Column(String,nullable=True)
    keywords=Column(ARRAY(String),nullable=True)





class ForexPricesMinUnadj(Base):

    #table name

    __tablename__="forex_prices_min_unadj"


    #tableAttr

    __table_args__ = tuple([UniqueConstraint('vendor_id', 'forex_id', "datetime")])





    #primary key

    id=Column(Integer,index=True,primary_key=True,autoincrement=True)


    #foreign keys

    unique_id=Column(String,ForeignKey("symbol.unique_id"))
    vendor_id=Column(Integer,ForeignKey("vendor.id"))
    forex_id=Column(String,ForeignKey("forex.ticker"))


    #columns


    datetime=Column(TIMESTAMP,nullable=False)
    open=Column(Float,nullable=False)
    high=Column(Float,nullable=False)
    low=Column(Float,nullable=False)
    close=Column(Float,nullable=False)
    volume=Column(BigInteger,nullable=False)
    vw_avg_price=Column(Float,nullable=True)









class ForexPricesHourlyUnadj(Base):

    #table name

    __tablename__ = "forex_prices_hourly_unadj"


    #tableAttr

    __table_args__ = tuple([UniqueConstraint('vendor_id', 'forex_id', "datetime")])






    #primary key

    id=Column(Integer,index=True,primary_key=True,autoincrement=True)


    #foreign keys

    unique_id=Column(String,ForeignKey("symbol.unique_id"))
    vendor_id=Column(Integer,ForeignKey("vendor.id"))
    forex_id=Column(String,ForeignKey("forex.ticker"))


    #columns


    datetime=Column(TIMESTAMP,nullable=False)
    open=Column(Float,nullable=False)
    high=Column(Float,nullable=False)
    low=Column(Float,nullable=False)
    close=Column(Float,nullable=False)
    volume=Column(BigInteger,nullable=False)
    vw_avg_price=Column(Float,nullable=True)








class ForexPricesHourlyAdj(Base):

    #table name

    __tablename__="forex_prices_hourly_adj"


    #tableAttr
    __table_args__ = tuple([UniqueConstraint('vendor_id', 'forex_id', "datetime")])






    #primary key

    id=Column(Integer,index=True,primary_key=True,autoincrement=True)


    #foreign keys

    unique_id=Column(String,ForeignKey("symbol.unique_id"))
    vendor_id=Column(Integer,ForeignKey("vendor.id"))
    forex_id=Column(String,ForeignKey("forex.ticker"))


    #columns


    datetime=Column(TIMESTAMP,nullable=False)
    open=Column(Float,nullable=False)
    high=Column(Float,nullable=False)
    low=Column(Float,nullable=False)
    close=Column(Float,nullable=False)
    volume=Column(BigInteger,nullable=False)
    vw_avg_price=Column(Float,nullable=True)








class ForexPricesDailyAdj(Base):

    #table name

    __tablename__="forex_prices_daily_adj"


    #tableAttr

    __table_args__ = tuple([UniqueConstraint('vendor_id', 'forex_id', "datetime")])







    #primary key

    id=Column(Integer,index=True,primary_key=True,autoincrement=True)


    #foreign keys

    unique_id=Column(String,ForeignKey("symbol.unique_id"))
    vendor_id=Column(Integer,ForeignKey("vendor.id"))
    forex_id=Column(String,ForeignKey("forex.ticker"))


    #columns


    datetime=Column(TIMESTAMP,nullable=False)
    open=Column(Float,nullable=False)
    high=Column(Float,nullable=False)
    low=Column(Float,nullable=False)
    close=Column(Float,nullable=False)
    volume=Column(BigInteger,nullable=False)
    vw_avg_price=Column(Float,nullable=True)







class ForexPricesDailyUnadj(Base):

    #table name

    __tablename__="forex_prices_daily_Unadj"


    #tableAttr

    __table_args__ = tuple([UniqueConstraint('vendor_id', 'forex_id', "datetime")])







    #primary key

    id=Column(Integer,index=True,primary_key=True,autoincrement=True)


    #foreign keys

    unique_id=Column(String,ForeignKey("symbol.unique_id"))
    vendor_id=Column(Integer,ForeignKey("vendor.id"))
    forex_id=Column(String,ForeignKey("forex.ticker"))


    #columns


    datetime=Column(TIMESTAMP,nullable=False)
    open=Column(Float,nullable=False)
    high=Column(Float,nullable=False)
    low=Column(Float,nullable=False)
    close=Column(Float,nullable=False)
    volume=Column(BigInteger,nullable=False)
    vw_avg_price=Column(Float,nullable=True)








class CryptoPricesMinAdj(Base):

    #table name

    __tablename__="crypto_prices_min_adj"


    #tableAttr

    __table_args__ = tuple([UniqueConstraint('vendor_id', 'crypto_id', "datetime")])







    #primary key

    id=Column(Integer,index=True,primary_key=True,autoincrement=True)


    #foreign keys

    unique_id=Column(String,ForeignKey("symbol.unique_id"))
    vendor_id=Column(Integer,ForeignKey("vendor.id"))
    crypto_id=Column(String,ForeignKey("crypto.ticker"))


    #columns


    datetime=Column(TIMESTAMP,nullable=False)
    open=Column(Float,nullable=False)
    high=Column(Float,nullable=False)
    low=Column(Float,nullable=False)
    close=Column(Float,nullable=False)
    volume=Column(BigInteger,nullable=False)
    vw_avg_price=Column(Float,nullable=True)








class CryptoPricesMinUnadj(Base):

    #table name

    __tablename__="crypto_prices_min_unadj"


    #tableAttr

    __table_args__ = tuple([UniqueConstraint('vendor_id', 'crypto_id', "datetime")])







    #primary key

    id=Column(Integer,index=True,primary_key=True,autoincrement=True)


    #foreign keys

    unique_id=Column(String,ForeignKey("symbol.unique_id"))
    vendor_id=Column(Integer,ForeignKey("vendor.id"))
    crypto_id=Column(String,ForeignKey("crypto.ticker"))


    #columns


    datetime=Column(TIMESTAMP,nullable=False)
    open=Column(Float,nullable=False)
    high=Column(Float,nullable=False)
    low=Column(Float,nullable=False)
    close=Column(Float,nullable=False)
    volume=Column(BigInteger,nullable=False)
    vw_avg_price=Column(Float,nullable=True)






class CryptoPricesHourlyUnadj(Base):

    #table name

    __tablename__="crypto_prices_hourly_unadj"


    #tableAttr

    __table_args__ = tuple([UniqueConstraint('vendor_id', 'crypto_id', "datetime")])







    #primary key

    id=Column(Integer,index=True,primary_key=True,autoincrement=True)


    #foreign keys

    unique_id=Column(String,ForeignKey("symbol.unique_id"))
    vendor_id=Column(Integer,ForeignKey("vendor.id"))
    crypto_id=Column(String,ForeignKey("crypto.ticker"))


    #columns


    datetime=Column(TIMESTAMP,nullable=False)
    open=Column(Float,nullable=False)
    high=Column(Float,nullable=False)
    low=Column(Float,nullable=False)
    close=Column(Float,nullable=False)
    volume=Column(BigInteger,nullable=False)
    vw_avg_price=Column(Float,nullable=True)








class CryptoPricesHourlyAdj(Base):

    #table name

    __tablename__="crypto_prices_hourly_adj"


    #tableAttr

    __table_args__ = tuple([UniqueConstraint('vendor_id', 'crypto_id', "datetime")])







    #primary key

    id=Column(Integer,index=True,primary_key=True,autoincrement=True)


    #foreign keys

    unique_id=Column(String,ForeignKey("symbol.unique_id"))
    vendor_id=Column(Integer,ForeignKey("vendor.id"))
    crypto_id=Column(String,ForeignKey("crypto.ticker"))


    #columns


    datetime=Column(TIMESTAMP,nullable=False)
    open=Column(Float,nullable=False)
    high=Column(Float,nullable=False)
    low=Column(Float,nullable=False)
    close=Column(Float,nullable=False)
    volume=Column(BigInteger,nullable=False)
    vw_avg_price=Column(Float,nullable=True)








class CryptoPricesDailyUnadj(Base):

    #table name

    __tablename__="crypto_prices_daily_unadj"


    #tableAttr

    __table_args__ = tuple([UniqueConstraint('vendor_id', 'crypto_id', "datetime")])





    #primary key

    id=Column(Integer,index=True,primary_key=True,autoincrement=True)


    #foreign keys

    unique_id=Column(String,ForeignKey("symbol.unique_id"))
    vendor_id=Column(Integer,ForeignKey("vendor.id"))
    crypto_id=Column(String,ForeignKey("crypto.ticker"))


    #columns


    datetime=Column(TIMESTAMP,nullable=False)
    open=Column(Float,nullable=False)
    high=Column(Float,nullable=False)
    low=Column(Float,nullable=False)
    close=Column(Float,nullable=False)
    volume=Column(BigInteger,nullable=False)
    vw_avg_price=Column(Float,nullable=True)















class CryptoPricesDailyAdj(Base):

    #table name

    __tablename__="crypto_prices_daily_adj"


    #tableAttr

    __table_args__ = tuple([UniqueConstraint('vendor_id', 'crypto_id', "datetime")])





    #primary key

    id=Column(Integer,index=True,primary_key=True,autoincrement=True)


    #foreign keys

    unique_id=Column(String,ForeignKey("symbol.unique_id"))
    vendor_id=Column(Integer,ForeignKey("vendor.id"))
    crypto_id=Column(String,ForeignKey("crypto.ticker"))


    #columns


    datetime=Column(TIMESTAMP,nullable=False)
    open=Column(Float,nullable=False)
    high=Column(Float,nullable=False)
    low=Column(Float,nullable=False)
    close=Column(Float,nullable=False)
    volume=Column(BigInteger,nullable=False)
    vw_avg_price=Column(Float,nullable=True)











class IndicesPriceDaily(Base):

    #table name

    __tablename__="indices_prices_daily"


    #tableAttr

    __table_args__ = tuple([UniqueConstraint('vendor_id', 'indices_id', "datetime")])





    #primary key

    id=Column(Integer,index=True,primary_key=True,autoincrement=True)


    #foreign keys

    unique_id=Column(String,ForeignKey("symbol.unique_id"))
    vendor_id=Column(Integer,ForeignKey("vendor.id"))
    indices_id=Column(String,ForeignKey("indices.ticker"))


    #columns


    datetime=Column(TIMESTAMP,nullable=False)
    open=Column(Float,nullable=False)
    high=Column(Float,nullable=False)
    low=Column(Float,nullable=False)
    close=Column(Float,nullable=False)
    volume=Column(BigInteger,nullable=False)
    vw_avg_price=Column(Float,nullable=True)













class IndicesPriceHourly(Base):

    #table name

    __tablename__="indices_prices_hourly"


    #tableAttr

    __table_args__ = tuple([UniqueConstraint('vendor_id', 'indices_id', "datetime")])





    #primary key

    id=Column(Integer,index=True,primary_key=True,autoincrement=True)


    #foreign keys

    unique_id=Column(String,ForeignKey("symbol.unique_id"))
    vendor_id=Column(Integer,ForeignKey("vendor.id"))
    indices_id=Column(String,ForeignKey("indices.ticker"))


    #columns


    datetime=Column(TIMESTAMP,nullable=False)
    open=Column(Float,nullable=False)
    high=Column(Float,nullable=False)
    low=Column(Float,nullable=False)
    close=Column(Float,nullable=False)
    volume=Column(BigInteger,nullable=False)
    vw_avg_price=Column(Float,nullable=True)






class IndicesPriceMin(Base):

    #table name

    __tablename__="indices_prices_min"


    #tableAttr

    __table_args__ = tuple([UniqueConstraint('vendor_id', 'indices_id', "datetime")])





    #primary key

    id=Column(Integer,index=True,primary_key=True,autoincrement=True)


    #foreign keys

    unique_id=Column(String,ForeignKey("symbol.unique_id"))
    vendor_id=Column(Integer,ForeignKey("vendor.id"))
    indices_id=Column(String,ForeignKey("indices.ticker"))


    #columns


    datetime=Column(TIMESTAMP,nullable=False)
    open=Column(Float,nullable=False)
    high=Column(Float,nullable=False)
    low=Column(Float,nullable=False)
    close=Column(Float,nullable=False)
    volume=Column(BigInteger,nullable=False)
    vw_avg_price=Column(Float,nullable=True)





    class Financials(Base):
        __tablename__="financials"


        #tableAttr

        __table_args__ = tuple([UniqueConstraint('vendor_id', 'company_id', "period","calender_date","report_period","updated")])





        #primary key

        id=Column(Integer,index=True,primary_key=True,autoincrement=True)


        #foreign keys

        vendor_id=Column(Integer,ForeignKey("vendor.id"))
        company_id=Column(String,ForeignKey("company.compositeFigi"))
        symbol_id=Column(String,ForeignKey("symbol.unique_id"))
        

        #columns


        period=Column(TIMESTAMP,nullable=False)
        calender_date=Column(Date,nullable=False)
        report_period=Column(Date,nullable=False)
        updated=Column(Date)
        accumulatedOtherComprehensiveIncome=Column(BigInteger,nullable=False)
        assets=Column(BigInteger,nullable=False)
        assetsAverage=Column(BigInteger,nullable=True)
        assetsCurrent=Column(BigInteger,nullable=True)
        assetTurnover=Column(BigInteger,nullable=True)
        assetsNonCurrent=Column(BigInteger,nullable=True)
        assetsCurrent=Column(BigInteger,nullable=True)
        
        bookValuePerShare=Column(Float,nullable=True)


        capitalExpenditure=Column(BigInteger,nullable=True)
        cashAndEquivalents=Column(BigInteger,nullable=True)
        cashAndEquivalentsUSD=Column(BigInteger,nullable=True)
        costOfRevenue=Column(BigInteger,nullable=True)
        consolidatedIncome=Column(BigInteger,nullable=True)
        currentRatio=Column(Float,nullable=True)
        

        debtToEquityRatio=Column(Float,nullable=True)
        debt=Column(BigInteger,nullable=True)
        debtCurrent=Column(BigInteger,nullable=True)
        debtNonCurrent=Column(BigInteger,nullable=True)
        debtUSD=Column(BigInteger,nullable=True)
        deferredRevenue=Column(BigInteger,nullable=True)
        depreciationAmortizationAndAccretion=Column(BigInteger,nullable=True)
        deposits=Column(BigInteger,nullable=True)
        dividendYield=Column(BigInteger,nullable=True)
        dividendsPerBasicCommonShare=Column(BigInteger,nullable=True)
        



        earningBeforeInterestTaxes=Column(BigInteger,nullable=True)
        earningsBeforeInterestTaxesDepreciationAmortization=Column(BigInteger,nullable=True)
        EBITDAMargin=Column(BigInteger,nullable=True)
        earningsBeforeInterestTaxesDepreciationAmortizationUSD=Column(BigInteger,nullable=True)
        earningBeforeInterestTaxesUSD=Column(Float,nullable=True)
        


        earningsBeforeTax=Column(BigInteger,nullable=True)
        cashAndEquivalents=Column(BigInteger,nullable=True)
        cashAndEquivalentsUSD=Column(BigInteger,nullable=True)
        costOfRevenue=Column(BigInteger,nullable=True)
        consolidatedIncome=Column(BigInteger,nullable=True)
        currentRatio=Column(Float,nullable=True)
        debtToEquityRatio=Column(Float,nullable=True)
        
        
        debt=Column(BigInteger,nullable=True)
        debtCurrent=Column(BigInteger,nullable=True)
        debtNonCurrent=Column(BigInteger,nullable=True)
        debtUSD=Column(BigInteger,nullable=True)
        deferredRevenue=Column(BigInteger,nullable=True)
        depreciationAmortizationAndAccretion=Column(BigInteger,nullable=True)
        deposits=Column(BigInteger,nullable=True)
        dividendYield=Column(BigInteger,nullable=True)
        dividendsPerBasicCommonShare=Column(BigInteger,nullable=True)
        earningBeforeInterestTaxes=Column(BigInteger,nullable=True)
        earningsBeforeInterestTaxesDepreciationAmortization=Column(BigInteger,nullable=True)
        EBITDAMargin=Column(BigInteger,nullable=True)
        earningsBeforeInterestTaxesDepreciationAmortizationUSD=Column(BigInteger,nullable=True)
        earningBeforeInterestTaxesUSD=Column(BigInteger,nullable=True)
        earningsBeforeTax=Column(BigInteger,nullable=True)
        earningsPerBasicShare=Column(Float,nullable=True)
        earningsPerDilutedShare=Column(Float,nullable=True)
        earningsPerBasicShareUSD=Column(Float,nullable=True)
        shareholdersEquity=Column(BigInteger,nullable=True)
        averageEquity=Column(BigInteger,nullable=True)
        shareholdersEquityUSD=Column(BigInteger,nullable=True)
        enterpriseValue=Column(BigInteger,nullable=True)
        enterpriseValueOverEBIT=Column(BigInteger,nullable=True)
        enterpriseValueOverEBITDA=Column(Float,nullable=True)
        freeCashFlow=Column(BigInteger,nullable=True)
        freeCashFlowPerShare=Column(BigInteger,nullable=True)
        foreignCurrencyUSDExchangeRate=Column(BigInteger,nullable=True)
        grossProfit=Column(BigInteger,nullable=True)
        grossMargin=Column(Float,nullable=True)
        goodwillAndIntangibleAssets=Column(BigInteger,nullable=True)
        interestExpense=Column(BigInteger,nullable=True)
        investedCapital=Column(BigInteger,nullable=True)
        investedCapitalAverage=Column(BigInteger,nullable=True)
        inventory=Column(BigInteger,nullable=True)
        investments=Column(BigInteger,nullable=True)
        investmentsCurrent=Column(BigInteger,nullable=True)
        investmentsNonCurrent=Column(BigInteger,nullable=True)
        totalLiabilities=Column(BigInteger,nullable=True)
        currentLiabilities=Column(BigInteger,nullable=True)
        liabilitiesNonCurrent=Column(BigInteger,nullable=True)
        marketCapitalization=Column(BigInteger,nullable=True)
        netCashFlow=Column(BigInteger,nullable=True)
        netCashFlowBusinessAcquisitionsDisposals=Column(BigInteger,nullable=True)
        issuanceEquityShares=Column(BigInteger,nullable=True)
        issuanceDebtSecurities=Column(BigInteger,nullable=True)
        paymentDividendsOtherCashDistributions=Column(BigInteger,nullable=True)
        netCashFlowFromFinancing=Column(BigInteger,nullable=True)
        netCashFlowFromInvesting=Column(BigInteger,nullable=True)
        netCashFlowInvestmentAcquisitionsDisposals=Column(BigInteger,nullable=True)
        netCashFlowFromOperations=Column(BigInteger,nullable=True)
        effectOfExchangeRateChangesOnCash=Column(BigInteger,nullable=True)
        netIncome=Column(BigInteger,nullable=True)
        netIncomeCommonStock=Column(BigInteger,nullable=True)
        netIncomeCommonStockUSD=Column(BigInteger,nullable=True)
        netLossIncomeFromDiscontinuedOperations=Column(BigInteger,nullable=True)
        netIncomeToNonControllingInterests=Column(BigInteger,nullable=True)
        profitMargin=Column(BigInteger,nullable=True)
        operatingExpenses=Column(BigInteger,nullable=True)
        operatingIncome=Column(BigInteger,nullable=True)
        tradeAndNonTradePayables=Column(BigInteger,nullable=True)
        payoutRatio=Column(BigInteger,nullable=True)
        priceToBookValue=Column(Float,nullable=True)
        priceEarnings=Column(Float,nullable=True)
        priceToEarningsRatio=Column(Float,nullable=True)
        propertyPlantEquipmentNet=Column(BigInteger,nullable=True)
        preferredDividendsIncomeStatementImpact=Column(BigInteger,nullable=True)
        sharePriceAdjustedClose=Column(Float,nullable=True)
        priceSales=Column(Float,nullable=True)
        priceToSalesRatio=Column(Float,nullable=True)
        tradeAndNonTradeReceivables=Column(BigInteger,nullable=True)
        accumulatedRetainedEarningsDeficit=Column(BigInteger,nullable=True)
        revenues=Column(BigInteger,nullable=True)
        revenuesUSD=Column(BigInteger,nullable=True)
        researchAndDevelopmentExpense=Column(BigInteger,nullable=True)
        returnOnAverageAssets=Column(BigInteger,nullable=True)
        returnOnAverageEquity=Column(BigInteger,nullable=True)
        returnOnInvestedCapital=Column(BigInteger,nullable=True)
        returnOnSales=Column(BigInteger,nullable=True)
        shareBasedCompensation=Column(BigInteger,nullable=True)
        sellingGeneralAndAdministrativeExpense=Column(BigInteger,nullable=True)
        shareFactor=Column(BigInteger,nullable=True)
        shares=Column(BigInteger,nullable=True)
        weightedAverageShares=Column(BigInteger,nullable=True)
        weightedAverageSharesDiluted=Column(BigInteger,nullable=True)
        salesPerShare=Column(Float,nullable=True)
        tangibleAssetValue=Column(BigInteger,nullable=True)
        taxAssets=Column(BigInteger,nullable=True)
        incomeTaxExpense=Column(BigInteger,nullable=True)
        taxLiabilities=Column(BigInteger,nullable=True)
        tangibleAssetsBookValuePerShare=Column(Float,nullable=True)
        workingCapital=Column(BigInteger,nullable=True)
        adjusted=Column(Boolean,nullable=False)


















# Alpaca = Vendor(name='Alpaca')
# Polygon = Vendor(name='Polygon')
# InteractiveBrokers = Vendor(name='InteractiveBrokers')
# SimFin = Vendor(name='SimFin')
# AlphaVantage = Vendor(name='AlphaVantage')
# Quandl = Vendor(name='Quandl')
# Internal = Vendor(name='Internal')

# @listens_for(Vendor.__table__, 'after_create')
# def insert_initial_values(self,*args, **kwargs):

#     self.url =config.DB_URL
#     self.Session =sessionmaker()
#     engine =create_engine(self.url)
#     self.Session.configure(bind=engine)
#     session =self.Session()

#     session.add(Alpaca)
#     session.add(Polygon)
#     session.add(InteractiveBrokers)
#     session.add(SimFin)
#     session.add(AlphaVantage)
#     session.add(Quandl)
#     session.add(Internal)
#     session.commit()

#
