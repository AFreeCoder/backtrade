import pandas as pd
from typing import Dict, Any
from .base_loader import BaseDataLoader

class APIDataLoader(BaseDataLoader):
    def __init__(self, data_dir: str = "data", api_config: Dict[str, Any] = None):
        """
        初始化API数据加载器
        :param data_dir: 数据目录
        :param api_config: API配置
        """
        super().__init__(data_dir)
        self.api_config = api_config

    def load_api_data(self, data: Dict[str, Any]) -> pd.DataFrame:
        """
        从API返回的数据加载数据
        :param data: API返回的数据
        :return: DataFrame
        """
        # 将API数据转换为DataFrame
        df = pd.DataFrame(data['data'])
        # 设置日期为索引
        df['day'] = pd.to_datetime(df['day'])
        df.set_index('day', inplace=True)
        
        if not self.validate_data(df):
            raise ValueError("Invalid data format")
        return df 