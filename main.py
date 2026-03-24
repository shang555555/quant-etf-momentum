from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from utils import load_prices
from strategies.momentum import signal, portfolio, backtest, performance
from strategies.mean_reversion import run_mean_reversion


def _plot_nav(strategy_nav, benchmark_nav, output_path: Path, title: str) -> None:
    strategy_nav = pd.Series(strategy_nav).dropna()
    benchmark_nav = pd.Series(benchmark_nav).dropna()

    if not benchmark_nav.empty:
        idx = strategy_nav.index.union(benchmark_nav.index)
        strategy_nav = strategy_nav.reindex(idx).ffill()
        benchmark_nav = benchmark_nav.reindex(idx).ffill()
        combined = pd.concat([strategy_nav, benchmark_nav], axis=1).dropna(how="any")
        if not combined.empty:
            strategy_nav = combined.iloc[:, 0]
            benchmark_nav = combined.iloc[:, 1]

    if not strategy_nav.empty:
        strategy_nav = strategy_nav / strategy_nav.iloc[0]
    if not benchmark_nav.empty:
        benchmark_nav = benchmark_nav / benchmark_nav.iloc[0]

    try:
        plt.figure(figsize=(10, 5))
    except Exception:
        plt.switch_backend("Agg")
        plt.figure(figsize=(10, 5))
    plt.plot(strategy_nav.index, strategy_nav.values, label="Strategy")
    if not benchmark_nav.empty:
        plt.plot(benchmark_nav.index, benchmark_nav.values, label="CSI300")
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Net Value")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)


def main() -> None:
    strategy = "momentum"  # "momentum" or "mean_reversion"
    run_walk_forward = False
    prices = load_prices()

    lookback = 20
    ma_window = 200
    benchmark_col = prices.columns[0]

    if strategy == "momentum":
        momentum = signal.compute_momentum(prices, window=lookback)
        ma = signal.compute_ma(prices[benchmark_col], window=ma_window)
        risk_on = prices[benchmark_col] > ma

        risk_off_asset = "511010" if "511010" in prices.columns else None
        positions = portfolio.build_positions(
            momentum,
            risk_on=risk_on,
            risk_off_asset=risk_off_asset,
        )
        hold_matrix = positions.reindex(prices.index).fillna(0.0)
        zero_days = int((hold_matrix.sum(axis=1) == 0).sum())
        total_days = int(len(hold_matrix))
        zero_ratio = zero_days / total_days if total_days > 0 else 0.0
        print("\n===== Hold Matrix Diagnostics =====")
        print("zero_holding_days:", zero_days)
        print("zero_holding_ratio:", f"{zero_ratio:.2%}")

        strategy_returns, nav, benchmark_nav = backtest.run_backtest(
            prices, positions, benchmark_col=benchmark_col
        )
        nav_name = "momentum_nav"

        if run_walk_forward:
            from analysis.walk_forward import rolling_test, plot_rolling_results

            n_list = [10, 15, 20, 30, 40]
            rolling_df = rolling_test(prices, n_list)
            plot_rolling_results(rolling_df)
    else:
        nav = run_mean_reversion(prices[benchmark_col])
        strategy_returns = nav.pct_change(fill_method=None).fillna(0.0)
        benchmark_nav = (1 + prices[benchmark_col].pct_change(fill_method=None).fillna(0.0)).cumprod()
        nav_name = "mean_reversion_nav"

    print("\n===== Strategy Return Diagnostics =====")
    print(strategy_returns.describe())
    print("max_abs_return:", float(strategy_returns.abs().max()))

    ann = performance.annual_return(nav)
    shp = performance.sharpe(strategy_returns)
    mdd = performance.max_drawdown(nav)

    print("年化收益:", f"{ann:.2%}")
    print("夏普比率:", f"{shp:.2f}")
    print("最大回撤:", f"{mdd:.2%}")

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    nav.to_csv(output_dir / f"{nav_name}.csv", header=["nav"])
    if not benchmark_nav.empty:
        benchmark_nav.to_csv(output_dir / f"{nav_name}_benchmark.csv", header=["benchmark"])
    equity_title = "Momentum Strategy vs Benchmark"
    _plot_nav(nav, benchmark_nav, output_dir / "equity_curve.png", equity_title)


if __name__ == "__main__":
    main()
