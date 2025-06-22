import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from config import TUSHARE_TOKEN, MAX_YEARS

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False


def find_high_rise_stocks():
    """找出是3年新高（或历史新高）且今天涨幅超过7%的股票"""
    # 初始化 tushare
    ts.set_token(TUSHARE_TOKEN)
    pro = ts.pro_api()
    
    # 获取最新可用交易日
    latest_trade_date = get_latest_trade_date(pro)
    if not latest_trade_date:
        print("无法获取最新交易日数据！")
        return None
    
    print(f"正在分析 {latest_trade_date} 的高涨幅创新高股票...")
    
    # 获取最新交易日数据
    df = pro.daily(trade_date=latest_trade_date)
    
    if df is None or df.empty:
        print(f"未获取到 {latest_trade_date} 的市场数据！")
        return None
    
    # 筛选涨幅超过7%的股票
    high_rise_df = df[df['pct_chg'] > 7.0].copy()
    
    if high_rise_df.empty:
        print("没有找到涨幅超过7%的股票！")
        return None
    
    print(f"找到 {len(high_rise_df)} 只涨幅超过7%的股票")
    
    # 分析这些股票是否为3年新高或历史新高
    high_rise_stocks = analyze_high_rise_stocks(pro, high_rise_df, latest_trade_date)
    
    # 显示结果
    display_high_rise_results(high_rise_stocks, latest_trade_date)
    
    # 绘制图表
    plot_high_rise_chart(high_rise_stocks, latest_trade_date)
    
    return high_rise_stocks


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


def analyze_high_rise_stocks(pro, high_rise_df, trade_date):
    """分析高涨幅股票是否为3年新高或历史新高"""
    high_rise_stocks = []
    
    # 计算日期范围
    end_date = datetime.strptime(trade_date, '%Y%m%d')
    start_date_3y = end_date - timedelta(days=MAX_YEARS * 365)
    start_date_all = end_date - timedelta(days=10 * 365)  # 10年数据用于判断历史新高
    
    end_date_str = end_date.strftime('%Y%m%d')
    start_date_3y_str = start_date_3y.strftime('%Y%m%d')
    start_date_all_str = start_date_all.strftime('%Y%m%d')
    
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
            
            # 获取更长期历史数据（用于判断历史新高）
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
            if df_all is not None and not df_all.empty:
                max_all = df_all['close'].max()
                is_all_time_high = current_price >= max_all
            
            # 获取股票名称
            stock_name = get_stock_name(pro, stock_code)
            
            high_rise_stocks.append({
                'ts_code': stock_code,
                'name': stock_name,
                'current_price': current_price,
                'pct_chg': pct_chg,
                'is_3y_high': is_3y_high,
                'is_all_time_high': is_all_time_high,
                'max_3y': max_3y,
                'max_all': max_all if df_all is not None and not df_all.empty else None
            })
            
        except Exception as e:
            print(f"分析 {stock_code} 时出错: {e}")
            continue
    
    return high_rise_stocks


def get_stock_name(pro, ts_code):
    """获取股票名称"""
    try:
        # 获取股票基本信息
        stock_basic = pro.stock_basic(ts_code=ts_code, fields='name')
        if stock_basic is not None and not stock_basic.empty:
            return stock_basic.iloc[0]['name']
        else:
            return "未知"
    except:
        return "未知"


