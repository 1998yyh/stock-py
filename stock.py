# -*- coding: utf-8 -*-
import akshare as ak
import pandas as pd
import numpy as np
import datetime
import os
import threading
import time
# import talib  # 暂时注释掉，因为安装有问题

# from talib import abstract
# from functools import lru_cache

def has_strong_support(stock_code):
    """ 判断股票是否在成交密集区上方 """
    try:
        # 获取最近 40 天 K 线数据，确保至少有 20 个交易日
        end_date = datetime.datetime.now().strftime("%Y%m%d")
        start_date = (datetime.datetime.now() - datetime.timedelta(days=40)).strftime("%Y%m%d")
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=start_date, end_date=end_date, adjust="")

        # 确保有足够的 20 根日K数据
        df = df.tail(20)
        if df.empty or len(df) < 20:
            return False

        # 计算均价（四价平均）
        df["均价"] = (df["收盘"] + df["开盘"] + df["最高"] + df["最低"]) / 4

        # 计算成交密集区
        hist, bin_edges = np.histogram(df["均价"], bins=10, weights=df["成交量"])

        # 找到成交量最高的价格区间
        max_bin_index = np.argmax(hist)
        #strong_support_zone = bin_edges[max_bin_index]  # 该区间的最小价格作为支撑位
        strong_support_zone = (bin_edges[max_bin_index] + bin_edges[max_bin_index + 1]) / 2  #优化 更准确地找到成交密集区的中心支撑位，而不是仅取区间下限。

        # 获取当前股价
        latest_price = df["收盘"].iloc[-1]
        print(f"{stock_code}: 当前股价 {latest_price}, 支撑位 {strong_support_zone}")

        return latest_price > strong_support_zone
    except Exception as e:
        print(f"{stock_code}: 支撑计算错误 {e}")
        return False
def has_support(stock_code):
    """ 判断股价是否一直在均线上方 """
    try:
        df = ak.stock_zh_a_hist_min_em(symbol=stock_code, period="1", adjust="")
        if df.empty or len(df) < 5:
            return False

        # 计算 5 均线
        df["intraday_MA"] = df["收盘"].rolling(window=5).mean()
        df.dropna(inplace=True)

        # 要求每一分钟股价都在均线上方
        return (df["收盘"] >= df["intraday_MA"] * 0.98).all()
    except Exception as e:
        print(f"{stock_code}: 均线计算错误 {e}")
        return False

def is_volume_stable(stock_code):
    """ 判断成交量是否稳定 """
    try:
        df = ak.stock_zh_a_hist_min_em(symbol=stock_code, period="1", adjust="")
        if df.empty or len(df) < 10:
            return False

        volume_std = np.std(df["成交量"], ddof=0)
        volume_mean = np.mean(df["成交量"])

        if volume_mean == 0:
            return False

        # 计算变异系数（波动率）
        volume_cv = volume_std / volume_mean

        return 1.5 <= volume_cv <= 1.8  # 设定波动范围
    except Exception as e:
        print(f"{stock_code}: 成交量计算错误 {e}")
        return False

# 修改策略配置结构
STRATEGY_CONFIG = {
    'volume_stable': {
        'enable': True,
        'name': '成交量稳定',  # 添加name字段
        'func': is_volume_stable,
        'msg': '无成交量稳定的股票'
    },
    'ma_support': {
        'enable': False,
        'name': '均线支撑',  # 添加name字段
        'func': has_support,
        'msg': '无符合均线支撑条件的股票'
    },
    'strong_support': {
        'enable': False,
        'name': '密集区支撑',  # 添加name字段
        'func': has_strong_support,
        'msg': '无成交密集区支撑的股票'
    }
}



