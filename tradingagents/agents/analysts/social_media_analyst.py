from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tradingagents.agents.utils.agent_utils import build_instrument_context, get_language_instruction, get_news
from tradingagents.dataflows.config import get_config


def create_social_media_analyst(llm):
    def social_media_analyst_node(state):
        current_date = state["trade_date"]
        instrument_context = build_instrument_context(state["company_of_interest"])

        tools = [
            get_news,
        ]

        system_message = (
            "你是一名社交媒体与公司相关新闻研究员/分析师，需要分析某家公司过去一周的社交媒体帖子、最新公司新闻和公众情绪。你会收到一家公司的名称，你的目标是在综合社交媒体舆情、每日情绪变化和近期公司新闻后，撰写一份完整且详细的长报告，说明这家公司当前状态对交易员和投资者的意义。请使用 `get_news(query, start_date, end_date)` 工具搜索公司相关新闻和社交媒体讨论，尽可能覆盖从社交媒体、情绪到新闻的各类来源。请基于证据给出具体、可执行的洞察，帮助交易员做出更明智的决策。"
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
            "sentiment_report": report,
        }

    return social_media_analyst_node
