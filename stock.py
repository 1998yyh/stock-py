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



# 技术指标函数
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

# 技术指标配置
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
    'UpDownMin':5,      # 涨跌幅下限(%)
    'UpDownMax':10,     # 涨跌幅上限(%)
    'TurnoverMin':5,    # 换手率下限(%)
    'TurnoverMax':10,   # 换手率上限(%)
    'ValMin':4000000000,    # 流通市值下限(40亿)
    'ValMax':30000000000,   # 流通市值上限(300亿)
    'Ratio':1           # 量比最小值
}

def is_trading_day(date=None):
    """判断指定日期是否为交易日
    :param date: 指定日期，默认为今天
    :return: True表示交易日，False表示非交易日
    """
    if date is None:
        check_date = datetime.datetime.now()
    else:
        if isinstance(date, str):
            check_date = datetime.datetime.strptime(date, "%Y-%m-%d")
        else:
            check_date = date
    
    # 检查是否为周末
    if check_date.weekday() >= 5:  # 5=周六, 6=周日
        return False
    
    # 检查是否为节假日（这里可以扩展为更完整的节假日判断）
    # 简单实现：可以在这里添加具体的节假日日期
    holidays = [
        # 2024年节假日示例（可根据实际情况更新）
        "2024-01-01",  # 元旦
        "2024-02-10", "2024-02-11", "2024-02-12", "2024-02-13", "2024-02-14", "2024-02-15", "2024-02-16", "2024-02-17",  # 春节
        "2024-04-04", "2024-04-05", "2024-04-06",  # 清明节
        "2024-05-01", "2024-05-02", "2024-05-03",  # 劳动节
        "2024-06-10",  # 端午节
        "2024-09-15", "2024-09-16", "2024-09-17",  # 中秋节
        "2024-10-01", "2024-10-02", "2024-10-03", "2024-10-04", "2024-10-05", "2024-10-06", "2024-10-07",  # 国庆节
        
        # 2025年节假日示例
        "2025-01-01",  # 元旦
        "2025-01-28", "2025-01-29", "2025-01-30", "2025-01-31", "2025-02-01", "2025-02-02", "2025-02-03", "2025-02-04",  # 春节
        "2025-04-05", "2025-04-06", "2025-04-07",  # 清明节
        "2025-05-01", "2025-05-02", "2025-05-03",  # 劳动节
        "2025-05-31",  # 端午节
        "2025-10-01", "2025-10-02", "2025-10-03", "2025-10-04", "2025-10-05", "2025-10-06", "2025-10-07",  # 国庆节
    ]
    
    date_str = check_date.strftime("%Y-%m-%d")
    if date_str in holidays:
        return False
    
    return True

def get_next_trading_day(date=None):
    """获取下个交易日日期
    :param date: 指定日期，默认为今天
    :return: 下个交易日的日期字符串 (YYYY-MM-DD)
    """
    if date is None:
        current = datetime.datetime.now()
    else:
        if isinstance(date, str):
            current = datetime.datetime.strptime(date, "%Y-%m-%d")
        else:
            current = date
    
    # 往后推，找到下个交易日
    next_day = current + datetime.timedelta(days=1)
    
    # 循环直到找到交易日
    while not is_trading_day(next_day):
        next_day = next_day + datetime.timedelta(days=1)
    
    return next_day.strftime("%Y-%m-%d")

def get_last_trading_day(date=None):
    """获取上个交易日日期
    :param date: 指定日期，默认为今天
    :return: 上个交易日的日期字符串 (YYYY-MM-DD)
    """
    if date is None:
        current = datetime.datetime.now()
    else:
        if isinstance(date, str):
            current = datetime.datetime.strptime(date, "%Y-%m-%d")
        else:
            current = date
    
    # 往前推，找到上个交易日
    last_day = current - datetime.timedelta(days=1)
    
    # 循环直到找到交易日
    while not is_trading_day(last_day):
        last_day = last_day - datetime.timedelta(days=1)
    
    return last_day.strftime("%Y-%m-%d")

