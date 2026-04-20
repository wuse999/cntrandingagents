from langchain_core.tools import tool
from typing import Annotated
from tradingagents.dataflows.interface import route_to_vendor

@tool
def get_news(
    ticker: Annotated[str, "股票代码"],
    start_date: Annotated[str, "开始日期，格式为 yyyy-mm-dd"],
    end_date: Annotated[str, "结束日期，格式为 yyyy-mm-dd"],
) -> str:
    """
    获取指定股票代码的新闻数据。
    使用当前配置的 `news_data` 数据供应商。

    参数：
        ticker (str): 股票代码
        start_date (str): 开始日期，格式为 yyyy-mm-dd
        end_date (str): 结束日期，格式为 yyyy-mm-dd

    返回：
        str: 包含新闻数据的格式化字符串
    """
    return route_to_vendor("get_news", ticker, start_date, end_date)

@tool
def get_global_news(
    curr_date: Annotated[str, "当前日期，格式为 yyyy-mm-dd"],
    look_back_days: Annotated[int, "向前回看的天数"] = 7,
    limit: Annotated[int, "返回的最大文章数"] = 5,
) -> str:
    """
    获取全球新闻数据。
    使用当前配置的 `news_data` 数据供应商。

    参数：
        curr_date (str): 当前日期，格式为 yyyy-mm-dd
        look_back_days (int): 向前回看的天数（默认 7）
        limit (int): 返回的最大文章数（默认 5）

    返回：
        str: 包含全球新闻数据的格式化字符串
    """
    return route_to_vendor("get_global_news", curr_date, look_back_days, limit)

@tool
def get_insider_transactions(
    ticker: Annotated[str, "股票代码"],
) -> str:
    """
    获取公司的内部人交易信息。
    使用当前配置的 `news_data` 数据供应商。

    参数：
        ticker (str): 公司股票代码

    返回：
        str: 一份内部人交易数据报告
    """
    return route_to_vendor("get_insider_transactions", ticker)
