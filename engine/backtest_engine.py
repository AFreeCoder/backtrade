import backtrader as bt
from datetime import datetime
import pandas as pd
from typing import Dict, Any, Optional
from config.backtest_config import BACKTEST_PARAMS

class BacktestEngine:
    def __init__(self):
        self.cerebro = bt.Cerebro()
        self.strategy = None
        self.data = None
        self.start_date = None
        self.end_date = None
        self.initial_cash = BACKTEST_PARAMS['initial_cash']
        
        # 设置手续费和滑点
        self.cerebro.broker.setcommission(commission=BACKTEST_PARAMS['commission'])
        self.cerebro.broker.set_slippage_perc(BACKTEST_PARAMS['slippage'])

        # 添加 observer
        # self.cerebro.addobserver(bt.observers.Broker)

        # 添加 writer
        self.cerebro.addwriter(bt.WriterFile, csv=True, out="backtest_results.csv", csv_counter=True)

    def set_strategy(self, strategy_class: bt.Strategy, strategy_params: Optional[Dict[str, Any]] = None):
        """
        设置回测策略
        :param strategy_class: 策略类
        :param strategy_params: 策略参数
        """
        if strategy_params:
            self.cerebro.addstrategy(strategy_class, **strategy_params)
        else:
            self.cerebro.addstrategy(strategy_class)
        self.strategy = strategy_class

    def set_data(self, data: pd.DataFrame):
        """
        设置回测数据
        :param data: 数据DataFrame
        """
        # 使用传入的data参数而不是重新读取文件
        self.data = bt.feeds.PandasData(
            dataname=data
        )

        self.cerebro.adddata(self.data)

    def set_initial_cash(self, cash: float):
        """
        设置初始资金
        :param cash: 初始资金金额
        """
        self.initial_cash = cash
        self.cerebro.broker.setcash(cash)

    def run(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        运行回测
        :return: 回测结果
        """
        if not self.strategy or self.data is None:
            raise ValueError("Strategy and data must be set before running backtest")

        # 运行回测
        initial_value = self.cerebro.broker.getvalue()
        results = self.cerebro.run(fromdate=start_date, todate=end_date)
        final_value = self.cerebro.broker.getvalue()

        # 计算回测结果
        total_return = (final_value - initial_value) / initial_value
        annual_return = total_return * (252 / (end_date - start_date).days)

        return {
            'initial_value': initial_value,
            'final_value': final_value,
            'total_return': total_return,
            'annual_return': annual_return,
            'strategy': self.strategy.__name__,
            'start_date': start_date,
            'end_date': end_date
        }

    def plot(self, **kwargs):
        """
        绘制回测结果图表
        """
        self.cerebro.plot(**kwargs) 
        # pass