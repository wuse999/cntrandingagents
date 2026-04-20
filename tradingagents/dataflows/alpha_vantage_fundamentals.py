from .alpha_vantage_common import _make_api_request


def _filter_reports_by_date(result, curr_date: str):
    """过滤 annualReports/quarterlyReports，排除晚于 curr_date 的条目。

    通过移除结束日期晚于当前模拟日期的财报周期，避免前视偏差。
    """
    if not curr_date or not isinstance(result, dict):
        return result
    for key in ("annualReports", "quarterlyReports"):
        if key in result:
            result[key] = [
                r for r in result[key]
                if r.get("fiscalDateEnding", "") <= curr_date
            ]
    return result


def get_fundamentals(ticker: str, curr_date: str = None) -> str:
    """
    使用 Alpha Vantage 获取指定股票代码的综合基本面数据。

    参数：
        ticker (str): 公司股票代码
        curr_date (str): 当前交易日期，格式为 yyyy-mm-dd（Alpha Vantage 不直接使用）

    返回：
        str: 公司概览数据，包含财务比率与关键指标
    """
    params = {
        "symbol": ticker,
    }

    return _make_api_request("OVERVIEW", params)


def get_balance_sheet(ticker: str, freq: str = "quarterly", curr_date: str = None):
    """使用 Alpha Vantage 获取指定股票代码的资产负债表数据。"""
    result = _make_api_request("BALANCE_SHEET", {"symbol": ticker})
    return _filter_reports_by_date(result, curr_date)


def get_cashflow(ticker: str, freq: str = "quarterly", curr_date: str = None):
    """使用 Alpha Vantage 获取指定股票代码的现金流量表数据。"""
    result = _make_api_request("CASH_FLOW", {"symbol": ticker})
    return _filter_reports_by_date(result, curr_date)


def get_income_statement(ticker: str, freq: str = "quarterly", curr_date: str = None):
    """使用 Alpha Vantage 获取指定股票代码的利润表数据。"""
    result = _make_api_request("INCOME_STATEMENT", {"symbol": ticker})
    return _filter_reports_by_date(result, curr_date)

