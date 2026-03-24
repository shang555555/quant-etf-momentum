import numpy as np
import pandas as pd
import os
from hurst import compute_Hc  # 需先安装：pip install hurst

#直接用相对路径
data_dir = os.path.join(os.getcwd(), "data")

# 读取 510300.csv
etf_code = "510300"
file_path = os.path.join(data_dir, f"{etf_code}.csv")

# 读取 CSV，把日期列设为索引
data = pd.read_csv(
    file_path,
    parse_dates=True,   # 自动解析日期
    index_col=0         # 把第一列（日期）设为索引
)

# 查看数据前5行，确认加载成功
print(f"成功加载 {etf_code} 数据，共 {len(data)} 行")
print(data.head())

def hurst_test(price_series):
    # 计算赫斯特指数（传入对数收益率或对数价格）
    H, c, data = compute_Hc(price_series, kind='price', simplified=True)
    print(f"赫斯特指数 H = {H:.3f}")
    
    if H < 0.5:
        print("✅ 序列表现为均值回归特性")
    elif np.isclose(H, 0.5, atol=0.02):
        print("⚠️  序列接近随机游走")
    else:
        print("📈 序列表现为趋势性特性")
    return H


price_series = data["收盘"] 
hurst_test(price_series)