import pandas as pd
from datetime import datetime
from typing import Optional, Dict, Any
import os

class BaseDataLoader:
    def __init__(self, data_dir: str = "data"):
        """
        初始化数据加载器
        :param data_dir: 数据目录
        """
        self.data_dir = data_dir

    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        验证数据格式是否正确
        :param df: DataFrame
        :return: 是否有效
        """
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        return all(col in df.columns for col in required_columns) 