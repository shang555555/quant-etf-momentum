from __future__ import annotations

from pathlib import Path

import matplotlib
import pandas as pd


def _is_non_interactive_backend() -> bool:
    backend = matplotlib.get_backend().lower()
    return "agg" in backend or "pdf" in backend or "svg" in backend or "ps" in backend


def plot_parameter_stability(param_df: pd.DataFrame, output_dir: str | Path = "output") -> None:
    if param_df is None or len(param_df) == 0:
        print("Parameter stability: no data available")
        return

    param_df = pd.DataFrame(param_df).dropna()
    if param_df.empty:
        print("Parameter stability: no valid data")
        return

    import matplotlib.pyplot as plt

    try:
        fig = plt.figure(figsize=(8, 4))
    except Exception:
        plt.switch_backend("Agg")
        fig = plt.figure(figsize=(8, 4))

    plt.plot(param_df["N"], param_df["annual_return"], marker="o")
    plt.title("Momentum Parameter Stability")
    plt.xlabel("Momentum Window N")
    plt.ylabel("Annual Return")
    plt.grid()

    if _is_non_interactive_backend():
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / "parameter_stability.png"
        fig.savefig(output_path, dpi=150)
        print(f"Parameter stability plot saved: {output_path}")
    else:
        plt.show()
