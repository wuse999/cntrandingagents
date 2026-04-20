"""各提供方的模型名称校验器。"""

from .model_catalog import get_known_models


VALID_MODELS = {
    provider: models
    for provider, models in get_known_models().items()
    if provider not in ("ollama", "openrouter")
}


def validate_model(provider: str, model: str) -> bool:
    """检查给定提供方下的模型名称是否合法。

    对 ollama、openrouter 而言，任何模型名都被接受。
    """
    provider_lower = provider.lower()

    if provider_lower in ("ollama", "openrouter"):
        return True

    if provider_lower not in VALID_MODELS:
        return True

    return model in VALID_MODELS[provider_lower]
