from abc import ABC, abstractmethod
from typing import Any, Optional
import warnings


def normalize_content(response):
    """将 LLM 响应内容规范化为纯字符串。

    多个提供方（如 OpenAI Responses API、Google Gemini 3）会把内容
    以类型化块列表的形式返回，例如 [{'type': 'reasoning', ...},
    {'type': 'text', 'text': '...'}]。
    下游智能体期望 response.content 是字符串，因此这里会提取并拼接文本块，
    丢弃 reasoning/metadata 等非正文块。
    """
    content = response.content
    if isinstance(content, list):
        texts = [
            item.get("text", "") if isinstance(item, dict) and item.get("type") == "text"
            else item if isinstance(item, str) else ""
            for item in content
        ]
        response.content = "\n".join(t for t in texts if t)
    return response


class BaseLLMClient(ABC):
    """LLM 客户端的抽象基类。"""

    def __init__(self, model: str, base_url: Optional[str] = None, **kwargs):
        self.model = model
        self.base_url = base_url
        self.kwargs = kwargs

    def get_provider_name(self) -> str:
        """返回告警信息中使用的提供方名称。"""
        provider = getattr(self, "provider", None)
        if provider:
            return str(provider)
        return self.__class__.__name__.removesuffix("Client").lower()

    def warn_if_unknown_model(self) -> None:
        """当模型不在该提供方的已知列表中时给出告警。"""
        if self.validate_model():
            return

        warnings.warn(
            (
                f"模型 '{self.model}' 不在提供方 "
                f"'{self.get_provider_name()}' 的已知模型列表中，仍将继续执行。"
            ),
            RuntimeWarning,
            stacklevel=2,
        )

    @abstractmethod
    def get_llm(self) -> Any:
        """返回已配置好的 LLM 实例。"""
        pass

    @abstractmethod
    def validate_model(self) -> bool:
        """校验该客户端是否支持当前模型。"""
        pass
