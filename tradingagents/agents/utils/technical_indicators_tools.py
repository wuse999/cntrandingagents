from langchain_core.tools import tool
from typing import Annotated
from tradingagents.dataflows.interface import route_to_vendor

@tool
def get_indicators(
    symbol: Annotated[str, "公司股票代码"],
    indicator: Annotated[str, "需要分析并生成报告的技术指标名称"],
    curr_date: Annotated[str, "当前交易日期，格式为 YYYY-mm-dd"],
    look_back_days: Annotated[int, "向前回看的天数"] = 30,
) -> str:
    """
    获取指定股票代码的单个技术指标数据。
    使用当前配置的 `technical_indicators` 数据供应商。

    参数：
        symbol (str): 公司股票代码，例如 AAPL、TSM
        indicator (str): 单个技术指标名称，例如 `rsi`、`macd`。每次调用只传一个指标。
        curr_date (str): 当前交易日期，格式为 YYYY-mm-dd
        look_back_days (int): 向前回看的天数，默认 30

    返回：
        str: 包含指定股票代码与指标结果的格式化数据表字符串。
    """
    # LLM 有时会把多个指标拼成逗号分隔字符串；
    # 这里拆开后逐个处理。
    indicators = [i.strip().lower() for i in indicator.split(",") if i.strip()]
    results = []
    for ind in indicators:
        try:
            results.append(route_to_vendor("get_indicators", symbol, ind, curr_date, look_back_days))
        except ValueError as e:
            results.append(str(e))
    return "\n\n".join(results)
