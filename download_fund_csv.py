from __future__ import annotations

from pathlib import Path
import argparse
import sys

import pandas as pd


FUND_MAP = {
    "000218": "国泰黄金ETF联接A",
    "009051": "易方达中证红利ETF联接A",
}


def fetch_fund_nav(symbol: str, start: str, end: str) -> pd.DataFrame:
    try:
        import akshare as ak
    except ImportError as exc:
        raise RuntimeError(
            "未安装 akshare。请先执行 pip install akshare pandas"
        ) from exc

    df = ak.fund_open_fund_info_em(
        symbol=symbol,
        indicator="单位净值走势",
    )

    if df is None or df.empty:
        raise RuntimeError(f"{symbol} 未获取到数据")

    # akshare 返回列名通常为：净值日期、单位净值、日增长率
    date_col = "净值日期"
    if date_col not in df.columns:
        raise RuntimeError(f"{symbol} 数据中未找到列: {date_col}")

    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col])

    start_dt = pd.to_datetime(start)
    end_dt = pd.to_datetime(end)
    df = df[(df[date_col] >= start_dt) & (df[date_col] <= end_dt)].copy()
    df = df.sort_values(date_col).reset_index(drop=True)
    return df


def main() -> int:
    parser = argparse.ArgumentParser(
        description="下载并保存基金历史 CSV 数据（000218 / 009051）"
    )
    parser.add_argument(
        "--start",
        default="2010-01-01",
        help="开始日期，格式 YYYY-MM-DD，默认 2010-01-01",
    )
    parser.add_argument(
        "--end",
        default=pd.Timestamp.today().strftime("%Y-%m-%d"),
        help="结束日期，格式 YYYY-MM-DD，默认今天",
    )
    parser.add_argument(
        "--outdir",
        default="data",
        help="输出目录，默认 data",
    )
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    print(f"下载区间: {args.start} ~ {args.end}")
    print(f"输出目录: {outdir.resolve()}")

    for symbol, name in FUND_MAP.items():
        df = fetch_fund_nav(symbol=symbol, start=args.start, end=args.end)
        out_path = outdir / f"{symbol}.csv"
        df.to_csv(out_path, index=False, encoding="utf-8-sig")
        print(f"已保存: {symbol} ({name}) -> {out_path}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"执行失败: {exc}", file=sys.stderr)
        raise SystemExit(1)
