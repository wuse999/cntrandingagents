from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import MessagesState


# 研究团队状态
class InvestDebateState(TypedDict):
    bull_history: Annotated[
        str, "看多方对话历史"
    ]  # 看多方对话历史
    bear_history: Annotated[
        str, "看空方对话历史"
    ]  # 看空方对话历史
    history: Annotated[str, "完整对话历史"]  # 完整对话历史
    current_response: Annotated[str, "最新回复"]  # 最新回复
    judge_decision: Annotated[str, "裁决者最终决定"]  # 裁决者最终决定
    count: Annotated[int, "当前对话长度"]  # 当前对话长度


# 风险管理团队状态
class RiskDebateState(TypedDict):
    aggressive_history: Annotated[
        str, "激进分析师对话历史"
    ]  # 激进分析师对话历史
    conservative_history: Annotated[
        str, "保守分析师对话历史"
    ]  # 保守分析师对话历史
    neutral_history: Annotated[
        str, "中性分析师对话历史"
    ]  # 中性分析师对话历史
    history: Annotated[str, "完整对话历史"]  # 完整对话历史
    latest_speaker: Annotated[str, "最后发言的分析师"]
    current_aggressive_response: Annotated[
        str, "激进分析师的最新回复"
    ]  # 激进分析师的最新回复
    current_conservative_response: Annotated[
        str, "保守分析师的最新回复"
    ]  # 保守分析师的最新回复
    current_neutral_response: Annotated[
        str, "中性分析师的最新回复"
    ]  # 中性分析师的最新回复
    judge_decision: Annotated[str, "裁决者决定"]
    count: Annotated[int, "当前对话长度"]  # 当前对话长度


class AgentState(MessagesState):
    company_of_interest: Annotated[str, "当前关注并准备交易的公司"]
    trade_date: Annotated[str, "当前模拟交易日期"]

    sender: Annotated[str, "发送这条消息的智能体"]

    # 研究阶段
    market_report: Annotated[str, "市场分析师报告"]
    sentiment_report: Annotated[str, "社交媒体分析师报告"]
    news_report: Annotated[
        str, "新闻分析师关于当前时事与宏观环境的报告"
    ]
    fundamentals_report: Annotated[str, "基本面分析师报告"]

    # 研究团队讨论阶段
    investment_debate_state: Annotated[
        InvestDebateState, "是否投资这一议题的当前辩论状态"
    ]
    investment_plan: Annotated[str, "研究经理生成的投资计划"]

    trader_investment_plan: Annotated[str, "交易员生成的交易方案"]

    # 风险管理团队讨论阶段
    risk_debate_state: Annotated[
        RiskDebateState, "风险评估辩论的当前状态"
    ]
    final_trade_decision: Annotated[str, "风险分析团队给出的最终交易决定"]
