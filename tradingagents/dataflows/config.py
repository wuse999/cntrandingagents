import tradingagents.default_config as default_config
from typing import Dict, Optional

# 默认加载基础配置，同时允许后续覆盖
_config: Optional[Dict] = None


def initialize_config():
    """使用默认值初始化配置。"""
    global _config
    if _config is None:
        _config = default_config.DEFAULT_CONFIG.copy()


def set_config(config: Dict):
    """使用自定义值更新配置。"""
    global _config
    if _config is None:
        _config = default_config.DEFAULT_CONFIG.copy()
    _config.update(config)


def get_config() -> Dict:
    """获取当前配置。"""
    if _config is None:
        initialize_config()
    return _config.copy()


# 启动时先加载默认配置
initialize_config()
