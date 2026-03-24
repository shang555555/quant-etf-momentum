import pandas as pd
#导入os库，处理文件文件夹路径
import os


#直接用相对路径
data_dir = os.path.join(os.getcwd(), "data")

# 读取 510500.csv
etf_code = "510500"
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

from statsmodels.tsa.stattools import adfuller

def adf_test(series):
    series=series.dropna()
    result = adfuller(series, maxlag=0)
   #_= result[3]
    print(f'ADF统计量: {result[0]}')
    print(f'p值: {result[1]}')
    print(f'滞后阶数: {result[2]}')
    print(f'临界值: {result[3]}')
    if result[1] < 0.05:
        print("✅ 序列平稳（拒绝单位根假设）")
    else:
        print("❌ 序列非平稳（无法拒绝单位根假设）")


price_series = data["收盘"]  # 或者 "收盘价"、"price" 等，看你 CSV 里的列名
adf_test(price_series)