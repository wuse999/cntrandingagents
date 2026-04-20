

def create_conservative_debator(llm):
    def conservative_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        conservative_history = risk_debate_state.get("conservative_history", "")

        current_aggressive_response = risk_debate_state.get("current_aggressive_response", "")
        current_neutral_response = risk_debate_state.get("current_neutral_response", "")

        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        trader_decision = state["trader_investment_plan"]

        prompt = f"""你是一名保守型风险分析师，你的首要目标是保护资产、降低波动，并确保稳定可靠的增长。你优先考虑稳健、安全与风险缓释，会认真评估潜在损失、经济下行和市场波动。在评估交易员的决策或计划时，请批判性审视其中的高风险部分，指出该决策可能使机构暴露于哪些不必要风险，以及哪些更谨慎的替代方案更有利于长期收益。以下是交易员的决策：

{trader_decision}

你的任务是主动反驳激进分析师和中性分析师的论点，指出他们的看法在哪些地方忽略了潜在威胁，或没有把可持续性放在足够重要的位置。请直接回应他们的论点，并结合以下数据来源，构建一套支持低风险调整方案的有力论证：

市场研究报告：{market_research_report}
社交媒体情绪报告：{sentiment_report}
最新时事报告：{news_report}
公司基本面报告：{fundamentals_report}
当前对话历史：{history}。激进分析师上一轮回应：{current_aggressive_response}。中性分析师上一轮回应：{current_neutral_response}。如果其他立场暂时还没有回应，请直接基于现有数据提出你自己的论证。

请通过质疑他们的乐观预期、强调其忽略的潜在下行风险来展开交锋。请逐点回应他们的反驳，说明为什么保守立场最终才是保护机构资产最安全的路径。重点应放在辩论和批评其论证，以展示低风险策略相较于他们方案的优势。请用自然口语式表达输出，不要使用特殊格式。"""

        response = llm.invoke(prompt)

        argument = f"Conservative Analyst: {response.content}"

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "aggressive_history": risk_debate_state.get("aggressive_history", ""),
            "conservative_history": conservative_history + "\n" + argument,
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "Conservative",
            "current_aggressive_response": risk_debate_state.get(
                "current_aggressive_response", ""
            ),
            "current_conservative_response": argument,
            "current_neutral_response": risk_debate_state.get(
                "current_neutral_response", ""
            ),
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return conservative_node
