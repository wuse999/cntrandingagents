from typing import Optional
import datetime
import typer
from pathlib import Path
from functools import wraps
from rich.console import Console
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
load_dotenv(".env.enterprise", override=False)
from rich.panel import Panel
from rich.spinner import Spinner
from rich.live import Live
from rich.columns import Columns
from rich.markdown import Markdown
from rich.layout import Layout
from rich.text import Text
from rich.table import Table
from collections import deque
import time
from rich.tree import Tree
from rich import box
from rich.align import Align
from rich.rule import Rule

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from cli.models import AnalystType
from cli.utils import *
from cli.announcements import fetch_announcements, display_announcements
from cli.stats_handler import StatsCallbackHandler

console = Console()

app = typer.Typer(
    name="TradingAgents",
    help="TradingAgents CLI：多智能体 LLM 金融交易框架命令行工具",
    add_completion=True,  # 启用 shell 自动补全
)

TEAM_DISPLAY_NAMES = {
    "Analyst Team": "分析师团队",
    "Research Team": "研究团队",
    "Trading Team": "交易团队",
    "Risk Management": "风控团队",
    "Portfolio Management": "投资组合管理",
}

AGENT_DISPLAY_NAMES = {
    "Market Analyst": "市场分析师",
    "Social Analyst": "社交媒体分析师",
    "News Analyst": "新闻分析师",
    "Fundamentals Analyst": "基本面分析师",
    "Bull Researcher": "看多研究员",
    "Bear Researcher": "看空研究员",
    "Research Manager": "研究经理",
    "Trader": "交易员",
    "Aggressive Analyst": "激进风控分析师",
    "Neutral Analyst": "中性风控分析师",
    "Conservative Analyst": "保守风控分析师",
    "Portfolio Manager": "投资组合经理",
}

STATUS_DISPLAY_NAMES = {
    "pending": "待开始",
    "in_progress": "进行中",
    "completed": "已完成",
    "error": "错误",
}

MESSAGE_TYPE_DISPLAY_NAMES = {
    "Tool": "工具",
    "System": "系统",
    "User": "用户",
    "Agent": "代理",
    "Data": "数据",
    "Control": "控制",
}

SECTION_DISPLAY_NAMES = {
    "market_report": "市场分析",
    "sentiment_report": "社交情绪分析",
    "news_report": "新闻分析",
    "fundamentals_report": "基本面分析",
    "investment_plan": "研究团队结论",
    "trader_investment_plan": "交易团队计划",
    "final_trade_decision": "投资组合管理结论",
}

ANALYST_VALUE_DISPLAY_NAMES = {
    "market": "市场分析师",
    "social": "社交媒体分析师",
    "news": "新闻分析师",
    "fundamentals": "基本面分析师",
}


def display_team_name(name: str) -> str:
    return TEAM_DISPLAY_NAMES.get(name, name)


def display_agent_name(name: str) -> str:
    return AGENT_DISPLAY_NAMES.get(name, name)


def display_status_name(status: str) -> str:
    return STATUS_DISPLAY_NAMES.get(status, status)


def display_message_type(message_type: str) -> str:
    return MESSAGE_TYPE_DISPLAY_NAMES.get(message_type, message_type)


def display_analyst_value(value: str) -> str:
    return ANALYST_VALUE_DISPLAY_NAMES.get(value, value)


def display_analyst_values(values) -> str:
    return ", ".join(display_analyst_value(value) for value in values)