def get_stock_data_with_fallback():
    """
    获取股票实时数据，支持多数据源备用机制
    优先使用东财数据源，失败时切换到同花顺数据源
    """
    print("🌐 正在获取实时股票数据...")
    
    # 尝试东财数据源 (stock_zh_a_spot_em)
    try:
        print("📊 尝试使用东财数据源 (akshare.stock_zh_a_spot_em)...")
        stock_data = ak.stock_zh_a_spot_em()
        
        if stock_data is not None and not stock_data.empty:
            print(f"✅ 东财数据源获取成功，共 {len(stock_data)} 只股票")
            return stock_data, "东财数据源"
        else:
            print("⚠️ 东财数据源返回空数据，尝试备用数据源")
            raise Exception("东财数据源返回空数据")
            
    except Exception as e:
        print(f"❌ 东财数据源获取失败: {str(e)}")
        print("🔄 切换到同花顺数据源...")
        
    # 尝试同花顺数据源 (stock_zh_a_spot_ths)
    try:
        print("📊 尝试使用同花顺数据源 (akshare.stock_zh_a_spot_ths)...")
        stock_data = ak.stock_zh_a_spot_ths()
        
        if stock_data is not None and not stock_data.empty:
            print(f"✅ 同花顺数据源获取成功，共 {len(stock_data)} 只股票")
            
            # 统一字段名称，确保与东财数据源格式一致
            column_mapping = {
                '股票代码': '代码',
                '股票名称': '名称', 
                '现价': '最新价',
                '涨跌': '涨跌额',
                '涨跌幅': '涨跌幅',
                '今开': '今开',
                '最高': '最高',
                '最低': '最低',
                '昨收': '昨收',
                '成交量': '成交量',
                '成交额': '成交额',
                '换手': '换手率',
                '市盈率': '市盈率',
                '市净率': '市净率',
                '总市值': '总市值',
                '流通市值': '流通市值'
            }
            
            # 重命名列
            for old_name, new_name in column_mapping.items():
                if old_name in stock_data.columns:
                    stock_data = stock_data.rename(columns={old_name: new_name})
            
            # 添加缺失的列（如果同花顺数据源没有）
            required_columns = ['代码', '名称', '最新价', '涨跌幅', '换手率', '流通市值', '量比']
            for col in required_columns:
                if col not in stock_data.columns:
                    if col == '量比':
                        stock_data[col] = 1.0  # 默认量比为1
                    else:
                        stock_data[col] = 0
                        
            return stock_data, "同花顺数据源"
        else:
            print("⚠️ 同花顺数据源返回空数据")
            raise Exception("同花顺数据源返回空数据")
            
    except Exception as e:
        print(f"❌ 同花顺数据源获取失败: {str(e)}")
        print("🔄 尝试腾讯财经数据源...")
        
    # 尝试腾讯财经数据源 (stock_zh_a_spot_tx)
    try:
        print("📊 尝试使用腾讯财经数据源 (akshare.stock_zh_a_spot_tx)...")
        stock_data = ak.stock_zh_a_spot_tx()
        
        if stock_data is not None and not stock_data.empty:
            print(f"✅ 腾讯财经数据源获取成功，共 {len(stock_data)} 只股票")
            
            # 统一字段名称
            column_mapping = {
                'code': '代码',
                'name': '名称',
                'price': '最新价',
                'change': '涨跌额',
                'changepercent': '涨跌幅',
                'open': '今开',
                'high': '最高',
                'low': '最低',
                'settlement': '昨收',
                'volume': '成交量',
                'turnoverratio': '换手率',
                'amount': '成交额',
                'per': '市盈率',
                'pb': '市净率',
                'mktcap': '总市值',
                'nmc': '流通市值'
            }
            
            # 重命名列
            for old_name, new_name in column_mapping.items():
                if old_name in stock_data.columns:
                    stock_data = stock_data.rename(columns={old_name: new_name})
            
            # 添加缺失的列
            required_columns = ['代码', '名称', '最新价', '涨跌幅', '换手率', '流通市值', '量比']
            for col in required_columns:
                if col not in stock_data.columns:
                    if col == '量比':
                        stock_data[col] = 1.0  # 默认量比为1
                    else:
                        stock_data[col] = 0
                        
            return stock_data, "腾讯财经数据源"
        else:
            print("⚠️ 腾讯财经数据源返回空数据")
            raise Exception("腾讯财经数据源返回空数据")
            
    except Exception as e:
        print(f"❌ 腾讯财经数据源获取失败: {str(e)}")
        
    # 所有数据源都失败
    print("❌ 所有数据源都无法获取数据，请检查网络连接或稍后重试")
    return pd.DataFrame(), "无可用数据源"

def get_data_date_info():
    """获取数据对应的日期信息"""
    now = datetime.datetime.now()
    current_time = now.time()
    cutoff_time = datetime.time(14, 50)  # 14:50
    
    today = now.strftime("%Y-%m-%d")
    last_trading_day = get_last_trading_day()
    
    # 判断当前应该显示哪天的数据
    if current_time < cutoff_time:
        # 14:50前显示上个交易日数据
        data_date = last_trading_day
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
        'last_trading_day': last_trading_day,
        'current_time': now.strftime("%Y-%m-%d %H:%M:%S"),
        'next_update_time': next_update_time.strftime("%Y-%m-%d %H:%M:%S"),
        'time_status': '今日数据' if is_today_data else f'上个交易日数据（{last_trading_day}，{cutoff_time.strftime("%H:%M")}后更新为今日数据）'
    }

