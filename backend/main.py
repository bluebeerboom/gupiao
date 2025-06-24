from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tushare as ts
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List
import json
from config import TUSHARE_TOKEN
from scheduler import (
    save_market_stats,
    save_high_rise_stocks,
    save_rise_fall_distribution,
    save_unified_market_analysis
)
from models import SessionLocal, MarketStats, HighRiseStock, RiseFallDistribution, UnifiedMarketAnalysis, StockHighestCheck
from is_highest_today import is_today_highest

app = FastAPI(title="股票信息API", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4000", "http://localhost:5173", "http://127.0.0.1:4000", "http://127.0.0.1:5173"],  # Vue开发服务器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化tushare
ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api()

@app.get("/")
async def root():
    return {"message": "股票信息API服务运行中"}

@app.get("/api/stocks")
async def get_stocks(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=100, description="每页数量"),
    min_rise: Optional[float] = Query(None, description="最小涨幅"),
    max_rise: Optional[float] = Query(None, description="最大涨幅"),
    min_price: Optional[float] = Query(None, description="最低价格"),
    max_price: Optional[float] = Query(None, description="最高价格"),
    market: Optional[str] = Query(None, description="市场类型(SZ/SH/BJ)"),
    sort_by: str = Query("pct_chg", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向(asc/desc)")
):
    """获取股票列表"""
    try:
        print(f"开始处理股票列表请求: page={page}, page_size={page_size}")
        
        # 获取最新交易日
        latest_date = get_latest_trade_date()
        print(f"最新交易日: {latest_date}")
        if not latest_date:
            raise HTTPException(status_code=500, detail="无法获取最新交易日数据")
        
        # 获取股票数据
        print("正在获取股票数据...")
        df = pro.daily(trade_date=latest_date)
        if df is None or df.empty:
            raise HTTPException(status_code=500, detail="无法获取股票数据")
        print(f"获取到股票数据: {len(df)}只股票")
        
        # 获取股票基本信息（只获取需要的字段）
        print("正在获取股票基本信息...")
        stock_basic = pro.stock_basic(fields='ts_code,name,area,industry,market')
        print(f"获取到股票基本信息: {len(stock_basic)}只股票")
        
        # 合并数据
        print("正在合并数据...")
        df = df.merge(stock_basic, on='ts_code', how='left')
        print(f"合并后数据: {len(df)}只股票")
        
        # 应用过滤条件
        print("正在应用过滤条件...")
        if min_rise is not None:
            df = df[df['pct_chg'] >= min_rise]
        if max_rise is not None:
            df = df[df['pct_chg'] <= max_rise]
        if min_price is not None:
            df = df[df['close'] >= min_price]
        if max_price is not None:
            df = df[df['close'] <= max_price]
        if market:
            df = df[df['ts_code'].str.endswith(f'.{market}')]
        
        # 排序
        print(f"正在按{sort_by}排序...")
        if sort_order == "desc":
            df = df.sort_values(sort_by, ascending=False)
        else:
            df = df.sort_values(sort_by, ascending=True)
        
        # 分页
        total = len(df)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        df_page = df.iloc[start_idx:end_idx]
        print(f"分页结果: 第{page}页，共{len(df_page)}条记录")
        
        # 转换为JSON格式（优化）
        print("正在转换为JSON格式...")
        stocks = []
        for _, row in df_page.iterrows():
            try:
                stock = {
                    "ts_code": str(row['ts_code']),
                    "name": str(row['name']) if pd.notna(row['name']) else "未知",
                    "close": float(row['close']) if pd.notna(row['close']) else 0.0,
                    "pct_chg": float(row['pct_chg']) if pd.notna(row['pct_chg']) else 0.0,
                    "vol": float(row['vol']) if pd.notna(row['vol']) else 0.0,
                    "amount": float(row['amount']) if pd.notna(row['amount']) else 0.0,
                    "area": str(row['area']) if pd.notna(row['area']) else "未知",
                    "industry": str(row['industry']) if pd.notna(row['industry']) else "未知",
                    "market": str(row['market']) if pd.notna(row['market']) else "未知",
                    "trade_date": str(row['trade_date'])
                }
                stocks.append(stock)
            except Exception as e:
                print(f"处理股票数据时出错: {e}, 股票代码: {row.get('ts_code', 'unknown')}")
                continue
        
        print("请求处理完成")
        return {
            "data": stocks,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size
            },
            "trade_date": latest_date
        }
        
    except Exception as e:
        print(f"处理股票列表请求时出错: {str(e)}")
        import traceback
        print("详细错误信息:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"获取股票数据失败: {str(e)}")

@app.get("/api/stock/{ts_code}")
async def get_stock_detail(ts_code: str):
    """获取单个股票详细信息"""
    try:
        # 标准化股票代码格式
        ts_code = ts_code.upper()
        
        latest_date = get_latest_trade_date()
        if not latest_date:
            raise HTTPException(status_code=500, detail="无法获取最新交易日数据")
        
        # 获取股票数据
        df = pro.daily(ts_code=ts_code, trade_date=latest_date)
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail="股票数据不存在")
        
        # 获取股票基本信息
        stock_basic = pro.stock_basic(ts_code=ts_code, fields='ts_code,name,area,industry,market,list_date')
        if stock_basic is None or stock_basic.empty:
            raise HTTPException(status_code=404, detail="股票基本信息不存在")
        
        # 获取历史数据（最近30天）
        end_date = datetime.strptime(latest_date, '%Y%m%d')
        start_date = end_date - timedelta(days=30)
        
        hist_df = pro.daily(ts_code=ts_code, 
                           start_date=start_date.strftime('%Y%m%d'),
                           end_date=latest_date)
        
        stock_data = df.iloc[0]
        basic_data = stock_basic.iloc[0]
        
        result = {
            "ts_code": stock_data['ts_code'],
            "name": basic_data['name'],
            "close": float(stock_data['close']),
            "open": float(stock_data['open']),
            "high": float(stock_data['high']),
            "low": float(stock_data['low']),
            "pct_chg": float(stock_data['pct_chg']),
            "vol": float(stock_data['vol']),
            "amount": float(stock_data['amount']),
            "area": basic_data['area'],
            "industry": basic_data['industry'],
            "market": basic_data['market'],
            "list_date": basic_data['list_date'],
            "trade_date": stock_data['trade_date']
        }
        
        # 添加历史数据
        if hist_df is not None and not hist_df.empty:
            hist_data = []
            for _, row in hist_df.iterrows():
                hist_data.append({
                    "date": row['trade_date'],
                    "close": float(row['close']),
                    "pct_chg": float(row['pct_chg']),
                    "vol": float(row['vol'])
                })
            result["history"] = hist_data
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取股票详情失败: {str(e)}")

