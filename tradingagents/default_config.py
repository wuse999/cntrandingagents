import os

_TRADINGAGENTS_HOME = os.path.join(os.path.expanduser("~"), ".tradingagents")

DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", os.path.join(_TRADINGAGENTS_HOME, "logs")),
    "data_cache_dir": os.getenv("TRADINGAGENTS_CACHE_DIR", os.path.join(_TRADINGAGENTS_HOME, "cache")),
    # LLM 设置
    "llm_provider": "openai",
    "deep_think_llm": "gpt-5.4",
    "quick_think_llm": "gpt-5.4-mini",
    "backend_url": "https://api.openai.com/v1",
    # 各提供方专属的 Thinking / Reasoning 配置
    "google_thinking_level": None,      # "high", "minimal" 等
    "openai_reasoning_effort": None,    # "medium", "high", "low"
    "anthropic_effort": None,           # "high", "medium", "low"
    # 输出语言配置，主要作用于显式追加语言指令的节点
    "output_language": "English",
    # 辩论与讨论轮次设置
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,
    # 数据供应商配置
    # 类别级配置（该类别下所有工具的默认供应商）
    "data_vendors": {
        "core_stock_apis": "yfinance",       # 可选：alpha_vantage、yfinance
        "technical_indicators": "yfinance",  # 可选：alpha_vantage、yfinance
        "fundamental_data": "yfinance",      # 可选：alpha_vantage、yfinance
        "news_data": "yfinance",             # 可选：alpha_vantage、yfinance
    },
    # 工具级配置（优先级高于类别级配置）
    "tool_vendors": {
        # 示例："get_stock_data": "alpha_vantage"  # 覆盖类别默认配置
    },
}
