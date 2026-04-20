import os
import requests
import pandas as pd
import json
from datetime import datetime
from io import StringIO

API_BASE_URL = "https://www.alphavantage.co/query"

def get_api_key() -> str:
    """从环境变量中读取 Alpha Vantage API Key。"""
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        raise ValueError("未设置环境变量 ALPHA_VANTAGE_API_KEY。")
    return api_key

def format_datetime_for_api(date_input) -> str:
    """将多种日期格式转换为 Alpha Vantage API 所需的 YYYYMMDDTHHMM 格式。"""
    if isinstance(date_input, str):
        # 如果已经是正确格式，直接返回
        if len(date_input) == 13 and 'T' in date_input:
            return date_input
        # 尝试解析常见日期格式
        try:
            dt = datetime.strptime(date_input, "%Y-%m-%d")
            return dt.strftime("%Y%m%dT0000")
        except ValueError:
            try:
                dt = datetime.strptime(date_input, "%Y-%m-%d %H:%M")
                return dt.strftime("%Y%m%dT%H%M")
            except ValueError:
                raise ValueError(f"不支持的日期格式：{date_input}")
    elif isinstance(date_input, datetime):
        return date_input.strftime("%Y%m%dT%H%M")
    else:
        raise ValueError(f"日期必须是字符串或 datetime 对象，当前收到：{type(date_input)}")

class AlphaVantageRateLimitError(Exception):
    """当 Alpha Vantage API 触发限流时抛出的异常。"""
    pass

def _make_api_request(function_name: str, params: dict) -> dict | str:
    """执行 API 请求并处理返回结果的辅助函数。

    异常：
        AlphaVantageRateLimitError: 当 API 达到速率限制时抛出
    """
    # 复制一份参数，避免修改原始对象
    api_params = params.copy()
    api_params.update({
        "function": function_name,
        "apikey": get_api_key(),
        "source": "trading_agents",
    })
    
    # 如果参数或全局变量中带有 entitlement，则一并处理
    current_entitlement = globals().get('_current_entitlement')
    entitlement = api_params.get("entitlement") or current_entitlement
    
    if entitlement:
        api_params["entitlement"] = entitlement
    elif "entitlement" in api_params:
        # 若 entitlement 为空，则移除该参数
        api_params.pop("entitlement", None)
    
    response = requests.get(API_BASE_URL, params=api_params)
    response.raise_for_status()

    response_text = response.text
    
    # 检查返回是否为 JSON（错误响应通常为 JSON）
    try:
        response_json = json.loads(response_text)
        # 检查是否为限流错误
        if "Information" in response_json:
            info_message = response_json["Information"]
            if "rate limit" in info_message.lower() or "api key" in info_message.lower():
                raise AlphaVantageRateLimitError(f"Alpha Vantage 触发限流：{info_message}")
    except json.JSONDecodeError:
        # 返回不是 JSON（通常意味着 CSV 数据），属于正常情况
        pass

    return response_text



def _filter_csv_by_date_range(csv_data: str, start_date: str, end_date: str) -> str:
    """
    过滤 CSV 数据，只保留指定日期区间内的行。

    参数：
        csv_data: 来自 Alpha Vantage API 的 CSV 字符串
        start_date: 开始日期，格式为 yyyy-mm-dd
        end_date: 结束日期，格式为 yyyy-mm-dd

    返回：
        过滤后的 CSV 字符串
    """
    if not csv_data or csv_data.strip() == "":
        return csv_data

    try:
        # 解析 CSV 数据
        df = pd.read_csv(StringIO(csv_data))

        # 默认第一列为日期列（timestamp）
        date_col = df.columns[0]
        df[date_col] = pd.to_datetime(df[date_col])

        # 按日期区间过滤
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)

        filtered_df = df[(df[date_col] >= start_dt) & (df[date_col] <= end_dt)]

        # 转回 CSV 字符串
        return filtered_df.to_csv(index=False)

    except Exception as e:
        # 如果过滤失败，则回退到原始数据并打印警告
        print(f"警告：按日期区间过滤 CSV 数据失败：{e}")
        return csv_data
