import tushare as ts
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from config import TUSHARE_TOKEN, MAX_YEARS
import pandas as pd

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False


def is_today_highest(stock_code: str):
    # 初始化 tushare
    ts.set_token(TUSHARE_TOKEN)
    pro = ts.pro_api()

    # 计算日期范围
    end_date = datetime.today()
    start_date = end_date - timedelta(days=MAX_YEARS * 365)
    end_date_str = end_date.strftime('%Y%m%d')
    start_date_str = start_date.strftime('%Y%m%d')

    # 判断股票类型
    if stock_code.endswith('.SZ') or stock_code.endswith('.SH') or stock_code.endswith('.BJ'):
        # A股
        df = pro.daily(ts_code=stock_code, start_date=start_date_str, end_date=end_date_str)
        market = 'A股'
    elif stock_code.endswith('.HK'):
        # 港股
        df = pro.hk_daily(ts_code=stock_code, start_date=start_date_str, end_date=end_date_str)
        market = '港股'
    elif stock_code.endswith('.US'):
        # 美股
        df = pro.us_daily(ts_code=stock_code, start_date=start_date_str, end_date=end_date_str)
        market = '美股'
    else:
        print(f"无法识别股票代码后缀，请输入标准股票代码，如 000001.SZ、01810.HK、AAPL.US")
        return

    if df is None or df.empty:
        print(f"未获取到股票 {stock_code} 的历史数据！请检查代码、权限或Tushare接口权限。")
        return

    # 按交易日期排序（最新在前）
    df = df.sort_values('trade_date', ascending=False)
    today_close = df.iloc[0]['close']
    max_close = df['close'].max()
    today_date = df.iloc[0]['trade_date']

    # 绘制价格曲线
    plot_price_curve(df, stock_code, market, today_close, max_close, today_date)
    print(df.head(10))

    if today_close >= max_close:
        print(f"{stock_code}（{market}）在 {today_date} 的收盘价 {today_close} 是近{MAX_YEARS}年内最高价！")
        return True
    else:
        print(f"{stock_code}（{market}）在 {today_date} 的收盘价 {today_close} 不是近{MAX_YEARS}年内最高价，最高为 {max_close}")
        return False


def plot_price_curve(df, stock_code, market, today_close, max_close, today_date):
    """绘制股价曲线"""
    # 转换日期格式
    df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
    
    # 按日期正序排列
    df_sorted = df.sort_values('trade_date')
    
    # 创建图表
    plt.figure(figsize=(12, 8))
    
    # 绘制收盘价曲线
    plt.plot(df_sorted['trade_date'], df_sorted['close'], linewidth=2, color='blue', label='收盘价')
    
    # 标注最高价点
    max_price_date = df_sorted.loc[df_sorted['close'].idxmax(), 'trade_date']
    plt.scatter(max_price_date, max_close, color='red', s=100, zorder=5, label=f'最高价: {max_close:.2f}')
    plt.annotate(f'最高价\n{max_close:.2f}', 
                xy=(max_price_date, max_close), 
                xytext=(10, 10), textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='red', alpha=0.7),
                fontsize=10, color='white')
    
    # 标注今日价格
    today_date_dt = pd.to_datetime(today_date, format='%Y%m%d')
    plt.scatter(today_date_dt, today_close, color='green', s=100, zorder=5, label=f'今日价格: {today_close:.2f}')
    plt.annotate(f'今日价格\n{today_close:.2f}', 
                xy=(today_date_dt, today_close), 
                xytext=(10, -20), textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='green', alpha=0.7),
                fontsize=10, color='white')
    
    # 设置图表属性
    plt.title(f'{stock_code}（{market}）近{MAX_YEARS}年股价走势图', fontsize=16, fontweight='bold')
    plt.xlabel('日期', fontsize=12)
    plt.ylabel('股价（元）', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # 设置x轴日期格式
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.xticks(rotation=45)
    
    # 自动调整布局
    plt.tight_layout()
    
    # 显示图表
    plt.show()


if __name__ == "__main__":
    # 示例：输入股票代码
    stock_code = input("请输入股票代码（如 000001.SZ、01810.HK、AAPL.US）: ")
    is_today_highest(stock_code) 