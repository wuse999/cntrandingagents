import time
import logging

import pandas as pd
import yfinance as yf
from yfinance.exceptions import YFRateLimitError
from stockstats import wrap
from typing import Annotated
import os
from .config import get_config

logger = logging.getLogger(__name__)


def yf_retry(func, max_retries=3, base_delay=2.0):
    """执行 yfinance 调用，并在限流时采用指数退避重试。

    yfinance 在 HTTP 429 响应时会抛出 YFRateLimitError，
    但不会自行重试。该包装器只对限流场景补充重试逻辑，
    其他异常会立即向外抛出。
    """
    for attempt in range(max_retries + 1):
        try:
            return func()
        except YFRateLimitError:
            if attempt < max_retries:
                delay = base_delay * (2 ** attempt)
                logger.warning(f"Yahoo Finance 触发限流，将在 {delay:.0f}s 后重试（第 {attempt + 1}/{max_retries} 次）")
                time.sleep(delay)
            else:
                raise


def _clean_dataframe(data: pd.DataFrame) -> pd.DataFrame:
    """为 stockstats 规范化股票 DataFrame：解析日期、剔除无效行、填补价格缺口。"""
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    data = data.dropna(subset=["Date"])

    price_cols = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c in data.columns]
    data[price_cols] = data[price_cols].apply(pd.to_numeric, errors="coerce")
    data = data.dropna(subset=["Close"])
    data[price_cols] = data[price_cols].ffill().bfill()

    return data


def load_ohlcv(symbol: str, curr_date: str) -> pd.DataFrame:
    """带缓存获取 OHLCV 数据，并过滤未来数据以防止前视偏差。

    会下载截至今天的长期历史数据并按 symbol 缓存。后续调用复用缓存。
    所有晚于 curr_date 的行都会被过滤，确保回测不会看到未来价格。
    """
    config = get_config()
    curr_date_dt = pd.to_datetime(curr_date)

    # 缓存使用固定时间窗口，因此每个 symbol 只维护一个文件
    today_date = pd.Timestamp.today()
    start_date = today_date - pd.DateOffset(years=5)
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = today_date.strftime("%Y-%m-%d")

    os.makedirs(config["data_cache_dir"], exist_ok=True)
    data_file = os.path.join(
        config["data_cache_dir"],
        f"{symbol}-YFin-data-{start_str}-{end_str}.csv",
    )

    if os.path.exists(data_file):
        data = pd.read_csv(data_file, on_bad_lines="skip")
    else:
        data = yf_retry(lambda: yf.download(
            symbol,
            start=start_str,
            end=end_str,
            multi_level_index=False,
            progress=False,
            auto_adjust=True,
        ))
        data = data.reset_index()
        data.to_csv(data_file, index=False)

    data = _clean_dataframe(data)

    # 过滤到 curr_date，避免回测时出现前视偏差
    data = data[data["Date"] <= curr_date_dt]

    return data


def filter_financials_by_date(data: pd.DataFrame, curr_date: str) -> pd.DataFrame:
    """删除晚于 curr_date 的财报列（财报期结束日期）。

    yfinance 财务报表会把财报期结束日期放在列名里。
    晚于 curr_date 的列意味着未来数据，因此需要移除以避免前视偏差。
    """
    if not curr_date or data.empty:
        return data
    cutoff = pd.Timestamp(curr_date)
    mask = pd.to_datetime(data.columns, errors="coerce") <= cutoff
    return data.loc[:, mask]


class StockstatsUtils:
    @staticmethod
    def get_stock_stats(
        symbol: Annotated[str, "公司股票代码"],
        indicator: Annotated[
            str, "基于公司股票数据计算的量化技术指标"
        ],
        curr_date: Annotated[
            str, "用于获取股价数据的参考日期，格式为 YYYY-mm-dd"
        ],
    ):
        data = load_ohlcv(symbol, curr_date)
        df = wrap(data)
        df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
        curr_date_str = pd.to_datetime(curr_date).strftime("%Y-%m-%d")

        df[indicator]  # 触发 stockstats 计算该指标
        matching_rows = df[df["Date"].str.startswith(curr_date_str)]

        if not matching_rows.empty:
            indicator_value = matching_rows[indicator].values[0]
            return indicator_value
        else:
            return "N/A：非交易日（周末或节假日）"
