
from tradingagents.agents.utils.agent_utils import build_instrument_context


def create_research_manager(llm, memory):
    def research_manager_node(state) -> dict:
        instrument_context = build_instrument_context(state["company_of_interest"])
        history = state["investment_debate_state"].get("history", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        investment_debate_state = state["investment_debate_state"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""你现在扮演投资组合经理兼辩论主持人，需要批判性地评估这一轮辩论，并给出明确结论：支持看空分析师、支持看多分析师，或者只有在论据足够充分时才选择 Hold。

请简洁总结双方的关键观点，重点关注最有说服力的证据与推理。你的建议必须清晰、可执行，结论应明确指向 Buy、Sell 或 Hold。不要仅因为双方都有道理就默认选择 Hold；请基于辩论中最强的论据做出立场鲜明的判断。

此外，你还需要为交易员制定一份详细的投资计划，其中应包括：

你的建议：基于最有说服力论据得出的明确立场。
结论依据：解释这些论据为何会导向你的判断。
策略动作：落实该建议的具体执行步骤。
同时请结合你在相似情景中的过往失误与反思，用这些经验来修正本次决策方式，确保你在持续学习与改进。请以自然对话式口吻输出，不要使用特殊格式。

以下是你过去的错误反思：
\"{past_memory_str}\"

{instrument_context}

以下是本轮辩论：
辩论历史：
{history}"""
        response = llm.invoke(prompt)

        new_investment_debate_state = {
            "judge_decision": response.content,
            "history": investment_debate_state.get("history", ""),
            "bear_history": investment_debate_state.get("bear_history", ""),
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": response.content,
            "count": investment_debate_state["count"],
        }

        return {
            "investment_debate_state": new_investment_debate_state,
            "investment_plan": response.content,
        }

    return research_manager_node
