from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tradingagents.agents.utils.agent_utils import (
    build_instrument_context,
    get_global_news,
    get_language_instruction,
    get_news,
)
from tradingagents.dataflows.config import get_config


def create_news_analyst(llm):
    def news_analyst_node(state):
        current_date = state["trade_date"]
        instrument_context = build_instrument_context(state["company_of_interest"])

        tools = [
            get_news,
            get_global_news,
        ]

        system_message = (
            "你是一名新闻研究员，需要分析过去一周的最新新闻与趋势。请撰写一份完整报告，概述当前与交易和宏观经济相关的世界状态。可使用工具 `get_news(query, start_date, end_date)` 搜索公司级或定向新闻，也可使用 `get_global_news(curr_date, look_back_days, limit)` 获取更广泛的宏观经济新闻。请基于证据给出具体、可执行的洞察，帮助交易员做出更明智的决策。"
            + """ 请务必在报告末尾追加一个 Markdown 表格，用于整理报告中的关键要点，确保结构清晰、便于阅读。"""
            + get_language_instruction()
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "你是一名乐于协作的 AI 助手，正在与其他助手共同完成任务。"
                    " 请使用已提供的工具持续推进问题求解。"
                    " 如果你无法独立完整回答，也没关系；其他拥有不同工具的助手会接续你的工作。"
                    " 请先完成你当前能完成的部分并推动任务前进。"
                    " 如果你或任何其他助手已经得出 FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** 或最终可交付结果，"
                    " 请在回复开头保留并输出 FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL**，让团队知道可以停止。"
                    " 你可以使用以下工具：{tool_names}。\n{system_message}"
                    "供你参考，当前日期为 {current_date}。{instrument_context}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(instrument_context=instrument_context)

        chain = prompt | llm.bind_tools(tools)
        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "news_report": report,
        }

    return news_analyst_node
