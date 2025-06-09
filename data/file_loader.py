import pandas as pd
from typing import Optional
import os
from .base_loader import BaseDataLoader

class FileDataLoader(BaseDataLoader):
    def load_excel(self, file_name: str, index_col: str = 'day', parse_dates: bool = True) -> pd.DataFrame:
        """
        从Excel文件加载数据
        :param file_name: 文件名
        :param index_col: 索引列名
        :param parse_dates: 是否解析日期
        :return: DataFrame
        """
        file_path = os.path.join(self.data_dir, file_name)
        df = pd.read_excel(file_path, index_col=index_col, parse_dates=parse_dates)
        if not self.validate_data(df):
            raise ValueError("Invalid data format")
        return df

    def load_csv(self, file_name: str, index_col: str = 'day', parse_dates: bool = True) -> pd.DataFrame:
        """
        从CSV文件加载数据
        :param file_name: 文件名
        :param index_col: 索引列名
        :param parse_dates: 是否解析日期
        :return: DataFrame
        """
        file_path = os.path.join(self.data_dir, file_name)
        df = pd.read_csv(file_path, index_col=index_col, parse_dates=parse_dates)
        if not self.validate_data(df):
            raise ValueError("Invalid data format")
        return df 