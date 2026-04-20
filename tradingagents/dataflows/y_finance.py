from typing import Annotated
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import yfinance as yf
import os
from .stockstats_utils import StockstatsUtils, _clean_dataframe, yf_retry, load_ohlcv, filter_financials_by_date

def get_YFin_data_online(
    symbol: Annotated[str, "公司股票代码"],
    start_date: Annotated[str, "开始日期，格式为 yyyy-mm-dd"],
    end_date: Annotated[str, "结束日期，格式为 yyyy-mm-dd"],
):

    datetime.strptime(start_date, "%Y-%m-%d")
    datetime.strptime(end_date, "%Y-%m-%d")

    # 创建 ticker 对象
    ticker = yf.Ticker(symbol.upper())

    # 获取指定日期区间的历史数据
    data = yf_retry(lambda: ticker.history(start=start_date, end=end_date))

    # 检查返回是否为空
    if data.empty:
        return (
            f"股票代码 '{symbol}' 在 {start_date} 到 {end_date} 之间没有找到数据。"
        )

    # 去除索引中的时区信息，便于输出阅读
    if data.index.tz is not None:
        data.index = data.index.tz_localize(None)

    # 将数值列四舍五入到 2 位小数，提升可读性
    numeric_columns = ["Open", "High", "Low", "Close", "Adj Close"]
    for col in numeric_columns:
        if col in data.columns:
            data[col] = data[col].round(2)

    # 将 DataFrame 转为 CSV 字符串
    csv_string = data.to_csv()

    # 添加报头信息
    header = f"# {symbol.upper()} 的股票数据（{start_date} 至 {end_date}）\n"
    header += f"# 总记录数：{len(data)}\n"
    header += f"# 数据获取时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    return header + csv_string

