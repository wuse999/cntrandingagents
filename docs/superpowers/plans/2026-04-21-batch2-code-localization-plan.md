# cntrandingagents 第二批代码注释与提示词汉化 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 完成 `cntrandingagents` 第二批汉化，将剩余代码注释、文档字符串和提示词切换为中文，同时保持逻辑与官方同步友好性。

**Architecture:** 先补设计与执行记录，再按“工具/数据层说明、图与客户端说明、分析与辩论提示词、CLI 剩余注释”四组逐批修改，最后用本地与 Ubuntu 双侧验证闭环。

**Tech Stack:** Python, Markdown, LangChain, LangGraph, PowerShell, Git, SSH

---

### Task 1: 建立第二批汉化文档基线

**Files:**
- Create: `D:\tranding\tranding_agents_cn\cntrandingagents\docs\superpowers\specs\2026-04-21-batch2-code-localization-design.md`
- Create: `D:\tranding\tranding_agents_cn\cntrandingagents\docs\superpowers\plans\2026-04-21-batch2-code-localization-plan.md`
- Create: `D:\tranding\tranding_agents_cn\cntrandingagents\docs\02-执行记录\2026-04-21-第二批代码注释与提示词汉化执行记录.md`
- Test: UTF-8 读取抽检

- [ ] 写明本轮范围、边界、风险、验证策略和正式仓库闭环方式。
- [ ] 建立执行记录骨架，预留“改动范围、验证结果、踩坑回收、结论”区块。
- [ ] 用 UTF-8 抽检文档内容，确认中文无乱码。

### Task 2: 汉化工具层与数据层说明文字

**Files:**
- Modify: `D:\tranding\tranding_agents_cn\cntrandingagents\tradingagents\agents\utils\agent_states.py`
- Modify: `D:\tranding\tranding_agents_cn\cntrandingagents\tradingagents\agents\utils\agent_utils.py`
- Modify: `D:\tranding\tranding_agents_cn\cntrandingagents\tradingagents\agents\utils\core_stock_tools.py`
- Modify: `D:\tranding\tranding_agents_cn\cntrandingagents\tradingagents\agents\utils\fundamental_data_tools.py`
- Modify: `D:\tranding\tranding_agents_cn\cntrandingagents\tradingagents\agents\utils\news_data_tools.py`
- Modify: `D:\tranding\tranding_agents_cn\cntrandingagents\tradingagents\agents\utils\technical_indicators_tools.py`
- Modify: `D:\tranding\tranding_agents_cn\cntrandingagents\tradingagents\agents\utils\memory.py`
- Modify: `D:\tranding\tranding_agents_cn\cntrandingagents\tradingagents\dataflows\*.py`
- Modify: `D:\tranding\tranding_agents_cn\cntrandingagents\tradingagents\default_config.py`
- Test: `python -m compileall tradingagents`

- [ ] 将说明性注释、文档字符串、工具参数描述改为中文。
- [ ] 对数据层返回报头、错误提示与指标说明做中文化，但保留 API 参数、字段名和内部键值。
- [ ] 对高风险字符串做抽检，确认未误改模型 ID、供应商名、工具名和内部路由值。

### Task 3: 汉化图编排与 LLM 提示词

**Files:**
- Modify: `D:\tranding\tranding_agents_cn\cntrandingagents\tradingagents\agents\analysts\*.py`
- Modify: `D:\tranding\tranding_agents_cn\cntrandingagents\tradingagents\agents\researchers\*.py`
- Modify: `D:\tranding\tranding_agents_cn\cntrandingagents\tradingagents\agents\managers\*.py`
- Modify: `D:\tranding\tranding_agents_cn\cntrandingagents\tradingagents\agents\risk_mgmt\*.py`
- Modify: `D:\tranding\tranding_agents_cn\cntrandingagents\tradingagents\agents\trader\trader.py`
- Modify: `D:\tranding\tranding_agents_cn\cntrandingagents\tradingagents\graph\reflection.py`
- Modify: `D:\tranding\tranding_agents_cn\cntrandingagents\tradingagents\graph\signal_processing.py`
- Test: `python -m py_compile` 针对关键提示词文件

- [ ] 将研究、辩论、交易、反思、信号提取提示词改为中文。
- [ ] 保留必须维持英文的强约束标记和评级枚举，避免破坏结果解析逻辑。
- [ ] 复核 `FINAL TRANSACTION PROPOSAL` 和 `BUY/OVERWEIGHT/HOLD/UNDERWEIGHT/SELL` 等关键字面值。

### Task 4: 汉化 CLI 剩余技术注释与客户端封装说明

**Files:**
- Modify: `D:\tranding\tranding_agents_cn\cntrandingagents\cli\announcements.py`
- Modify: `D:\tranding\tranding_agents_cn\cntrandingagents\cli\config.py`
- Modify: `D:\tranding\tranding_agents_cn\cntrandingagents\cli\main.py`
- Modify: `D:\tranding\tranding_agents_cn\cntrandingagents\cli\utils.py`
- Modify: `D:\tranding\tranding_agents_cn\cntrandingagents\tradingagents\llm_clients\*.py`
- Test: `python -m compileall cli tradingagents main.py`

- [ ] 将 CLI 内部注释和技术性文档字符串改为中文。
- [ ] 将 LLM 客户端包装层的说明与校验文档字符串改为中文。
- [ ] 确认汉化未影响命令入口和模型选择逻辑。

### Task 5: 验证、回填记录、同步 Ubuntu 并正式提交

**Files:**
- Modify: `D:\tranding\tranding_agents_cn\cntrandingagents\docs\02-执行记录\2026-04-21-第二批代码注释与提示词汉化执行记录.md`
- Modify: `D:\tranding\tranding_agents_cn\cntrandingagents\docs\02-执行记录\00-长期踩坑与经验回收.md`
- Test: `git status -sb`, `git diff --name-only`, `python -m compileall`, Ubuntu 复核命令

- [ ] 回填实际改动范围、验证结果、遗留风险和新增经验。
- [ ] 将变更同步到 Ubuntu 正式主工作树，执行编译与 Git 复核。
- [ ] 在 Ubuntu 正式主工作树提交并推送到 `origin/main` 与 `gitee/main`，随后把 Windows 镜像对齐到最新提交。
