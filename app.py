# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import sys
import traceback
import pandas as pd
from datetime import datetime, timedelta

# 导入股票筛选模块
from stock import get_active_stocks, SELECT_CONFIG, INDICATOR_CONFIG, get_data_date_info, start_daily_update_task

app = Flask(__name__)
CORS(app)  # 允许跨域请求

@app.route('/')
def index():
    """前端页面"""
    return render_template('index.html')

@app.route('/api/stocks/current', methods=['GET'])
def get_current_stocks():
    """获取当前符合条件的股票"""
    try:
        # 检查是否强制刷新
        force_refresh = request.args.get('refresh', 'false').lower() == 'true'
        
        # 获取数据日期信息
        date_info = get_data_date_info()
        
        # 获取股票数据
        stocks = get_active_stocks(use_cache=not force_refresh, save_cache=True, force_refresh=force_refresh)
        
        if stocks.empty:
            return jsonify({
                'success': False,
                'message': '无符合条件的股票',
                'data': [],
                'date_info': date_info
            })
        
        # 转换为列表格式
        result = []
        for _, row in stocks.iterrows():
            result.append({
                'code': row['代码'],
                'name': row['名称'],
                'change_percent': float(row['涨跌幅']) if pd.notna(row['涨跌幅']) else 0,
                'price': float(row['最新价']) if pd.notna(row['最新价']) else 0,
                'turnover': float(row['换手率']) if pd.notna(row['换手率']) else 0,
                'volume_ratio': float(row['量比']) if pd.notna(row['量比']) else 0,
                'market_cap': float(row['流通市值']) if pd.notna(row['流通市值']) else 0
            })
        
        # 判断数据来源
        if force_refresh:
            data_source = "强制刷新"
        else:
            # 检查是否从缓存读取
            today_cache = os.path.join("data", f"{datetime.now().strftime('%Y-%m-%d')}_current_stocks.txt")
            yesterday_cache = os.path.join("data", f"{(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')}_current_stocks.txt")
            
            if date_info['is_today_data'] and os.path.exists(today_cache):
                data_source = "今日缓存"
            elif not date_info['is_today_data'] and os.path.exists(yesterday_cache):
                data_source = "昨日缓存"
            else:
                data_source = "实时获取"
        
        return jsonify({
            'success': True,
            'message': f'找到 {len(result)} 只符合条件的股票 ({date_info["time_status"]})',
            'data': result,
            'data_source': data_source,
            'date_info': date_info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取股票数据失败: {str(e)}',
            'data': [],
            'date_info': get_data_date_info()
        })



@app.route('/api/cache/status', methods=['GET'])
def get_cache_status():
    """获取缓存状态"""
    try:
        data_dir = "data"
        if not os.path.exists(data_dir):
            return jsonify({
                'success': True,
                'data': {
                    'cache_files': [],
                    'total_files': 0,
                    'cache_size': 0
                }
            })
        
        cache_files = []
        total_size = 0
        
        for filename in os.listdir(data_dir):
            if filename.endswith('.txt'):
                file_path = os.path.join(data_dir, filename)
                file_stat = os.stat(file_path)
                file_size = file_stat.st_size
                modified_time = datetime.fromtimestamp(file_stat.st_mtime)
                
                cache_files.append({
                    'filename': filename,
                    'size': file_size,
                    'modified_time': modified_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'type': 'current' if '_current_stocks.txt' in filename else 'strategy'
                })
                total_size += file_size
        
        # 按修改时间排序
        cache_files.sort(key=lambda x: x['modified_time'], reverse=True)
        
        return jsonify({
            'success': True,
            'data': {
                'cache_files': cache_files,
                'total_files': len(cache_files),
                'cache_size': total_size
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取缓存状态失败: {str(e)}',
            'data': {}
        })

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """清理缓存"""
    try:
        data = request.get_json()
        clear_type = data.get('type', 'all')  # all, current, strategy
        date_str = data.get('date')  # 指定日期
        
        data_dir = "data"
        if not os.path.exists(data_dir):
            return jsonify({
                'success': True,
                'message': '缓存目录不存在，无需清理'
            })
        
        deleted_files = []
        for filename in os.listdir(data_dir):
            if not filename.endswith('.txt'):
                continue
                
            should_delete = False
            if clear_type == 'all':
                should_delete = True
            elif clear_type == 'current' and '_current_stocks.txt' in filename:
                should_delete = True
            elif clear_type == 'strategy' and '_strategy.txt' in filename:
                should_delete = True
            
            if date_str and should_delete:
                # 如果指定了日期，只删除该日期的文件
                if date_str in filename:
                    should_delete = True
                else:
                    should_delete = False
            
            if should_delete:
                file_path = os.path.join(data_dir, filename)
                try:
                    os.remove(file_path)
                    deleted_files.append(filename)
                except Exception as e:
                    print(f"删除文件失败 {filename}: {e}")
        
        return jsonify({
            'success': True,
            'message': f'成功删除 {len(deleted_files)} 个缓存文件',
            'deleted_files': deleted_files
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'清理缓存失败: {str(e)}'
        })

@app.route('/api/config', methods=['GET'])
def get_config():
    """获取当前配置"""
    try:
        # 转换配置格式
        select_config = {
            'upDownMin': SELECT_CONFIG['UpDownMin'],
            'upDownMax': SELECT_CONFIG['UpDownMax'],
            'turnoverMin': SELECT_CONFIG['TurnoverMin'],
            'turnoverMax': SELECT_CONFIG['TurnoverMax'],
            'valMin': SELECT_CONFIG['ValMin'] / 100000000,  # 转换为亿
            'valMax': SELECT_CONFIG['ValMax'] / 100000000,  # 转换为亿
            'ratio': SELECT_CONFIG['Ratio']
        }
        
        indicators = {}
        for name, config in INDICATOR_CONFIG.items():
            indicators[name] = {
                'enable': config['enable'],
                'name': config['name']
            }
        
        return jsonify({
            'success': True,
            'data': {
                'selectConfig': select_config,
                'indicators': indicators
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取配置失败: {str(e)}',
            'data': {}
        })

if __name__ == '__main__':
    # 创建templates目录
    os.makedirs('templates', exist_ok=True)
    
    # 启动后台定时更新任务
    start_daily_update_task()
    
    print("启动股票筛选服务...")
    print("访问地址: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