def get_stock_stats_indicators_window(
    symbol: Annotated[str, "公司股票代码"],
    indicator: Annotated[str, "需要分析并生成报告的技术指标"],
    curr_date: Annotated[
        str, "当前交易日期，格式为 YYYY-mm-dd"
    ],
    look_back_days: Annotated[int, "向前回看的天数"],
) -> str:

    best_ind_params = {
        # 移动平均类
        "close_50_sma": (
            "50 SMA：中期趋势指标。"
            "用途：识别趋势方向，并可作为动态支撑/阻力。"
            "提示：它对价格有滞后性，最好搭配更快的指标获得更及时的信号。"
        ),
        "close_200_sma": (
            "200 SMA：长期趋势基准。"
            "用途：确认整体市场趋势，并识别金叉/死叉结构。"
            "提示：反应较慢，更适合战略级趋势确认，而非频繁入场。"
        ),
        "close_10_ema": (
            "10 EMA：响应迅速的短期均线。"
            "用途：捕捉动量快速变化与潜在入场点。"
            "提示：震荡市场中噪声较多，宜结合更长期均线过滤假信号。"
        ),
        # MACD 相关
        "macd": (
            "MACD：通过 EMA 差值计算动量。"
            "用途：观察交叉与背离，识别趋势变化。"
            "提示：在低波动或横盘市场中，需结合其他指标确认。"
        ),
        "macds": (
            "MACD 信号线：MACD 线的平滑 EMA。"
            "用途：配合 MACD 线交叉触发交易信号。"
            "提示：应作为更完整策略的一部分，避免误报。"
        ),
        "macdh": (
            "MACD 柱状图：展示 MACD 线与信号线之间的差距。"
            "用途：可视化动量强弱，并更早发现背离。"
            "提示：波动可能较大，快速市场中建议搭配额外过滤条件。"
        ),
        # 动量指标
        "rsi": (
            "RSI：衡量动量，用于识别超买/超卖。"
            "用途：应用 70/30 阈值，并观察背离以提示反转。"
            "提示：在强趋势中 RSI 可能长时间处于极值区间，需始终结合趋势分析。"
        ),
        # 波动率指标
        "boll": (
            "布林带中轨：本质是 20 日 SMA。"
            "用途：作为价格运动的动态基准。"
            "提示：结合上下轨使用，更适合识别突破或反转。"
        ),
        "boll_ub": (
            "布林带上轨：通常位于中轨上方 2 个标准差。"
            "用途：提示潜在超买区域与突破区间。"
            "提示：需结合其他工具确认，强趋势中价格可能沿上轨运行。"
        ),
        "boll_lb": (
            "布林带下轨：通常位于中轨下方 2 个标准差。"
            "用途：提示潜在超卖区域。"
            "提示：应结合其他分析，避免误判反转。"
        ),
        "atr": (
            "ATR：通过平均真实波幅衡量波动率。"
            "用途：设定止损水平，并根据当前波动率调整仓位规模。"
            "提示：它属于滞后型指标，应纳入更完整的风控框架中使用。"
        ),
        # 成交量类指标
        "vwma": (
            "VWMA：按成交量加权的移动平均。"
            "用途：将价格行为与成交量结合，用于确认趋势。"
            "提示：成交量突增可能造成偏差，建议配合其他量能分析一起使用。"
        ),
        "mfi": (
            "MFI：资金流量指标，结合价格与成交量衡量买卖压力。"
            "用途：识别超买（>80）或超卖（<20）状态，并确认趋势或反转强度。"
            "提示：可与 RSI 或 MACD 配合使用；价格与 MFI 的背离可能预示潜在反转。"
        ),
    }

    if indicator not in best_ind_params:
        raise ValueError(
            f"不支持指标 {indicator}。请从以下选项中选择：{list(best_ind_params.keys())}"
        )

    end_date = curr_date
    curr_date_dt = datetime.strptime(curr_date, "%Y-%m-%d")
    before = curr_date_dt - relativedelta(days=look_back_days)

    # 优化：只获取一次股价数据，并一次性计算全部日期的指标
    try:
        indicator_data = _get_stock_stats_bulk(symbol, indicator, curr_date)
        
        # 生成所需日期区间
        current_dt = curr_date_dt
        date_values = []
        
        while current_dt >= before:
            date_str = current_dt.strftime('%Y-%m-%d')
            
            # 读取该日期对应的指标值
            if date_str in indicator_data:
                indicator_value = indicator_data[date_str]
            else:
                indicator_value = "N/A：非交易日（周末或节假日）"
            
            date_values.append((date_str, indicator_value))
            current_dt = current_dt - relativedelta(days=1)
        
        # 构建结果字符串
        ind_string = ""
        for date_str, value in date_values:
            ind_string += f"{date_str}: {value}\n"
        
    except Exception as e:
        print(f"批量获取 stockstats 指标数据时出错：{e}")
        # 如果批量方法失败，则回退到原始逐日实现
        ind_string = ""
        curr_date_dt = datetime.strptime(curr_date, "%Y-%m-%d")
        while curr_date_dt >= before:
            indicator_value = get_stockstats_indicator(
                symbol, indicator, curr_date_dt.strftime("%Y-%m-%d")
            )
            ind_string += f"{curr_date_dt.strftime('%Y-%m-%d')}: {indicator_value}\n"
            curr_date_dt = curr_date_dt - relativedelta(days=1)

    result_str = (
        f"## {indicator} 指标值（{before.strftime('%Y-%m-%d')} 至 {end_date}）\n\n"
        + ind_string
        + "\n\n"
        + best_ind_params.get(indicator, "暂无说明。")
    )

    return result_str


