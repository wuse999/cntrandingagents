import os
from typing import Any, Optional

from langchain_openai import ChatOpenAI

from .base_client import BaseLLMClient, normalize_content
from .validators import validate_model


class NormalizedChatOpenAI(ChatOpenAI):
    """带有内容规范化输出的 ChatOpenAI。

    Responses API 会把内容以类型化块列表返回
    （reasoning、text 等）。这里将其规整为字符串，
    便于下游统一处理。
    """

    def invoke(self, input, config=None, **kwargs):
        return normalize_content(super().invoke(input, config, **kwargs))

# 从用户配置透传到 ChatOpenAI 的 kwargs
_PASSTHROUGH_KWARGS = (
    "timeout", "max_retries", "reasoning_effort",
    "api_key", "callbacks", "http_client", "http_async_client",
)

# 提供方基础 URL 与 API Key 环境变量
_PROVIDER_CONFIG = {
    "xai": ("https://api.x.ai/v1", "XAI_API_KEY"),
    "deepseek": ("https://api.deepseek.com", "DEEPSEEK_API_KEY"),
    "qwen": ("https://dashscope-intl.aliyuncs.com/compatible-mode/v1", "DASHSCOPE_API_KEY"),
    "glm": ("https://api.z.ai/api/paas/v4/", "ZHIPU_API_KEY"),
    "openrouter": ("https://openrouter.ai/api/v1", "OPENROUTER_API_KEY"),
    "ollama": ("http://localhost:11434/v1", None),
}


class OpenAIClient(BaseLLMClient):
    """适配 OpenAI、Ollama、OpenRouter 与 xAI 的客户端。

    对原生 OpenAI 模型，使用 Responses API（/v1/responses），
    以便在 GPT-4.1、GPT-5 等模型族上统一支持 reasoning_effort
    与函数工具。第三方兼容提供方（xAI、OpenRouter、Ollama）
    则使用标准 Chat Completions。
    """

    def __init__(
        self,
        model: str,
        base_url: Optional[str] = None,
        provider: str = "openai",
        **kwargs,
    ):
        super().__init__(model, base_url, **kwargs)
        self.provider = provider.lower()

    def get_llm(self) -> Any:
        """返回已配置好的 ChatOpenAI 实例。"""
        self.warn_if_unknown_model()
        llm_kwargs = {"model": self.model}

        # 提供方专属基础 URL 与鉴权
        if self.provider in _PROVIDER_CONFIG:
            base_url, api_key_env = _PROVIDER_CONFIG[self.provider]
            llm_kwargs["base_url"] = base_url
            if api_key_env:
                api_key = os.environ.get(api_key_env)
                if api_key:
                    llm_kwargs["api_key"] = api_key
            else:
                llm_kwargs["api_key"] = "ollama"
        elif self.base_url:
            llm_kwargs["base_url"] = self.base_url

        # 透传用户传入的 kwargs
        for key in _PASSTHROUGH_KWARGS:
            if key in self.kwargs:
                llm_kwargs[key] = self.kwargs[key]

        # 原生 OpenAI 使用 Responses API，以统一模型族行为。
        # 第三方兼容提供方继续使用 Chat Completions。
        if self.provider == "openai":
            llm_kwargs["use_responses_api"] = True

        return NormalizedChatOpenAI(**llm_kwargs)

    def validate_model(self) -> bool:
        """校验该提供方下的模型是否合法。"""
        return validate_model(self.provider, self.model)
