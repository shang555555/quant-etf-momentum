#类型转换工具
from typing import cast

import pandas as pd
import matplotlib.pyplot as plt

from strategies.momentum_rotation import run_strategy


def _run_strategy_metrics(data: pd.DataFrame, n: int) -> tuple[float, float, float]:
    #策略封装调用，统一返回指标
    #cast强制类型转换
    return cast(tuple[float, float, float], run_strategy(data, n))

#滚动向前测试
def rolling_test(
    data: pd.DataFrame,
    n_list: list[int],#待测试的参数列表
    train_years: int = 5,#训练
    test_years: int = 1,#测试
) -> pd.DataFrame:
    #1.预处理：确保索引是时间格式(Pylance是代码提示工具，避免提示报错)
    index = pd.DatetimeIndex(data.index)
    results: list[dict[str, float | int | str]] = []  #存储每轮测试结果

    #2.确定年份范围
    start_year = int(index.year.min())
    end_year = int(index.year.max())

    #3.滚动遍历窗口
    for train_start in range(start_year, end_year - train_years - test_years + 2):
        #每轮年份节点
        train_end = train_start + train_years - 1
        test_start = train_end + 1
        test_end = test_start + test_years - 1

        #截取对应年份数据
        train_data = data.loc[f"{train_start}-01-01" : f"{train_end}-12-31"]
        test_data = data.loc[f"{test_start}-01-01" : f"{test_end}-12-31"]

        #数据量太少，过滤
        if len(train_data) < 200 or len(test_data) < 50:
            continue

        print(f"\n训练期 {train_start}-{train_end} | 测试期 {test_start}-{test_end}")

        #5.找最优参数n
        best_calmar = float("-inf")#初始化负无穷
        best_n: int | None = None#  "|"新写法  后续使用需判断是否为None
        for n in n_list:#遍历
            #训练数据跑策略结果
            annual_return, max_drawdown, calmar = _run_strategy_metrics(train_data, n)
            #选最佳calmar
            if calmar > best_calmar:
                best_calmar = calmar
                best_n = n

        if best_n is None:
            continue

        #6.测试最佳n跑数据
        test_annual, test_drawdown, test_calmar = _run_strategy_metrics(test_data, best_n)

        print(f"最优N={best_n} | 测试年化={test_annual:.2%} | Calmar={test_calmar:.2f}")

        # 计算同期基准年化收益（默认使用510300，如不存在则用首列）
        benchmark_col = "510300" if "510300" in test_data.columns else test_data.columns[0]
        benchmark_prices = test_data[benchmark_col].dropna()
        if len(benchmark_prices) < 2:
            benchmark_annual = 0.0
        else:
            benchmark_returns = benchmark_prices.pct_change().fillna(0.0)
            benchmark_nav = (1 + benchmark_returns).cumprod()
            benchmark_annual = benchmark_nav.iloc[-1] ** (252 / len(benchmark_nav)) - 1

        #7.保存添加结果
        results.append(
            {
                "训练期": f"{train_start}-{train_end}",
                "测试期": f"{test_start}-{test_end}",
                "最优N": best_n,
                "测试年化": test_annual,
                "测试最大回撤": test_drawdown,
                "测试Calmar": test_calmar,
                "基准年化": benchmark_annual,
            }
        )

    #8.返回测试结果的DataFrame
    df = pd.DataFrame(results)
    avg_return = df["测试年化"].mean()
    avg_drawdown = df["测试最大回撤"].mean()
    avg_calmar = df["测试Calmar"].mean()
    overall_calmar = avg_return / abs(avg_drawdown) if avg_drawdown != 0 else float("inf")
    win_rate = (df["测试年化"] > 0).mean()

    print("\n====Rolling Test Summary====")
    print(f"平均年化: {avg_return:.2%}")
    print(f"平均回撤: {avg_drawdown:.2%}")
    print(f"Calmar（整体）: {overall_calmar:.2f}")
    print(f"平均Calmar（仅参考）: {avg_calmar:.2f}")
    print(f"胜率: {win_rate:.2%}")

return df


def plot_rolling_results(df: pd.DataFrame) -> None:
    import matplotlib.ticker as mtick

    strategy = df["????"]
    benchmark = df["????"]
    avg_return = strategy.mean()

    x = range(len(df))
    plt.figure(figsize=(12, 6))
    plt.bar(x, strategy, width=0.4, label="Strategy", color="#1f77b4")
    plt.bar([i + 0.4 for i in x], benchmark, width=0.4, label="CSI300", color="#ff7f0e", alpha=0.7)

    plt.xticks([i + 0.2 for i in x], df["???"], rotation=45)
    plt.axhline(0, linestyle="--", color="gray", linewidth=1)
    plt.axhline(avg_return, linestyle="--", color="#1f77b4", linewidth=1.2, label="Strategy Mean")
    plt.title("Walk-forward Out-of-Sample Performance")
    plt.xlabel("Test Period")
    plt.ylabel("Annual Return")
    plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    plt.ylim(-0.3, 0.2)
    plt.grid(axis="y", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("output/rolling_test.png")

#参数稳定性测试
def parameter_stability_test(data: pd.DataFrame, n_list: list[int]) -> pd.DataFrame:
    results = []

    #遍历
    for n in n_list:
        annual_return, max_drawdown, calmar = _run_strategy_metrics(data, n)
        results.append(
            {
                "N": n,
                "annual_return": annual_return,
                "max_drawdown": max_drawdown,
                "calmar": calmar,
            }
        )

    return pd.DataFrame(results)