# 创建一个定长 deque，用于保存最近消息
class MessageBuffer:
    # 固定团队节点，始终执行（用户不可取消）
    FIXED_AGENTS = {
        "Research Team": ["Bull Researcher", "Bear Researcher", "Research Manager"],
        "Trading Team": ["Trader"],
        "Risk Management": ["Aggressive Analyst", "Neutral Analyst", "Conservative Analyst"],
        "Portfolio Management": ["Portfolio Manager"],
    }

    # 分析师名称映射
    ANALYST_MAPPING = {
        "market": "Market Analyst",
        "social": "Social Analyst",
        "news": "News Analyst",
        "fundamentals": "Fundamentals Analyst",
    }

    # 报告分区映射：`section -> (用于筛选的 analyst_key, 负责收尾的 finalizing_agent)`
    # `analyst_key`：由哪个分析师是否被选中来决定该分区是否启用（`None` 表示始终启用）
    # `finalizing_agent`：该报告要计为完成，哪个智能体必须处于 `completed`
    REPORT_SECTIONS = {
        "market_report": ("market", "Market Analyst"),
        "sentiment_report": ("social", "Social Analyst"),
        "news_report": ("news", "News Analyst"),
        "fundamentals_report": ("fundamentals", "Fundamentals Analyst"),
        "investment_plan": (None, "Research Manager"),
        "trader_investment_plan": (None, "Trader"),
        "final_trade_decision": (None, "Portfolio Manager"),
    }

    def __init__(self, max_length=100):
        self.messages = deque(maxlen=max_length)
        self.tool_calls = deque(maxlen=max_length)
        self.current_report = None
        self.final_report = None  # 保存完整的最终报告
        self.agent_status = {}
        self.current_agent = None
        self.report_sections = {}
        self.selected_analysts = []
        self._processed_message_ids = set()

    def init_for_analysis(self, selected_analysts):
        """根据所选分析师初始化状态与报告分区。

        参数：
            selected_analysts: 分析师类型字符串列表（例如 ["market", "news"]）
        """
        self.selected_analysts = [a.lower() for a in selected_analysts]

        # 动态构建 agent_status
        self.agent_status = {}

        # 添加已选择的分析师
        for analyst_key in self.selected_analysts:
            if analyst_key in self.ANALYST_MAPPING:
                self.agent_status[self.ANALYST_MAPPING[analyst_key]] = "pending"

        # 添加固定团队节点
        for team_agents in self.FIXED_AGENTS.values():
            for agent in team_agents:
                self.agent_status[agent] = "pending"

        # 动态构建 report_sections
        self.report_sections = {}
        for section, (analyst_key, _) in self.REPORT_SECTIONS.items():
            if analyst_key is None or analyst_key in self.selected_analysts:
                self.report_sections[section] = None

        # 重置其他状态
        self.current_report = None
        self.final_report = None
        self.current_agent = None
        self.messages.clear()
        self.tool_calls.clear()
        self._processed_message_ids.clear()

    def get_completed_reports_count(self):
        """统计已经真正完成的报告数量（负责收尾的智能体已完成）。

        报告被视为完成，需要同时满足：
        1. 报告分区已有内容（不是 None）；以及
        2. 负责最终产出该报告的智能体状态为 "completed"

        这样可以避免把辩论中途的临时更新误计为最终完成。
        """
        count = 0
        for section in self.report_sections:
            if section not in self.REPORT_SECTIONS:
                continue
            _, finalizing_agent = self.REPORT_SECTIONS[section]
            # 只有“已有内容”且“收尾智能体已完成”时，该报告才算完成
            has_content = self.report_sections.get(section) is not None
            agent_done = self.agent_status.get(finalizing_agent) == "completed"
            if has_content and agent_done:
                count += 1
        return count

    def add_message(self, message_type, content):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.messages.append((timestamp, message_type, content))

    def add_tool_call(self, tool_name, args):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.tool_calls.append((timestamp, tool_name, args))

    def update_agent_status(self, agent, status):
        if agent in self.agent_status:
            self.agent_status[agent] = status
            self.current_agent = agent

    def update_report_section(self, section_name, content):
        if section_name in self.report_sections:
            self.report_sections[section_name] = content
            self._update_current_report()

    def _update_current_report(self):
        # 面板展示时，仅显示最近一次更新的分区
        latest_section = None
        latest_content = None

        # 找出最近更新的分区
        for section, content in self.report_sections.items():
            if content is not None:
                latest_section = section
                latest_content = content
               
        if latest_section and latest_content:
            # 将当前分区格式化后用于展示
            self.current_report = (
                f"### {SECTION_DISPLAY_NAMES[latest_section]}\n{latest_content}"
            )

        # 更新最终完整报告
        self._update_final_report()

    def _update_final_report(self):
        report_parts = []

        # 分析师团队报告：使用 .get() 兼容缺失分区
        analyst_sections = ["market_report", "sentiment_report", "news_report", "fundamentals_report"]
        if any(self.report_sections.get(section) for section in analyst_sections):
            report_parts.append("## 分析师团队报告")
            if self.report_sections.get("market_report"):
                report_parts.append(
                    f"### 市场分析\n{self.report_sections['market_report']}"
                )
            if self.report_sections.get("sentiment_report"):
                report_parts.append(
                    f"### 社交情绪分析\n{self.report_sections['sentiment_report']}"
                )
            if self.report_sections.get("news_report"):
                report_parts.append(
                    f"### 新闻分析\n{self.report_sections['news_report']}"
                )
            if self.report_sections.get("fundamentals_report"):
                report_parts.append(
                    f"### 基本面分析\n{self.report_sections['fundamentals_report']}"
                )

        # 研究团队报告
        if self.report_sections.get("investment_plan"):
            report_parts.append("## 研究团队结论")
            report_parts.append(f"{self.report_sections['investment_plan']}")

        # 交易团队报告
        if self.report_sections.get("trader_investment_plan"):
            report_parts.append("## 交易团队计划")
            report_parts.append(f"{self.report_sections['trader_investment_plan']}")

        # 投资组合管理决策
        if self.report_sections.get("final_trade_decision"):
            report_parts.append("## 投资组合管理结论")
            report_parts.append(f"{self.report_sections['final_trade_decision']}")

        self.final_report = "\n\n".join(report_parts) if report_parts else None


message_buffer = MessageBuffer()


def create_layout():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=3),
    )
    layout["main"].split_column(
        Layout(name="upper", ratio=3), Layout(name="analysis", ratio=5)
    )
    layout["upper"].split_row(
        Layout(name="progress", ratio=2), Layout(name="messages", ratio=3)
    )
    return layout


def format_tokens(n):
    """将 token 数量格式化为便于展示的形式。"""
    if n >= 1000:
        return f"{n/1000:.1f}k"
    return str(n)


