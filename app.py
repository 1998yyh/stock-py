# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import sys
import traceback
import pandas as pd
from datetime import datetime, timedelta

# 导入股票筛选模块
from stock import get_active_stocks, SELECT_CONFIG, INDICATOR_CONFIG, get_data_date_info, start_daily_update_task, get_last_trading_day

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
                'code': str(row['代码']).zfill(6),  # 确保股票代码为6位数字，前导零补全
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
            last_trading_day_cache = os.path.join("data", f"{get_last_trading_day()}_current_stocks.txt")
            
            if date_info['is_today_data'] and os.path.exists(today_cache):
                data_source = "今日缓存"
            elif not date_info['is_today_data'] and os.path.exists(last_trading_day_cache):
                data_source = "上个交易日缓存"
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

@app.route('/api/cache/view', methods=['GET'])
def view_cache_data():
    """查看缓存数据"""
    try:
        filename = request.args.get('file')
        if not filename:
            return jsonify({
                'success': False,
                'message': '请指定要查看的缓存文件'
            })
        
        data_dir = "data"
        file_path = os.path.join(data_dir, filename)
        
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'message': f'缓存文件不存在: {filename}'
            })
        
        # 读取缓存数据
        try:
            # 指定代码列为字符串类型，保留前导零
            cached_data = pd.read_csv(file_path, sep="\t", encoding="utf-8", dtype={'代码': str})
            if cached_data.empty:
                return jsonify({
                    'success': True,
                    'message': '缓存文件为空',
                    'data': [],
                    'filename': filename
                })
            
            # 转换为API格式
            result = []
            for _, row in cached_data.iterrows():
                result.append({
                    'code': str(row['代码']).zfill(6),  # 确保股票代码为6位数字，前导零补全
                    'name': row['名称'],
                    'change_percent': float(row['涨跌幅']) if pd.notna(row['涨跌幅']) else 0,
                    'price': float(row['最新价']) if pd.notna(row['最新价']) else 0,
                    'turnover': float(row['换手率']) if pd.notna(row['换手率']) else 0,
                    'volume_ratio': float(row['量比']) if pd.notna(row['量比']) else 0,
                    'market_cap': float(row['流通市值']) if pd.notna(row['流通市值']) else 0
                })
            
            # 获取文件信息
            file_stat = os.stat(file_path)
            file_info = {
                'filename': filename,
                'size': file_stat.st_size,
                'modified_time': datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'record_count': len(result)
            }
            
            return jsonify({
                'success': True,
                'message': f'读取缓存数据成功，共 {len(result)} 条记录',
                'data': result,
                'file_info': file_info
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'读取缓存文件失败: {str(e)}'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查看缓存数据失败: {str(e)}'
        })

@app.route('/api/cache/price-change', methods=['GET'])
def get_cache_price_change():
    """查询缓存数据的距今涨幅"""
    try:
        filename = request.args.get('file')
        if not filename:
            return jsonify({
                'success': False,
                'message': '请指定要查询的缓存文件'
            })
        
        data_dir = "data"
        file_path = os.path.join(data_dir, filename)
        
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'message': f'缓存文件不存在: {filename}'
            })
        
        try:
            # 读取缓存数据，指定代码列为字符串类型
            cached_data = pd.read_csv(file_path, sep="\t", encoding="utf-8", dtype={'代码': str})
            if cached_data.empty:
                return jsonify({
                    'success': True,
                    'message': '缓存文件为空',
                    'data': []
                })
            
            # 获取当前实时数据
            try:
                import akshare as ak
                current_data = ak.stock_zh_a_spot_em()
                if current_data.empty:
                    return jsonify({
                        'success': False,
                        'message': '无法获取当前股票数据'
                    })
                
                # 创建当前股价字典，方便查找 - 确保股票代码格式一致
                current_prices = {}
                for _, row in current_data.iterrows():
                    code = str(row['代码']).zfill(6)  # 确保6位代码格式
                    price = float(row['最新价']) if pd.notna(row['最新价']) else 0
                    current_prices[code] = price
                
                # 计算价格变化
                result = []
                for _, row in cached_data.iterrows():
                    cache_code = str(row['代码']).zfill(6)  # 确保6位代码格式
                    cache_price = float(row['最新价']) if pd.notna(row['最新价']) else 0
                    
                    current_price = current_prices.get(cache_code, 0)
                    
                    # 计算涨幅百分比
                    if cache_price > 0 and current_price > 0:
                        price_change_percent = ((current_price - cache_price) / cache_price) * 100
                    else:
                        price_change_percent = 0
                    
                    result.append({
                        'code': cache_code,
                        'name': row['名称'],
                        'cache_price': cache_price,
                        'current_price': current_price,
                        'price_change_percent': round(price_change_percent, 2),
                        'data_available': current_price > 0
                    })
                
                return jsonify({
                    'success': True,
                    'message': f'价格对比完成，共 {len(result)} 只股票',
                    'data': result,
                    'filename': filename
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'获取实时数据失败: {str(e)}'
                })
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'读取缓存文件失败: {str(e)}'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查询价格变化失败: {str(e)}'
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