def display_high_rise_results(high_rise_stocks, trade_date):
    """显示高涨幅创新高股票结果"""
    if not high_rise_stocks:
        print("没有找到符合条件的股票！")
        return
    
    print("\n" + "="*100)
    print(f"📈 {trade_date} 高涨幅创新高股票分析结果")
    print("="*100)
    
    # 分类统计
    three_year_highs = [stock for stock in high_rise_stocks if stock['is_3y_high']]
    all_time_highs = [stock for stock in high_rise_stocks if stock['is_all_time_high']]
    
    print(f"\n📊 统计摘要:")
    print(f"   涨幅超过7%的股票总数: {len(high_rise_stocks)}")
    print(f"   其中3年新高股票: {len(three_year_highs)}")
    print(f"   其中历史新高股票: {len(all_time_highs)}")
    
    # 显示3年新高股票
    if three_year_highs:
        print(f"\n🏆 3年新高股票列表:")
        print("-" * 80)
        print(f"{'代码':<12} {'名称':<15} {'现价':<8} {'涨幅':<8} {'3年最高':<10} {'是否历史新高'}")
        print("-" * 80)
        
        for stock in sorted(three_year_highs, key=lambda x: x['pct_chg'], reverse=True):
            all_time_mark = "✅" if stock['is_all_time_high'] else "❌"
            print(f"{stock['ts_code']:<12} {stock['name']:<15} {stock['current_price']:<8.2f} "
                  f"{stock['pct_chg']:<8.2f}% {stock['max_3y']:<10.2f} {all_time_mark}")
    
    # 显示历史新高股票
    if all_time_highs:
        print(f"\n🎯 历史新高股票列表:")
        print("-" * 80)
        print(f"{'代码':<12} {'名称':<15} {'现价':<8} {'涨幅':<8} {'历史最高':<10}")
        print("-" * 80)
        
        for stock in sorted(all_time_highs, key=lambda x: x['pct_chg'], reverse=True):
            print(f"{stock['ts_code']:<12} {stock['name']:<15} {stock['current_price']:<8.2f} "
                  f"{stock['pct_chg']:<8.2f}% {stock['max_all']:<10.2f}")
    
    # 显示所有高涨幅股票
    print(f"\n📋 所有涨幅超过7%的股票:")
    print("-" * 80)
    print(f"{'代码':<12} {'名称':<15} {'现价':<8} {'涨幅':<8} {'3年新高':<8} {'历史新高':<8}")
    print("-" * 80)
    
    for stock in sorted(high_rise_stocks, key=lambda x: x['pct_chg'], reverse=True):
        three_year_mark = "✅" if stock['is_3y_high'] else "❌"
        all_time_mark = "✅" if stock['is_all_time_high'] else "❌"
        print(f"{stock['ts_code']:<12} {stock['name']:<15} {stock['current_price']:<8.2f} "
              f"{stock['pct_chg']:<8.2f}% {three_year_mark:<8} {all_time_mark:<8}")


def plot_high_rise_chart(high_rise_stocks, trade_date):
    """绘制高涨幅创新高股票图表"""
    if not high_rise_stocks:
        return
    
    # 准备数据
    three_year_highs = [stock for stock in high_rise_stocks if stock['is_3y_high']]
    all_time_highs = [stock for stock in high_rise_stocks if stock['is_all_time_high']]
    other_high_rise = [stock for stock in high_rise_stocks if not stock['is_3y_high']]
    
    # 创建图表
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))
    
    # 上图：涨幅分布
    categories = ['3年新高', '历史新高', '其他高涨幅']
    counts = [len(three_year_highs), len(all_time_highs), len(other_high_rise)]
    colors = ['#FF6B6B', '#4ECDC4', '#FFE66D']
    
    bars1 = ax1.bar(categories, counts, color=colors, alpha=0.8)
    ax1.set_title(f'{trade_date} 高涨幅股票分类统计', fontsize=14, fontweight='bold')
    ax1.set_ylabel('股票数量')
    ax1.grid(True, alpha=0.3)
    
    # 在柱子上添加数值标签
    for bar, count in zip(bars1, counts):
        if count > 0:
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                    str(count), ha='center', va='bottom', fontweight='bold')
    
    # 下图：涨幅分布散点图
    if high_rise_stocks:
        prices = [stock['current_price'] for stock in high_rise_stocks]
        pct_chgs = [stock['pct_chg'] for stock in high_rise_stocks]
        colors_scatter = ['red' if stock['is_3y_high'] else 'blue' for stock in high_rise_stocks]
        sizes = [100 if stock['is_all_time_high'] else 50 for stock in high_rise_stocks]
        
        scatter = ax2.scatter(prices, pct_chgs, c=colors_scatter, s=sizes, alpha=0.7)
        ax2.set_title(f'{trade_date} 高涨幅股票价格-涨幅分布', fontsize=14, fontweight='bold')
        ax2.set_xlabel('股价（元）')
        ax2.set_ylabel('涨幅（%）')
        ax2.grid(True, alpha=0.3)
        
        # 添加图例
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='red', alpha=0.7, label='3年新高'),
            Patch(facecolor='blue', alpha=0.7, label='其他高涨幅'),
            Patch(facecolor='white', edgecolor='black', label='大圆点=历史新高')
        ]
        ax2.legend(handles=legend_elements, loc='upper right')
    
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    print("🚀 开始分析高涨幅创新高股票...")
    find_high_rise_stocks() 