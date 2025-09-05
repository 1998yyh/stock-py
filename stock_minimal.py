# -*- coding: utf-8 -*-
# 最小版本 - 用于测试部署
import pandas as pd
import numpy as np
import datetime
import os
import threading
import time

# 模拟数据用于测试
def get_mock_stock_data():
    """生成模拟股票数据用于测试"""
    return pd.DataFrame({
        '代码': ['000001', '000002', '600000', '600036', '002415'],
        '名称': ['平安银行', '万科A', '浦发银行', '招商银行', '海康威视'],
        '涨跌幅': [2.5, 3.2, 1.8, 4.1, 2.9],
        '最新价': [12.5, 15.2, 8.9, 45.6, 32.1],
        '换手率': [6.5, 7.2, 5.8, 8.1, 6.9],
        '量比': [1.2, 1.5, 1.1, 1.8, 1.4],
        '流通市值': [50000000000, 80000000000, 30000000000, 120000000000, 90000000000]
    })

# 配置参数
SELECT_CONFIG = {
    'UpDownMin': 2,
    'UpDownMax': 6,
    'TurnoverMin': 5,
    'TurnoverMax': 10,
    'ValMin': 4000000000,
    'ValMax': 30000000000,
    'Ratio': 1
}

INDICATOR_CONFIG = {
    'RSI': {'enable': True, 'name': 'RSI指标'},
    'MACD': {'enable': False, 'name': 'MACD金叉'},
    'BOLL': {'enable': True, 'name': '布林线突破'},
    'OBV': {'enable': True, 'name': '量能潮'}
}

def get_data_date_info():
    """获取数据对应的日期信息"""
    now = datetime.datetime.now()
    current_time = now.time()
    cutoff_time = datetime.time(14, 50)
    
    today = now.strftime("%Y-%m-%d")
    yesterday = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    
    if current_time < cutoff_time:
        data_date = yesterday
        is_today_data = False
        next_update_time = datetime.datetime.combine(now.date(), cutoff_time)
    else:
        data_date = today
        is_today_data = True
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
    """获取符合条件的活跃股票（模拟版本）"""
    print("⚠️ 使用模拟数据（akshare未安装）")
    
    # 检查缓存
    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")
    yesterday = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    current_time = now.time()
    cutoff_time = datetime.time(14, 50)
    
    if not force_refresh and current_time < cutoff_time and use_cache:
        yesterday_cache = os.path.join("data", f"{yesterday}_current_stocks.txt")
        if os.path.exists(yesterday_cache):
            try:
                print(f"📁 14:50前，从缓存读取昨日数据: {yesterday_cache}")
                cached_data = pd.read_csv(yesterday_cache, sep="\t", encoding="utf-8")
                if not cached_data.empty:
                    return cached_data
            except Exception as e:
                print(f"⚠️ 昨日缓存读取失败: {e}")
    
    if use_cache and not force_refresh:
        today_cache = os.path.join("data", f"{today}_current_stocks.txt")
        if os.path.exists(today_cache):
            try:
                print(f"📁 从缓存读取今日数据: {today_cache}")
                cached_data = pd.read_csv(today_cache, sep="\t", encoding="utf-8")
                if not cached_data.empty:
                    return cached_data
            except Exception as e:
                print(f"⚠️ 今日缓存读取失败: {e}")
    
    # 使用模拟数据
    print("🎭 使用模拟股票数据...")
    filtered_stocks = get_mock_stock_data()
    
    # 保存缓存
    if save_cache and not filtered_stocks.empty:
        try:
            os.makedirs("data", exist_ok=True)
            save_date = datetime.datetime.now().strftime("%Y-%m-%d")
            cache_file = os.path.join("data", f"{save_date}_current_stocks.txt")
            filtered_stocks.to_csv(cache_file, sep="\t", index=False, encoding="utf-8")
            print(f"💾 模拟数据已缓存至: {cache_file}")
        except Exception as e:
            print(f"⚠️ 缓存保存失败: {e}")
    
    return filtered_stocks

def start_daily_update_task():
    """启动后台定时更新任务（模拟版本）"""
    print("📅 模拟定时更新任务已启动")

if __name__ == "__main__":
    print("🎭 运行模拟版本...")
    stocks = get_active_stocks()
    print(f"获取到 {len(stocks)} 只模拟股票数据")
    print(stocks)
