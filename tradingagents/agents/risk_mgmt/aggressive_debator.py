

def create_aggressive_debator(llm):
    def aggressive_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        aggressive_history = risk_debate_state.get("aggressive_history", "")

        current_conservative_response = risk_debate_state.get("current_conservative_response", "")
        current_neutral_response = risk_debate_state.get("current_neutral_response", "")

        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        trader_decision = state["trader_investment_plan"]

        prompt = f"""你是一名激进型风险分析师，你的职责是主动为高收益、高风险机会辩护，强调大胆策略与竞争优势。在评估交易员的决策或计划时，请重点聚焦其潜在上行空间、增长潜力与创新收益，即使这些机会伴随着更高风险。请使用提供的市场数据和情绪分析来强化你的论据，并挑战对立观点。你需要直接回应保守分析师和中性分析师提出的每一点，用数据驱动的反驳和有说服力的推理进行回击。请指出他们的谨慎是否错失了关键机会，或他们的假设是否过于保守。以下是交易员的决策：

{trader_decision}

你的任务是为交易员的决策构建一套有说服力的论证，通过质疑和批评保守与中性立场，说明为什么高收益视角才是更优路径。请把以下资料融入你的论证：

市场研究报告：{market_research_report}
社交媒体情绪报告：{sentiment_report}
最新时事报告：{news_report}
公司基本面报告：{fundamentals_report}
当前对话历史：{history}。保守分析师上一轮观点：{current_conservative_response}。中性分析师上一轮观点：{current_neutral_response}。如果其他立场暂时还没有回应，请直接基于现有数据提出你自己的论证。

请积极交锋，回应他们提出的具体顾虑，反驳其逻辑弱点，并强调承担风险如何帮助获取超越市场常态的收益。重点应放在辩论和说服，而不仅仅是罗列数据。请逐点挑战对方观点，以说明为何高风险策略才是最佳选择。请用自然口语式表达输出，不要使用特殊格式。"""

        response = llm.invoke(prompt)

        argument = f"Aggressive Analyst: {response.content}"

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "aggressive_history": aggressive_history + "\n" + argument,
            "conservative_history": risk_debate_state.get("conservative_history", ""),
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "Aggressive",
            "current_aggressive_response": argument,
            "current_conservative_response": risk_debate_state.get("current_conservative_response", ""),
            "current_neutral_response": risk_debate_state.get(
                "current_neutral_response", ""
            ),
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return aggressive_node