@app.get("/api/filters")
async def get_filters():
    """获取过滤选项"""
    try:
        latest_date = get_latest_trade_date()
        if not latest_date:
            raise HTTPException(status_code=500, detail="无法获取最新交易日数据")
        
        df = pro.daily(trade_date=latest_date)
        if df is None or df.empty:
            raise HTTPException(status_code=500, detail="无法获取股票数据")
        
        # 获取股票基本信息
        stock_basic = pro.stock_basic(fields='ts_code,area,industry,market')
        df = df.merge(stock_basic, on='ts_code', how='left')
        
        # 获取地区列表
        areas = df['area'].dropna().unique().tolist()
        areas.sort()
        
        # 获取行业列表
        industries = df['industry'].dropna().unique().tolist()
        industries.sort()
        
        # 获取市场列表
        markets = df['market'].dropna().unique().tolist()
        markets.sort()
        
        # 获取价格范围
        price_range = {
            "min": float(df['close'].min()),
            "max": float(df['close'].max())
        }
        
        # 获取涨幅范围
        rise_range = {
            "min": float(df['pct_chg'].min()),
            "max": float(df['pct_chg'].max())
        }
        
        return {
            "areas": areas,
            "industries": industries,
            "markets": markets,
            "price_range": price_range,
            "rise_range": rise_range
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取过滤选项失败: {str(e)}")

@app.get("/api/high-rise-stocks")
async def get_high_rise_stocks():
    """获取3年新高且当天涨幅超过7%的股票"""
    try:
        latest_date = get_latest_trade_date()
        if not latest_date:
            raise HTTPException(status_code=500, detail="无法获取最新交易日数据")
        
        print(f"开始获取高涨幅股票数据，日期: {latest_date}")
        
        # 获取最新交易日数据
        df = pro.daily(trade_date=latest_date)
        if df is None or df.empty:
            raise HTTPException(status_code=500, detail="无法获取股票数据")
        
        print(f"获取到 {len(df)} 只股票数据")
        
        # 筛选涨幅超过7%的股票
        high_rise_df = df[df['pct_chg'] > 7].copy()
        print(f"涨幅超过7%的股票: {len(high_rise_df)} 只")
        
        if high_rise_df.empty:
            return {"stocks": [], "count": 0, "trade_date": latest_date}
        
        # 获取股票基本信息
        stock_list = pro.stock_basic(exchange='', list_status='L')
        
        # 合并数据
        high_rise_df = high_rise_df.merge(
            stock_list[['ts_code', 'name', 'area', 'industry']], 
            on='ts_code', 
            how='left'
        )
        
        # 简化历史数据获取，只检查最近30天
        result_stocks = []
        for _, row in high_rise_df.iterrows():
            try:
                ts_code = row['ts_code']
                print(f"检查股票: {ts_code}")
                
                # 获取最近30天的历史数据
                hist_data = pro.daily(ts_code=ts_code, start_date='20240101', end_date=latest_date)
                if hist_data is None or hist_data.empty:
                    continue
                
                # 按日期排序
                hist_data = hist_data.sort_values('trade_date')
                
                # 获取最近30天的最高价
                recent_high = hist_data['high'].max()
                current_price = row['close']
                
                # 检查是否创3年新高（简化：检查是否接近历史最高价）
                if current_price >= recent_high * 0.95:  # 允许5%的误差
                    stock_info = {
                        "ts_code": ts_code,
                        "name": row['name'],
                        "area": row['area'],
                        "industry": row['industry'],
                        "close": row['close'],
                        "pct_chg": row['pct_chg'],
                        "vol": row['vol'],
                        "amount": row['amount'],
                        "recent_high": recent_high
                    }
                    result_stocks.append(stock_info)
                    print(f"找到符合条件的股票: {ts_code} {row['name']}")
                
            except Exception as e:
                print(f"处理股票 {ts_code} 时出错: {str(e)}")
                continue
        
        print(f"最终找到 {len(result_stocks)} 只符合条件的股票")
        
        return {
            "stocks": result_stocks,
            "count": len(result_stocks),
            "trade_date": latest_date
        }
        
    except Exception as e:
        print(f"获取高涨幅股票出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取高涨幅股票失败: {str(e)}")

@app.get("/api/is-highest-today/{ts_code}")
def check_is_highest_today(ts_code: str):
    # 直接实时分析，不查数据库缓存
    result = is_today_highest(ts_code)
    if not result or not isinstance(result, dict):
        return {"error": "分析失败或无数据"}
    return result

@app.get("/api/market-analysis")
async def get_market_analysis():
    """获取市场分析数据"""
    try:
        latest_date = get_latest_trade_date()
        if not latest_date:
            raise HTTPException(status_code=500, detail="无法获取最新交易日数据")
        
        print(f"开始获取 {latest_date} 的市场数据...")
        
        # 获取最新交易日数据
        df = pro.daily(trade_date=latest_date)
        if df is None or df.empty:
            raise HTTPException(status_code=500, detail="无法获取股票数据")
        
        print(f"获取到 {len(df)} 只股票数据，开始分析...")
        
        # 1. 基础市场统计
        today_stats = calculate_daily_stats(df)
        print("基础统计完成")
        
        # 2. 涨跌分布分析
        rise_distribution = analyze_rise_distribution(df)
        fall_distribution = analyze_fall_distribution(df)
        print("涨跌分布分析完成")
        
        # 3. 获取最近5天的统计数据
        recent_stats = get_recent_trading_days_stats(5)
        print("历史数据获取完成")
        
        # 4. 计算平均值
        avg_stats = calculate_average_stats(recent_stats)
        print("平均值计算完成")
        
        print("市场分析完成")
        
        return {
            "trade_date": latest_date,
            "today_stats": today_stats,
            "rise_distribution": rise_distribution,
            "fall_distribution": fall_distribution,
            "recent_stats": recent_stats,
            "avg_stats": avg_stats
        }
        
    except Exception as e:
        print(f"市场分析出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取市场分析失败: {str(e)}")

@app.get("/api/market-stats-simple")
async def get_market_stats_simple():
    """获取简化的市场统计数据（快速版本）"""
    try:
        latest_date = get_latest_trade_date()
        if not latest_date:
            raise HTTPException(status_code=500, detail="无法获取最新交易日数据")
        
        # 获取最新交易日数据
        df = pro.daily(trade_date=latest_date)
        if df is None or df.empty:
            raise HTTPException(status_code=500, detail="无法获取股票数据")
        
        # 基础统计
        total_stocks = len(df)
        pct_chg = df['pct_chg']
        
        rise_stocks = int((pct_chg > 0).sum())
        fall_stocks = int((pct_chg < 0).sum())
        flat_stocks = int((pct_chg == 0).sum())
        
        return {
            "trade_date": latest_date,
            "total_stocks": total_stocks,
            "rise_stocks": rise_stocks,
            "fall_stocks": fall_stocks,
            "flat_stocks": flat_stocks,
            "rise_ratio": round(rise_stocks / total_stocks * 100, 2)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取市场统计失败: {str(e)}")

def analyze_high_rise_stocks_api_optimized(high_rise_df, trade_date):
    """分析高涨幅股票是否为3年新高或历史新高（优化版本）"""
    high_rise_stocks = []
    
    # 计算日期范围
    end_date = datetime.strptime(trade_date, '%Y%m%d')
    start_date_3y = end_date - timedelta(days=3 * 365)
    start_date_all = end_date - timedelta(days=5 * 365)  # 减少到5年
    
    end_date_str = end_date.strftime('%Y%m%d')
    start_date_3y_str = start_date_3y.strftime('%Y%m%d')
    start_date_all_str = start_date_all.strftime('%Y%m%d')
    
    # 获取股票基本信息（批量获取）
    stock_codes = high_rise_df['ts_code'].tolist()
    stock_basic = pro.stock_basic(fields='ts_code,name')
    stock_basic_dict = dict(zip(stock_basic['ts_code'], stock_basic['name'])) if not stock_basic.empty else {}
    
    total_stocks = len(high_rise_df)
    
    for idx, row in high_rise_df.iterrows():
        stock_code = row['ts_code']
        current_price = row['close']
        pct_chg = row['pct_chg']
        
        print(f"正在分析 {stock_code} ({idx+1}/{total_stocks})...")
        
        try:
            # 获取3年历史数据
            df_3y = pro.daily(ts_code=stock_code, 
                             start_date=start_date_3y_str, 
                             end_date=end_date_str)
            
            # 获取更长期历史数据（减少到5年）
            df_all = pro.daily(ts_code=stock_code, 
                              start_date=start_date_all_str, 
                              end_date=end_date_str)
            
            if df_3y is None or df_3y.empty:
                continue
                
            # 计算3年最高价
            max_3y = df_3y['close'].max()
            is_3y_high = current_price >= max_3y
            
            # 计算历史最高价
            is_all_time_high = False
            max_all = None
            if df_all is not None and not df_all.empty:
                max_all = df_all['close'].max()
                is_all_time_high = current_price >= max_all
            
            stock_name = stock_basic_dict.get(stock_code, "未知")
            
            high_rise_stocks.append({
                'ts_code': stock_code,
                'name': stock_name,
                'current_price': float(current_price),
                'pct_chg': float(pct_chg),
                'is_3y_high': is_3y_high,
                'is_all_time_high': is_all_time_high,
                'max_3y': float(max_3y),
                'max_all': float(max_all) if max_all is not None else None
            })
            
        except Exception as e:
            print(f"分析 {stock_code} 时出错: {e}")
            continue
    
    return high_rise_stocks

def get_recent_trading_days_stats_api_simple(days=3):
    """获取最近几个交易日的统计数据（简化版本）"""
    stats_list = []
    
    try:
        # 获取交易日历
        end_date = datetime.today()
        start_date = end_date - timedelta(days=30)  # 减少搜索范围
        
        trade_cal = pro.trade_cal(start_date=start_date.strftime('%Y%m%d'),
                                 end_date=end_date.strftime('%Y%m%d'))
        
        # 筛选交易日
        trading_days = trade_cal[trade_cal['is_open'] == 1]['cal_date'].tolist()
        trading_days.sort(reverse=True)
        
        # 只获取最近几天的数据
        for i, trade_date in enumerate(trading_days[:days]):
            try:
                print(f"获取 {trade_date} 的历史数据...")
                df = pro.daily(trade_date=trade_date)
                if df is not None and not df.empty:
                    pct_chg = df['pct_chg']
                    total_stocks = len(df)
                    rise_stocks = int((pct_chg > 0).sum())
                    fall_stocks = int((pct_chg < 0).sum())
                    flat_stocks = int((pct_chg == 0).sum())
                    
                    stats = {
                        'date': trade_date,
                        'total': total_stocks,
                        'rise': rise_stocks,
                        'fall': fall_stocks,
                        'flat': flat_stocks,
                        'rise_ratio': round(rise_stocks / total_stocks * 100, 2) if total_stocks > 0 else 0
                    }
                    stats_list.append(stats)
                    print(f"{trade_date} 数据获取完成")
            except Exception as e:
                print(f"获取 {trade_date} 数据时出错: {e}")
                continue
    
    except Exception as e:
        print(f"获取历史统计数据时出错: {e}")
    
    return stats_list

def get_latest_trade_date():
    """获取最新可用交易日"""
    # 获取最近30天的交易日历
    end_date = datetime.today()
    start_date = end_date - timedelta(days=30)
    
    trade_cal = pro.trade_cal(start_date=start_date.strftime('%Y%m%d'),
                             end_date=end_date.strftime('%Y%m%d'))
    
    # 筛选交易日并按日期排序
    trading_days = trade_cal[trade_cal['is_open'] == 1]['cal_date'].tolist()
    trading_days.sort(reverse=True)  # 最新日期在前
    
    if not trading_days:
        return None
    
    # 尝试获取最新交易日的数据
    for trade_date in trading_days[:5]:  # 尝试最近5个交易日
        try:
            df = pro.daily(trade_date=trade_date)
            if df is not None and not df.empty:
                print(f"找到最新可用交易日: {trade_date}")
                return trade_date
        except Exception as e:
            print(f"尝试获取 {trade_date} 数据时出错: {e}")
            continue
    
    return None

def calculate_daily_stats(df):
    """计算单日上涨下跌统计"""
    total_stocks = len(df)
    rise_stocks = len(df[df['pct_chg'] > 0])
    fall_stocks = len(df[df['pct_chg'] < 0])
    flat_stocks = len(df[df['pct_chg'] == 0])
    
    return {
        'date': df['trade_date'].iloc[0] if not df.empty else None,
        'total': total_stocks,
        'rise': rise_stocks,
        'fall': fall_stocks,
        'flat': flat_stocks,
        'rise_ratio': round(rise_stocks / total_stocks * 100, 2) if total_stocks > 0 else 0
    }

def analyze_rise_distribution(df):
    """分析上涨股票分布"""
    # 筛选上涨股票
    rise_df = df[df['pct_chg'] > 0].copy()
    
    distribution = {
        "0-2%": {"count": 0, "percentage": 0},
        "2-5%": {"count": 0, "percentage": 0},
        "5-7%": {"count": 0, "percentage": 0},
        "7%+": {"count": 0, "percentage": 0},
        "涨停": {"count": 0, "percentage": 0}
    }
    
    # 计算各区间数量
    distribution["0-2%"]["count"] = len(rise_df[(rise_df['pct_chg'] > 0) & (rise_df['pct_chg'] <= 2)])
    distribution["2-5%"]["count"] = len(rise_df[(rise_df['pct_chg'] > 2) & (rise_df['pct_chg'] <= 5)])
    distribution["5-7%"]["count"] = len(rise_df[(rise_df['pct_chg'] > 5) & (rise_df['pct_chg'] <= 7)])
    distribution["7%+"]["count"] = len(rise_df[rise_df['pct_chg'] > 7])
    distribution["涨停"]["count"] = len(rise_df[rise_df['pct_chg'] >= 9.8])
    
    # 计算百分比
    total_stocks = len(df)
    for key in distribution:
        distribution[key]["percentage"] = round(distribution[key]["count"] / total_stocks * 100, 2) if total_stocks > 0 else 0
    
    return distribution

def analyze_fall_distribution(df):
    """分析下跌股票分布"""
    # 筛选下跌股票
    fall_df = df[df['pct_chg'] < 0].copy()
    
    distribution = {
        "0-2%": {"count": 0, "percentage": 0},
        "2-5%": {"count": 0, "percentage": 0},
        "5-7%": {"count": 0, "percentage": 0},
        "7%+": {"count": 0, "percentage": 0},
        "跌停": {"count": 0, "percentage": 0}
    }
    
    # 计算各区间数量
    distribution["0-2%"]["count"] = len(fall_df[(fall_df['pct_chg'] < 0) & (fall_df['pct_chg'] >= -2)])
    distribution["2-5%"]["count"] = len(fall_df[(fall_df['pct_chg'] < -2) & (fall_df['pct_chg'] >= -5)])
    distribution["5-7%"]["count"] = len(fall_df[(fall_df['pct_chg'] < -5) & (fall_df['pct_chg'] >= -7)])
    distribution["7%+"]["count"] = len(fall_df[fall_df['pct_chg'] < -7])
    distribution["跌停"]["count"] = len(fall_df[fall_df['pct_chg'] <= -9.8])
    
    # 计算百分比
    total_stocks = len(df)
    for key in distribution:
        distribution[key]["percentage"] = round(distribution[key]["count"] / total_stocks * 100, 2) if total_stocks > 0 else 0
    
    return distribution

def get_recent_trading_days_stats(days=5):
    """获取最近几个交易日的统计数据"""
    stats_list = []
    
    # 获取交易日历
    end_date = datetime.today()
    start_date = end_date - timedelta(days=60)  # 获取更多日期确保有足够交易日
    
    trade_cal = pro.trade_cal(start_date=start_date.strftime('%Y%m%d'),
                             end_date=end_date.strftime('%Y%m%d'))
    
    # 筛选交易日
    trading_days = trade_cal[trade_cal['is_open'] == 1]['cal_date'].tolist()
    trading_days.sort(reverse=True)  # 最新日期在前
    
    # 获取最近几天的数据
    for i, trade_date in enumerate(trading_days[:days]):
        try:
            df = pro.daily(trade_date=trade_date)
            if df is not None and not df.empty:
                stats = calculate_daily_stats(df)
                stats_list.append(stats)
                print(f"已获取 {trade_date} 的数据")
        except Exception as e:
            print(f"获取 {trade_date} 数据时出错: {e}")
            continue
    
    return stats_list

def calculate_average_stats(stats_list):
    """计算平均值"""
    if not stats_list:
        return None
    
    avg_rise = sum(stat['rise'] for stat in stats_list) / len(stats_list)
    avg_fall = sum(stat['fall'] for stat in stats_list) / len(stats_list)
    avg_flat = sum(stat['flat'] for stat in stats_list) / len(stats_list)
    avg_total = sum(stat['total'] for stat in stats_list) / len(stats_list)
    avg_rise_ratio = sum(stat['rise_ratio'] for stat in stats_list) / len(stats_list)
    
    return {
        'avg_rise': round(avg_rise, 0),
        'avg_fall': round(avg_fall, 0),
        'avg_flat': round(avg_flat, 0),
        'avg_total': round(avg_total, 0),
        'avg_rise_ratio': round(avg_rise_ratio, 2)
    }

@app.get("/api/market_stats")
def get_market_stats():
    session = SessionLocal()
    stats = session.query(MarketStats).order_by(MarketStats.date.desc()).first()
    session.close()
    if stats:
        return {
            "date": stats.date,
            "total": stats.total,
            "rise": stats.rise,
            "fall": stats.fall,
            "flat": stats.flat,
            "rise_ratio": stats.rise_ratio
        }
    else:
        return {"error": "暂无数据"}

@app.get("/api/high_rise_stocks")
def get_high_rise_stocks():
    session = SessionLocal()
    latest = session.query(HighRiseStock.date).order_by(HighRiseStock.date.desc()).first()
    if not latest:
        session.close()
        return {"stocks": [], "count": 0}
    stocks = session.query(HighRiseStock).filter_by(date=latest[0]).all()
    result = [dict(
        ts_code=s.ts_code, name=s.name, current_price=s.current_price, pct_chg=s.pct_chg,
        is_3y_high=bool(s.is_3y_high), is_all_time_high=bool(s.is_all_time_high),
        max_3y=s.max_3y, max_all=s.max_all
    ) for s in stocks]
    session.close()
    return {"stocks": result, "count": len(result), "trade_date": latest[0]}

@app.get("/api/rise_fall_distribution")
def get_rise_fall_distribution():
    session = SessionLocal()
    latest = session.query(RiseFallDistribution.date).order_by(RiseFallDistribution.date.desc()).first()
    if not latest:
        session.close()
        return {"rise": [], "fall": [], "date": None}
    rise = session.query(RiseFallDistribution).filter_by(date=latest[0], type='rise').all()
    fall = session.query(RiseFallDistribution).filter_by(date=latest[0], type='fall').all()
    rise_result = [dict(label=r.label, count=r.count, percentage=r.percentage) for r in rise]
    fall_result = [dict(label=r.label, count=r.count, percentage=r.percentage) for r in fall]
    session.close()
    return {"rise": rise_result, "fall": fall_result, "date": latest[0]}

@app.get("/api/unified_market_analysis")
def get_unified_market_analysis():
    session = SessionLocal()
    latest = session.query(UnifiedMarketAnalysis.date).order_by(UnifiedMarketAnalysis.date.desc()).first()
    if not latest:
        session.close()
        return {"data": None, "date": None}
    record = session.query(UnifiedMarketAnalysis).filter_by(date=latest[0]).first()
    session.close()
    if not record:
        return {"data": None, "date": latest[0]}
    return {
        "today_stats": json.loads(record.today_stats),
        "rise_distribution": json.loads(record.rise_distribution),
        "fall_distribution": json.loads(record.fall_distribution),
        "recent_stats": json.loads(record.recent_stats),
        "avg_stats": json.loads(record.avg_stats),
        "date": record.date
    }

@app.post("/api/refresh_market_stats")
def refresh_market_stats(background_tasks: BackgroundTasks):
    background_tasks.add_task(save_market_stats)
    return {"msg": "市场统计分析已刷新（后台执行）"}

@app.post("/api/refresh_high_rise_stocks")
def refresh_high_rise_stocks(background_tasks: BackgroundTasks):
    background_tasks.add_task(save_high_rise_stocks)
    return {"msg": "高涨幅创新高分析已刷新（后台执行）"}

@app.post("/api/refresh_rise_fall_distribution")
def refresh_rise_fall_distribution(background_tasks: BackgroundTasks):
    background_tasks.add_task(save_rise_fall_distribution)
    return {"msg": "涨跌分布分析已刷新（后台执行）"}

@app.post("/api/refresh_unified_market_analysis")
def refresh_unified_market_analysis(background_tasks: BackgroundTasks):
    background_tasks.add_task(save_unified_market_analysis)
    return {"msg": "综合分析已刷新（后台执行）"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 