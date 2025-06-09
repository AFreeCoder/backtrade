import requests
import pandas as pd

# 定义接口 URL 和请求头
url = 'https://stockdata.market.alicloudapi.com/hk/kline?symbol=09888&type=240&limit=3650'
headers = {
    'Authorization': 'APPCODE ce4ac5ac06e145e69bc699b3450cb769'
}

# 发送 GET 请求
response = requests.get(url, headers=headers)

# 检查请求是否成功
if response.status_code == 200:
    data = response.json()
    
    # 检查返回的代码
    if data['code'] == 1:
        # 提取数据
        kline_data = data['data']
        
        # 将数据转换为 DataFrame
        df = pd.DataFrame(kline_data)
        
        # 保存为 Excel 文件
        df.to_excel('stock_data.xlsx', index=False)
        print("数据已成功保存为 stock_data.xlsx")
    else:
        print("错误信息:", data['message'])
else:
    print("请求失败，状态码:", response.status_code)