# 新增技术指标函数 ↓
# @lru_cache(maxsize=100)
def get_hist_data(stock_code, end_date=None, lookback_days=60):
    """获取带技术指标的日线数据（支持指定截止日期）。
    :param end_date: 字符串 YYYY-MM-DD 或 YYYYMMDD，默认至今天
    :param lookback_days: 回看天数，用于计算指标
    """
    if end_date is None:
        end_dt = datetime.datetime.now()
    else:
        try:
            if "-" in end_date:
                end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d")
            else:
                end_dt = datetime.datetime.strptime(end_date, "%Y%m%d")
        except Exception:
            end_dt = datetime.datetime.now()
    start_dt = end_dt - datetime.timedelta(days=lookback_days)
    end_str = end_dt.strftime("%Y%m%d")
    start_str = start_dt.strftime("%Y%m%d")
    return ak.stock_zh_a_hist(symbol=stock_code, period="daily",
                            start_date=start_str, end_date=end_str, adjust="qfq")

def check_macd(stock_code, end_date=None):
    # 暂时返回True，因为talib未安装
    return True

def check_rsi(stock_code, end_date=None):
    # 暂时返回True，因为talib未安装
    return True

def check_bollinger(stock_code, end_date=None):
    # 暂时返回True，因为talib未安装
    return True

def check_obv(stock_code, period=14, end_date=None):
    """ 参数化量能潮指标 
    :param period: OBV均线周期（默认14日）
    """
    # 暂时返回True，因为talib未安装
    return True

# 在导入区域添加 ↓
# - RSI优先 ：快速排除超买（>70）或超卖（<30）的股票
# - MACD第二 ：捕捉短期趋势启动信号（金叉）
# - BOLL第三 ：确认突破布林线上轨的强势形态
# - OBV最后 ：验证量价同步的健康上涨
INDICATOR_CONFIG = {
    'RSI': {
        'enable': True,
        'name': 'RSI指标',
        'period': 14,  #7日线代表短期, 24日代表中长期
        'min': 30,
        'max': 70,
        'func': check_rsi
    },
    'MACD': {
        'enable': False,
        'name': 'MACD金叉',
        'fast': 12,
        'slow': 26,
        'signal': 9,
        'func': check_macd
    },
    'BOLL': {
        'enable': True,
        'name': '布林线突破',
        'period': 20,
        'func': check_bollinger
    },
    'OBV': {
        'enable': True,
        'name': '量能潮',
        'period': 14,  #6- 24
        'func': check_obv
    }
}

SELECT_CONFIG={
    'UpDownMin':2,      # 涨跌幅下限(%)
    'UpDownMax':6,      # 涨跌幅上限(%)
    'TurnoverMin':5,    # 换手率下限(%)
    'TurnoverMax':10,   # 换手率上限(%)
    'ValMin':4000000000,    # 流通市值下限(40亿)
    'ValMax':30000000000,   # 流通市值上限(300亿)
    'Ratio':1           # 量比最小值
}

def get_data_date_info():
    """获取数据对应的日期信息"""
    now = datetime.datetime.now()
    current_time = now.time()
    cutoff_time = datetime.time(14, 50)  # 14:50
    
    today = now.strftime("%Y-%m-%d")
    yesterday = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    
    # 判断当前应该显示哪天的数据
    if current_time < cutoff_time:
        # 14:50前显示昨日数据
        data_date = yesterday
        is_today_data = False
        next_update_time = datetime.datetime.combine(now.date(), cutoff_time)
    else:
        # 14:50后显示今日数据
        data_date = today
        is_today_data = True
        # 下次更新时间是明天14:50
        tomorrow = now + datetime.timedelta(days=1)
        next_update_time = datetime.datetime.combine(tomorrow.date(), cutoff_time)
    
    return {
        'data_date': data_date,
        'is_today_data': is_today_data,
        'current_time': now.strftime("%Y-%m-%d %H:%M:%S"),
        'next_update_time': next_update_time.strftime("%Y-%m-%d %H:%M:%S"),
        'time_status': '今日数据' if is_today_data else f'昨日数据（{cutoff_time.strftime("%H:%M")}后更新为今日数据）'
    }

