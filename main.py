from datetime import datetime
import pandas as pd
from engine.backtest_engine import BacktestEngine
from strategy.percentile_strategy import PercentileStrategy
from data.file_loader import FileDataLoader
from config.strategy_config import STRATEGY_PARAMS
from config.backtest_config import BACKTEST_PARAMS

def run_backtest(strategy_name: str, data_file: str, start_date: str, end_date: str):
    """
    运行回测
    :param strategy_name: 策略名称 ('ma_cross' 或 'rsi')
    :param data_file: 数据文件路径
    :param start_date: 开始日期 (YYYY-MM-DD)
    :param end_date: 结束日期 (YYYY-MM-DD)
    """
    # 初始化数据加载器
    loader = FileDataLoader()
    
    # 加载数据
    if data_file.endswith('.xlsx'):
        data = loader.load_excel(data_file)
    elif data_file.endswith('.csv'):
        data = loader.load_csv(data_file)
    else:
        raise ValueError("不支持的文件格式，请使用 .xlsx 或 .csv 文件")
    # 转换日期字符串为datetime对象
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    # 初始化回测引擎
    engine = BacktestEngine()
    
    # 设置策略
    if strategy_name == 'PercentileStrategy':
        engine.set_strategy(PercentileStrategy, STRATEGY_PARAMS['PercentileStrategy'])
    else:
        raise ValueError(f"不支持的策略名称: {strategy_name}")
    
    # 设置数据
    engine.set_data(data)
    
    # 设置初始资金
    engine.set_initial_cash(BACKTEST_PARAMS['initial_cash'])
    
    # 运行回测
    results = engine.run(start_date, end_date)
    
    # 打印回测结果
    print("\n=== 回测结果 ===")
    print(f"策略: {results['strategy']}")
    print(f"回测区间: {results['start_date'].strftime('%Y-%m-%d')} 至 {results['end_date'].strftime('%Y-%m-%d')}")
    print(f"初始资金: {results['initial_value']:,.2f}")
    print(f"最终资金: {results['final_value']:,.2f}")
    print(f"总收益率: {results['total_return']*100:.2f}%")
    print(f"年化收益率: {results['annual_return']*100:.2f}%")
    
    # 绘制回测结果图表
    engine.plot(style='candlestick')

if __name__ == '__main__':
    run_backtest(
        strategy_name='PercentileStrategy',
        data_file='baidu-sw.xlsx',
        start_date='2022-03-22',
        end_date='2025-06-07'
    ) 