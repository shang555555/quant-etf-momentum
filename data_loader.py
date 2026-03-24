import os

import pandas as pd


def _read_csv_with_fallback(file_path: str) -> pd.DataFrame:
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


def load_single_csv(filename: str) -> pd.Series:
    file_path = os.path.join("data", filename)
    df = _read_csv_with_fallback(file_path)

    # Auto-detect date column.
    date_candidates = ["trade_date", "日期", "净值日期"]
    date_col = next((c for c in date_candidates if c in df.columns), None)
    if date_col is None:
        raise ValueError(f"{filename}: date column not found")

    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col]).sort_values(date_col)
    df.set_index(date_col, inplace=True)

    # Auto-detect price column.
    price_candidates = ["close", "收盘", "单位净值"]
    price_col = next((c for c in price_candidates if c in df.columns), None)
    if price_col is None:
        raise ValueError(f"{filename}: price column not found")

    series = pd.to_numeric(df[price_col], errors="coerce")
    return series


def get_data() -> pd.DataFrame:
    files = {
        "510300": "510300.csv",
        "510500": "510500.csv",
        "159915": "159915.csv",
        "511010": "511010.csv",
        "000218": "000218.csv",
        "009051": "009051.csv",
    }

    df_all = pd.DataFrame()

    for name, file in files.items():
        series = load_single_csv(file)
        series.name = name

        if df_all.empty:
            df_all = series.to_frame()
        else:
            df_all = df_all.join(series, how="outer")

    df_all.sort_index(inplace=True)

    return df_all
