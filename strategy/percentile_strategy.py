import backtrader as bt
import numpy as np
from datetime import timedelta, datetime
from utils.excel_writer import ExcelWriter

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

        # 如果实际起始日大于目标起始日，则需要增加交易天数
        while self.datetime.datetime(-self.trade_days+1) > start_date and self.trade_days < len(self.dataclose):
            self.trade_days += 1
        
        # 如果实际起始日小于目标起始日，则需要减去交易天数
        while self.datetime.datetime(-self.trade_days+1) < start_date and self.trade_days > 1:
            self.trade_days -= 1
        
        # 如果起始日大于目标起始日，说明历史数据不足，抛出异常
        if self.datetime.datetime(-len(self.dataclose)+1) > start_date:
            self.lines.percentile[0] = float('nan')  # 设置为 NaN，表示跳过计算
            return

        # 收集指定自然日期范围内的所有交易日数据
        historical_data = [self.dataclose[i] for i in range(-self.trade_days+1, 0)]
        
        # 计算当前值在历史数据中的百分位
        data_array = np.array(historical_data)
        percentile = (np.sum(data_array <= current_value) / len(data_array)) * 100
        self.lines.percentile[0] = percentile

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
        self.percentile = PercentileIndicator(
            dataclose=self.dataclose,
            lookback_days=self.params.lookback_days
        )
        
        # 初始化Excel写入器
        self.excel_writer = ExcelWriter('backtest_results.xlsx')
        
        # 创建每日数据sheet
        self.excel_writer.create_sheet('Daily Data', [
            'Date', 'Close Price', 'Percentile', 'Position Size', 'Total Value'
        ])
        
        # 创建交易记录sheet
        self.excel_writer.create_sheet('Trade Records', [
            'Date', 'Action', 'Price', 'Size', 'Value', 'Commission', 'Total Value'
        ])

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'{self.datetime.datetime(0).date()} BUY EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
                # 记录买入交易
                self.excel_writer.write_row('Trade Records', {
                    'Date': self.datetime.datetime(0).date(),
                    'Action': 'BUY EXECUTED',
                    'Price': order.executed.price,
                    'Size': order.executed.size,
                    'Value': order.executed.value,
                    'Commission': order.executed.comm,
                    'Total Value': self.broker.getvalue()
                })
            elif order.issell():
                self.log(f'{self.datetime.datetime(0).date()} SELL EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
                # 记录卖出交易
                self.excel_writer.write_row('Trade Records', {
                    'Date': self.datetime.datetime(0).date(),
                    'Action': 'SELL EXECUTED',
                    'Price': order.executed.price,
                    'Size': order.executed.size,
                    'Value': order.executed.value,
                    'Commission': order.executed.comm,
                    'Total Value': self.broker.getvalue()
                })
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
            # 记录取消/保证金不足/拒绝的交易
            self.excel_writer.write_row('Trade Records', {
                'Date': self.datetime.datetime(0).date(),
                'Action': f'ORDER {order.status}',
                'Price': order.created.price,
                'Size': order.created.size,
                'Value': 0,
                'Commission': 0,
                'Total Value': self.broker.getvalue()
            })

        self.order = None

    def next(self):
        # 记录每日数据
        self.excel_writer.write_row('Daily Data', {
            'Date': self.datetime.datetime(0).date(),
            'Close Price': self.dataclose[0],
            'Percentile': self.percentile[0],
            'Position Size': self.position.size if self.position else 0,
            'Total Value': self.broker.getvalue()
        })

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
                # 记录买入创建
                self.excel_writer.write_row('Trade Records', {
                    'Date': self.datetime.datetime(0).date(),
                    'Action': 'BUY CREATE',
                    'Price': price,
                    'Size': shares,
                    'Value': price * shares,
                    'Commission': 0,
                    'Total Value': self.broker.getvalue()
                })
                self.order = self.buy(size=shares)
        else:
            # 计算当前持仓的盈利比例
            current_price = self.dataclose[0]
            cost_price = self.position.price
            profit_ratio = (current_price - cost_price) / cost_price

            # 如果盈利超过阈值，卖出所有持仓
            if profit_ratio > self.params.profit_threshold:
                self.log(f'{self.datetime.datetime(0).date()} SELL CREATE, {self.position.size} shares at {current_price:.2f}, Profit: {profit_ratio:.2%}')
                # 记录卖出创建
                self.excel_writer.write_row('Trade Records', {
                    'Date': self.datetime.datetime(0).date(),
                    'Action': 'SELL CREATE',
                    'Price': current_price,
                    'Size': self.position.size,
                    'Value': current_price * self.position.size,
                    'Commission': 0,
                    'Total Value': self.broker.getvalue()
                })
                self.order = self.sell(size=self.position.size) 
            # 如果亏损超过阈值，卖出所有持仓
            elif profit_ratio < -self.params.max_loss_threshold:
                self.log(f'{self.datetime.datetime(0).date()} SELL CREATE, {self.position.size} shares at {current_price:.2f}, Profit: {profit_ratio:.2%}')
                # 记录卖出创建
                self.excel_writer.write_row('Trade Records', {
                    'Date': self.datetime.datetime(0).date(),
                    'Action': 'SELL CREATE',
                    'Price': current_price,
                    'Size': self.position.size,
                    'Value': current_price * self.position.size,
                    'Commission': 0,
                    'Total Value': self.broker.getvalue()
                })
                self.order = self.sell(size=self.position.size)

    def stop(self):
        """
        策略结束时保存Excel文件
        """
        self.excel_writer.close() 