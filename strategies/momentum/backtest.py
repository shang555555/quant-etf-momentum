import pandas as pd


def compute_returns(prices: pd.DataFrame) -> pd.DataFrame:
    prices = pd.DataFrame(prices).copy()
    prices.index = pd.DatetimeIndex(prices.index)
    returns = prices.pct_change(fill_method=None)
    # Guard against abnormal single-day spikes (data issues / splits).
    returns = returns.where(returns.abs() <= 0.10)
    return returns.fillna(0.0)


def compute_nav(returns: pd.Series, start_value: float = 1.0) -> pd.Series:
    r = pd.Series(returns).fillna(0.0)
    nav = (1 + r).cumprod() * float(start_value)
    nav.name = "nav"
    nav.index = pd.DatetimeIndex(nav.index)
    return nav


def run_backtest(
    prices: pd.DataFrame,
    positions: pd.DataFrame,
    benchmark_col: str | None = None,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    prices = pd.DataFrame(prices).copy()
    prices.index = pd.DatetimeIndex(prices.index)
    positions = pd.DataFrame(positions).reindex(prices.index).fillna(0.0)

    returns = compute_returns(prices)
    positions = positions.reindex(returns.index).fillna(0.0)

    strategy_returns = (positions.shift(1).fillna(0.0) * returns).sum(axis=1)
    strategy_nav = compute_nav(strategy_returns)

    if benchmark_col is None:
        benchmark_col = prices.columns[0] if len(prices.columns) > 0 else None

    if benchmark_col is None or benchmark_col not in returns.columns:
        benchmark_nav = pd.Series(dtype=float)
    else:
        benchmark_returns = returns[benchmark_col]
        benchmark_nav = compute_nav(benchmark_returns)

    if not benchmark_nav.empty:
        strategy_nav, benchmark_nav = strategy_nav.align(benchmark_nav, join="inner")
        if not strategy_nav.empty:
            strategy_nav = strategy_nav / strategy_nav.iloc[0]
        if not benchmark_nav.empty:
            benchmark_nav = benchmark_nav / benchmark_nav.iloc[0]
        strategy_returns = strategy_returns.reindex(strategy_nav.index).fillna(0.0)
    else:
        if not strategy_nav.empty:
            strategy_nav = strategy_nav / strategy_nav.iloc[0]
            strategy_returns = strategy_returns.reindex(strategy_nav.index).fillna(0.0)

    return strategy_returns, strategy_nav, benchmark_nav