def update_display(layout, spinner_text=None, stats_handler=None, start_time=None):
    # 顶部欢迎栏
    layout["header"].update(
        Panel(
            "[bold green]欢迎使用 TradingAgents CLI[/bold green]\n"
            "[dim]© [Tauric Research](https://github.com/TauricResearch)[/dim]",
            title="欢迎使用 TradingAgents",
            border_style="green",
            padding=(1, 2),
            expand=True,
        )
    )

    # 展示智能体状态的进度面板
    progress_table = Table(
        show_header=True,
        header_style="bold magenta",
        show_footer=False,
        box=box.SIMPLE_HEAD,  # 使用简洁表头和横线
        title=None,  # 去掉重复的 Progress 标题
        padding=(0, 2),  # 增加横向内边距
        expand=True,  # 让表格自动填满可用空间
    )
    progress_table.add_column("团队", style="cyan", justify="center", width=20)
    progress_table.add_column("代理", style="green", justify="center", width=20)
    progress_table.add_column("状态", style="yellow", justify="center", width=20)

    # 按团队分组，仅展示 agent_status 中存在的智能体
    all_teams = {
        "Analyst Team": [
            "Market Analyst",
            "Social Analyst",
            "News Analyst",
            "Fundamentals Analyst",
        ],
        "Research Team": ["Bull Researcher", "Bear Researcher", "Research Manager"],
        "Trading Team": ["Trader"],
        "Risk Management": ["Aggressive Analyst", "Neutral Analyst", "Conservative Analyst"],
        "Portfolio Management": ["Portfolio Manager"],
    }

    # 过滤团队，只保留当前启用的智能体
    teams = {}
    for team, agents in all_teams.items():
        active_agents = [a for a in agents if a in message_buffer.agent_status]
        if active_agents:
            teams[team] = active_agents

    for team, agents in teams.items():
        # 添加每个团队的第一位智能体，并带上团队名
        first_agent = agents[0]
        status = message_buffer.agent_status.get(first_agent, "pending")
        if status == "in_progress":
            spinner = Spinner(
                "dots", text="[blue]进行中[/blue]", style="bold cyan"
            )
            status_cell = spinner
        else:
            status_color = {
                "pending": "yellow",
                "completed": "green",
                "error": "red",
            }.get(status, "white")
            status_cell = f"[{status_color}]{display_status_name(status)}[/{status_color}]"
        progress_table.add_row(display_team_name(team), display_agent_name(first_agent), status_cell)

        # 添加该团队其余智能体
        for agent in agents[1:]:
            status = message_buffer.agent_status.get(agent, "pending")
            if status == "in_progress":
                spinner = Spinner(
                    "dots", text="[blue]进行中[/blue]", style="bold cyan"
                )
                status_cell = spinner
            else:
                status_color = {
                    "pending": "yellow",
                    "completed": "green",
                    "error": "red",
                }.get(status, "white")
                status_cell = f"[{status_color}]{display_status_name(status)}[/{status_color}]"
            progress_table.add_row("", display_agent_name(agent), status_cell)

        # 每个团队结束后添加分隔线
        progress_table.add_row("─" * 20, "─" * 20, "─" * 20, style="dim")

    layout["progress"].update(
        Panel(progress_table, title="进度", border_style="cyan", padding=(1, 2))
    )

    # 消息面板：展示最近消息与工具调用
    messages_table = Table(
        show_header=True,
        header_style="bold magenta",
        show_footer=False,
        expand=True,  # 让表格自动填满可用空间
        box=box.MINIMAL,  # 使用更轻量的边框样式
        show_lines=True,  # 保留横向分隔线
        padding=(0, 1),  # 在列之间增加少量留白
    )
    messages_table.add_column("时间", style="cyan", width=8, justify="center")
    messages_table.add_column("类型", style="green", width=10, justify="center")
    messages_table.add_column(
        "内容", style="white", no_wrap=False, ratio=1
    )  # 让内容列自适应扩展

    # 合并工具调用与普通消息
    all_messages = []

    # 加入工具调用
    for timestamp, tool_name, args in message_buffer.tool_calls:
        formatted_args = format_tool_args(args)
        all_messages.append((timestamp, "Tool", f"{tool_name}: {formatted_args}"))

    # 加入普通消息
    for timestamp, msg_type, content in message_buffer.messages:
        content_str = str(content) if content else ""
        if len(content_str) > 200:
            content_str = content_str[:197] + "..."
        all_messages.append((timestamp, msg_type, content_str))

    # 按时间戳倒序排序（最新在前）
    all_messages.sort(key=lambda x: x[0], reverse=True)

    # 根据可用空间计算最多可展示多少条消息
    max_messages = 12

    # 取前 N 条消息（即最新消息）
    recent_messages = all_messages[:max_messages]

    # 将消息加入表格（当前已经是最新在前的顺序）
    for timestamp, msg_type, content in recent_messages:
        # 对内容进行换行整理
        wrapped_content = Text(content, overflow="fold")
        messages_table.add_row(timestamp, display_message_type(msg_type), wrapped_content)

    layout["messages"].update(
        Panel(
            messages_table,
            title="消息与工具",
            border_style="blue",
            padding=(1, 2),
        )
    )

    # 分析面板：展示当前报告
    if message_buffer.current_report:
        layout["analysis"].update(
            Panel(
                Markdown(message_buffer.current_report),
                title="当前报告",
                border_style="green",
                padding=(1, 2),
            )
        )
    else:
        layout["analysis"].update(
            Panel(
                "[italic]等待分析报告...[/italic]",
                title="当前报告",
                border_style="green",
                padding=(1, 2),
            )
        )

    # 底部统计栏
    # 智能体进度由 agent_status 字典推导
    agents_completed = sum(
        1 for status in message_buffer.agent_status.values() if status == "completed"
    )
    agents_total = len(message_buffer.agent_status)

    # 报告进度以智能体完成状态为准，而不仅仅看是否已有内容
    reports_completed = message_buffer.get_completed_reports_count()
    reports_total = len(message_buffer.report_sections)

    # 构建统计信息片段
    stats_parts = [f"代理: {agents_completed}/{agents_total}"]

    # 从回调处理器中获取 LLM 与工具统计
    if stats_handler:
        stats = stats_handler.get_stats()
        stats_parts.append(f"LLM: {stats['llm_calls']}")
        stats_parts.append(f"工具: {stats['tool_calls']}")

        # 令牌统计展示，无法获取时优雅降级
        if stats["tokens_in"] > 0 or stats["tokens_out"] > 0:
            tokens_str = f"令牌: {format_tokens(stats['tokens_in'])}\u2191 {format_tokens(stats['tokens_out'])}\u2193"
        else:
            tokens_str = "令牌: --"
        stats_parts.append(tokens_str)

    stats_parts.append(f"报告: {reports_completed}/{reports_total}")

    # 已用时间
    if start_time:
        elapsed = time.time() - start_time
        elapsed_str = f"\u23f1 {int(elapsed // 60):02d}:{int(elapsed % 60):02d}"
        stats_parts.append(elapsed_str)

    stats_table = Table(show_header=False, box=None, padding=(0, 2), expand=True)
    stats_table.add_column("统计", justify="center")
    stats_table.add_row(" | ".join(stats_parts))

    layout["footer"].update(Panel(stats_table, border_style="grey50"))


