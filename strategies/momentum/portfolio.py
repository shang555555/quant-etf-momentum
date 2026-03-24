import pandas as pd


def select_asset(momentum_row: pd.Series) -> str | None:
    row = pd.Series(momentum_row).dropna()
    if row.empty:
        return None
    best = row.idxmax()
    return best if row.max() > 0 else None


def build_positions(
    momentum: pd.DataFrame,
    risk_on: pd.Series | None = None,
    risk_off_asset: str | None = None,
) -> pd.DataFrame:
    momentum = pd.DataFrame(momentum).copy()
    momentum.index = pd.DatetimeIndex(momentum.index)
    positions = pd.DataFrame(0.0, index=momentum.index, columns=momentum.columns)

    risk_flag = None
    if risk_on is not None:
        risk_flag = pd.Series(risk_on).reindex(momentum.index).fillna(False)

    if risk_off_asset is not None and risk_off_asset not in positions.columns:
        risk_off_asset = None

    for dt, row in momentum.iterrows():
        if risk_flag is not None and not bool(risk_flag.loc[dt]):
            if risk_off_asset is not None:
                positions.at[dt, risk_off_asset] = 1.0
            continue
        asset = select_asset(row)
        if asset is None and risk_off_asset is not None:
            asset = risk_off_asset
        if asset is not None:
            positions.at[dt, asset] = 1.0

    return positions