def _get_stock_stats_bulk(
    symbol: Annotated[str, "公司股票代码"],
    indicator: Annotated[str, "需要计算的技术指标"],
    curr_date: Annotated[str, "参考日期"]
) -> dict:
    """
    优化版批量 stockstats 指标计算。
    只获取一次数据，并计算所有可用日期的指标值。
    返回一个“日期字符串 -> 指标值”的字典。
    """
    from stockstats import wrap

    data = load_ohlcv(symbol, curr_date)
    df = wrap(data)
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
    
    # 一次性计算所有行的指标
    df[indicator]  # 触发 stockstats 计算该指标
    
    # 构建“日期字符串 -> 指标值”的映射字典
    result_dict = {}
    for _, row in df.iterrows():
        date_str = row["Date"]
        indicator_value = row[indicator]
        
        # 处理 NaN/None
        if pd.isna(indicator_value):
            result_dict[date_str] = "N/A"
        else:
            result_dict[date_str] = str(indicator_value)
    
    return result_dict


def get_stockstats_indicator(
    symbol: Annotated[str, "公司股票代码"],
    indicator: Annotated[str, "需要分析并生成报告的技术指标"],
    curr_date: Annotated[
        str, "当前交易日期，格式为 YYYY-mm-dd"
    ],
) -> str:

    curr_date_dt = datetime.strptime(curr_date, "%Y-%m-%d")
    curr_date = curr_date_dt.strftime("%Y-%m-%d")

    try:
        indicator_value = StockstatsUtils.get_stock_stats(
            symbol,
            indicator,
            curr_date,
        )
    except Exception as e:
        print(
            f"获取 {curr_date} 的 stockstats 指标 {indicator} 数据时出错：{e}"
        )
        return ""

    return str(indicator_value)


def get_fundamentals(
    ticker: Annotated[str, "公司股票代码"],
    curr_date: Annotated[str, "当前日期（yfinance 不使用该参数）"] = None
):
    """从 yfinance 获取公司基本面概览。"""
    try:
        ticker_obj = yf.Ticker(ticker.upper())
        info = yf_retry(lambda: ticker_obj.info)

        if not info:
            return f"股票代码 '{ticker}' 没有找到基本面数据。"

        fields = [
            ("公司名称", info.get("longName")),
            ("所属板块", info.get("sector")),
            ("所属行业", info.get("industry")),
            ("市值", info.get("marketCap")),
            ("市盈率（TTM）", info.get("trailingPE")),
            ("预期市盈率", info.get("forwardPE")),
            ("PEG 比率", info.get("pegRatio")),
            ("市净率", info.get("priceToBook")),
            ("每股收益（TTM）", info.get("trailingEps")),
            ("预期每股收益", info.get("forwardEps")),
            ("股息率", info.get("dividendYield")),
            ("Beta", info.get("beta")),
            ("52 周最高价", info.get("fiftyTwoWeekHigh")),
            ("52 周最低价", info.get("fiftyTwoWeekLow")),
            ("50 日均价", info.get("fiftyDayAverage")),
            ("200 日均价", info.get("twoHundredDayAverage")),
            ("营收（TTM）", info.get("totalRevenue")),
            ("毛利润", info.get("grossProfits")),
            ("EBITDA", info.get("ebitda")),
            ("净利润", info.get("netIncomeToCommon")),
            ("利润率", info.get("profitMargins")),
            ("营业利润率", info.get("operatingMargins")),
            ("净资产收益率", info.get("returnOnEquity")),
            ("总资产收益率", info.get("returnOnAssets")),
            ("资产负债率", info.get("debtToEquity")),
            ("流动比率", info.get("currentRatio")),
            ("每股净资产", info.get("bookValue")),
            ("自由现金流", info.get("freeCashflow")),
        ]

        lines = []
        for label, value in fields:
            if value is not None:
                lines.append(f"{label}: {value}")

        header = f"# {ticker.upper()} 的公司基本面\n"
        header += f"# 数据获取时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        return header + "\n".join(lines)

    except Exception as e:
        return f"获取 {ticker} 基本面数据失败：{str(e)}"


