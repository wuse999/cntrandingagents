import questionary
from typing import List, Optional, Tuple, Dict

from rich.console import Console

from cli.models import AnalystType
from tradingagents.llm_clients.model_catalog import get_model_options

console = Console()

TICKER_INPUT_EXAMPLES = "示例：SPY、CNC.TO、7203.T、0700.HK"

ANALYST_ORDER = [
    ("市场分析师", AnalystType.MARKET),
    ("社交媒体分析师", AnalystType.SOCIAL),
    ("新闻分析师", AnalystType.NEWS),
    ("基本面分析师", AnalystType.FUNDAMENTALS),
]


def get_ticker() -> str:
    """提示用户输入股票代码。"""
    ticker = questionary.text(
        f"请输入要分析的准确股票代码（{TICKER_INPUT_EXAMPLES}）：",
        validate=lambda x: len(x.strip()) > 0 or "请输入有效的股票代码。",
        style=questionary.Style(
            [
                ("text", "fg:green"),
                ("highlighted", "noinherit"),
            ]
        ),
    ).ask()

    if not ticker:
        console.print("\n[red]未提供股票代码，程序即将退出。[/red]")
        exit(1)

    return normalize_ticker_symbol(ticker)


def normalize_ticker_symbol(ticker: str) -> str:
    """规范化股票代码输入，同时保留交易所后缀。"""
    return ticker.strip().upper()


def get_analysis_date() -> str:
    """提示用户输入 YYYY-MM-DD 格式的日期。"""
    import re
    from datetime import datetime

    def validate_date(date_str: str) -> bool:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            return False
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    date = questionary.text(
        "请输入分析日期（YYYY-MM-DD）：",
        validate=lambda x: validate_date(x.strip())
        or "请输入 YYYY-MM-DD 格式的有效日期。",
        style=questionary.Style(
            [
                ("text", "fg:green"),
                ("highlighted", "noinherit"),
            ]
        ),
    ).ask()

    if not date:
        console.print("\n[red]未提供分析日期，程序即将退出。[/red]")
        exit(1)

    return date.strip()


def select_analysts() -> List[AnalystType]:
    """通过交互式多选框选择分析师。"""
    choices = questionary.checkbox(
        "请选择你的[分析师团队]：",
        choices=[
            questionary.Choice(display, value=value) for display, value in ANALYST_ORDER
        ],
        instruction="\n- 按空格选择/取消选择分析师\n- 按 'a' 全选/取消全选\n- 按 Enter 完成",
        validate=lambda x: len(x) > 0 or "至少需要选择一位分析师。",
        style=questionary.Style(
            [
                ("checkbox-selected", "fg:green"),
                ("selected", "fg:green noinherit"),
                ("highlighted", "noinherit"),
                ("pointer", "noinherit"),
            ]
        ),
    ).ask()

    if not choices:
        console.print("\n[red]未选择分析师，程序即将退出。[/red]")
        exit(1)

    return choices


