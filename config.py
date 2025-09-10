# -*- coding: utf-8 -*-
"""
部署配置文件
根据环境变量自动切换本地和线上配置
"""

import os

# 环境配置
ENV = os.getenv('DEPLOY_ENV', 'local')  # 默认为本地环境

# 配置字典
CONFIG = {
    'local': {
        'HOST': '127.0.0.1',
        'PORT': 5000,
        'BASE_URL': 'http://localhost:5000',
        'API_BASE_URL': 'http://localhost:5000/api',
        'DEBUG': True,
        'ENV_NAME': '本地开发环境'
    },
    'production': {
        'HOST': '0.0.0.0',
        'PORT': 5000,
        'BASE_URL': 'http://8.152.212.206:5000',
        'API_BASE_URL': 'http://8.152.212.206:5000/api',
        'DEBUG': False,
        'ENV_NAME': '生产环境'
    }
}

def get_config():
    """获取当前环境配置"""
    return CONFIG.get(ENV, CONFIG['local'])

def is_production():
    """判断是否为生产环境"""
    return ENV == 'production'

def is_local():
    """判断是否为本地环境"""
    return ENV == 'local'

# 当前配置
CURRENT_CONFIG = get_config()

# 快捷访问
HOST = CURRENT_CONFIG['HOST']
PORT = CURRENT_CONFIG['PORT']
BASE_URL = CURRENT_CONFIG['BASE_URL']
API_BASE_URL = CURRENT_CONFIG['API_BASE_URL']
DEBUG = CURRENT_CONFIG['DEBUG']
ENV_NAME = CURRENT_CONFIG['ENV_NAME']

if __name__ == '__main__':
    print(f"当前环境: {ENV_NAME}")
    print(f"主机地址: {HOST}:{PORT}")
    print(f"访问地址: {BASE_URL}")
    print(f"API地址: {API_BASE_URL}")
    print(f"调试模式: {DEBUG}")
