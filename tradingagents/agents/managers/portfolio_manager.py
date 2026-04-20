from tradingagents.agents.utils.agent_utils import build_instrument_context, get_language_instruction


def create_portfolio_manager(llm, memory):
    def portfolio_manager_node(state) -> dict:

        instrument_context = build_instrument_context(state["company_of_interest"])

        history = state["risk_debate_state"]["history"]
        risk_debate_state = state["risk_debate_state"]
        market_research_report = state["market_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]
        sentiment_report = state["sentiment_report"]
        research_plan = state["investment_plan"]
        trader_plan = state["trader_investment_plan"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""你现在是投资组合经理，需要综合风险分析师们的辩论结果，并给出最终交易决定。

{instrument_context}

---

**评级刻度**（必须且只能选择一个，评级词请保留下列英文之一）：
- **BUY**：强烈看好，适合建仓或加仓
- **OVERWEIGHT**：前景偏积极，适合逐步提高仓位
- **HOLD**：维持现有仓位，暂不动作
- **UNDERWEIGHT**：降低敞口，可部分止盈或减仓
- **SELL**：退出持仓或避免入场

**上下文：**
- 研究经理的投资计划：**{research_plan}**
- 交易员的交易提案：**{trader_plan}**
- 过往决策中的经验教训：**{past_memory_str}**

**必须遵守的输出结构：**
1. **Rating**：明确写出 `BUY` / `OVERWEIGHT` / `HOLD` / `UNDERWEIGHT` / `SELL` 其中之一。
2. **Executive Summary**：简要行动方案，覆盖入场策略、仓位大小、关键风险位和时间周期。
3. **Investment Thesis**：结合分析师辩论与过往反思，给出详细论证。

---

**风险分析师辩论历史：**
{history}

---

请果断下结论，并确保每一个判断都能落到分析师提供的具体证据上。{get_language_instruction()}"""

        response = llm.invoke(prompt)

        new_risk_debate_state = {
            "judge_decision": response.content,
            "history": risk_debate_state["history"],
            "aggressive_history": risk_debate_state["aggressive_history"],
            "conservative_history": risk_debate_state["conservative_history"],
            "neutral_history": risk_debate_state["neutral_history"],
            "latest_speaker": "Judge",
            "current_aggressive_response": risk_debate_state["current_aggressive_response"],
            "current_conservative_response": risk_debate_state["current_conservative_response"],
            "current_neutral_response": risk_debate_state["current_neutral_response"],
            "count": risk_debate_state["count"],
        }

        return {
            "risk_debate_state": new_risk_debate_state,
            "final_trade_decision": response.content,
        }

    return portfolio_manager_node