def get_balance_sheet(
    ticker: Annotated[str, "公司股票代码"],
    freq: Annotated[str, "数据频率：'annual' 或 'quarterly'"] = "quarterly",
    curr_date: Annotated[str, "当前日期，格式为 YYYY-MM-DD"] = None
):
    """从 yfinance 获取资产负债表数据。"""
    try:
        ticker_obj = yf.Ticker(ticker.upper())

        if freq.lower() == "quarterly":
            data = yf_retry(lambda: ticker_obj.quarterly_balance_sheet)
        else:
            data = yf_retry(lambda: ticker_obj.balance_sheet)

        data = filter_financials_by_date(data, curr_date)

        if data.empty:
            return f"股票代码 '{ticker}' 没有找到资产负债表数据。"
            
        # 转为 CSV 字符串，保持与其他函数输出一致
        csv_string = data.to_csv()
        
        # 添加报头信息
        header = f"# {ticker.upper()} 的资产负债表数据（{freq}）\n"
        header += f"# 数据获取时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        return header + csv_string
        
    except Exception as e:
        return f"获取 {ticker} 资产负债表失败：{str(e)}"


def get_cashflow(
    ticker: Annotated[str, "公司股票代码"],
    freq: Annotated[str, "数据频率：'annual' 或 'quarterly'"] = "quarterly",
    curr_date: Annotated[str, "当前日期，格式为 YYYY-MM-DD"] = None
):
    """从 yfinance 获取现金流量表数据。"""
    try:
        ticker_obj = yf.Ticker(ticker.upper())

        if freq.lower() == "quarterly":
            data = yf_retry(lambda: ticker_obj.quarterly_cashflow)
        else:
            data = yf_retry(lambda: ticker_obj.cashflow)

        data = filter_financials_by_date(data, curr_date)

        if data.empty:
            return f"股票代码 '{ticker}' 没有找到现金流量表数据。"
            
        # 转为 CSV 字符串，保持与其他函数输出一致
        csv_string = data.to_csv()
        
        # 添加报头信息
        header = f"# {ticker.upper()} 的现金流量表数据（{freq}）\n"
        header += f"# 数据获取时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        return header + csv_string
        
    except Exception as e:
        return f"获取 {ticker} 现金流量表失败：{str(e)}"


def get_income_statement(
    ticker: Annotated[str, "公司股票代码"],
    freq: Annotated[str, "数据频率：'annual' 或 'quarterly'"] = "quarterly",
    curr_date: Annotated[str, "当前日期，格式为 YYYY-MM-DD"] = None
):
    """从 yfinance 获取利润表数据。"""
    try:
        ticker_obj = yf.Ticker(ticker.upper())

        if freq.lower() == "quarterly":
            data = yf_retry(lambda: ticker_obj.quarterly_income_stmt)
        else:
            data = yf_retry(lambda: ticker_obj.income_stmt)

        data = filter_financials_by_date(data, curr_date)

        if data.empty:
            return f"股票代码 '{ticker}' 没有找到利润表数据。"
            
        # 转为 CSV 字符串，保持与其他函数输出一致
        csv_string = data.to_csv()
        
        # 添加报头信息
        header = f"# {ticker.upper()} 的利润表数据（{freq}）\n"
        header += f"# 数据获取时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        return header + csv_string
        
    except Exception as e:
        return f"获取 {ticker} 利润表失败：{str(e)}"


def get_insider_transactions(
    ticker: Annotated[str, "公司股票代码"]
):
    """从 yfinance 获取内部人交易数据。"""
    try:
        ticker_obj = yf.Ticker(ticker.upper())
        data = yf_retry(lambda: ticker_obj.insider_transactions)
        
        if data is None or data.empty:
            return f"股票代码 '{ticker}' 没有找到内部人交易数据。"
            
        # 转为 CSV 字符串，保持与其他函数输出一致
        csv_string = data.to_csv()
        
        # 添加报头信息
        header = f"# {ticker.upper()} 的内部人交易数据\n"
        header += f"# 数据获取时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        return header + csv_string
        
    except Exception as e:
        return f"获取 {ticker} 内部人交易数据失败：{str(e)}"