def get_active_stocks(use_cache=True, save_cache=True, force_refresh=False):
    """ 获取符合条件的活跃股票 
    :param use_cache: 是否优先使用缓存数据
    :param save_cache: 是否保存数据到缓存
    :param force_refresh: 是否强制刷新数据（忽略时间判断）
    """
    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")
    yesterday = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    current_time = now.time()
    
    # 判断当前时间是否在14:50之前
    cutoff_time = datetime.time(14, 50)  # 14:50
    
    # 如果不是强制刷新，且当前时间在14:50之前，尝试读取昨日数据
    if not force_refresh and current_time < cutoff_time and use_cache:
        yesterday_cache = os.path.join("data", f"{yesterday}_current_stocks.txt")
        if os.path.exists(yesterday_cache):
            try:
                print(f"📁 14:50前，从缓存读取昨日数据: {yesterday_cache}")
                cached_data = pd.read_csv(yesterday_cache, sep="\t", encoding="utf-8")
                if not cached_data.empty:
                    print(f"✅ 昨日缓存数据加载成功，共 {len(cached_data)} 只股票")
                    return cached_data
            except Exception as e:
                print(f"⚠️ 昨日缓存读取失败: {e}")
    
    # 检查今日缓存（14:50后或强制刷新时优先使用）
    if use_cache and not force_refresh:
        today_cache = os.path.join("data", f"{today}_current_stocks.txt")
        if os.path.exists(today_cache):
            try:
                print(f"📁 从缓存读取今日数据: {today_cache}")
                cached_data = pd.read_csv(today_cache, sep="\t", encoding="utf-8")
                if not cached_data.empty:
                    print(f"✅ 今日缓存数据加载成功，共 {len(cached_data)} 只股票")
                    return cached_data
            except Exception as e:
                print(f"⚠️ 今日缓存读取失败: {e}，将重新获取数据")
    
    # 获取实时数据
    print("🌐 正在获取实时股票数据...")
    stock_data = ak.stock_zh_a_spot_em()
    if stock_data.empty:
        print("未能获取到 A 股实时数据")
        return pd.DataFrame()

    # 转换数值类型，防止 NaN 数据
    for col in ["换手率", "涨跌幅", "流通市值", "量比"]:
        stock_data[col] = pd.to_numeric(stock_data[col], errors="coerce")

    selected_stocks = stock_data[stock_data["代码"].str.startswith(("00", "60"))]
    # print(pd.DataFrame(selected_stocks))

    filtered_stocks = selected_stocks[
        (selected_stocks["涨跌幅"] >=SELECT_CONFIG['UpDownMin']) & 
        (selected_stocks["涨跌幅"] <= SELECT_CONFIG['UpDownMax']) & 
        (selected_stocks["换手率"] >= SELECT_CONFIG['TurnoverMin']) & 
        (selected_stocks["换手率"] <= SELECT_CONFIG['TurnoverMax']) & 
        (selected_stocks["流通市值"] >= SELECT_CONFIG['ValMin']) & 
        (selected_stocks["流通市值"] <= SELECT_CONFIG['ValMax']) & 
        (selected_stocks["量比"] > SELECT_CONFIG['Ratio'])
    ]
    if filtered_stocks.empty:
        print("\nx 没有符合初步筛选条件的股票")
        return pd.DataFrame()

    # print(pd.DataFrame(filtered_stocks))
    # **打印筛选出的股票**
    print("\n===== 初步筛选出的股票 =====")
    for index, row in filtered_stocks.iterrows():
        print(f"代码: {row['代码']} | 名称: {row['名称']}-- {row['涨跌幅']}%")
    
    # 使用策略配置进行循环筛选
    # for config in STRATEGY_CONFIG.items():
    #     if not config['enable']:
    #         continue
            
    #     filtered_stocks = filtered_stocks[filtered_stocks["代码"].apply(config['func'])]
    #     if filtered_stocks.empty:
    #         print(f"\nx {config['msg']}，停止筛选")
    #         return pd.DataFrame()

    # 新增技术指标筛选 ↓
    print("\n===== 技术指标筛选 =====")
    
    for indicator_name, config in INDICATOR_CONFIG.items():
        if config['enable']:
            before_count = len(filtered_stocks)
            filtered_stocks = filtered_stocks[filtered_stocks["代码"].apply(config['func'])]
            print(f"{indicator_name}筛选后剩余: {len(filtered_stocks)}/{before_count}",filtered_stocks["代码"].to_numpy())
            if filtered_stocks.empty:
                return pd.DataFrame()

    # 保存缓存
    if save_cache and not filtered_stocks.empty:
        try:
            os.makedirs("data", exist_ok=True)
            # 保存时使用今日日期
            save_date = datetime.datetime.now().strftime("%Y-%m-%d")
            cache_file = os.path.join("data", f"{save_date}_current_stocks.txt")
            filtered_stocks.to_csv(cache_file, sep="\t", index=False, encoding="utf-8")
            print(f"💾 数据已缓存至: {cache_file}")
        except Exception as e:
            print(f"⚠️ 缓存保存失败: {e}")

    return filtered_stocks




