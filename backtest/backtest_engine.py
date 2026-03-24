import pandas as pd


def backtest_portfolio(prices: pd.DataFrame, N: int) -> pd.Series:
    prices = pd.DataFrame(prices).dropna()
    if prices.empty or N <= 0 or len(prices) <= N:
        return pd.Series(dtype=float, name="equity")

    returns = prices.pct_change(fill_method=None)
    equity = [1.0]

    for i in range(N, len(prices) - 1):
        window = prices.iloc[i - N : i]
        momentum = window.iloc[-1] / window.iloc[0] - 1
        holding = momentum.idxmax()
        period_return = returns.iloc[i + 1][holding]
        equity.append(equity[-1] * (1 + period_return))

    equity_series = pd.Series(equity, index=prices.index[N:], name="equity")
    return equity_series
