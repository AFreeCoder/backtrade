from typing import Dict, Any

# 策略参数配置
STRATEGY_PARAMS = {
    'PercentileStrategy': {
        'lookback_days': 365,
        'percentile_threshold': 10,
        'min_amount': 10000,
        'profit_threshold': 0.10,
        'max_loss_threshold': 0.10,
        'cooling_days': 3
    }
    # 可以添加更多策略的参数配置
} 