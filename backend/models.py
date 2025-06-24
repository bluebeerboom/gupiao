from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import json

Base = declarative_base()

class MarketStats(Base):
    __tablename__ = 'market_stats'
    id = Column(Integer, primary_key=True)
    date = Column(String, unique=True)  # 交易日
    total = Column(Integer)
    rise = Column(Integer)
    fall = Column(Integer)
    flat = Column(Integer)
    rise_ratio = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class HighRiseStock(Base):
    __tablename__ = 'high_rise_stocks'
    id = Column(Integer, primary_key=True)
    date = Column(String, index=True)
    ts_code = Column(String)
    name = Column(String)
    current_price = Column(Float)
    pct_chg = Column(Float)
    is_3y_high = Column(Boolean)
    is_all_time_high = Column(Boolean)
    max_3y = Column(Float)
    max_all = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class RiseFallDistribution(Base):
    __tablename__ = 'rise_fall_distribution'
    id = Column(Integer, primary_key=True)
    date = Column(String, index=True)
    label = Column(String)  # 区间标签，如"0-2%"
    count = Column(Integer)
    percentage = Column(Float)
    type = Column(String)  # 'rise' 或 'fall'
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class UnifiedMarketAnalysis(Base):
    __tablename__ = 'unified_market_analysis'
    id = Column(Integer, primary_key=True)
    date = Column(String, index=True)
    today_stats = Column(Text)  # JSON字符串
    rise_distribution = Column(Text)
    fall_distribution = Column(Text)
    recent_stats = Column(Text)
    avg_stats = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class StockHighestCheck(Base):
    __tablename__ = 'stock_highest_check'
    id = Column(Integer, primary_key=True)
    ts_code = Column(String, index=True)
    date = Column(String, index=True)  # 检查日期
    is_highest = Column(Boolean)
    today_close = Column(Float)
    max_close = Column(Float)
    min_close = Column(Float)
    trade_date = Column(String)
    pct_chg = Column(Float)
    vol = Column(Float)
    amount = Column(Float)
    checked_at = Column(DateTime, default=datetime.datetime.utcnow)

engine = create_engine('sqlite:///market.db')
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine) 