def get_user_selections():
    """在开始分析展示前，收集全部用户选择。"""
    # 显示 ASCII 欢迎信息
    with open(Path(__file__).parent / "static" / "welcome.txt", "r") as f:
        welcome_ascii = f.read()

    # 构建欢迎框内容
    welcome_content = f"{welcome_ascii}\n"
    welcome_content += "[bold green]TradingAgents：多智能体 LLM 金融交易框架 - CLI[/bold green]\n\n"
    welcome_content += "[bold]工作流程：[/bold]\n"
    welcome_content += "I. 分析师团队 → II. 研究团队 → III. 交易员 → IV. 风控团队 → V. 投资组合管理\n\n"
    welcome_content += (
        "[dim]由 [Tauric Research](https://github.com/TauricResearch) 构建[/dim]"
    )

    # 创建并居中显示欢迎框
    welcome_box = Panel(
        welcome_content,
        border_style="green",
        padding=(1, 2),
        title="欢迎使用 TradingAgents",
        subtitle="多智能体 LLM 金融交易框架",
    )
    console.print(Align.center(welcome_box))
    console.print()
    console.print()  # 在公告前增加一行空白

    # 获取并展示公告（失败时静默处理）
    announcements = fetch_announcements()
    display_announcements(console, announcements)

    # 为每个步骤创建带边框的问题卡片
    def create_question_box(title, prompt, default=None):
        box_content = f"[bold]{title}[/bold]\n"
        box_content += f"[dim]{prompt}[/dim]"
        if default:
            box_content += f"\n[dim]默认值：{default}[/dim]"
        return Panel(box_content, border_style="blue", padding=(1, 2))

    # 第 1 步：股票代码
    console.print(
        create_question_box(
            "第 1 步：股票代码",
            "请输入要分析的准确股票代码；如有需要请带上交易所后缀（示例：SPY、CNC.TO、7203.T、0700.HK）",
            "SPY",
        )
    )
    selected_ticker = get_ticker()

    # 第 2 步：分析日期
    default_date = datetime.datetime.now().strftime("%Y-%m-%d")
    console.print(
        create_question_box(
            "第 2 步：分析日期",
            "请输入分析日期（YYYY-MM-DD）",
            default_date,
        )
    )
    analysis_date = get_analysis_date()

    # 第 3 步：输出语言
    console.print(
        create_question_box(
            "第 3 步：输出语言",
            "请选择分析师报告和最终结论的输出语言"
        )
    )
    output_language = ask_output_language()

    # 第 4 步：选择分析师
    console.print(
        create_question_box(
            "第 4 步：分析师团队", "请选择参与本次分析的 LLM 分析师代理"
        )
    )
    selected_analysts = select_analysts()
    console.print(
        f"[green]已选择分析师：[/green] {display_analyst_values(analyst.value for analyst in selected_analysts)}"
    )

    # 第 5 步：研究深度
    console.print(
        create_question_box(
            "第 5 步：研究深度", "请选择本次研究深度"
        )
    )
    selected_research_depth = select_research_depth()

    # 第 6 步：LLM 提供方
    console.print(
        create_question_box(
            "第 6 步：LLM 提供方", "请选择本次分析使用的 LLM 提供方"
        )
    )
    selected_llm_provider, backend_url = select_llm_provider()

    # 第 7 步：Thinking 智能体
    console.print(
        create_question_box(
            "第 7 步：思考模型", "请选择本次分析使用的思考模型"
        )
    )
    selected_shallow_thinker = select_shallow_thinking_agent(selected_llm_provider)
    selected_deep_thinker = select_deep_thinking_agent(selected_llm_provider)

    # 第 8 步：提供方专属 thinking 配置
    thinking_level = None
    reasoning_effort = None
    anthropic_effort = None

    provider_lower = selected_llm_provider.lower()
    if provider_lower == "google":
        console.print(
            create_question_box(
                "第 8 步：Thinking 模式",
                "配置 Gemini 的 Thinking 模式"
            )
        )
        thinking_level = ask_gemini_thinking_config()
    elif provider_lower == "openai":
        console.print(
            create_question_box(
                "第 8 步：推理强度",
                "配置 OpenAI 的推理强度"
            )
        )
        reasoning_effort = ask_openai_reasoning_effort()
    elif provider_lower == "anthropic":
        console.print(
            create_question_box(
                "第 8 步：努力级别",
                "配置 Claude 的努力级别"
            )
        )
        anthropic_effort = ask_anthropic_effort()

    return {
        "ticker": selected_ticker,
        "analysis_date": analysis_date,
        "analysts": selected_analysts,
        "research_depth": selected_research_depth,
        "llm_provider": selected_llm_provider.lower(),
        "backend_url": backend_url,
        "shallow_thinker": selected_shallow_thinker,
        "deep_thinker": selected_deep_thinker,
        "google_thinking_level": thinking_level,
        "openai_reasoning_effort": reasoning_effort,
        "anthropic_effort": anthropic_effort,
        "output_language": output_language,
    }


def get_ticker():
    """从用户输入中获取股票代码。"""
    return typer.prompt("", default="SPY")


def get_analysis_date():
    """从用户输入中获取分析日期。"""
    while True:
        date_str = typer.prompt(
            "", default=datetime.datetime.now().strftime("%Y-%m-%d")
        )
        try:
            # 校验日期格式，并确保日期不晚于今天
            analysis_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            if analysis_date.date() > datetime.datetime.now().date():
                console.print("[red]错误：分析日期不能晚于今天。[/red]")
                continue
            return date_str
        except ValueError:
            console.print(
                "[red]错误：日期格式无效，请使用 YYYY-MM-DD。[/red]"
            )


