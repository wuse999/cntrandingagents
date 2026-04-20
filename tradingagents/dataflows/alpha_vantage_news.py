from .alpha_vantage_common import _make_api_request, format_datetime_for_api

def get_news(ticker, start_date, end_date) -> dict[str, str] | str:
    """返回来自全球主流媒体的实时与历史市场新闻及情绪数据。

    覆盖股票、加密货币、外汇，以及财政政策、并购、IPO 等主题。

    参数：
        ticker: 用于检索新闻文章的股票代码。
        start_date: 新闻检索开始日期。
        end_date: 新闻检索结束日期。

    返回：
        包含新闻情绪数据的字典或 JSON 字符串。
    """

    params = {
        "tickers": ticker,
        "time_from": format_datetime_for_api(start_date),
        "time_to": format_datetime_for_api(end_date),
    }

    return _make_api_request("NEWS_SENTIMENT", params)

def get_global_news(curr_date, look_back_days: int = 7, limit: int = 50) -> dict[str, str] | str:
    """返回不带股票代码过滤条件的全球市场新闻与情绪数据。

    覆盖金融市场、经济等更广泛的主题。

    参数：
        curr_date: 当前日期，格式为 yyyy-mm-dd。
        look_back_days: 向前回看的天数（默认 7）。
        limit: 最大文章数（默认 50）。

    返回：
        包含全球新闻情绪数据的字典或 JSON 字符串。
    """
    from datetime import datetime, timedelta

    # 计算起始日期
    curr_dt = datetime.strptime(curr_date, "%Y-%m-%d")
    start_dt = curr_dt - timedelta(days=look_back_days)
    start_date = start_dt.strftime("%Y-%m-%d")

    params = {
        "topics": "financial_markets,economy_macro,economy_monetary",
        "time_from": format_datetime_for_api(start_date),
        "time_to": format_datetime_for_api(curr_date),
        "limit": str(limit),
    }

    return _make_api_request("NEWS_SENTIMENT", params)


def get_insider_transactions(symbol: str) -> dict[str, str] | str:
    """返回关键内部人最新及历史交易数据。

    覆盖创始人、高管、董事会成员等相关交易记录。

    参数：
        symbol: 股票代码，例如 "IBM"。

    返回：
        包含内部人交易数据的字典或 JSON 字符串。
    """

    params = {
        "symbol": symbol,
    }

    return _make_api_request("INSIDER_TRANSACTIONS", params)
