# 图信号处理

from typing import Any


class SignalProcessor:
    """处理交易信号并提取可执行决策。"""

    def __init__(self, quick_thinking_llm: Any):
        """使用一个 LLM 初始化信号处理器。"""
        self.quick_thinking_llm = quick_thinking_llm

    def process_signal(self, full_signal: str) -> str:
        """
        处理完整交易信号并提取核心决策。

        参数：
            full_signal: 完整的交易信号文本

        返回：
            提取出的评级（BUY、OVERWEIGHT、HOLD、UNDERWEIGHT 或 SELL）
        """
        messages = [
            (
                "system",
                "你是一名高效助手，需要从分析师报告中提取交易决定。"
                "请将评级精确提取为以下五者之一：BUY、OVERWEIGHT、HOLD、UNDERWEIGHT、SELL。"
                "只输出单个评级词，不要输出任何其他内容。",
            ),
            ("human", full_signal),
        ]

        return self.quick_thinking_llm.invoke(messages).content