def save_report_to_disk(final_state, ticker: str, save_path: Path):
    """将完整分析报告按子目录结构保存到磁盘。"""
    save_path.mkdir(parents=True, exist_ok=True)
    sections = []

    # 1. 分析师团队
    analysts_dir = save_path / "1_analysts"
    analyst_parts = []
    if final_state.get("market_report"):
        analysts_dir.mkdir(exist_ok=True)
        (analysts_dir / "market.md").write_text(final_state["market_report"])
        analyst_parts.append(("市场分析师", final_state["market_report"]))
    if final_state.get("sentiment_report"):
        analysts_dir.mkdir(exist_ok=True)
        (analysts_dir / "sentiment.md").write_text(final_state["sentiment_report"])
        analyst_parts.append(("社交媒体分析师", final_state["sentiment_report"]))
    if final_state.get("news_report"):
        analysts_dir.mkdir(exist_ok=True)
        (analysts_dir / "news.md").write_text(final_state["news_report"])
        analyst_parts.append(("新闻分析师", final_state["news_report"]))
    if final_state.get("fundamentals_report"):
        analysts_dir.mkdir(exist_ok=True)
        (analysts_dir / "fundamentals.md").write_text(final_state["fundamentals_report"])
        analyst_parts.append(("基本面分析师", final_state["fundamentals_report"]))
    if analyst_parts:
        content = "\n\n".join(f"### {name}\n{text}" for name, text in analyst_parts)
        sections.append(f"## I. 分析师团队报告\n\n{content}")

    # 2. 研究团队
    if final_state.get("investment_debate_state"):
        research_dir = save_path / "2_research"
        debate = final_state["investment_debate_state"]
        research_parts = []
        if debate.get("bull_history"):
            research_dir.mkdir(exist_ok=True)
            (research_dir / "bull.md").write_text(debate["bull_history"])
            research_parts.append(("看多研究员", debate["bull_history"]))
        if debate.get("bear_history"):
            research_dir.mkdir(exist_ok=True)
            (research_dir / "bear.md").write_text(debate["bear_history"])
            research_parts.append(("看空研究员", debate["bear_history"]))
        if debate.get("judge_decision"):
            research_dir.mkdir(exist_ok=True)
            (research_dir / "manager.md").write_text(debate["judge_decision"])
            research_parts.append(("研究经理", debate["judge_decision"]))
        if research_parts:
            content = "\n\n".join(f"### {name}\n{text}" for name, text in research_parts)
            sections.append(f"## II. 研究团队结论\n\n{content}")

    # 3. 交易团队
    if final_state.get("trader_investment_plan"):
        trading_dir = save_path / "3_trading"
        trading_dir.mkdir(exist_ok=True)
        (trading_dir / "trader.md").write_text(final_state["trader_investment_plan"])
        sections.append(f"## III. 交易团队计划\n\n### 交易员\n{final_state['trader_investment_plan']}")

    # 4. 风控团队
    if final_state.get("risk_debate_state"):
        risk_dir = save_path / "4_risk"
        risk = final_state["risk_debate_state"]
        risk_parts = []
        if risk.get("aggressive_history"):
            risk_dir.mkdir(exist_ok=True)
            (risk_dir / "aggressive.md").write_text(risk["aggressive_history"])
            risk_parts.append(("激进风控分析师", risk["aggressive_history"]))
        if risk.get("conservative_history"):
            risk_dir.mkdir(exist_ok=True)
            (risk_dir / "conservative.md").write_text(risk["conservative_history"])
            risk_parts.append(("保守风控分析师", risk["conservative_history"]))
        if risk.get("neutral_history"):
            risk_dir.mkdir(exist_ok=True)
            (risk_dir / "neutral.md").write_text(risk["neutral_history"])
            risk_parts.append(("中性风控分析师", risk["neutral_history"]))
        if risk_parts:
            content = "\n\n".join(f"### {name}\n{text}" for name, text in risk_parts)
            sections.append(f"## IV. 风控团队结论\n\n{content}")

        # 5. 投资组合经理
        if risk.get("judge_decision"):
            portfolio_dir = save_path / "5_portfolio"
            portfolio_dir.mkdir(exist_ok=True)
            (portfolio_dir / "decision.md").write_text(risk["judge_decision"])
            sections.append(f"## V. 投资组合经理结论\n\n### 投资组合经理\n{risk['judge_decision']}")

    # 写入整合后的完整报告
    header = f"# 交易分析报告：{ticker}\n\n生成时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    (save_path / "complete_report.md").write_text(header + "\n\n".join(sections))
    return save_path / "complete_report.md"


