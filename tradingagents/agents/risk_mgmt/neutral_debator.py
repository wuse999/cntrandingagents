

def create_neutral_debator(llm):
    def neutral_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        neutral_history = risk_debate_state.get("neutral_history", "")

        current_aggressive_response = risk_debate_state.get("current_aggressive_response", "")
        current_conservative_response = risk_debate_state.get("current_conservative_response", "")

        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        trader_decision = state["trader_investment_plan"]

        prompt = f"""你是一名中性风险分析师，你的职责是提供平衡视角，同时权衡交易员决策或计划的潜在收益与风险。你强调均衡方法，在评估利弊时也会纳入更广泛的市场趋势、潜在经济变化和分散化策略。以下是交易员的决策：

{trader_decision}

你的任务是同时挑战激进分析师和保守分析师，指出两种视角分别在哪些地方过于乐观或过于谨慎。请利用以下资料，为一种中等风险、可持续的调整方案提供支撑：

市场研究报告：{market_research_report}
社交媒体情绪报告：{sentiment_report}
最新时事报告：{news_report}
公司基本面报告：{fundamentals_report}
当前对话历史：{history}。激进分析师上一轮回应：{current_aggressive_response}。保守分析师上一轮回应：{current_conservative_response}。如果其他立场暂时还没有回应，请直接基于现有数据提出你自己的论证。

请积极交锋，批判性分析双方立场，指出激进与保守论证中的弱点，从而为更平衡的方法辩护。请逐点回应他们的观点，说明中等风险策略如何兼顾增长潜力与风险控制，既避免极端波动，又保留上行机会。重点应放在辩论而非单纯呈现数据，目标是证明平衡视角更可能带来可靠结果。请用自然口语式表达输出，不要使用特殊格式。"""

        response = llm.invoke(prompt)

        argument = f"Neutral Analyst: {response.content}"

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "aggressive_history": risk_debate_state.get("aggressive_history", ""),
            "conservative_history": risk_debate_state.get("conservative_history", ""),
            "neutral_history": neutral_history + "\n" + argument,
            "latest_speaker": "Neutral",
            "current_aggressive_response": risk_debate_state.get(
                "current_aggressive_response", ""
            ),
            "current_conservative_response": risk_debate_state.get("current_conservative_response", ""),
            "current_neutral_response": argument,
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return neutral_node
