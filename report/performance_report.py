from pathlib import Path

import matplotlib
import pandas as pd


def _is_non_interactive_backend() -> bool:
    backend = matplotlib.get_backend().lower()
    return "agg" in backend or "pdf" in backend or "svg" in backend or "ps" in backend


def performance_report(equity) -> None:
    if equity is None or len(equity) == 0:
        print("绩效报告: 无净值数据")
        return

    equity = pd.Series(equity).dropna()
    if equity.empty:
        print("绩效报告: 无有效净值数据")
        return

    returns = equity.pct_change().dropna()
    total_return = equity.iloc[-1] / equity.iloc[0] - 1 if len(equity) > 1 else 0.0
    years = len(equity) / 252 if len(equity) > 0 else 0.0
    annual = (
        (equity.iloc[-1] / equity.iloc[0]) ** (1 / years) - 1
        if years > 0 and len(equity) > 1
        else 0.0
    )

    rolling_max = equity.cummax()
    drawdown = equity / rolling_max - 1
    max_dd = drawdown.min() if not drawdown.empty else 0.0
    sharpe = (
        returns.mean() / returns.std() * (252 ** 0.5)
        if len(returns) > 1 and returns.std() != 0
        else 0.0
    )

    print("\n=====策略绩效报告=====")
    print(f"总收益: {total_return:.2%}")
    print(f"年化收益: {annual:.2%}")
    print(f"最大回撤: {max_dd:.2%}")
    print(f"夏普比率: {sharpe:.2f}")


def benchmark_equity(data: pd.DataFrame) -> pd.Series:
    if data is None or len(data) == 0:
        return pd.Series(dtype=float)

    prices = pd.DataFrame(data).dropna(how="all")
    if prices.empty:
        return pd.Series(dtype=float)

    benchmark = prices.mean(axis=1).dropna()
    if benchmark.empty:
        return pd.Series(dtype=float)

    return benchmark / benchmark.iloc[0]


def benchmark_equity_single(prices: pd.Series) -> pd.Series:
    if prices is None or len(prices) == 0:
        return pd.Series(dtype=float)

    series = pd.Series(prices).dropna()
    if series.empty:
        return pd.Series(dtype=float)

    return series / series.iloc[0]


def plot_equity(
    equity,
    benchmark=None,
    output_name: str = "equity_curve.png",
    title: str = "Momentum Strategy vs Benchmark",
):
    if equity is None or len(equity) == 0:
        print("净值曲线: 无数据可用")
        return None

    equity = pd.Series(equity).dropna()
    if equity.empty:
        print("净值曲线: 无有效数据可用")
        return None

    import matplotlib.pyplot as plt

    try:
        fig = plt.figure(figsize=(10, 5))
    except Exception:
        plt.switch_backend("Agg")
        fig = plt.figure(figsize=(10, 5))

    benchmark_series = pd.Series(benchmark).dropna() if benchmark is not None else pd.Series(dtype=float)
    if not benchmark_series.empty:
        idx = equity.index.union(benchmark_series.index)
        equity = equity.reindex(idx).ffill()
        benchmark_series = benchmark_series.reindex(idx).ffill()
        combined = pd.concat([equity, benchmark_series], axis=1).dropna(how="any")
        if not combined.empty:
            equity = combined.iloc[:, 0] / combined.iloc[:, 0].iloc[0]
            benchmark_series = combined.iloc[:, 1] / combined.iloc[:, 1].iloc[0]
        else:
            equity = pd.Series(dtype=float)
            benchmark_series = pd.Series(dtype=float)
    else:
        equity = equity / equity.iloc[0]

    plt.plot(equity.index, equity.values, label="Strategy")
    if not benchmark_series.empty:
        plt.plot(benchmark_series.index, benchmark_series.values, label="CSI300")

    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Net Value")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    if _is_non_interactive_backend():
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / output_name
        fig.savefig(output_path, dpi=150)
        print(f"净值曲线已保存: {output_path}")

    return fig


def plot_equity_multi(equity_map, output_name: str = "equity_curve_multi.png", title: str = "Equity Curve Comparison"):
    if equity_map is None or len(equity_map) == 0:
        print("净值曲线: 无数据可用")
        return None

    import matplotlib.pyplot as plt

    try:
        fig = plt.figure(figsize=(10, 5))
    except Exception:
        plt.switch_backend("Agg")
        fig = plt.figure(figsize=(10, 5))

    has_series = False
    for label, equity in equity_map.items():
        series = pd.Series(equity).dropna()
        if series.empty:
            continue
        plt.plot(series.index, series.values, label=str(label))
        has_series = True

    if not has_series:
        print("净值曲线: 无有效数据可用")
        return None

    plt.title("Momentum Strategy vs CSI 300\n(Trend Filter + Weekly Rebalance)")
    plt.xlabel("Date")
    plt.ylabel("Net Value")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    if _is_non_interactive_backend():
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / output_name
        fig.savefig(output_path, dpi=150)
        print(f"净值曲线已保存: {output_path}")

    return fig
