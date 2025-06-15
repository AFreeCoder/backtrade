from typing import Dict, Any

# 策略参数配置
STRATEGY_PARAMS = {
    'PercentileStrategy': {
        'lookback_days': 365,
        'percentile_threshold': 0.10,
        'profit_threshold': 0.15,
        'max_loss_threshold': 0.08,
        'cooling_days': 3
    }
    # 可以添加更多策略的参数配置
} 

# 最佳参数一
# 'PercentileStrategy': {
#         'lookback_days': 365,
#         'percentile_threshold': 0.005,
#         'profit_threshold': 0.30,
#         'max_loss_threshold': 0.10,
#         'cooling_days': 3
#     }
# 策略: PercentileStrategy
# 回测区间: 2022-03-22 至 2025-06-07
# 初始资金: 30,000.00
# 最终资金: 82,528.15
# 总收益率: 175.09%
# 年化收益率: 37.01%

# 最佳参数二
# 'PercentileStrategy': {
#         'lookback_days': 365,
#         'percentile_threshold': 0.10,
#         'profit_threshold': 0.15,
#         'max_loss_threshold': 0.08,
#         'cooling_days': 3
#     }
# 策略: PercentileStrategy
# 回测区间: 2022-03-22 至 2025-06-07
# 初始资金: 30,000.00
# 最终资金: 76,389.38
# 总收益率: 154.63%
# 年化收益率: 33.75%