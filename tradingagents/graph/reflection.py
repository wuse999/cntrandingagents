# 图复盘逻辑

from typing import Any, Dict


class Reflector:
    """负责对决策进行复盘并更新记忆。"""

    def __init__(self, quick_thinking_llm: Any):
        """使用一个 LLM 初始化复盘器。"""
        self.quick_thinking_llm = quick_thinking_llm
        self.reflection_system_prompt = self._get_reflection_prompt()

    def _get_reflection_prompt(self) -> str:
        """获取用于复盘的系统提示词。"""
        return """
你是一名资深金融分析师，需要复盘交易决策/分析并给出一份完整、分步骤的分析。
你的目标是对投资决策给出细致洞察，并指出可改进之处。请严格遵守以下要求：

1. 推理：
   - 对每一项交易决策，判断其正确还是错误。正确决策会提升收益，错误决策则会带来相反效果。
   - 分析每次成功或失误的成因，至少考虑：
     - 市场情报
     - 技术指标
     - 技术信号
     - 价格走势分析
     - 整体市场数据分析
     - 新闻分析
     - 社交媒体与情绪分析
     - 基本面数据分析
   - 说明这些因素在决策过程中的重要性权重。

2. 改进：
   - 对任何错误决策，提出可提升收益的修正方案。
   - 给出详细的纠正动作或改进建议，包括具体建议（例如在某个日期将 HOLD 改为 BUY）。

3. 总结：
   - 总结成功与失误中得到的经验教训。
   - 说明这些经验如何迁移到未来的交易情景，并将相似场景联系起来，以复用已获得的知识。

4. 检索句：
   - 从总结中提炼关键洞察，压缩成一句不超过 1000 tokens 的简洁语句。
   - 确保这句话能抓住核心经验与推理，便于后续快速检索。

请严格遵守这些说明，确保输出详细、准确、可执行。你还会获得关于市场的客观描述，包括价格走势、技术指标、新闻和情绪视角，以便为分析补充背景。
"""

    def _extract_current_situation(self, current_state: Dict[str, Any]) -> str:
        """从状态中提取当前市场情景。"""
        curr_market_report = current_state["market_report"]
        curr_sentiment_report = current_state["sentiment_report"]
        curr_news_report = current_state["news_report"]
        curr_fundamentals_report = current_state["fundamentals_report"]

        return f"{curr_market_report}\n\n{curr_sentiment_report}\n\n{curr_news_report}\n\n{curr_fundamentals_report}"

    def _reflect_on_component(
        self, component_type: str, report: str, situation: str, returns_losses
    ) -> str:
        """为某个组件生成复盘内容。"""
        messages = [
            ("system", self.reflection_system_prompt),
            (
                "human",
                f"收益结果：{returns_losses}\n\n分析/决策内容：{report}\n\n供参考的客观市场报告：{situation}",
            ),
        ]

        result = self.quick_thinking_llm.invoke(messages).content
        return result

    def reflect_bull_researcher(self, current_state, returns_losses, bull_memory):
        """复盘看多研究员的分析并更新记忆。"""
        situation = self._extract_current_situation(current_state)
        bull_debate_history = current_state["investment_debate_state"]["bull_history"]

        result = self._reflect_on_component(
            "BULL", bull_debate_history, situation, returns_losses
        )
        bull_memory.add_situations([(situation, result)])

    def reflect_bear_researcher(self, current_state, returns_losses, bear_memory):
        """复盘看空研究员的分析并更新记忆。"""
        situation = self._extract_current_situation(current_state)
        bear_debate_history = current_state["investment_debate_state"]["bear_history"]

        result = self._reflect_on_component(
            "BEAR", bear_debate_history, situation, returns_losses
        )
        bear_memory.add_situations([(situation, result)])

    def reflect_trader(self, current_state, returns_losses, trader_memory):
        """复盘交易员的决策并更新记忆。"""
        situation = self._extract_current_situation(current_state)
        trader_decision = current_state["trader_investment_plan"]

        result = self._reflect_on_component(
            "TRADER", trader_decision, situation, returns_losses
        )
        trader_memory.add_situations([(situation, result)])

    def reflect_invest_judge(self, current_state, returns_losses, invest_judge_memory):
        """复盘投资裁决者的决定并更新记忆。"""
        situation = self._extract_current_situation(current_state)
        judge_decision = current_state["investment_debate_state"]["judge_decision"]

        result = self._reflect_on_component(
            "INVEST JUDGE", judge_decision, situation, returns_losses
        )
        invest_judge_memory.add_situations([(situation, result)])

    def reflect_portfolio_manager(self, current_state, returns_losses, portfolio_manager_memory):
        """复盘投资组合经理的决定并更新记忆。"""
        situation = self._extract_current_situation(current_state)
        judge_decision = current_state["risk_debate_state"]["judge_decision"]

        result = self._reflect_on_component(
            "PORTFOLIO MANAGER", judge_decision, situation, returns_losses
        )
        portfolio_manager_memory.add_situations([(situation, result)])
