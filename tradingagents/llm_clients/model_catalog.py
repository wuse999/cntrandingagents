"""供 CLI 选择与校验共用的模型目录。"""

from __future__ import annotations

from typing import Dict, List, Tuple

ModelOption = Tuple[str, str]
ProviderModeOptions = Dict[str, Dict[str, List[ModelOption]]]


MODEL_OPTIONS: ProviderModeOptions = {
    "openai": {
        "quick": [
            ("GPT-5.4 Mini - 快速，代码与工具能力强", "gpt-5.4-mini"),
            ("GPT-5.4 Nano - 最低成本，适合高并发任务", "gpt-5.4-nano"),
            ("GPT-5.4 - 最新前沿模型，1M 上下文", "gpt-5.4"),
            ("GPT-4.1 - 最强非推理模型", "gpt-4.1"),
        ],
        "deep": [
            ("GPT-5.4 - 最新前沿模型，1M 上下文", "gpt-5.4"),
            ("GPT-5.2 - 推理强，性价比高", "gpt-5.2"),
            ("GPT-5.4 Mini - 快速，代码与工具能力强", "gpt-5.4-mini"),
            ("GPT-5.4 Pro - 能力最强，成本较高（每 1M tokens 为 $30/$180）", "gpt-5.4-pro"),
        ],
    },
    "anthropic": {
        "quick": [
            ("Claude Sonnet 4.6 - 速度与智能平衡最佳", "claude-sonnet-4-6"),
            ("Claude Haiku 4.5 - 很快，接近即时响应", "claude-haiku-4-5"),
            ("Claude Sonnet 4.5 - 适合代理与编码", "claude-sonnet-4-5"),
        ],
        "deep": [
            ("Claude Opus 4.6 - 智能最强，适合代理与编码", "claude-opus-4-6"),
            ("Claude Opus 4.5 - 高端档，智能上限高", "claude-opus-4-5"),
            ("Claude Sonnet 4.6 - 速度与智能平衡最佳", "claude-sonnet-4-6"),
            ("Claude Sonnet 4.5 - 适合代理与编码", "claude-sonnet-4-5"),
        ],
    },
    "google": {
        "quick": [
            ("Gemini 3 Flash - 新一代高速模型", "gemini-3-flash-preview"),
            ("Gemini 2.5 Flash - 平衡且稳定", "gemini-2.5-flash"),
            ("Gemini 3.1 Flash Lite - 成本效率最高", "gemini-3.1-flash-lite-preview"),
            ("Gemini 2.5 Flash Lite - 快速且低成本", "gemini-2.5-flash-lite"),
        ],
        "deep": [
            ("Gemini 3.1 Pro - 推理优先，适合复杂工作流", "gemini-3.1-pro-preview"),
            ("Gemini 3 Flash - 新一代高速模型", "gemini-3-flash-preview"),
            ("Gemini 2.5 Pro - 稳定的专业版模型", "gemini-2.5-pro"),
            ("Gemini 2.5 Flash - 平衡且稳定", "gemini-2.5-flash"),
        ],
    },
    "xai": {
        "quick": [
            ("Grok 4.1 Fast（非推理）- 速度优化，2M 上下文", "grok-4-1-fast-non-reasoning"),
            ("Grok 4 Fast（非推理）- 速度优化", "grok-4-fast-non-reasoning"),
            ("Grok 4.1 Fast（推理）- 高性能，2M 上下文", "grok-4-1-fast-reasoning"),
        ],
        "deep": [
            ("Grok 4 - 旗舰模型", "grok-4-0709"),
            ("Grok 4.1 Fast（推理）- 高性能，2M 上下文", "grok-4-1-fast-reasoning"),
            ("Grok 4 Fast（推理）- 高性能", "grok-4-fast-reasoning"),
            ("Grok 4.1 Fast（非推理）- 速度优化，2M 上下文", "grok-4-1-fast-non-reasoning"),
        ],
    },
    "deepseek": {
        "quick": [
            ("DeepSeek V3.2", "deepseek-chat"),
            ("自定义模型 ID", "custom"),
        ],
        "deep": [
            ("DeepSeek V3.2（thinking）", "deepseek-reasoner"),
            ("DeepSeek V3.2", "deepseek-chat"),
            ("自定义模型 ID", "custom"),
        ],
    },
    "qwen": {
        "quick": [
            ("Qwen 3.5 Flash", "qwen3.5-flash"),
            ("Qwen Plus", "qwen-plus"),
            ("自定义模型 ID", "custom"),
        ],
        "deep": [
            ("Qwen 3.6 Plus", "qwen3.6-plus"),
            ("Qwen 3.5 Plus", "qwen3.5-plus"),
            ("Qwen 3 Max", "qwen3-max"),
            ("自定义模型 ID", "custom"),
        ],
    },
    "glm": {
        "quick": [
            ("GLM-4.7", "glm-4.7"),
            ("GLM-5", "glm-5"),
            ("自定义模型 ID", "custom"),
        ],
        "deep": [
            ("GLM-5.1", "glm-5.1"),
            ("GLM-5", "glm-5"),
            ("自定义模型 ID", "custom"),
        ],
    },
    # OpenRouter：动态拉取。Azure：接受任意已部署模型名。
    "ollama": {
        "quick": [
            ("Qwen3:latest（8B，本地）", "qwen3:latest"),
            ("GPT-OSS:latest（20B，本地）", "gpt-oss:latest"),
            ("GLM-4.7-Flash:latest（30B，本地）", "glm-4.7-flash:latest"),
        ],
        "deep": [
            ("GLM-4.7-Flash:latest（30B，本地）", "glm-4.7-flash:latest"),
            ("GPT-OSS:latest（20B，本地）", "gpt-oss:latest"),
            ("Qwen3:latest（8B，本地）", "qwen3:latest"),
        ],
    },
}


def get_model_options(provider: str, mode: str) -> List[ModelOption]:
    """返回某个提供方在指定模式下的共享模型选项。"""
    return MODEL_OPTIONS[provider.lower()][mode]


def get_known_models() -> Dict[str, List[str]]:
    """根据共享 CLI 模型目录构建已知模型名列表。"""
    return {
        provider: sorted(
            {
                value
                for options in mode_options.values()
                for _, value in options
            }
        )
        for provider, mode_options in MODEL_OPTIONS.items()
    }
