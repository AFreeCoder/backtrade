from typing import Dict, Any

# 数据源配置
DATA_SOURCES = {
    'excel': {
        'data_dir': 'data',
        'file_pattern': '*.xlsx'
    },
    'csv': {
        'data_dir': 'data',
        'file_pattern': '*.csv'
    },
    'api': {
        'base_url': 'https://stockdata.market.alicloudapi.com',
        'headers': {
            'Authorization': 'APPCODE ce4ac5ac06e145e69bc699b3450cb769'
        }
    }
} 