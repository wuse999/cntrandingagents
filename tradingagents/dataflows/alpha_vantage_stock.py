from datetime import datetime
from .alpha_vantage_common import _make_api_request, _filter_csv_by_date_range

def get_stock(
    symbol: str,
    start_date: str,
    end_date: str
) -> str:
    """
    返回原始日线 OHLCV、复权收盘价以及历史拆股/分红事件，
    并按指定日期区间过滤。

    参数：
        symbol: 股票代码，例如 `IBM`
        start_date: 开始日期，格式为 yyyy-mm-dd
        end_date: 结束日期，格式为 yyyy-mm-dd

    返回：
        str: 过滤后的日度复权时间序列 CSV 字符串。
    """
    # 解析日期以确定请求区间
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    today = datetime.now()

    # 根据请求区间是否落在最近 100 天内决定 outputsize
    # `compact` 只返回最近 100 个数据点，因此需要判断 start_date 是否足够接近当前
    days_from_today_to_start = (today - start_dt).days
    outputsize = "compact" if days_from_today_to_start < 100 else "full"

    params = {
        "symbol": symbol,
        "outputsize": outputsize,
        "datatype": "csv",
    }

    response = _make_api_request("TIME_SERIES_DAILY_ADJUSTED", params)

    return _filter_csv_by_date_range(response, start_date, end_date)