def display_complete_report(final_state):
    """按顺序展示完整分析报告，避免终端截断。"""
    console.print()
    console.print(Rule("完整分析报告", style="bold green"))

    # 第一部分：分析师团队报告
    analysts = []
    if final_state.get("market_report"):
        analysts.append(("市场分析师", final_state["market_report"]))
    if final_state.get("sentiment_report"):
        analysts.append(("社交媒体分析师", final_state["sentiment_report"]))
    if final_state.get("news_report"):
        analysts.append(("新闻分析师", final_state["news_report"]))
    if final_state.get("fundamentals_report"):
        analysts.append(("基本面分析师", final_state["fundamentals_report"]))
    if analysts:
        console.print(Panel("[bold]I. 分析师团队报告[/bold]", border_style="cyan"))
        for title, content in analysts:
            console.print(Panel(Markdown(content), title=title, border_style="blue", padding=(1, 2)))

    # 第二部分：研究团队报告
    if final_state.get("investment_debate_state"):
        debate = final_state["investment_debate_state"]
        research = []
        if debate.get("bull_history"):
            research.append(("看多研究员", debate["bull_history"]))
        if debate.get("bear_history"):
            research.append(("看空研究员", debate["bear_history"]))
        if debate.get("judge_decision"):
            research.append(("研究经理", debate["judge_decision"]))
        if research:
            console.print(Panel("[bold]II. 研究团队结论[/bold]", border_style="magenta"))
            for title, content in research:
                console.print(Panel(Markdown(content), title=title, border_style="blue", padding=(1, 2)))

    # 第三部分：交易团队
    if final_state.get("trader_investment_plan"):
        console.print(Panel("[bold]III. 交易团队计划[/bold]", border_style="yellow"))
        console.print(Panel(Markdown(final_state["trader_investment_plan"]), title="交易员", border_style="blue", padding=(1, 2)))

    # 第四部分：风险管理团队
    if final_state.get("risk_debate_state"):
        risk = final_state["risk_debate_state"]
        risk_reports = []
        if risk.get("aggressive_history"):
            risk_reports.append(("激进风控分析师", risk["aggressive_history"]))
        if risk.get("conservative_history"):
            risk_reports.append(("保守风控分析师", risk["conservative_history"]))
        if risk.get("neutral_history"):
            risk_reports.append(("中性风控分析师", risk["neutral_history"]))
        if risk_reports:
            console.print(Panel("[bold]IV. 风控团队结论[/bold]", border_style="red"))
            for title, content in risk_reports:
                console.print(Panel(Markdown(content), title=title, border_style="blue", padding=(1, 2)))

        # 第五部分：投资组合经理决策
        if risk.get("judge_decision"):
            console.print(Panel("[bold]V. 投资组合经理结论[/bold]", border_style="green"))
            console.print(Panel(Markdown(risk["judge_decision"]), title="投资组合经理", border_style="blue", padding=(1, 2)))


def update_research_team_status(status):
    """更新研究团队成员状态（不包含 `Trader` 节点）。"""
    research_team = ["Bull Researcher", "Bear Researcher", "Research Manager"]
    for agent in research_team:
        message_buffer.update_agent_status(agent, status)


# 用于状态流转的分析师固定顺序
ANALYST_ORDER = ["market", "social", "news", "fundamentals"]
ANALYST_AGENT_NAMES = {
    "market": "Market Analyst",
    "social": "Social Analyst",
    "news": "News Analyst",
    "fundamentals": "Fundamentals Analyst",
}
ANALYST_REPORT_MAP = {
    "market": "market_report",
    "social": "sentiment_report",
    "news": "news_report",
    "fundamentals": "fundamentals_report",
}


def update_analyst_statuses(message_buffer, chunk):
    """基于累计报告状态更新分析师进度。

    逻辑：
    - 如果当前 chunk 含有新报告内容，则先写入
    - 基于累计的 report_sections（而不是仅看当前 chunk）判断状态
    - 已产出报告的分析师记为 `completed`
    - 第一个尚未产出报告的分析师记为 `in_progress`
    - 其余尚未产出报告的分析师记为 `pending`
    - 当所有分析师都完成后，将 `Bull Researcher` 切换为 `in_progress`
    """
    selected = message_buffer.selected_analysts
    found_active = False

    for analyst_key in ANALYST_ORDER:
        if analyst_key not in selected:
            continue

        agent_name = ANALYST_AGENT_NAMES[analyst_key]
        report_key = ANALYST_REPORT_MAP[analyst_key]

        # 从当前 chunk 中提取新的报告内容
        if chunk.get(report_key):
            message_buffer.update_report_section(report_key, chunk[report_key])

        # 根据累计分区内容判断状态，而不是只看当前 chunk
        has_report = bool(message_buffer.report_sections.get(report_key))

        if has_report:
            message_buffer.update_agent_status(agent_name, "completed")
        elif not found_active:
            message_buffer.update_agent_status(agent_name, "in_progress")
            found_active = True
        else:
            message_buffer.update_agent_status(agent_name, "pending")

    # 当所有分析师完成后，将研究团队切换为 in_progress
    if not found_active and selected:
        if message_buffer.agent_status.get("Bull Researcher") == "pending":
            message_buffer.update_agent_status("Bull Researcher", "in_progress")

def extract_content_string(content):
    """从多种消息格式中提取字符串内容。

    如果没有有意义的文本内容，则返回 None。
    """
    import ast

    def is_empty(val):
        """利用 Python 的真值规则判断内容是否为空。"""
        if val is None or val == '':
            return True
        if isinstance(val, str):
            s = val.strip()
            if not s:
                return True
            try:
                return not bool(ast.literal_eval(s))
            except (ValueError, SyntaxError):
                return False  # 无法解析说明是真实文本
        return not bool(val)

    if is_empty(content):
        return None

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, dict):
        text = content.get('text', '')
        return text.strip() if not is_empty(text) else None

    if isinstance(content, list):
        text_parts = [
            item.get('text', '').strip() if isinstance(item, dict) and item.get('type') == 'text'
            else (item.strip() if isinstance(item, str) else '')
            for item in content
        ]
        result = ' '.join(t for t in text_parts if t and not is_empty(t))
        return result if result else None

    return str(content).strip() if not is_empty(content) else None


def classify_message_type(message) -> tuple[str, str | None]:
    """将 LangChain 消息归类为展示类型，并提取内容。

    返回：
        (type, content)
        - `type` 取值之一：`User`、`Agent`、`Data`、`Control`
        - `content` 为提取出的字符串或 `None`
    """
    from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

    content = extract_content_string(getattr(message, 'content', None))

    if isinstance(message, HumanMessage):
        if content and content.strip() == "Continue":
            return ("Control", content)
        return ("User", content)

    if isinstance(message, ToolMessage):
        return ("Data", content)

    if isinstance(message, AIMessage):
        return ("Agent", content)

    # 未知类型的回退分支
    return ("System", content)


