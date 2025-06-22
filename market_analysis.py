import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from config import TUSHARE_TOKEN

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False


def get_market_rise_fall_stats(days=5):
    """
    计算市场上涨下跌股票统计
    days: 计算最近几天的数据，默认5天
    """
    # 初始化 tushare
    ts.set_token(TUSHARE_TOKEN)
    pro = ts.pro_api()
    
    # 获取最新可用交易日
    latest_trade_date = get_latest_trade_date(pro)
    if not latest_trade_date:
        print("无法获取最新交易日数据！")
        return None
    
    print(f"正在获取最新交易日 {latest_trade_date} 的市场数据...")
    
    # 获取最新交易日数据
    df = pro.daily(trade_date=latest_trade_date)
    
    if df is None or df.empty:
        print(f"未获取到 {latest_trade_date} 的市场数据！")
        return None
    
    # 计算最新交易日上涨下跌统计
    today_stats = calculate_daily_stats(df)
    
    # 获取最近5个交易日的统计数据
    recent_stats = get_recent_trading_days_stats(pro, days)
    
    # 计算5日平均值
    avg_stats = calculate_5day_average(recent_stats)
    
    # 显示结果
    display_results(today_stats, recent_stats, avg_stats)
    
    # 绘制图表
    plot_market_trend(recent_stats, today_stats)
    
    return today_stats, recent_stats, avg_stats


def get_latest_trade_date(pro):
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
        'rise_ratio': rise_stocks / total_stocks * 100 if total_stocks > 0 else 0
    }


def get_recent_trading_days_stats(pro, days=5):
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


def calculate_5day_average(stats_list):
    """计算5日平均值"""
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


def display_results(today_stats, recent_stats, avg_stats):
    """显示统计结果"""
    print("\n" + "="*60)
    print("📊 市场上涨下跌股票统计")
    print("="*60)
    
    if today_stats:
        print(f"\n📅 最新交易日 ({today_stats['date']}) 统计:")
        print(f"   总股票数: {today_stats['total']:,}")
        print(f"   上涨股票: {today_stats['rise']:,} ({today_stats['rise_ratio']:.1f}%)")
        print(f"   下跌股票: {today_stats['fall']:,}")
        print(f"   平盘股票: {today_stats['flat']:,}")
    
    if avg_stats:
        print(f"\n📈 近5日平均值:")
        print(f"   平均上涨股票: {avg_stats['avg_rise']:,.0f}")
        print(f"   平均下跌股票: {avg_stats['avg_fall']:,.0f}")
        print(f"   平均平盘股票: {avg_stats['avg_flat']:,.0f}")
        print(f"   平均上涨比例: {avg_stats['avg_rise_ratio']:.1f}%")
    
    if recent_stats:
        print(f"\n📋 最近5个交易日详情:")
        for stat in recent_stats:
            print(f"   {stat['date']}: 上涨{stat['rise']:,}只 ({stat['rise_ratio']:.1f}%)")


def plot_market_trend(recent_stats, today_stats):
    """绘制市场趋势图"""
    if not recent_stats:
        return
    
    # 准备数据
    dates = [stat['date'] for stat in recent_stats]
    rise_counts = [stat['rise'] for stat in recent_stats]
    fall_counts = [stat['fall'] for stat in recent_stats]
    
    # 创建图表
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # 上图：上涨下跌股票数量
    x = range(len(dates))
    ax1.bar([i-0.2 for i in x], rise_counts, width=0.4, label='上涨股票', color='red', alpha=0.7)
    ax1.bar([i+0.2 for i in x], fall_counts, width=0.4, label='下跌股票', color='green', alpha=0.7)
    
    ax1.set_title('近5日上涨下跌股票数量对比', fontsize=14, fontweight='bold')
    ax1.set_ylabel('股票数量')
    ax1.set_xticks(x)
    ax1.set_xticklabels(dates, rotation=45)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 下图：上涨比例
    rise_ratios = [stat['rise_ratio'] for stat in recent_stats]
    ax2.plot(x, rise_ratios, marker='o', linewidth=2, color='blue', label='上涨比例')
    ax2.axhline(y=50, color='gray', linestyle='--', alpha=0.5, label='50%分界线')
    
    ax2.set_title('近5日上涨股票比例变化', fontsize=14, fontweight='bold')
    ax2.set_ylabel('上涨比例 (%)')
    ax2.set_xlabel('日期')
    ax2.set_xticks(x)
    ax2.set_xticklabels(dates, rotation=45)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    print("🚀 开始分析市场上涨下跌股票统计...")
    get_market_rise_fall_stats(days=5) 