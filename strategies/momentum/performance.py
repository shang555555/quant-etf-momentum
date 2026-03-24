import pandas as pd


def annual_return(nav: pd.Series, periods_per_year: int = 252) -> float:
    series = pd.Series(nav).dropna()
    if series.empty or len(series) < 2:
        return 0.0
    years = len(series) / float(periods_per_year)
    return (series.iloc[-1] / series.iloc[0]) ** (1 / years) - 1 if years > 0 else 0.0


def sharpe(returns: pd.Series, periods_per_year: int = 252) -> float:
    r = pd.Series(returns).dropna()
    if r.empty or r.std() == 0:
        return 0.0
    return r.mean() / r.std() * (periods_per_year ** 0.5)


def max_drawdown(nav: pd.Series) -> float:
    series = pd.Series(nav).dropna()
    if series.empty:
        return 0.0
    rolling_max = series.cummax()
    drawdown = series / rolling_max - 1
    return float(drawdown.min())


def calmar(nav: pd.Series, periods_per_year: int = 252) -> float:
    ann = annual_return(nav, periods_per_year=periods_per_year)
    mdd = max_drawdown(nav)
    return ann / abs(mdd) if mdd != 0 else 0.0
