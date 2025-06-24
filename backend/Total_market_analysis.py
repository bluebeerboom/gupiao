import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
from config import TUSHARE_TOKEN, RISE_RANGES, FALL_RANGES

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False


def unified_market_analysis(days=5):
    """
    统一的市场分析功能
    包含：涨跌分布分析、市场统计、趋势分析
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
    
    print(f"正在分析 {latest_trade_date} 的市场数据...")
    
    # 获取最新交易日数据
    df = pro.daily(trade_date=latest_trade_date)
    
    if df is None or df.empty:
        print(f"未获取到 {latest_trade_date} 的市场数据！")
        return None
    
    # 1. 基础市场统计
    today_stats = calculate_daily_stats(df)
    
    # 2. 涨跌分布分析
    rise_distribution = analyze_rise_distribution(df)
    fall_distribution = analyze_fall_distribution(df)
    
    # 3. 获取最近几天的统计数据
    recent_stats = get_recent_trading_days_stats(pro, days)
    
    # 4. 计算平均值
    avg_stats = calculate_average_stats(recent_stats)
    
    # 5. 显示综合结果
    display_unified_results(today_stats, rise_distribution, fall_distribution, 
                           recent_stats, avg_stats, latest_trade_date)
    
    # 6. 绘制综合图表
    plot_unified_charts(rise_distribution, fall_distribution, recent_stats, 
                       today_stats, latest_trade_date)
    
    return {
        'today_stats': today_stats,
        'rise_distribution': rise_distribution,
        'fall_distribution': fall_distribution,
        'recent_stats': recent_stats,
        'avg_stats': avg_stats
    }


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


def display_unified_results(today_stats, rise_distribution, fall_distribution, 
                           recent_stats, avg_stats, trade_date):
    """显示统一的分析结果"""
    print("\n" + "="*100)
    print(f"📊 {trade_date} 统一市场分析报告")
    print("="*100)
    
    # 1. 基础市场统计
    if today_stats:
        print(f"\n📅 最新交易日基础统计:")
        print("-" * 50)
        print(f"   总股票数: {today_stats['total']:,}")
        print(f"   上涨股票: {today_stats['rise']:,} ({today_stats['rise_ratio']:.1f}%)")
        print(f"   下跌股票: {today_stats['fall']:,}")
        print(f"   平盘股票: {today_stats['flat']:,}")
    
    # 2. 涨跌分布详情
    print(f"\n📈 上涨股票分布:")
    print("-" * 50)
    total_rise = sum(item['count'] for item in rise_distribution.values())
    for label, data in rise_distribution.items():
        print(f"   {label:8}: {data['count']:4d} 只 ({data['percentage']:5.1f}%)")
    print(f"   总计上涨: {total_rise} 只")
    
    print(f"\n📉 下跌股票分布:")
    print("-" * 50)
    total_fall = sum(item['count'] for item in fall_distribution.values())
    for label, data in fall_distribution.items():
        print(f"   {label:8}: {data['count']:4d} 只 ({data['percentage']:5.1f}%)")
    print(f"   总计下跌: {total_fall} 只")
    
    # 3. 历史对比
    if avg_stats:
        print(f"\n📈 近{len(recent_stats)}日平均值对比:")
        print("-" * 50)
        print(f"   平均上涨股票: {avg_stats['avg_rise']:,.0f} (今日: {today_stats['rise']:,})")
        print(f"   平均下跌股票: {avg_stats['avg_fall']:,.0f} (今日: {today_stats['fall']:,})")
        print(f"   平均上涨比例: {avg_stats['avg_rise_ratio']:.1f}% (今日: {today_stats['rise_ratio']:.1f}%)")
        
        # 计算变化
        rise_change = today_stats['rise'] - avg_stats['avg_rise']
        ratio_change = today_stats['rise_ratio'] - avg_stats['avg_rise_ratio']
        print(f"\n🔄 与平均值对比:")
        print(f"   上涨股票变化: {rise_change:+.0f} ({'📈' if rise_change > 0 else '📉'})")
        print(f"   上涨比例变化: {ratio_change:+.1f}% ({'📈' if ratio_change > 0 else '📉'})")
    
    # 4. 最近交易日详情
    if recent_stats:
        print(f"\n📋 最近{len(recent_stats)}个交易日详情:")
        print("-" * 50)
        # 反转顺序，让日期从远到近显示
        for stat in recent_stats[::-1]:
            trend_emoji = "📈" if stat['rise_ratio'] > 50 else "📉"
            print(f"   {stat['date']}: 上涨{stat['rise']:,}只 ({stat['rise_ratio']:.1f}%) {trend_emoji}")


def plot_unified_charts(rise_distribution, fall_distribution, recent_stats, 
                       today_stats, trade_date):
    """绘制统一的图表"""
    fig = plt.figure(figsize=(16, 12))
    
    # 创建2x2的子图布局
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
    
    # 1. 左上：涨跌分布柱状图
    ax1 = fig.add_subplot(gs[0, 0])
    plot_distribution_chart(ax1, rise_distribution, fall_distribution, trade_date)
    
    # 2. 右上：最近趋势图
    ax2 = fig.add_subplot(gs[0, 1])
    plot_trend_chart(ax2, recent_stats, trade_date)
    
    # 3. 左下：涨跌对比图
    ax3 = fig.add_subplot(gs[1, 0])
    plot_comparison_chart(ax3, recent_stats, today_stats, trade_date)
    
    # 4. 右下：市场情绪图
    ax4 = fig.add_subplot(gs[1, 1])
    plot_sentiment_chart(ax4, rise_distribution, fall_distribution, trade_date)
    
    plt.suptitle(f'{trade_date} 市场综合分析', fontsize=16, fontweight='bold')
    plt.show()


def plot_distribution_chart(ax, rise_distribution, fall_distribution, trade_date):
    """绘制涨跌分布图"""
    # 上涨分布
    rise_labels = list(rise_distribution.keys())
    rise_counts = [rise_distribution[label]['count'] for label in rise_labels]
    rise_colors = ['#FF6B6B', '#FF8E8E', '#FFB1B1', '#FFD4D4', '#FF0000']
    
    # 只显示有数据的部分
    non_zero_indices = [i for i, count in enumerate(rise_counts) if count > 0]
    if non_zero_indices:
        filtered_labels = [rise_labels[i] for i in non_zero_indices]
        filtered_counts = [rise_counts[i] for i in non_zero_indices]
        filtered_colors = [rise_colors[i] for i in non_zero_indices]
        
        bars1 = ax.bar(filtered_labels, filtered_counts, color=filtered_colors, alpha=0.8)
        ax.set_title('涨跌分布', fontsize=12, fontweight='bold')
        ax.set_ylabel('股票数量')
        ax.grid(True, alpha=0.3)
        
        # 添加数值标签
        for bar, count in zip(bars1, filtered_counts):
            if count > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                       str(count), ha='center', va='bottom', fontsize=8)


def plot_trend_chart(ax, recent_stats, trade_date):
    """绘制趋势图"""
    if not recent_stats:
        return
    
    # 反转数据顺序，让日期从远到近显示
    dates = [stat['date'] for stat in recent_stats][::-1]
    rise_counts = [stat['rise'] for stat in recent_stats][::-1]
    fall_counts = [stat['fall'] for stat in recent_stats][::-1]
    
    x = range(len(dates))
    ax.bar([i-0.2 for i in x], rise_counts, width=0.4, label='上涨', color='red', alpha=0.7)
    ax.bar([i+0.2 for i in x], fall_counts, width=0.4, label='下跌', color='green', alpha=0.7)
    
    ax.set_title('近5日涨跌趋势', fontsize=12, fontweight='bold')
    ax.set_ylabel('股票数量')
    ax.set_xticks(x)
    ax.set_xticklabels(dates, rotation=45)
    ax.legend()
    ax.grid(True, alpha=0.3)


def plot_comparison_chart(ax, recent_stats, today_stats, trade_date):
    """绘制对比图"""
    if not recent_stats:
        return
    
    # 反转数据顺序，让日期从远到近显示
    dates = [stat['date'] for stat in recent_stats][::-1]
    rise_ratios = [stat['rise_ratio'] for stat in recent_stats][::-1]
    
    x = range(len(dates))
    ax.plot(x, rise_ratios, marker='o', linewidth=2, color='blue', label='上涨比例')
    ax.axhline(y=50, color='gray', linestyle='--', alpha=0.5, label='50%分界线')
    
    # 标注今日数据
    if today_stats:
        ax.axhline(y=today_stats['rise_ratio'], color='red', linestyle=':', alpha=0.7, label=f'今日: {today_stats["rise_ratio"]:.1f}%')
    
    ax.set_title('上涨比例变化', fontsize=12, fontweight='bold')
    ax.set_ylabel('上涨比例 (%)')
    ax.set_xticks(x)
    ax.set_xticklabels(dates, rotation=45)
    ax.legend()
    ax.grid(True, alpha=0.3)


def plot_sentiment_chart(ax, rise_distribution, fall_distribution, trade_date):
    """绘制市场情绪图"""
    # 计算市场情绪指标
    strong_rise = rise_distribution.get('7%+', {}).get('count', 0)
    strong_fall = fall_distribution.get('7%+', {}).get('count', 0)
    limit_up = rise_distribution.get('涨停', {}).get('count', 0)
    limit_down = fall_distribution.get('跌停', {}).get('count', 0)
    
    categories = ['强势上涨', '强势下跌', '涨停', '跌停']
    values = [strong_rise, strong_fall, limit_up, limit_down]
    colors = ['#FF6B6B', '#4ECDC4', '#FF0000', '#00FF00']
    
    bars = ax.bar(categories, values, color=colors, alpha=0.8)
    ax.set_title('市场情绪指标', fontsize=12, fontweight='bold')
    ax.set_ylabel('股票数量')
    ax.grid(True, alpha=0.3)
    
    # 添加数值标签
    for bar, value in zip(bars, values):
        if value > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                   str(value), ha='center', va='bottom', fontsize=8)


if __name__ == "__main__":
    print("🚀 开始统一市场分析...")
    unified_market_analysis(days=5) 