if __name__ == "__main__":
    active_stocks = get_active_stocks()
    # pd.set_option("display.float_format", "{:.2f}".format)

    if active_stocks.empty:
        print("\n- 无符合条件的股票，程序结束")
    else:
        # print(active_stocks[["代码", "名称", "最新价", "涨跌幅", "流通市值", "换手率", "量比"]].to_string(index=False))
        print( pd.DataFrame(active_stocks,columns=["代码","名称","涨跌幅", "最新价",   "换手率", "量比","流通市值"]))

        # 获取次日日期
        tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

        # 目标文件夹路径
        folder_path = r"data"
        os.makedirs(folder_path, exist_ok=True)

        # 生成 TXT 文件路径
        file_path = os.path.join(folder_path, f"{tomorrow}.txt")

        # 保存数据到 TXT
        active_stocks.to_csv(file_path, sep="\t", index=False, encoding="utf-8")
        print(f"数据已保存至 {file_path}")

def auto_daily_update():
    """自动每日更新任务：在14:50自动获取今日数据"""
    while True:
        try:
            now = datetime.datetime.now()
            target_time = datetime.time(14, 50)  # 14:50
            current_time = now.time()
            
            # 计算到目标时间的等待时间
            if current_time < target_time:
                # 今天还没到14:50
                target_datetime = datetime.datetime.combine(now.date(), target_time)
            else:
                # 今天已过14:50，等待明天14:50
                tomorrow = now.date() + datetime.timedelta(days=1)
                target_datetime = datetime.datetime.combine(tomorrow, target_time)
            
            wait_seconds = (target_datetime - now).total_seconds()
            print(f"⏰ 定时任务启动，将在 {target_datetime.strftime('%Y-%m-%d %H:%M:%S')} 自动更新今日数据")
            
            # 等待到目标时间
            time.sleep(wait_seconds)
            
            # 执行数据更新
            print("🚀 开始自动更新今日股票数据...")
            try:
                stocks = get_active_stocks(use_cache=False, save_cache=True, force_refresh=True)
                if not stocks.empty:
                    print(f"✅ 自动更新完成，获取到 {len(stocks)} 只股票")
                else:
                    print("⚠️ 自动更新完成，但未获取到股票数据")
            except Exception as e:
                print(f"❌ 自动更新失败: {e}")
                
        except Exception as e:
            print(f"⚠️ 定时任务异常: {e}")
            # 异常时等待1小时后重试
            time.sleep(3600)

def start_daily_update_task():
    """启动后台定时更新任务"""
    task_thread = threading.Thread(target=auto_daily_update, daemon=True)
    task_thread.start()
    print("📅 后台定时更新任务已启动")
