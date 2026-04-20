from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tradingagents.agents.utils.agent_utils import (
    build_instrument_context,
    get_indicators,
    get_language_instruction,
    get_stock_data,
)
from tradingagents.dataflows.config import get_config


def create_market_analyst(llm):

    def market_analyst_node(state):
        current_date = state["trade_date"]
        instrument_context = build_instrument_context(state["company_of_interest"])

        tools = [
            get_stock_data,
            get_indicators,
        ]

        system_message = (
            """你是一名交易分析助手，需要分析金融市场。你的职责是从下列指标中，为当前市场环境或交易策略挑选**最相关的指标**。目标是在不重复的前提下，最多选择 **8 个**能够提供互补洞察的指标。各类别及对应指标如下：

移动平均类：
- close_50_sma: 50 SMA：中期趋势指标。用途：识别趋势方向，并可作为动态支撑/阻力。提示：它对价格有滞后性，最好搭配更快的指标获得更及时的信号。
- close_200_sma: 200 SMA：长期趋势基准。用途：确认整体市场趋势，并识别金叉/死叉结构。提示：反应较慢，更适合战略级趋势确认，而非频繁入场。
- close_10_ema: 10 EMA：响应迅速的短期均线。用途：捕捉动量快速变化与潜在入场点。提示：震荡市场中噪声较多，宜结合更长期均线过滤假信号。

MACD 相关：
- macd: MACD：通过 EMA 差值计算动量。用途：观察交叉与背离，识别趋势变化。提示：在低波动或横盘市场中，需结合其他指标确认。
- macds: MACD 信号线：MACD 线的平滑 EMA。用途：配合 MACD 线交叉触发交易信号。提示：应作为更完整策略的一部分，避免误报。
- macdh: MACD 柱状图：展示 MACD 线与信号线之间的差距。用途：可视化动量强弱，并更早发现背离。提示：波动可能较大，快速市场中建议搭配额外过滤条件。

动量指标：
- rsi: RSI：衡量动量，用于识别超买/超卖。用途：应用 70/30 阈值，并观察背离以提示反转。提示：在强趋势中 RSI 可能长时间处于极值区间，需始终结合趋势分析。

波动率指标：
- boll: 布林带中轨：本质是 20 日 SMA。用途：作为价格运动的动态基准。提示：结合上下轨使用，更适合识别突破或反转。
- boll_ub: 布林带上轨：通常位于中轨上方 2 个标准差。用途：提示潜在超买区域与突破区间。提示：需结合其他工具确认，强趋势中价格可能沿上轨运行。
- boll_lb: 布林带下轨：通常位于中轨下方 2 个标准差。用途：提示潜在超卖区域。提示：应结合其他分析，避免误判反转。
- atr: ATR：通过平均真实波幅衡量波动率。用途：设定止损水平，并根据当前波动率调整仓位规模。提示：它属于滞后型指标，应纳入更完整的风控框架中使用。

成交量类指标：
- vwma: VWMA：按成交量加权的移动平均。用途：将价格行为与成交量结合，用于确认趋势。提示：成交量突增可能造成偏差，建议配合其他量能分析一起使用。

- 请选择能提供多样且互补信息的指标，避免冗余（例如不要同时选择 rsi 与 stochrsi）。同时请简要说明这些指标为什么适合当前市场语境。调用工具时，必须使用上面列出的精确指标名称，因为它们是已定义参数，否则调用会失败。请务必先调用 get_stock_data 获取生成指标所需的 CSV，再使用 get_indicators 针对具体指标名逐项分析。请撰写一份非常细致、富有层次的趋势报告，并基于证据提供具体、可执行的洞察，帮助交易员做出更明智的决策。"""
            + """ 请务必在报告末尾追加一个 Markdown 表格，用于整理报告中的关键要点，确保结构清晰、便于阅读。"""
            + get_language_instruction()
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "你是一名乐于协作的 AI 助手，正在与其他助手共同完成任务。"
                    " 请使用已提供的工具持续推进问题求解。"
                    " 如果你无法独立完整回答，也没关系；其他拥有不同工具的助手会接续你的工作。"
                    " 请先完成你当前能完成的部分并推动任务前进。"
                    " 如果你或任何其他助手已经得出 FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** 或最终可交付结果，"
                    " 请在回复开头保留并输出 FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL**，让团队知道可以停止。"
                    " 你可以使用以下工具：{tool_names}。\n{system_message}"
                    "供你参考，当前日期为 {current_date}。{instrument_context}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(instrument_context=instrument_context)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "market_report": report,
        }

    return market_analyst_node
