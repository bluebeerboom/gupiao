import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
from config import TUSHARE_TOKEN, RISE_RANGES, FALL_RANGES

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False


def analyze_rise_fall_distribution():
    """分析当日上涨下跌股票分布"""
    # 初始化 tushare
    ts.set_token(TUSHARE_TOKEN)
    pro = ts.pro_api()
    
    # 获取最新可用交易日
    latest_trade_date = get_latest_trade_date(pro)
    if not latest_trade_date:
        print("无法获取最新交易日数据！")
        return None
    
    print(f"正在分析 {latest_trade_date} 的股票涨跌分布...")
    
    # 获取最新交易日数据
    df = pro.daily(trade_date=latest_trade_date)
    
    if df is None or df.empty:
        print(f"未获取到 {latest_trade_date} 的市场数据！")
        return None
    
    # 分析上涨股票分布
    rise_distribution = analyze_rise_distribution(df)
    
    # 分析下跌股票分布
    fall_distribution = analyze_fall_distribution(df)
    
    # 显示结果
    display_distribution_results(rise_distribution, fall_distribution, latest_trade_date)
    
    # 绘制图表
    plot_bar_chart(rise_distribution, fall_distribution, latest_trade_date)
    
    return rise_distribution, fall_distribution


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


def analyze_rise_distribution(df):
    """分析上涨股票分布"""
    # 筛选上涨股票
    rise_df = df[df['pct_chg'] > 0].copy()
    
    distribution = {}
    
    for min_pct, max_pct, label in RISE_RANGES:
        if max_pct == float('inf'):
            # 处理涨停情况
            if label == "涨停":
                count = len(rise_df[rise_df['pct_chg'] >= 9.8])  # 涨停通常为9.8%以上
            else:
                count = len(rise_df[rise_df['pct_chg'] >= min_pct])
        else:
            count = len(rise_df[(rise_df['pct_chg'] >= min_pct) & (rise_df['pct_chg'] < max_pct)])
        
        distribution[label] = {
            'count': count,
            'percentage': count / len(df) * 100 if len(df) > 0 else 0
        }
    
    return distribution


def analyze_fall_distribution(df):
    """分析下跌股票分布"""
    # 筛选下跌股票
    fall_df = df[df['pct_chg'] < 0].copy()
    
    distribution = {}
    
    for min_pct, max_pct, label in FALL_RANGES:
        if max_pct == float('inf'):
            # 处理跌停情况
            if label == "跌停":
                count = len(fall_df[fall_df['pct_chg'] <= -9.8])  # 跌停通常为-9.8%以下
            else:
                count = len(fall_df[fall_df['pct_chg'] <= -min_pct])
        else:
            count = len(fall_df[(fall_df['pct_chg'] <= -min_pct) & (fall_df['pct_chg'] > -max_pct)])
        
        distribution[label] = {
            'count': count,
            'percentage': count / len(df) * 100 if len(df) > 0 else 0
        }
    
    return distribution


def display_distribution_results(rise_distribution, fall_distribution, trade_date):
    """显示分布结果"""
    print("\n" + "="*80)
    print(f"📊 {trade_date} 股票涨跌分布分析")
    print("="*80)
    
    # 显示上涨分布
    print("\n📈 上涨股票分布:")
    print("-" * 50)
    total_rise = sum(item['count'] for item in rise_distribution.values())
    for label, data in rise_distribution.items():
        print(f"   {label:8}: {data['count']:4d} 只 ({data['percentage']:5.1f}%)")
    print(f"   总计上涨: {total_rise} 只")
    
    # 显示下跌分布
    print("\n📉 下跌股票分布:")
    print("-" * 50)
    total_fall = sum(item['count'] for item in fall_distribution.values())
    for label, data in fall_distribution.items():
        print(f"   {label:8}: {data['count']:4d} 只 ({data['percentage']:5.1f}%)")
    print(f"   总计下跌: {total_fall} 只")
    
    # 计算平盘股票
    total_stocks = total_rise + total_fall
    flat_stocks = total_stocks - total_rise - total_fall  # 这里需要重新计算
    print(f"\n➖ 平盘股票: {flat_stocks} 只")





def plot_bar_chart(rise_distribution, fall_distribution, trade_date):
    """绘制柱状图对比"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # 上涨分布柱状图
    rise_labels = list(rise_distribution.keys())
    rise_counts = [rise_distribution[label]['count'] for label in rise_labels]
    
    bars1 = ax1.bar(rise_labels, rise_counts, color='red', alpha=0.7)
    ax1.set_title(f'{trade_date} 上涨股票数量分布', fontsize=14, fontweight='bold')
    ax1.set_ylabel('股票数量')
    ax1.grid(True, alpha=0.3)
    
    # 在柱子上添加数值标签
    for bar, count in zip(bars1, rise_counts):
        if count > 0:
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, 
                    str(count), ha='center', va='bottom', fontweight='bold')
    
    # 下跌分布柱状图
    fall_labels = list(fall_distribution.keys())
    fall_counts = [fall_distribution[label]['count'] for label in fall_labels]
    
    bars2 = ax2.bar(fall_labels, fall_counts, color='green', alpha=0.7)
    ax2.set_title(f'{trade_date} 下跌股票数量分布', fontsize=14, fontweight='bold')
    ax2.set_ylabel('股票数量')
    ax2.grid(True, alpha=0.3)
    
    # 在柱子上添加数值标签
    for bar, count in zip(bars2, fall_counts):
        if count > 0:
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, 
                    str(count), ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    print("🚀 开始分析股票涨跌分布...")
    analyze_rise_fall_distribution() 