def select_research_depth() -> int:
    """通过交互式选择器选择研究深度。"""

    # 定义研究深度选项及其对应值
    DEPTH_OPTIONS = [
        ("浅度：快速研究，较少辩论与策略讨论轮次", 1),
        ("中度：平衡模式，适中的辩论与策略讨论轮次", 3),
        ("深度：全面研究，更多辩论与策略讨论轮次", 5),
    ]

    choice = questionary.select(
        "请选择你的[研究深度]：",
        choices=[
            questionary.Choice(display, value=value) for display, value in DEPTH_OPTIONS
        ],
        instruction="\n- 使用方向键移动\n- 按 Enter 选择",
        style=questionary.Style(
            [
                ("selected", "fg:yellow noinherit"),
                ("highlighted", "fg:yellow noinherit"),
                ("pointer", "fg:yellow noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        console.print("\n[red]未选择研究深度，程序即将退出。[/red]")
        exit(1)

    return choice


def _fetch_openrouter_models() -> List[Tuple[str, str]]:
    """从 OpenRouter API 拉取可用模型列表。"""
    import requests
    try:
        resp = requests.get("https://openrouter.ai/api/v1/models", timeout=10)
        resp.raise_for_status()
        models = resp.json().get("data", [])
        return [(m.get("name") or m["id"], m["id"]) for m in models]
    except Exception as e:
        console.print(f"\n[yellow]无法获取 OpenRouter 模型列表：{e}[/yellow]")
        return []


def select_openrouter_model() -> str:
    """从最新可用模型中选择 OpenRouter 模型，或手动输入自定义 ID。"""
    models = _fetch_openrouter_models()

    choices = [questionary.Choice(name, value=mid) for name, mid in models[:5]]
    choices.append(questionary.Choice("自定义模型 ID", value="custom"))

    choice = questionary.select(
        "请选择 OpenRouter 模型（优先显示最新可用模型）：",
        choices=choices,
        instruction="\n- 使用方向键移动\n- 按 Enter 选择",
        style=questionary.Style([
            ("selected", "fg:magenta noinherit"),
            ("highlighted", "fg:magenta noinherit"),
            ("pointer", "fg:magenta noinherit"),
        ]),
    ).ask()

    if choice is None or choice == "custom":
        return questionary.text(
            "请输入 OpenRouter 模型 ID（例如：google/gemma-4-26b-a4b-it）：",
            validate=lambda x: len(x.strip()) > 0 or "请输入模型 ID。",
        ).ask().strip()

    return choice


def _prompt_custom_model_id() -> str:
    """提示用户输入自定义模型 ID。"""
    return questionary.text(
        "请输入模型 ID：",
        validate=lambda x: len(x.strip()) > 0 or "请输入模型 ID。",
    ).ask().strip()


def _select_model(provider: str, mode: str) -> str:
    """为指定提供方和模式（quick/deep）选择模型。"""
    thinking_mode_label = "浅层思考" if mode == "quick" else "深度思考"

    if provider.lower() == "openrouter":
        return select_openrouter_model()

    if provider.lower() == "azure":
        return questionary.text(
            f"请输入 Azure 部署名称（用于{thinking_mode_label}）：",
            validate=lambda x: len(x.strip()) > 0 or "请输入部署名称。",
        ).ask().strip()

    choice = questionary.select(
        f"请选择你的[{thinking_mode_label} LLM 模型]：",
        choices=[
            questionary.Choice(display, value=value)
            for display, value in get_model_options(provider, mode)
        ],
        instruction="\n- 使用方向键移动\n- 按 Enter 选择",
        style=questionary.Style(
            [
                ("selected", "fg:magenta noinherit"),
                ("highlighted", "fg:magenta noinherit"),
                ("pointer", "fg:magenta noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        console.print(f"\n[red]未选择{thinking_mode_label} LLM 模型，程序即将退出。[/red]")
        exit(1)

    if choice == "custom":
        return _prompt_custom_model_id()

    return choice


def select_shallow_thinking_agent(provider) -> str:
    """通过交互式选择器选择浅层思考 LLM 引擎。"""
    return _select_model(provider, "quick")


def select_deep_thinking_agent(provider) -> str:
    """通过交互式选择器选择深度思考 LLM 引擎。"""
    return _select_model(provider, "deep")

def select_llm_provider() -> tuple[str, str | None]:
    """选择 LLM 提供方及其 API 接入地址。"""
    # (display_name, provider_key, base_url)
    PROVIDERS = [
        ("OpenAI", "openai", "https://api.openai.com/v1"),
        ("Google", "google", None),
        ("Anthropic", "anthropic", "https://api.anthropic.com/"),
        ("xAI", "xai", "https://api.x.ai/v1"),
        ("DeepSeek", "deepseek", "https://api.deepseek.com"),
        ("Qwen", "qwen", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
        ("GLM", "glm", "https://open.bigmodel.cn/api/paas/v4/"),
        ("OpenRouter", "openrouter", "https://openrouter.ai/api/v1"),
        ("Azure OpenAI", "azure", None),
        ("Ollama", "ollama", "http://localhost:11434/v1"),
    ]

    choice = questionary.select(
        "请选择你的 LLM 提供方：",
        choices=[
            questionary.Choice(display, value=(provider_key, url))
            for display, provider_key, url in PROVIDERS
        ],
        instruction="\n- 使用方向键移动\n- 按 Enter 选择",
        style=questionary.Style(
            [
                ("selected", "fg:magenta noinherit"),
                ("highlighted", "fg:magenta noinherit"),
                ("pointer", "fg:magenta noinherit"),
            ]
        ),
    ).ask()
    
    if choice is None:
        console.print("\n[red]未选择 LLM 提供方，程序即将退出。[/red]")
        exit(1)

    provider, url = choice
    return provider, url


def ask_openai_reasoning_effort() -> str:
    """询问 OpenAI 的推理强度级别。"""
    choices = [
        questionary.Choice("中等（默认）", "medium"),
        questionary.Choice("高（更充分）", "high"),
        questionary.Choice("低（更快）", "low"),
    ]
    return questionary.select(
        "请选择推理强度：",
        choices=choices,
        style=questionary.Style([
            ("selected", "fg:cyan noinherit"),
            ("highlighted", "fg:cyan noinherit"),
            ("pointer", "fg:cyan noinherit"),
        ]),
    ).ask()


def ask_anthropic_effort() -> str | None:
    """询问 Anthropic 的 effort 级别。

    该配置会影响 Claude 4.5+ 与 4.6 模型的 token 使用量和回答展开程度。
    """
    return questionary.select(
        "请选择努力级别：",
        choices=[
            questionary.Choice("高（推荐）", "high"),
            questionary.Choice("中（平衡）", "medium"),
            questionary.Choice("低（更快、更省）", "low"),
        ],
        style=questionary.Style([
            ("selected", "fg:cyan noinherit"),
            ("highlighted", "fg:cyan noinherit"),
            ("pointer", "fg:cyan noinherit"),
        ]),
    ).ask()


def ask_gemini_thinking_config() -> str | None:
    """询问 Gemini 的思考配置。

    返回的 thinking_level 为 "high" 或 "minimal"。
    客户端会根据模型系列映射到合适的 API 参数。
    """
    return questionary.select(
        "请选择 Gemini 思考模式：",
        choices=[
            questionary.Choice("启用思考（推荐）", "high"),
            questionary.Choice("最小化 / 关闭思考", "minimal"),
        ],
        style=questionary.Style([
            ("selected", "fg:green noinherit"),
            ("highlighted", "fg:green noinherit"),
            ("pointer", "fg:green noinherit"),
        ]),
    ).ask()


def ask_output_language() -> str:
    """询问报告输出语言。"""
    choice = questionary.select(
        "请选择输出语言：",
        choices=[
            questionary.Choice("英文（默认）", "English"),
            questionary.Choice("中文", "Chinese"),
            questionary.Choice("日语（日本語）", "Japanese"),
            questionary.Choice("韩语（한국어）", "Korean"),
            questionary.Choice("印地语（हिन्दी）", "Hindi"),
            questionary.Choice("西班牙语（Español）", "Spanish"),
            questionary.Choice("葡萄牙语（Português）", "Portuguese"),
            questionary.Choice("法语（Français）", "French"),
            questionary.Choice("德语（Deutsch）", "German"),
            questionary.Choice("阿拉伯语（العربية）", "Arabic"),
            questionary.Choice("俄语（Русский）", "Russian"),
            questionary.Choice("自定义语言", "custom"),
        ],
        style=questionary.Style([
            ("selected", "fg:yellow noinherit"),
            ("highlighted", "fg:yellow noinherit"),
            ("pointer", "fg:yellow noinherit"),
        ]),
    ).ask()

    if choice == "custom":
        return questionary.text(
            "请输入语言名称（例如：Turkish、Vietnamese、Thai、Indonesian）：",
            validate=lambda x: len(x.strip()) > 0 or "请输入语言名称。",
        ).ask().strip()

    return choice
