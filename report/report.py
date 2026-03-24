from __future__ import annotations

from pathlib import Path
import sys

import matplotlib

from analysis import parameter_heatmap, parameter_stability_test, rolling_test
from analysis.plots import plot_parameter_stability
from backtest import backtest_portfolio
from data_loader import get_data
from strategies.mean_reversion import run_mean_reversion
from strategies.momentum_rotation import run_strategy
from .performance_report import benchmark_equity, performance_report, plot_equity


def configure_matplotlib_backend() -> None:
    tcl_dir = Path(sys.base_prefix) / "tcl"
    if not any(tcl_dir.glob("tcl*")):
        matplotlib.use("Agg")


def load_data():
    data = get_data()
    print("data shape:", data.shape)
    print(data.head())
    return data


def run_walk_forward(
    data,
    strategy_func,
    param_grid,
):
    print("\n===== walk-forward test =====")

    rolling_df = rolling_test(
        data,
        strategy_func=strategy_func,
        param_grid=param_grid,
    )
    print(rolling_df)

    if rolling_df.empty:
        print("walk-forward results empty")
    else:
        avg_return = rolling_df["test_annual"].mean()
        avg_drawdown = rolling_df["test_max_drawdown"].mean()
        avg_calmar = rolling_df["test_calmar"].mean()
        overall_calmar = avg_return / abs(avg_drawdown) if avg_drawdown != 0 else float("inf")
        print("\n平均年化:", f"{avg_return:.2%}")
        print("平均回撤:", f"{avg_drawdown:.2%}")
        print("Calmar（整体）:", f"{overall_calmar:.2f}")
        print("平均Calmar（仅参考）:", f"{avg_calmar:.2f}")

    return rolling_df


def run_backtest(data, n: int):
    equity = backtest_portfolio(data, N=n)
    benchmark = benchmark_equity(data)
    return equity, benchmark


def run_reports(equity, benchmark) -> None:
    performance_report(equity)
    plot_equity(equity, benchmark)


def run_parameter_stability(
    data,
    n_list: list[int] | None = None,
    strategy_fn=None,
    param_list=None,
):
    print("\n===== parameter stability test =====")
    param_df = parameter_stability_test(
        data,
        n_list=n_list,
        strategy_fn=strategy_fn,
        param_list=param_list,
    )
    print(param_df)
    plot_parameter_stability(param_df)
    return param_df


def run_parameter_heatmap(
    data,
    n_list: list[int],
    slope_list: list[float],
    strategy: str = "momentum_rotation",
    price_col: str | None = None,
):
    print("\n===== parameter heatmap =====")
    return parameter_heatmap(
        data,
        n_list,
        slope_list,
        strategy=strategy,
        price_col=price_col,
    )


def run() -> None:
    configure_matplotlib_backend()

    data = load_data()

    STRATEGY = "momentum_rotation"  # or "mean_reversion"
    MEAN_REVERSION_ETF = "510300"
    MEAN_REVERSION_PARAM_GRID = {
        "window": [10, 20, 30],
        "std": [1.5, 2.0, 2.5],
    }
    MEAN_REVERSION_PARAM_LIST = [
        {"window": 10, "std_n": 1.5},
        {"window": 20, "std_n": 2.0},
        {"window": 30, "std_n": 2.5},
    ]

    if STRATEGY == "mean_reversion":
        strategy_data = data[MEAN_REVERSION_ETF]
        strategy_func = run_mean_reversion
        param_grid = MEAN_REVERSION_PARAM_GRID
        n_list = None
        param_list = MEAN_REVERSION_PARAM_LIST
        heatmap_strategy = "mean_reversion"
        heatmap_price_col = MEAN_REVERSION_ETF
    else:
        strategy_data = data
        def momentum_strategy(data, window, std_n):
            return run_strategy(data, N=window)

        strategy_func = momentum_strategy
        param_grid = {"window": [5, 10, 15, 20, 30, 40, 60], "std": [0]}
        n_list = [5, 10, 15, 20, 30, 40, 60]
        param_list = None
        heatmap_strategy = "momentum_rotation"
        heatmap_price_col = None

    run_walk_forward(
        strategy_data,
        strategy_func=strategy_func,
        param_grid=param_grid,
    )

    if STRATEGY == "momentum_rotation":
        equity, benchmark = run_backtest(strategy_data, n=15)
        run_reports(equity, benchmark)

    run_parameter_stability(
        strategy_data,
        n_list=n_list,
        strategy_fn=strategy_func,
        param_list=param_list,
    )

    heatmap_n_list = [5, 10, 15, 20, 30]
    slope_list = [0.005, 0.01, 0.02, 0.03]
    run_parameter_heatmap(
        data,
        heatmap_n_list,
        slope_list,
        strategy=heatmap_strategy,
        price_col=heatmap_price_col,
    )


__all__ = [
    "benchmark_equity",
    "performance_report",
    "plot_equity",
    "run",
]
