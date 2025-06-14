import backtrader as bt
from indicator.percentile_indicator import PercentileIndicator

class PercentileStrategy(bt.Strategy):
    params = (
        ('lookback_days', 365),  # 自然日天数，默认一年
        ('percentile_threshold', 10),  # 百分位阈值
        ('min_amount', 10000),  # 最小买入金额
        ('profit_threshold', 0.10),  # 盈利阈值，10%
        ('max_loss_threshold', 0.10),  # 最大亏损阈值，10%
    )

    def log(self, txt, dt=None):
        # 简化日志记录，不使用日期
        # pass
        print(f'{txt}')

    def __init__(self):
        # 引用收盘价
        self.dataclose = self.datas[0].close
        self.datetime = self.datas[0].datetime
        
        # 跟踪订单
        self.order = None
        
        # 计算百分位
        self.percentile = PercentileIndicator()

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'{self.datetime.datetime(0).date()} BUY EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
            elif order.issell():
                self.log(f'{self.datetime.datetime(0).date()} SELL EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def next(self):
        # 如果有挂起的订单，不执行新的订单
        if self.order:
            return

        # 检查是否持仓
        if not self.position:
            # 如果百分位低于阈值，且当前价格 * 股数 > 最小买入金额
            if self.percentile[0] < self.params.percentile_threshold:
                # 计算可以买入的股数（确保金额超过最小买入金额）
                price = self.dataclose[0]
                shares = int(self.params.min_amount / price) + 1
                
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
            # 如果亏损超过阈值，卖出所有持仓
            elif profit_ratio < -self.params.max_loss_threshold:
                self.log(f'{self.datetime.datetime(0).date()} SELL CREATE, {self.position.size} shares at {current_price:.2f}, Profit: {profit_ratio:.2%}')

                self.order = self.sell(size=self.position.size)

    def stop(self):
        pass