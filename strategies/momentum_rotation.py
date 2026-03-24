import pandas as pd
import numpy as np

from backtest import backtest_portfolio

print("strategy module loaded")


def _strict_returns(prices: pd.DataFrame) -> pd.DataFrame:
    prev = prices.shift(1)
    returns = prices.divide(prev) - 1
    return returns.where(prices.notna() & prev.notna())


def run_strategy(data: pd.DataFrame, N: int) -> tuple[float, float, float]:
    data = data.copy()
    data.index = pd.DatetimeIndex(data.index)
    assets = [
        "510300",
        "510500",
        "159915",
        "511010",
        "000218",
        "009051",
    ]
    available_assets = [asset for asset in assets if asset in data.columns]
    if not available_assets:
        raise ValueError("No available asset columns in data")

    returns = _strict_returns(data)
    momentum = data / data.shift(N) - 1

    ma200 = data["510300"].rolling(200).mean()
    ma_slope = ma200 - ma200.shift(20)

    _vol = returns["510300"].rolling(20).std() * np.sqrt(252)
    _vol_threshold = 0.25

    momentum_for_signal = momentum[available_assets]
    valid_momentum = momentum_for_signal.dropna(how="all")
    period_index = pd.DatetimeIndex(valid_momentum.index).to_period("W")
    weekly_dates = (
        valid_momentum
        .groupby(period_index)
        .apply(lambda x: x.index[-1])
        .values
    )

    strategy_returns = []
    last_holding = None

    for i in range(len(weekly_dates) - 1):
        date = weekly_dates[i]
        next_date = weekly_dates[i + 1]

        momentum_now = momentum.loc[date, available_assets].dropna()
        if momentum_now.empty:
            continue

        best_asset = momentum_now.idxmax()
        vol_now = returns.loc[:date, available_assets].rolling(20).std().iloc[-1].dropna()
        low_vol_asset = vol_now.idxmin() if not vol_now.empty else best_asset

        # if pd.isna(_vol.loc[date]) or _vol.loc[date] > _vol_threshold:
        #     holding = low_vol_asset

        if pd.isna(ma200.loc[date]) or data.loc[date, "510300"] < ma200.loc[date]:
            holding = low_vol_asset
        elif pd.isna(ma_slope.loc[date]) or ma_slope.loc[date] <= 0.01:
            holding = low_vol_asset
        else:
            if momentum_now.max() > 0:
                holding = best_asset
            else:
                holding = low_vol_asset

        period = returns.loc[date:next_date].iloc[1:][holding]

        if last_holding is not None and holding != last_holding:
            period.iloc[0] -= 0.001

        strategy_returns.append(period)
        last_holding = holding

    if not strategy_returns:
        return 0.0, 0.0, 0.0

    strategy_returns = pd.concat(strategy_returns).dropna()
    if strategy_returns.empty:
        return 0.0, 0.0, 0.0

    nav = (1 + strategy_returns).cumprod()

    rolling_max = nav.cummax()
    dd = nav / rolling_max - 1
    max_dd = dd.min()

    years = len(nav) / 252
    annual = nav.iloc[-1] ** (1 / years) - 1

    calmar = annual / abs(max_dd)

    return annual, max_dd, calmar


def run_momentum(data: pd.DataFrame, N: int = 15) -> pd.Series:
    return backtest_portfolio(data, N=N)


def generate_live_signal(
    data: pd.DataFrame, N: int = 15, slope_threshold: float = 0.01
) -> str:
    data = data.copy()
    data.index = pd.DatetimeIndex(data.index)
    momentum = data[["510300", "510500", "159915"]].pct_change(N, fill_method=None)

    ma200 = data["510300"].rolling(200).mean()
    ma_slope = ma200 - ma200.shift(20)

    date = data.index[-1]

    risk_momentum = momentum.loc[date]
    best_etf = risk_momentum.idxmax()

    safe_asset = "511010"

    if pd.isna(ma_slope.loc[date]) or ma_slope.loc[date] <= slope_threshold:
        holding = safe_asset
        reason = "trend weak"
    elif risk_momentum.max() <= 0:
        holding = safe_asset
        reason = "momentum negative"
    else:
        holding = best_etf
        reason = "momentum strongest"

    print("\n===== next week signal =====")
    print("signal date:", date.date())
    print("holding:", holding)
    print("reason:", reason)
    print("\n")

    return holding


print("run_strategy exists:", "run_strategy" in globals())
