from langchain_core.tools import tool
from typing import Annotated
from tradingagents.dataflows.interface import route_to_vendor


@tool
def get_fundamentals(
    ticker: Annotated[str, "股票代码"],
    curr_date: Annotated[str, "当前交易日期，格式为 yyyy-mm-dd"],
) -> str:
    """
    获取指定股票代码的综合基本面数据。
    使用当前配置的 `fundamental_data` 数据供应商。

    参数：
        ticker (str): 公司股票代码
        curr_date (str): 当前交易日期，格式为 yyyy-mm-dd

    返回：
        str: 一份格式化后的综合基本面报告
    """
    return route_to_vendor("get_fundamentals", ticker, curr_date)


@tool
def get_balance_sheet(
    ticker: Annotated[str, "股票代码"],
    freq: Annotated[str, "财报频率：annual/quarterly"] = "quarterly",
    curr_date: Annotated[str, "当前交易日期，格式为 yyyy-mm-dd"] = None,
) -> str:
    """
    获取指定股票代码的资产负债表数据。
    使用当前配置的 `fundamental_data` 数据供应商。

    参数：
        ticker (str): 公司股票代码
        freq (str): 财报频率：annual/quarterly（默认 quarterly）
        curr_date (str): 当前交易日期，格式为 yyyy-mm-dd

    返回：
        str: 一份格式化后的资产负债表报告
    """
    return route_to_vendor("get_balance_sheet", ticker, freq, curr_date)


@tool
def get_cashflow(
    ticker: Annotated[str, "股票代码"],
    freq: Annotated[str, "财报频率：annual/quarterly"] = "quarterly",
    curr_date: Annotated[str, "当前交易日期，格式为 yyyy-mm-dd"] = None,
) -> str:
    """
    获取指定股票代码的现金流量表数据。
    使用当前配置的 `fundamental_data` 数据供应商。

    参数：
        ticker (str): 公司股票代码
        freq (str): 财报频率：annual/quarterly（默认 quarterly）
        curr_date (str): 当前交易日期，格式为 yyyy-mm-dd

    返回：
        str: 一份格式化后的现金流量表报告
    """
    return route_to_vendor("get_cashflow", ticker, freq, curr_date)


@tool
def get_income_statement(
    ticker: Annotated[str, "股票代码"],
    freq: Annotated[str, "财报频率：annual/quarterly"] = "quarterly",
    curr_date: Annotated[str, "当前交易日期，格式为 yyyy-mm-dd"] = None,
) -> str:
    """
    获取指定股票代码的利润表数据。
    使用当前配置的 `fundamental_data` 数据供应商。

    参数：
        ticker (str): 公司股票代码
        freq (str): 财报频率：annual/quarterly（默认 quarterly）
        curr_date (str): 当前交易日期，格式为 yyyy-mm-dd

    返回：
        str: 一份格式化后的利润表报告
    """
    return route_to_vendor("get_income_statement", ticker, freq, curr_date)
