

def create_bear_researcher(llm, memory):
    def bear_node(state) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bear_history = investment_debate_state.get("bear_history", "")

        current_response = investment_debate_state.get("current_response", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""你是一名看空分析师，立场是反对投资这只股票。你的目标是提出一套推理严谨的论证，重点强调风险、挑战和负面指标。请充分利用提供的研究资料与数据，挖掘潜在下行风险，并有效反驳看多观点。

重点关注以下方面：

- 风险与挑战：突出市场饱和、财务不稳定、宏观经济威胁等可能拖累股价表现的因素。
- 竞争弱点：强调市场地位偏弱、创新能力下滑或竞争对手压力等脆弱点。
- 负面指标：使用财务数据、市场趋势或近期利空新闻支撑你的判断。
- 对看多观点的反驳：基于具体数据与扎实推理，揭示看多论证中的薄弱点或过度乐观假设。
- 互动性：请以对话式风格展开论证，直接回应看多分析师的观点，体现真实辩论，而不是只罗列事实。

可用资料：

市场研究报告：{market_research_report}
社交媒体情绪报告：{sentiment_report}
最新时事新闻：{news_report}
公司基本面报告：{fundamentals_report}
辩论历史：{history}
上一轮看多观点：{current_response}
相似情景下的反思与经验教训：{past_memory_str}
请基于这些信息输出一段有说服力的看空论证，反驳看多方主张，并通过动态辩论展示投资这只股票所面临的风险与弱点。你还必须结合这些反思，吸取过往失误与经验。
"""

        response = llm.invoke(prompt)

        argument = f"Bear Analyst: {response.content}"

        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bear_history": bear_history + "\n" + argument,
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bear_node
