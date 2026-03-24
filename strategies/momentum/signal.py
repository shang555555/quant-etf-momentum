import pandas as pd


def compute_momentum(prices: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    prices = pd.DataFrame(prices).copy()
    prices.index = pd.DatetimeIndex(prices.index)
    if window <= 0:
        raise ValueError("window must be > 0")
    return prices.divide(prices.shift(window)) - 1


def compute_ma(series: pd.Series, window: int = 200) -> pd.Series:
    s = pd.Series(series).copy()
    s.index = pd.DatetimeIndex(s.index)
    if window <= 0:
        raise ValueError("window must be > 0")
    return s.rolling(window).mean()
