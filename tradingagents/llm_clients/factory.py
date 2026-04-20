from typing import Optional

from .base_client import BaseLLMClient
from .openai_client import OpenAIClient
from .anthropic_client import AnthropicClient
from .google_client import GoogleClient
from .azure_client import AzureOpenAIClient

# 使用 OpenAI 兼容 Chat Completions API 的提供方
_OPENAI_COMPATIBLE = (
    "openai", "xai", "deepseek", "qwen", "glm", "ollama", "openrouter",
)


def create_llm_client(
    provider: str,
    model: str,
    base_url: Optional[str] = None,
    **kwargs,
) -> BaseLLMClient:
    """为指定提供方创建 LLM 客户端。

    参数：
        provider: LLM 提供方名称
        model: 模型名称/标识符
        base_url: 可选的 API 基础地址
        **kwargs: 其他提供方专属参数

    返回：
        BaseLLMClient: 已配置的客户端实例

    异常：
        ValueError: 当 provider 不受支持时抛出
    """
    provider_lower = provider.lower()

    if provider_lower in _OPENAI_COMPATIBLE:
        return OpenAIClient(model, base_url, provider=provider_lower, **kwargs)

    if provider_lower == "anthropic":
        return AnthropicClient(model, base_url, **kwargs)

    if provider_lower == "google":
        return GoogleClient(model, base_url, **kwargs)

    if provider_lower == "azure":
        return AzureOpenAIClient(model, base_url, **kwargs)

    raise ValueError(f"不支持的 LLM 提供方：{provider}")
