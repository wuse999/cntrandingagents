from .alpha_vantage_common import _make_api_request

def get_indicator(
    symbol: str,
    indicator: str,
    curr_date: str,
    look_back_days: int,
    interval: str = "daily",
    time_period: int = 14,
    series_type: str = "close"
) -> str:
    """
    返回 Alpha Vantage 在指定时间窗口内的技术指标数值。

    参数：
        symbol: 公司股票代码
        indicator: 需要分析和生成报告的技术指标
        curr_date: 当前交易日期，格式为 YYYY-mm-dd
        look_back_days: 向前回看的天数
        interval: 时间间隔（daily、weekly、monthly）
        time_period: 指标计算所需的数据点数量
        series_type: 价格类型（close、open、high、low）

    返回：
        str: 包含指标数值与说明的字符串
    """
    from datetime import datetime
    from dateutil.relativedelta import relativedelta

    supported_indicators = {
        "close_50_sma": ("50 SMA", "close"),
        "close_200_sma": ("200 SMA", "close"),
        "close_10_ema": ("10 EMA", "close"),
        "macd": ("MACD", "close"),
        "macds": ("MACD 信号线", "close"),
        "macdh": ("MACD 柱状图", "close"),
        "rsi": ("RSI", "close"),
        "boll": ("布林带中轨", "close"),
        "boll_ub": ("布林带上轨", "close"),
        "boll_lb": ("布林带下轨", "close"),
        "atr": ("ATR", None),
        "vwma": ("VWMA", "close")
    }

    indicator_descriptions = {
        "close_50_sma": "50 SMA：中期趋势指标。用途：识别趋势方向，并可作为动态支撑/阻力。提示：它对价格有滞后性，最好搭配更快的指标获得更及时的信号。",
        "close_200_sma": "200 SMA：长期趋势基准。用途：确认整体市场趋势，并识别金叉/死叉结构。提示：反应较慢，更适合战略级趋势确认，而非频繁入场。",
        "close_10_ema": "10 EMA：响应迅速的短期均线。用途：捕捉动量快速变化与潜在入场点。提示：震荡市场中噪声较多，宜结合更长期均线过滤假信号。",
        "macd": "MACD：通过 EMA 差值计算动量。用途：观察交叉与背离，识别趋势变化。提示：在低波动或横盘市场中，需结合其他指标确认。",
        "macds": "MACD 信号线：MACD 线的平滑 EMA。用途：配合 MACD 线交叉触发交易信号。提示：应作为更完整策略的一部分，避免误报。",
        "macdh": "MACD 柱状图：展示 MACD 线与信号线之间的差距。用途：可视化动量强弱，并更早发现背离。提示：波动可能较大，快速市场中建议搭配额外过滤条件。",
        "rsi": "RSI：衡量动量，用于识别超买/超卖。用途：应用 70/30 阈值，并观察背离以提示反转。提示：在强趋势中 RSI 可能长时间处于极值区间，需始终结合趋势分析。",
        "boll": "布林带中轨：本质是 20 日 SMA。用途：作为价格运动的动态基准。提示：结合上下轨使用，更适合识别突破或反转。",
        "boll_ub": "布林带上轨：通常位于中轨上方 2 个标准差。用途：提示潜在超买区域与突破区间。提示：需结合其他工具确认，强趋势中价格可能沿上轨运行。",
        "boll_lb": "布林带下轨：通常位于中轨下方 2 个标准差。用途：提示潜在超卖区域。提示：应结合其他分析，避免误判反转。",
        "atr": "ATR：通过平均真实波幅衡量波动率。用途：设定止损水平，并根据当前波动率调整仓位规模。提示：它属于滞后型指标，应纳入更完整的风控框架中使用。",
        "vwma": "VWMA：按成交量加权的移动平均。用途：将价格行为与成交量结合，用于确认趋势。提示：成交量突增可能造成偏差，建议配合其他量能分析一起使用。"
    }

    if indicator not in supported_indicators:
        raise ValueError(
            f"不支持指标 {indicator}。请从以下选项中选择：{list(supported_indicators.keys())}"
        )

    curr_date_dt = datetime.strptime(curr_date, "%Y-%m-%d")
    before = curr_date_dt - relativedelta(days=look_back_days)

    # 获取整个时间窗口的数据，而不是逐日单独请求
    _, required_series_type = supported_indicators[indicator]

    # 优先使用指标要求的 series_type
    if required_series_type:
        series_type = required_series_type

    try:
        # 获取该指标在时间窗口内的数据
        if indicator == "close_50_sma":
            data = _make_api_request("SMA", {
                "symbol": symbol,
                "interval": interval,
                "time_period": "50",
                "series_type": series_type,
                "datatype": "csv"
            })
        elif indicator == "close_200_sma":
            data = _make_api_request("SMA", {
                "symbol": symbol,
                "interval": interval,
                "time_period": "200",
                "series_type": series_type,
                "datatype": "csv"
            })
        elif indicator == "close_10_ema":
            data = _make_api_request("EMA", {
                "symbol": symbol,
                "interval": interval,
                "time_period": "10",
                "series_type": series_type,
                "datatype": "csv"
            })
        elif indicator == "macd":
            data = _make_api_request("MACD", {
                "symbol": symbol,
                "interval": interval,
                "series_type": series_type,
                "datatype": "csv"
            })
        elif indicator == "macds":
            data = _make_api_request("MACD", {
                "symbol": symbol,
                "interval": interval,
                "series_type": series_type,
                "datatype": "csv"
            })
        elif indicator == "macdh":
            data = _make_api_request("MACD", {
                "symbol": symbol,
                "interval": interval,
                "series_type": series_type,
                "datatype": "csv"
            })
        elif indicator == "rsi":
            data = _make_api_request("RSI", {
                "symbol": symbol,
                "interval": interval,
                "time_period": str(time_period),
                "series_type": series_type,
                "datatype": "csv"
            })
        elif indicator in ["boll", "boll_ub", "boll_lb"]:
            data = _make_api_request("BBANDS", {
                "symbol": symbol,
                "interval": interval,
                "time_period": "20",
                "series_type": series_type,
                "datatype": "csv"
            })
        elif indicator == "atr":
            data = _make_api_request("ATR", {
                "symbol": symbol,
                "interval": interval,
                "time_period": str(time_period),
                "datatype": "csv"
            })
        elif indicator == "vwma":
            # Alpha Vantage 不直接提供 VWMA，这里返回说明信息
            # 真正实现时需要基于 OHLCV 原始数据自行计算
            return f"## {symbol} 的 VWMA（成交量加权移动平均）\n\nVWMA 的计算依赖 OHLCV 原始数据，Alpha Vantage API 不直接提供该指标。\n需要基于原始股价数据进行成交量加权平均计算。\n\n{indicator_descriptions.get('vwma', '暂无说明。')}"
        else:
            return f"错误：指标 {indicator} 尚未实现。"

        # 解析 CSV 并提取目标日期区间的数值
        lines = data.strip().split('\n')
        if len(lines) < 2:
            return f"错误：指标 {indicator} 没有返回数据。"

        # 解析表头和数据
        header = [col.strip() for col in lines[0].split(',')]
        try:
            date_col_idx = header.index('time')
        except ValueError:
            return f"错误：指标 {indicator} 的返回数据中找不到 'time' 列。当前可用列：{header}"

        # 将内部指标名映射到 Alpha Vantage CSV 返回中的实际列名
        col_name_map = {
            "macd": "MACD", "macds": "MACD_Signal", "macdh": "MACD_Hist",
            "boll": "Real Middle Band", "boll_ub": "Real Upper Band", "boll_lb": "Real Lower Band",
            "rsi": "RSI", "atr": "ATR", "close_10_ema": "EMA",
            "close_50_sma": "SMA", "close_200_sma": "SMA"
        }

        target_col_name = col_name_map.get(indicator)

        if not target_col_name:
            # 若没有显式映射，则默认取第二列
            value_col_idx = 1
        else:
            try:
                value_col_idx = header.index(target_col_name)
            except ValueError:
                return f"错误：指标 '{indicator}' 对应的列 '{target_col_name}' 未找到。当前可用列：{header}"

        result_data = []
        for line in lines[1:]:
            if not line.strip():
                continue
            values = line.split(',')
            if len(values) > value_col_idx:
                try:
                    date_str = values[date_col_idx].strip()
                    # 解析日期
                    date_dt = datetime.strptime(date_str, "%Y-%m-%d")

                    # 检查日期是否落在目标区间
                    if before <= date_dt <= curr_date_dt:
                        value = values[value_col_idx].strip()
                        result_data.append((date_dt, value))
                except (ValueError, IndexError):
                    continue

        # 按日期排序并格式化输出
        result_data.sort(key=lambda x: x[0])

        ind_string = ""
        for date_dt, value in result_data:
            ind_string += f"{date_dt.strftime('%Y-%m-%d')}: {value}\n"

        if not ind_string:
            ind_string = "指定日期区间内没有可用数据。\n"

        result_str = (
            f"## {indicator.upper()} 指标值（{before.strftime('%Y-%m-%d')} 至 {curr_date}）\n\n"
            + ind_string
            + "\n\n"
            + indicator_descriptions.get(indicator, "暂无说明。")
        )

        return result_str

    except Exception as e:
        print(f"获取 Alpha Vantage 指标 {indicator} 数据时出错：{e}")
        return f"获取 {indicator} 数据失败：{str(e)}"