def get_active_stocks(use_cache=True, save_cache=True, force_refresh=False):
    """ 获取符合条件的活跃股票 
    :param use_cache: 是否优先使用缓存数据
    :param save_cache: 是否保存数据到缓存
    :param force_refresh: 是否强制刷新数据（忽略时间判断）
    """
    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")
    last_trading_day = get_last_trading_day()
    current_time = now.time()
    
    # 判断当前时间是否在14:50之前
    cutoff_time = datetime.time(14, 50)  # 14:50
    
    # 如果不是强制刷新，且当前时间在14:50之前，尝试读取上个交易日数据
    if not force_refresh and current_time < cutoff_time and use_cache:
        last_trading_day_cache = os.path.join("data", f"{last_trading_day}_current_stocks.txt")
        if os.path.exists(last_trading_day_cache):
            try:
                print(f"📁 14:50前，从缓存读取上个交易日数据: {last_trading_day_cache}")
                cached_data = pd.read_csv(last_trading_day_cache, sep="\t", encoding="utf-8", comment='#')
                if not cached_data.empty:
                    # 尝试读取数据源信息
                    data_source_info = "未知数据源"
                    try:
                        with open(last_trading_day_cache, 'r', encoding='utf-8') as f:
                            first_line = f.readline().strip()
                            if first_line.startswith("# 数据来源:"):
                                data_source_info = first_line.replace("# 数据来源:", "").strip()
                    except:
                        pass
                    print(f"✅ 上个交易日缓存数据加载成功，共 {len(cached_data)} 只股票 (数据源: {data_source_info})")
                    return cached_data
            except Exception as e:
                print(f"⚠️ 上个交易日缓存读取失败: {e}")
    
    # 检查今日缓存（14:50后或强制刷新时优先使用）
    if use_cache and not force_refresh:
        today_cache = os.path.join("data", f"{today}_current_stocks.txt")
        if os.path.exists(today_cache):
            try:
                print(f"📁 从缓存读取今日数据: {today_cache}")
                cached_data = pd.read_csv(today_cache, sep="\t", encoding="utf-8", comment='#')
                if not cached_data.empty:
                    # 尝试读取数据源信息
                    data_source_info = "未知数据源"
                    try:
                        with open(today_cache, 'r', encoding='utf-8') as f:
                            first_line = f.readline().strip()
                            if first_line.startswith("# 数据来源:"):
                                data_source_info = first_line.replace("# 数据来源:", "").strip()
                    except:
                        pass
                    print(f"✅ 今日缓存数据加载成功，共 {len(cached_data)} 只股票 (数据源: {data_source_info})")
                    return cached_data
            except Exception as e:
                print(f"⚠️ 今日缓存读取失败: {e}，将重新获取数据")
    
    # 获取实时数据（使用备用数据源机制）
    stock_data, data_source = get_stock_data_with_fallback()
    if stock_data.empty:
        print("❌ 未能从任何数据源获取到 A 股实时数据")
        return pd.DataFrame()
    
    print(f"📊 数据来源: {data_source}")
    print(f"🔢 获取到股票总数: {len(stock_data)}")
    
    # 显示数据列信息用于调试
    print(f"📋 数据列名: {list(stock_data.columns)}")

    # 转换数值类型，防止 NaN 数据
    for col in ["换手率", "涨跌幅", "流通市值", "量比"]:
        stock_data[col] = pd.to_numeric(stock_data[col], errors="coerce")

    selected_stocks = stock_data[stock_data["代码"].str.startswith(("00", "60"))]

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
    # **打印筛选出的股票**
    print("\n===== 初步筛选出的股票 =====")
    for index, row in filtered_stocks.iterrows():
        print(f"代码: {row['代码']} | 名称: {row['名称']}-- {row['涨跌幅']}%")
    
    # 技术指标筛选
    print("\n===== 技术指标筛选 =====")
    
    for indicator_name, config in INDICATOR_CONFIG.items():
        if config['enable']:
            before_count = len(filtered_stocks)
            filtered_stocks = filtered_stocks[filtered_stocks["代码"].apply(config['func'])]
            print(f"{indicator_name}筛选后剩余: {len(filtered_stocks)}/{before_count}",filtered_stocks["代码"].to_numpy())
            if filtered_stocks.empty:
                return pd.DataFrame()

    # 保存缓存（包含数据源信息）
    if save_cache and not filtered_stocks.empty:
        try:
            os.makedirs("data", exist_ok=True)
            # 保存时使用今日日期
            save_date = datetime.datetime.now().strftime("%Y-%m-%d")
            cache_file = os.path.join("data", f"{save_date}_current_stocks.txt")
            
            # 添加数据源信息到文件头部
            with open(cache_file, 'w', encoding='utf-8') as f:
                # 写入元数据信息
                f.write(f"# 数据来源: {data_source}\n")
                f.write(f"# 生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# 股票数量: {len(filtered_stocks)}\n")
                f.write("# " + "="*50 + "\n")
                
            # 追加数据内容
            filtered_stocks.to_csv(cache_file, sep="\t", index=False, encoding="utf-8", mode='a')
            print(f"💾 数据已缓存至: {cache_file} (数据源: {data_source})")
        except Exception as e:
            print(f"⚠️ 缓存保存失败: {e}")

    return filtered_stocks




