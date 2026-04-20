import functools

from tradingagents.agents.utils.agent_utils import build_instrument_context


def create_trader(llm, memory):
    def trader_node(state, name):
        company_name = state["company_of_interest"]
        instrument_context = build_instrument_context(company_name)
        investment_plan = state["investment_plan"]
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        if past_memories:
            for i, rec in enumerate(past_memories, 1):
                past_memory_str += rec["recommendation"] + "\n\n"
        else:
            past_memory_str = "未找到过往相似记忆。"

        context = {
            "role": "user",
            "content": f"基于一组分析师的综合研究，这里有一份为 {company_name} 定制的投资计划。{instrument_context} 这份计划整合了当前技术面趋势、宏观经济指标和社交媒体情绪等洞察。请将这份计划作为评估下一步交易决策的基础。\n\n拟定投资计划：{investment_plan}\n\n请结合这些洞察做出审慎、具策略性的交易决定。",
        }

        messages = [
            {
                "role": "system",
                "content": f"""你是一名交易智能体，需要分析市场数据并做出投资决策。请基于你的分析，明确给出买入、卖出或持有建议。结尾必须给出坚定结论，并始终以 'FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL**' 结束，以确认你的建议。请吸收以往交易决策中的经验教训来强化本次分析。以下是你在相似情景中的反思与学习总结：{past_memory_str}""",
            },
            context,
        ]

        result = llm.invoke(messages)

        return {
            "messages": [result],
            "trader_investment_plan": result.content,
            "sender": name,
        }

    return functools.partial(trader_node, name="Trader")
