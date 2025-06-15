import backtrader as bt
import numpy as np
from datetime import timedelta

class PercentileIndicator(bt.Indicator):
    """
    自定义百分位指标
    计算当前价格在指定自然日区间内交易日的百分位排名
    """
    lines = ('percentile',)
    
    def __init__(self, lookback_days):
        self.trade_days = 0
        self.lookback_days = lookback_days
    
    def next(self):
        current_value = self.data.close[0]
        
        # 获取当前日期（backtrader中的日期访问方式）和目标起始日期
        current_date = self.data.datetime.datetime(0)
        start_date = current_date - timedelta(days=self.lookback_days)

        # 如果实际起始日大于目标起始日，则需要增加交易天数
        while self.data.datetime.datetime(-self.trade_days+1) > start_date and self.trade_days < len(self.data.close):
            self.trade_days += 1
        
        # 如果实际起始日小于目标起始日，则需要减去交易天数
        while self.data.datetime.datetime(-self.trade_days+1) < start_date and self.trade_days > 1:
            self.trade_days -= 1
        
        # 如果起始日大于目标起始日，说明历史数据不足，抛出异常
        if self.data.datetime.datetime(-len(self.data.close)+1) > start_date:
            self.lines.percentile[0] = float('nan')  # 设置为 NaN，表示跳过计算
            return

        # 收集指定自然日期范围内的所有交易日数据
        historical_data = [self.data.close[i] for i in range(-self.trade_days+1, 0)]
        
        # 计算当前值在历史数据中的百分位
        data_array = np.array(historical_data)
        percentile = (np.sum(data_array <= current_value) / len(data_array))
        self.lines.percentile[0] = percentile 