def format_tool_args(args, max_length=80) -> str:
    """将工具参数格式化为适合终端显示的短文本。"""
    result = str(args)
    if len(result) > max_length:
        return result[:max_length - 3] + "..."
    return result

def run_analysis():
    # 先获取全部用户选择
    selections = get_user_selections()

    # 根据所选研究深度构建配置
    config = DEFAULT_CONFIG.copy()
    config["max_debate_rounds"] = selections["research_depth"]
    config["max_risk_discuss_rounds"] = selections["research_depth"]
    config["quick_think_llm"] = selections["shallow_thinker"]
    config["deep_think_llm"] = selections["deep_thinker"]
    config["backend_url"] = selections["backend_url"]
    config["llm_provider"] = selections["llm_provider"].lower()
    # 提供方专属 thinking 配置
    config["google_thinking_level"] = selections.get("google_thinking_level")
    config["openai_reasoning_effort"] = selections.get("openai_reasoning_effort")
    config["anthropic_effort"] = selections.get("anthropic_effort")
    config["output_language"] = selections.get("output_language", "English")

    # 创建统计回调处理器，用于跟踪 LLM/工具调用
    stats_handler = StatsCallbackHandler()

    # 将分析师选择归一化为预定义顺序（原始选择为 set，顺序不固定）
    selected_set = {analyst.value for analyst in selections["analysts"]}
    selected_analyst_keys = [a for a in ANALYST_ORDER if a in selected_set]

    # 初始化图，并把回调绑定到 LLM
    graph = TradingAgentsGraph(
        selected_analyst_keys,
        config=config,
        debug=True,
        callbacks=[stats_handler],
    )

    # 使用所选分析师初始化消息缓冲区
    message_buffer.init_for_analysis(selected_analyst_keys)

    # 记录开始时间，用于展示耗时
    start_time = time.time()

    # 创建结果目录
    results_dir = Path(config["results_dir"]) / selections["ticker"] / selections["analysis_date"]
    results_dir.mkdir(parents=True, exist_ok=True)
    report_dir = results_dir / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    log_file = results_dir / "message_tool.log"
    log_file.touch(exist_ok=True)

    def save_message_decorator(obj, func_name):
        func = getattr(obj, func_name)
        @wraps(func)
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            timestamp, message_type, content = obj.messages[-1]
            content = content.replace("\n", " ")  # 将换行替换为空格
            with open(log_file, "a") as f:
                f.write(f"{timestamp} [{message_type}] {content}\n")
        return wrapper
    
    def save_tool_call_decorator(obj, func_name):
        func = getattr(obj, func_name)
        @wraps(func)
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            timestamp, tool_name, args = obj.tool_calls[-1]
            args_str = ", ".join(f"{k}={v}" for k, v in args.items())
            with open(log_file, "a") as f:
                f.write(f"{timestamp} [Tool Call] {tool_name}({args_str})\n")
        return wrapper

    def save_report_section_decorator(obj, func_name):
        func = getattr(obj, func_name)
        @wraps(func)
        def wrapper(section_name, content):
            func(section_name, content)
            if section_name in obj.report_sections and obj.report_sections[section_name] is not None:
                content = obj.report_sections[section_name]
                if content:
                    file_name = f"{section_name}.md"
                    text = "\n".join(str(item) for item in content) if isinstance(content, list) else content
                    with open(report_dir / file_name, "w") as f:
                        f.write(text)
        return wrapper

    message_buffer.add_message = save_message_decorator(message_buffer, "add_message")
    message_buffer.add_tool_call = save_tool_call_decorator(message_buffer, "add_tool_call")
    message_buffer.update_report_section = save_report_section_decorator(message_buffer, "update_report_section")

    # 现在开始渲染展示布局
    layout = create_layout()

    with Live(layout, refresh_per_second=4) as live:
        # 首次渲染
        update_display(layout, stats_handler=stats_handler, start_time=start_time)

        # 添加初始消息
        message_buffer.add_message("System", f"已选择股票代码：{selections['ticker']}")
        message_buffer.add_message(
            "System", f"分析日期：{selections['analysis_date']}"
        )
        message_buffer.add_message(
            "System",
            f"已选择分析师：{display_analyst_values(analyst.value for analyst in selections['analysts'])}",
        )
        update_display(layout, stats_handler=stats_handler, start_time=start_time)

        # 将第一位分析师的状态切换为 in_progress
        first_analyst = f"{selections['analysts'][0].value.capitalize()} Analyst"
        message_buffer.update_agent_status(first_analyst, "in_progress")
        update_display(layout, stats_handler=stats_handler, start_time=start_time)

        # 构建加载提示文本
        spinner_text = (
            f"正在分析 {selections['ticker']}（日期：{selections['analysis_date']}）..."
        )
        update_display(layout, spinner_text, stats_handler=stats_handler, start_time=start_time)

        # 初始化状态，并获取带回调的图执行参数
        init_agent_state = graph.propagator.create_initial_state(
            selections["ticker"], selections["analysis_date"]
        )
        # 将回调传给图配置，用于跟踪工具执行
        # （LLM 跟踪通过 LLM 构造函数单独处理）
        args = graph.propagator.get_graph_args(callbacks=[stats_handler])

        # 流式执行分析
        trace = []
        for chunk in graph.graph.stream(init_agent_state, **args):
            # 处理 chunk 中的全部消息，并按消息 ID 去重
            for message in chunk.get("messages", []):
                msg_id = getattr(message, "id", None)
                if msg_id is not None:
                    if msg_id in message_buffer._processed_message_ids:
                        continue
                    message_buffer._processed_message_ids.add(msg_id)

                msg_type, content = classify_message_type(message)
                if content and content.strip():
                    message_buffer.add_message(msg_type, content)

                if hasattr(message, "tool_calls") and message.tool_calls:
                    for tool_call in message.tool_calls:
                        if isinstance(tool_call, dict):
                            message_buffer.add_tool_call(tool_call["name"], tool_call["args"])
                        else:
                            message_buffer.add_tool_call(tool_call.name, tool_call.args)

            # 基于报告状态更新分析师进度（每个 chunk 都会执行）
            update_analyst_statuses(message_buffer, chunk)

            # 研究团队：处理 `investment_debate_state`
            if chunk.get("investment_debate_state"):
                debate_state = chunk["investment_debate_state"]
                bull_hist = debate_state.get("bull_history", "").strip()
                bear_hist = debate_state.get("bear_history", "").strip()
                judge = debate_state.get("judge_decision", "").strip()

                # 仅在确实存在内容时才更新状态
                if bull_hist or bear_hist:
                    update_research_team_status("in_progress")
                if bull_hist:
                    message_buffer.update_report_section(
                        "investment_plan", f"### 看多研究员分析\n{bull_hist}"
                    )
                if bear_hist:
                    message_buffer.update_report_section(
                        "investment_plan", f"### 看空研究员分析\n{bear_hist}"
                    )
                if judge:
                    message_buffer.update_report_section(
                        "investment_plan", f"### 研究经理结论\n{judge}"
                    )
                    update_research_team_status("completed")
                    message_buffer.update_agent_status("Trader", "in_progress")

            # 交易团队
            if chunk.get("trader_investment_plan"):
                message_buffer.update_report_section(
                    "trader_investment_plan", chunk["trader_investment_plan"]
                )
                if message_buffer.agent_status.get("Trader") != "completed":
                    message_buffer.update_agent_status("Trader", "completed")
                    message_buffer.update_agent_status("Aggressive Analyst", "in_progress")

            # 风险管理团队：处理 `risk_debate_state`
            if chunk.get("risk_debate_state"):
                risk_state = chunk["risk_debate_state"]
                agg_hist = risk_state.get("aggressive_history", "").strip()
                con_hist = risk_state.get("conservative_history", "").strip()
                neu_hist = risk_state.get("neutral_history", "").strip()
                judge = risk_state.get("judge_decision", "").strip()

                if agg_hist:
                    if message_buffer.agent_status.get("Aggressive Analyst") != "completed":
                        message_buffer.update_agent_status("Aggressive Analyst", "in_progress")
                    message_buffer.update_report_section(
                        "final_trade_decision", f"### 激进风控分析师分析\n{agg_hist}"
                    )
                if con_hist:
                    if message_buffer.agent_status.get("Conservative Analyst") != "completed":
                        message_buffer.update_agent_status("Conservative Analyst", "in_progress")
                    message_buffer.update_report_section(
                        "final_trade_decision", f"### 保守风控分析师分析\n{con_hist}"
                    )
                if neu_hist:
                    if message_buffer.agent_status.get("Neutral Analyst") != "completed":
                        message_buffer.update_agent_status("Neutral Analyst", "in_progress")
                    message_buffer.update_report_section(
                        "final_trade_decision", f"### 中性风控分析师分析\n{neu_hist}"
                    )
                if judge:
                    if message_buffer.agent_status.get("Portfolio Manager") != "completed":
                        message_buffer.update_agent_status("Portfolio Manager", "in_progress")
                        message_buffer.update_report_section(
                            "final_trade_decision", f"### 投资组合经理结论\n{judge}"
                        )
                        message_buffer.update_agent_status("Aggressive Analyst", "completed")
                        message_buffer.update_agent_status("Conservative Analyst", "completed")
                        message_buffer.update_agent_status("Neutral Analyst", "completed")
                        message_buffer.update_agent_status("Portfolio Manager", "completed")

            # 刷新展示
            update_display(layout, stats_handler=stats_handler, start_time=start_time)

            trace.append(chunk)

        # 获取最终状态与最终决策
        final_state = trace[-1]
        decision = graph.process_signal(final_state["final_trade_decision"])

        # 将所有智能体状态更新为 completed
        for agent in message_buffer.agent_status:
            message_buffer.update_agent_status(agent, "completed")

        message_buffer.add_message(
            "System", f"已完成 {selections['analysis_date']} 的分析"
        )

        # 更新最终报告分区
        for section in message_buffer.report_sections.keys():
            if section in final_state:
                message_buffer.update_report_section(section, final_state[section])

        update_display(layout, stats_handler=stats_handler, start_time=start_time)

    # 分析结束后的额外交互（放在 Live 之外，避免界面干扰）
    console.print("\n[bold cyan]分析完成！[/bold cyan]\n")

    # 提示是否保存报告
    save_choice = typer.prompt("是否保存报告？", default="Y").strip().upper()
    if save_choice in ("Y", "YES", ""):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_path = Path.cwd() / "reports" / f"{selections['ticker']}_{timestamp}"
        save_path_str = typer.prompt(
            "保存路径（直接回车使用默认值）",
            default=str(default_path)
        ).strip()
        save_path = Path(save_path_str)
        try:
            report_file = save_report_to_disk(final_state, selections["ticker"], save_path)
            console.print(f"\n[green]✓ 报告已保存至：[/green] {save_path.resolve()}")
            console.print(f"  [dim]完整报告：[/dim] {report_file.name}")
        except Exception as e:
            console.print(f"[red]保存报告时出错：{e}[/red]")

    # 提示是否显示完整报告
    display_choice = typer.prompt("\n是否在屏幕上显示完整报告？", default="Y").strip().upper()
    if display_choice in ("Y", "YES", ""):
        display_complete_report(final_state)


@app.command()
def analyze():
    run_analysis()


if __name__ == "__main__":
    app()
