import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime

class ExcelWriter:
    def __init__(self, file_name: str):
        """
        初始化Excel写入器
        :param file_name: Excel文件名
        """
        self.file_name = file_name
        self.writer = pd.ExcelWriter(file_name, engine='openpyxl')
        self.sheets: Dict[str, List[Dict[str, Any]]] = {}
        
    def create_sheet(self, sheet_name: str, columns: List[str]):
        """
        创建新的sheet页
        :param sheet_name: sheet页名称
        :param columns: 列名列表
        """
        if sheet_name in self.sheets:
            raise ValueError(f"Sheet {sheet_name} already exists")
        self.sheets[sheet_name] = []
        
    def write_row(self, sheet_name: str, data: Dict[str, Any]):
        """
        写入一行数据
        :param sheet_name: sheet页名称
        :param data: 数据字典，键为列名，值为数据
        """
        if sheet_name not in self.sheets:
            raise ValueError(f"Sheet {sheet_name} does not exist")
        self.sheets[sheet_name].append(data)
        
    def close(self):
        """
        保存并关闭Excel文件
        """
        for sheet_name, data in self.sheets.items():
            if data:  # 只有当有数据时才创建DataFrame
                df = pd.DataFrame(data)
                df.to_excel(self.writer, sheet_name=sheet_name, index=False)
        self.writer.close() 