import backtrader as bt
import pandas as pd
from datetime import datetime

# 创建一个策略
class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' 记录功能'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # 引用到数据的close Line
        self.dataclose = self.datas[0].close

        # 跟踪订单
        self.order = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # 订单提交和成交当前不做处理
            return

        # 检查订单是否成交
        # 注意，如果现金不够的话，订单会被拒接
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # 记录没有挂起的订单
        self.order = None

    def next(self):
        #记录close的价格
        self.log('Close, %.2f' % self.dataclose[0])

        # 检查是否有挂起的订单，如果有的话，不能再发起一个订单
        if self.order:
            return

        # 检查是否在市场（有持仓）
        if not self.position:

            # 不在，那么连续3天价格下跌就买点
            if self.dataclose[0] < self.dataclose[-1]:
                    # 当前价格比上一次低

                    if self.dataclose[-1] < self.dataclose[-2]:
                        # 上一次的价格比上上次低

                        # 买入!!! 
                        self.log('BUY CREATE, %.2f' % self.dataclose[0])

                        # Keep track of the created order to avoid a 2nd order
                        self.order = self.buy()

        else:

            # 已经在市场，5天后就卖掉。
            if len(self) >= (self.bar_executed + 5):#这里注意，Len(self)返回的是当前执行的bar数量，每次next会加1.而Self.bar_executed记录的最后一次交易执行时的bar位置。
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()

if __name__ == '__main__':
    cerebro = bt.Cerebro()

    cerebro.addstrategy(TestStrategy)

    start_date = datetime(2025, 3, 23)  # 回测开始时间
    end_date = datetime(2025, 6, 7)  # 回测结束时间

    stock_hfq_df = pd.read_excel("./data/baidu-sw.xlsx",index_col='day',parse_dates=True)
    data = bt.feeds.PandasData(dataname=stock_hfq_df, fromdate=start_date, todate=end_date,datetime=None)  # 加载数据
    cerebro.adddata(data)

    cerebro.broker.setcash(10000000)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())