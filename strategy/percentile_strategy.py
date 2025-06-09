import backtrader as bt
import numpy as np
from datetime import timedelta

class PercentileIndicator(bt.Indicator):
    """
    自定义百分位指标
    计算当前价格在指定自然日区间内交易日的百分位排名
    """
    lines = ('percentile',)
    
    def __init__(self, dataclose, lookback_days):
        self.dataclose = dataclose
        self.datetime = self.datas[0].datetime
        self.lookback_days = lookback_days
        self.trade_days = 0
    
    def next(self):
        current_value = self.dataclose[0]
        
        # 获取当前日期（backtrader中的日期访问方式）和目标起始日期
        current_date = self.datetime.datetime(0)
        start_date = current_date - timedelta(days=self.lookback_days)

        while self.datetime.datetime(-self.trade_days+1) > start_date and self.trade_days < len(self.dataclose):
            self.trade_days += 1
        
        # 如果起始日大于目标起始日，说明历史数据不足，抛出异常
        if self.datetime.datetime(-self.trade_days+1) > start_date:
            self.lines.percentile[0] = float('nan')  # 设置为 NaN，表示跳过计算
            # print(self.trade_days, start_date, self.datetime.datetime(0), len(self.datetime), self.datetime.datetime(-self.trade_days+1))
            # print(f"历史数据不足: 需要从{start_date}开始的历史数据，但只能追溯到{self.datetime.datetime(-self.trade_days)}的数据")
            return
        
        # 如果实际起始日小于目标起始日，说明历史数据足够，但需要减去1天
        if self.datetime.datetime(-self.trade_days+1) < start_date:
            self.trade_days -= 1

        # 收集指定自然日期范围内的所有交易日数据
        historical_data = [self.dataclose[i] for i in range(-self.trade_days+1, 0)]

        
        # 计算当前值在历史数据中的百分位
        data_array = np.array(historical_data)
        percentile = (np.sum(data_array <= current_value) / len(data_array)) * 100
        
        self.lines.percentile[0] = percentile

        # print(f'目标起始日期: {start_date.date()}, 实际起始日期: {self.datetime.datetime(-self.trade_days+1).date()}, 当前日期: {current_date.date()}, 历史数据天数: {self.trade_days}, 百分位: {percentile}')

class PercentileStrategy(bt.Strategy):
    params = (
        ('lookback_days', 365),  # 自然日天数，默认一年
        ('percentile_threshold', 10),  # 百分位阈值
        ('min_amount', 10000),  # 最小买入金额
        ('profit_threshold', 0.10),  # 盈利阈值，10%
    )

    def log(self, txt, dt=None):
        # 简化日志记录，不使用日期
        print(f'{txt}')

    def __init__(self):
        # 引用收盘价
        self.dataclose = self.datas[0].close
        self.datetime = self.datas[0].datetime
        
        # 跟踪订单
        self.order = None
        
        # 计算百分位
        self.percentile = PercentileIndicator(
            dataclose=self.dataclose,
            lookback_days=self.params.lookback_days
        )

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Date: {self.datetime.datetime(0).date()}, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, Date: {self.datetime.datetime(0).date()}, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def next(self):
        # 记录当前收盘价和百分位
        self.log(f'{self.datetime.datetime(0).date()} Close: {self.dataclose[0]:.2f}, Percentile: {self.percentile[0]:.2f}, Position: {self.position.size}, Order: {self.order}')

        # 如果有挂起的订单，不执行新的订单
        if self.order:
            return

        # 检查是否持仓
        if not self.position:
            # 如果百分位低于阈值，且当前价格 * 股数 > 最小买入金额
            if self.percentile[0] < self.params.percentile_threshold:
                print(f'{self.datetime.datetime(0).date()}, {self.percentile[0]}, {self.params.percentile_threshold}, {self.percentile[0] < self.params.percentile_threshold}')
                # 计算可以买入的股数（确保金额超过最小买入金额）
                price = self.dataclose[0]
                shares = int(self.params.min_amount / price) + 1 # 直接计算股数，不限制100的整数倍
                
                self.log(f'{self.datetime.datetime(0).date()} BUY CREATE, {shares} shares at {price:.2f}')
                self.order = self.buy(size=shares)
        else:
            # 计算当前持仓的盈利比例
            current_price = self.dataclose[0]
            cost_price = self.position.price
            profit_ratio = (current_price - cost_price) / cost_price

            # 如果盈利超过阈值，卖出所有持仓
            if profit_ratio > self.params.profit_threshold:
                self.log(f'{self.datetime.datetime(0).date()} SELL CREATE, {self.position.size} shares at {current_price:.2f}, Profit: {profit_ratio:.2%}')
                self.order = self.sell(size=self.position.size) 
            elif profit_ratio < -self.params.profit_threshold:
                self.log(f'{self.datetime.datetime(0).date()} SELL CREATE, {self.position.size} shares at {current_price:.2f}, Profit: {profit_ratio:.2%}')
                self.order = self.sell(size=self.position.size) 