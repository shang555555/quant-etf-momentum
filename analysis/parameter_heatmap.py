from pathlib import Path

import matplotlib
import pandas as pd

from strategies.momentum_rotation import run_strategy
from strategies.mean_reversion import run_mean_reversion


def _is_non_interactive_backend() -> bool:
    backend = matplotlib.get_backend().lower()
    return "agg" in backend or "pdf" in backend or "svg" in backend or "ps" in backend


def _calmar_from_equity(equity: pd.Series) -> float:
    equity = equity.dropna()
    if equity.empty:
        return 0.0

    rolling_max = equity.cummax()
    dd = equity / rolling_max - 1
    max_dd = dd.min()
    if pd.isna(max_dd) or max_dd == 0:
        return 0.0

    years = len(equity) / 252
    if years <= 0:
        return 0.0

    annual = equity.iloc[-1] ** (1 / years) - 1
    if pd.isna(annual):
        return 0.0

    return annual / abs(max_dd)


def _select_price_series(data: pd.DataFrame | pd.Series, price_col: str | None) -> pd.Series:
    if isinstance(data, pd.Series):
        return data

    if price_col is not None:
        if price_col not in data.columns:
            raise ValueError(f"price_col '{price_col}' not found in data columns")
        return data[price_col]

    numeric_cols = data.select_dtypes(include=["number"]).columns
    if numeric_cols.empty:
        raise ValueError("No numeric columns found in data for mean reversion heatmap")
    return data[numeric_cols[0]]


def parameter_heatmap(
    data: pd.DataFrame | pd.Series,
    n_list: list[int],
    slope_list: list[float],
    strategy: str = "momentum_rotation",
    price_col: str | None = None,
) -> pd.DataFrame:
    heatmap_data = []

    strategy_key = strategy.strip().lower()

    if strategy_key in ("momentum_rotation", "momentum"):
        for _slope in slope_list:
            row = []
            for n in n_list:
                _, _, calmar = run_strategy(data, n)
                row.append(calmar)
            heatmap_data.append(row)
        x_label = "Momentum Window N"
        y_label = "Slope Threshold"
        title = "Momentum Rotation Parameter Heatmap"
        output_name = "parameter_heatmap_momentum_rotation.png"
    elif strategy_key in ("mean_reversion", "mean"):
        price_series = _select_price_series(data, price_col)
        for window in n_list:
            row = []
            for std_n in slope_list:
                equity = run_mean_reversion(price_series, window=window, std_n=std_n)
                calmar = _calmar_from_equity(equity)
                row.append(calmar)
            heatmap_data.append(row)
        x_label = "Std Multiplier"
        y_label = "Window"
        title = "Mean Reversion Parameter Heatmap"
        output_name = "parameter_heatmap_mean_reversion.png"
    else:
        raise ValueError(f"Unknown strategy: {strategy}")

    if strategy_key in ("mean_reversion", "mean"):
        heatmap_df = pd.DataFrame(heatmap_data, index=n_list, columns=slope_list)
    else:
        heatmap_df = pd.DataFrame(heatmap_data, index=slope_list, columns=n_list)

    import matplotlib.pyplot as plt

    plt.figure(figsize=(8, 4))
    plt.imshow(heatmap_df, aspect="auto", cmap="YlOrRd", origin="lower")
    plt.colorbar(label="Calmar")
    if strategy_key in ("mean_reversion", "mean"):
        plt.xticks(range(len(slope_list)), [f"{s:.3f}".rstrip("0").rstrip(".") for s in slope_list])
        plt.yticks(range(len(n_list)), [str(n) for n in n_list])
    else:
        plt.xticks(range(len(n_list)), [str(n) for n in n_list])
        plt.yticks(range(len(slope_list)), [f"{s:.3f}".rstrip("0").rstrip(".") for s in slope_list])
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.tight_layout()

    print(heatmap_df)

    if _is_non_interactive_backend():
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / output_name
        plt.savefig(output_path, dpi=150)
        print(f"parameter heatmap saved: {output_path}")
    else:
        plt.show()

    return heatmap_df
