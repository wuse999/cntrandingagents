

def create_bull_researcher(llm, memory):
    def bull_node(state) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bull_history = investment_debate_state.get("bull_history", "")

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

        prompt = f"""你是一名看多分析师，立场是支持投资这只股票。你的任务是建立一套有力、基于证据的论证，重点强调增长潜力、竞争优势和积极的市场信号。请充分利用提供的研究资料与数据，回应质疑并有效反驳看空观点。

重点关注以下方面：
- 增长潜力：突出公司的市场机会、收入前景与可扩展性。
- 竞争优势：强调独特产品、品牌优势或市场地位等因素。
- 积极指标：使用财务健康度、行业趋势和近期利好新闻作为证据。
- 对看空观点的反驳：基于具体数据与扎实推理，深入回应看空方疑虑，说明为什么看多立场更有说服力。
- 互动性：请以对话式风格展开论证，直接回应看空分析师的观点，体现真实辩论，而不是只罗列数据。

可用资料：
市场研究报告：{market_research_report}
社交媒体情绪报告：{sentiment_report}
最新时事新闻：{news_report}
公司基本面报告：{fundamentals_report}
辩论历史：{history}
上一轮看空观点：{current_response}
相似情景下的反思与经验教训：{past_memory_str}
请基于这些信息输出一段有说服力的看多论证，反驳看空方关切，并通过动态辩论展示看多立场的优势。你还必须结合这些反思，吸取过往失误与经验。
"""

        response = llm.invoke(prompt)

        argument = f"Bull Analyst: {response.content}"

        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bull_history": bull_history + "\n" + argument,
            "bear_history": investment_debate_state.get("bear_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bull_node
