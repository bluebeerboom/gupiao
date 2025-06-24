from market_analysis import get_market_rise_fall_stats
from high_rise_stocks import find_high_rise_stocks
from models import MarketStats, SessionLocal, HighRiseStock, RiseFallDistribution, UnifiedMarketAnalysis
import datetime
from rise_fall_analysis import analyze_rise_fall_distribution
import json
from Total_market_analysis import unified_market_analysis

def save_market_stats():
    today_stats, _, _ = get_market_rise_fall_stats(days=5)
    if today_stats:
        session = SessionLocal()
        # 检查当天是否已存在
        exists = session.query(MarketStats).filter_by(date=today_stats['date']).first()
        if not exists:
            stats = MarketStats(
                date=today_stats['date'],
                total=today_stats['total'],
                rise=today_stats['rise'],
                fall=today_stats['fall'],
                flat=today_stats['flat'],
                rise_ratio=today_stats['rise_ratio'],
                created_at=datetime.datetime.utcnow()
            )
            session.add(stats)
            session.commit()
        session.close()

def save_high_rise_stocks():
    stocks = find_high_rise_stocks()
    if stocks:
        session = SessionLocal()
        date = stocks[0].get('trade_date') or datetime.datetime.now().strftime('%Y%m%d')
        # 先删除当天旧数据
        session.query(HighRiseStock).filter_by(date=date).delete()
        for s in stocks:
            stock = HighRiseStock(
                date=date,
                ts_code=s['ts_code'],
                name=s['name'],
                current_price=s['current_price'],
                pct_chg=s['pct_chg'],
                is_3y_high=bool(s['is_3y_high']),
                is_all_time_high=bool(s['is_all_time_high']),
                max_3y=s['max_3y'],
                max_all=s['max_all']
            )
            session.add(stock)
        session.commit()
        session.close()

def save_rise_fall_distribution():
    result = analyze_rise_fall_distribution()
    if result:
        rise_distribution, fall_distribution = result
        # 获取今天日期
        today = datetime.datetime.now().strftime('%Y%m%d')
        session = SessionLocal()
        # 先删除当天旧数据
        session.query(RiseFallDistribution).filter_by(date=today).delete()
        # 写入上涨分布
        for label, data in rise_distribution.items():
            record = RiseFallDistribution(
                date=today,
                label=label,
                count=data['count'],
                percentage=data['percentage'],
                type='rise'
            )
            session.add(record)
        # 写入下跌分布
        for label, data in fall_distribution.items():
            record = RiseFallDistribution(
                date=today,
                label=label,
                count=data['count'],
                percentage=data['percentage'],
                type='fall'
            )
            session.add(record)
        session.commit()
        session.close()

def save_unified_market_analysis():
    result = unified_market_analysis()
    if result:
        today = result['today_stats']['date'] if result['today_stats'] else datetime.datetime.now().strftime('%Y%m%d')
        session = SessionLocal()
        # 先删除当天旧数据
        session.query(UnifiedMarketAnalysis).filter_by(date=today).delete()
        record = UnifiedMarketAnalysis(
            date=today,
            today_stats=json.dumps(result['today_stats'], ensure_ascii=False),
            rise_distribution=json.dumps(result['rise_distribution'], ensure_ascii=False),
            fall_distribution=json.dumps(result['fall_distribution'], ensure_ascii=False),
            recent_stats=json.dumps(result['recent_stats'], ensure_ascii=False),
            avg_stats=json.dumps(result['avg_stats'], ensure_ascii=False)
        )
        session.add(record)
        session.commit()
        session.close() 