# 测试代码已移除，请使用API接口进行测试

def auto_daily_update():
    """自动每日更新任务：只在交易日的14:50自动获取数据"""
    while True:
        try:
            now = datetime.datetime.now()
            target_time = datetime.time(14, 50)  # 14:50
            current_time = now.time()
            
            # 检查今天是否为交易日
            today_is_trading_day = is_trading_day(now)
            
            if today_is_trading_day:
                # 今天是交易日
                if current_time < target_time:
                    # 今天还没到14:50，等待到14:50
                    target_datetime = datetime.datetime.combine(now.date(), target_time)
                    wait_seconds = (target_datetime - now).total_seconds()
                    print(f"⏰ 今日为交易日，将在 {target_datetime.strftime('%Y-%m-%d %H:%M:%S')} 自动更新股票数据")
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
                    
                    # 更新完成后，等待到下个交易日
                    next_trading_day = get_next_trading_day(now)
                    next_target = datetime.datetime.strptime(f"{next_trading_day} 14:50:00", "%Y-%m-%d %H:%M:%S")
                    wait_seconds = (next_target - datetime.datetime.now()).total_seconds()
                    print(f"📅 下次数据更新时间: {next_target.strftime('%Y-%m-%d %H:%M:%S')} (下个交易日)")
                    time.sleep(max(wait_seconds, 60))  # 至少等待1分钟
                else:
                    # 今天是交易日但已过14:50，等待到下个交易日
                    next_trading_day = get_next_trading_day(now)
                    next_target = datetime.datetime.strptime(f"{next_trading_day} 14:50:00", "%Y-%m-%d %H:%M:%S")
                    wait_seconds = (next_target - now).total_seconds()
                    print(f"⏰ 今日已过更新时间，等待下个交易日 {next_target.strftime('%Y-%m-%d %H:%M:%S')} 更新")
                    time.sleep(max(wait_seconds, 60))
            else:
                # 今天不是交易日，等待到下个交易日
                next_trading_day = get_next_trading_day(now)
                next_target = datetime.datetime.strptime(f"{next_trading_day} 14:50:00", "%Y-%m-%d %H:%M:%S")
                wait_seconds = (next_target - now).total_seconds()
                
                # 判断今天是周末还是节假日
                if now.weekday() >= 5:
                    day_type = "周末"
                else:
                    day_type = "节假日"
                
                print(f"📅 今日为{day_type}，不进行数据更新，等待下个交易日 {next_target.strftime('%Y-%m-%d %H:%M:%S')}")
                time.sleep(max(wait_seconds, 3600))  # 非交易日至少等待1小时
                
        except Exception as e:
            print(f"⚠️ 定时任务异常: {e}")
            # 异常时等待1小时后重试
            time.sleep(3600)

def start_daily_update_task():
    """启动后台定时更新任务"""
    task_thread = threading.Thread(target=auto_daily_update, daemon=True)
    task_thread.start()
    
    # 显示任务启动信息
    now = datetime.datetime.now()
    today_is_trading_day = is_trading_day(now)
    
    if today_is_trading_day:
        next_update = datetime.datetime.combine(now.date(), datetime.time(14, 50))
        if now.time() >= datetime.time(14, 50):
            # 今天已过更新时间，显示下个交易日
            next_trading_day = get_next_trading_day(now)
            next_update = datetime.datetime.strptime(f"{next_trading_day} 14:50:00", "%Y-%m-%d %H:%M:%S")
        print(f"📅 后台定时更新任务已启动（仅交易日运行）")
        print(f"⏰ 下次更新时间: {next_update.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        next_trading_day = get_next_trading_day(now)
        next_update = datetime.datetime.strptime(f"{next_trading_day} 14:50:00", "%Y-%m-%d %H:%M:%S")
        day_type = "周末" if now.weekday() >= 5 else "节假日"
        print(f"📅 后台定时更新任务已启动（仅交易日运行）")
        print(f"📝 今日为{day_type}，下次更新时间: {next_update.strftime('%Y-%m-%d %H:%M:%S')}")
