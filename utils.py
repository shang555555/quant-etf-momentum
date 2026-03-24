from __future__ import annotations

from pathlib import Path
import pandas as pd


def _read_csv_with_fallback(file_path: Path) -> pd.DataFrame:
    encodings = ("utf-8-sig", "utf-8", "gbk")
    last_error: Exception | None = None
    for encoding in encodings:
        try:
            return pd.read_csv(file_path, encoding=encoding)
        except Exception as exc:
            last_error = exc
    if last_error is not None:
        raise last_error
    raise RuntimeError(f"{file_path}: failed to read CSV")


def _detect_column(df: pd.DataFrame, candidates: list[str]) -> str:
    col = next((c for c in candidates if c in df.columns), None)
    if col is None:
        raise ValueError("required column not found")
    return col


def _load_price_series(file_path: Path) -> pd.Series:
    df = _read_csv_with_fallback(file_path)
    date_col = _detect_column(df, ["trade_date", "date", "日期", "净值日期"])
    price_col = _detect_column(df, ["close", "收盘", "单位净值", "nav"])

    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col]).sort_values(date_col)
    df.set_index(date_col, inplace=True)
    df.index = pd.DatetimeIndex(df.index)

    series = pd.to_numeric(df[price_col], errors="coerce")
    return series


def load_prices(
    files: dict[str, str] | None = None,
    data_dir: str | Path = "data",
) -> pd.DataFrame:
    default_files = {
        "510300": "510300.csv",
        "510500": "510500.csv",
        "159915": "159915.csv",
        "511010": "511010.csv",
        "000218": "000218.csv",
        "009051": "009051.csv",
    }
    file_map = files or default_files
    data_dir = Path(data_dir)

    frames = []
    for name, filename in file_map.items():
        series = _load_price_series(data_dir / filename)
        series.name = name
        frames.append(series)

    prices = pd.concat(frames, axis=1).sort_index()
    prices.index = pd.DatetimeIndex(prices.index)
    return prices
