#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票筛选系统测试脚本
"""

import requests
import json

def test_api():
    """测试API接口"""
    base_url = "http://8.152.212.206/api"
    
    print("🧪 开始测试API接口...")
    
    # 测试配置接口
    try:
        response = requests.get(f"{base_url}/config")
        if response.status_code == 200:
            data = response.json()
            print("✅ 配置接口正常")
            print(f"   筛选条件: 涨跌幅 {data['data']['selectConfig']['upDownMin']}%-{data['data']['selectConfig']['upDownMax']}%")
            print(f"   技术指标: {len(data['data']['indicators'])} 个")
        else:
            print("❌ 配置接口异常")
    except Exception as e:
        print(f"❌ 配置接口错误: {e}")
    
    # 测试当前股票接口
    try:
        response = requests.get(f"{base_url}/stocks/current")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✅ 当前股票接口正常，找到 {len(data['data'])} 只股票")
            else:
                print(f"⚠️  当前股票接口: {data['message']}")
        else:
            print("❌ 当前股票接口异常")
    except Exception as e:
        print(f"❌ 当前股票接口错误: {e}")
    
    # 测试历史查询接口
    try:
        response = requests.post(f"{base_url}/stocks/history", 
                               json={"date": "2025-08-25"})
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✅ 历史查询接口正常，找到 {len(data['data'])} 只股票")
            else:
                print(f"⚠️  历史查询接口: {data['message']}")
        else:
            print("❌ 历史查询接口异常")
    except Exception as e:
        print(f"❌ 历史查询接口错误: {e}")
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    test_api()

