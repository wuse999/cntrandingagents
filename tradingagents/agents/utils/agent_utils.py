from langchain_core.messages import HumanMessage, RemoveMessage

# 从拆分后的工具模块中导入工具
from tradingagents.agents.utils.core_stock_tools import (
    get_stock_data
)
from tradingagents.agents.utils.technical_indicators_tools import (
    get_indicators
)
from tradingagents.agents.utils.fundamental_data_tools import (
    get_fundamentals,
    get_balance_sheet,
    get_cashflow,
    get_income_statement
)
from tradingagents.agents.utils.news_data_tools import (
    get_news,
    get_insider_transactions,
    get_global_news
)


def get_language_instruction() -> str:
    """返回与当前输出语言配置对应的提示词指令。

    当输出语言为英文（默认值）时返回空字符串，以避免额外消耗 token。
    仅对显式调用该辅助函数的智能体生效；其他节点使用各自固定提示词。
    """
    from tradingagents.dataflows.config import get_config
    lang = get_config().get("output_language", "English")
    if lang.strip().lower() == "english":
        return ""
    return f" 请使用{lang}完整输出你的全部回复。"


def build_instrument_context(ticker: str) -> str:
    """描述精确的交易标的，确保智能体保留带交易所后缀的代码。"""
    return (
        f"需要分析的交易标的是 `{ticker}`。"
        "在每一次工具调用、报告和交易建议中都必须使用这个精确代码，"
        "并保留交易所后缀（例如 `.TO`、`.L`、`.HK`、`.T`）。"
    )

def create_msg_delete():
    def delete_messages(state):
        """清空消息，并为 Anthropic 兼容性补充占位消息。"""
        messages = state["messages"]

        # 移除全部历史消息
        removal_operations = [RemoveMessage(id=m.id) for m in messages]

        # 添加最小占位消息
        placeholder = HumanMessage(content="Continue")

        return {"messages": removal_operations + [placeholder]}

    return delete_messages


        
