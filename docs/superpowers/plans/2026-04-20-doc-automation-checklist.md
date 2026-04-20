# cntrandingagents 文档自动执行清单 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an AI-executable documentation checklist, a long-term pitfall ledger, and a stronger execution record template so future localization work is automatically recorded, checked, and iterated.

**Architecture:** Keep stable workflow rules in `docs/01-项目约定`, keep factual session records and reusable pitfalls in `docs/02-执行记录`, and wire both into the existing index files so every future session starts from the same entry points. Make UTF-8 handling, pitfall capture, and index maintenance part of the default workflow instead of optional follow-up work.

**Tech Stack:** Markdown, Git, PowerShell, Ubuntu shell

---

### Task 1: Add the default AI execution checklist

**Files:**
- Create: `d:\tranding\tranding_agents_cn\cntrandingagents\docs\01-项目约定\11-AI自动执行文档与检查清单.md`
- Modify: `d:\tranding\tranding_agents_cn\cntrandingagents\docs\00-总索引.md`
- Modify: `d:\tranding\tranding_agents_cn\cntrandingagents\docs\01-项目约定\README.md`
- Test: `Get-Content -Encoding UTF8` spot-checks on the new and updated files

- [ ] Define the scope, default startup reading order, pre-flight checks, execution flow, recording rules, and UTF-8 anti-garble rules in the new checklist document.
- [ ] Add the new checklist document to the project-wide index.
- [ ] Add the new checklist document to the governance README so it becomes part of the default reading path.
- [ ] Re-read the new checklist with UTF-8 output enabled and confirm the rendered Chinese text is intact.

### Task 2: Add pitfall recovery and strengthen the execution record template

**Files:**
- Create: `d:\tranding\tranding_agents_cn\cntrandingagents\docs\02-执行记录\00-长期踩坑与经验回收.md`
- Modify: `d:\tranding\tranding_agents_cn\cntrandingagents\docs\02-执行记录\README.md`
- Modify: `d:\tranding\tranding_agents_cn\cntrandingagents\docs\02-执行记录\模板-汉化执行记录.md`
- Test: `Get-Content -Encoding UTF8` spot-checks on the new and updated files

- [ ] Seed the long-term pitfall ledger with the issues already discovered during repository bootstrap.
- [ ] Update the execution record README so it explains the new pitfall ledger and when to promote lessons into governance docs.
- [ ] Expand the execution record template so each future session captures environment checks, UTF-8 checks, new pitfalls, and rule write-backs.
- [ ] Re-read the new ledger and updated template with UTF-8 output enabled and confirm the structure is usable as the new default workflow.

### Task 3: Record this rollout and verify the wiring

**Files:**
- Create: `d:\tranding\tranding_agents_cn\cntrandingagents\docs\02-执行记录\2026-04-20-自动执行文档体系落地记录.md`
- Modify: `d:\tranding\tranding_agents_cn\cntrandingagents\docs\00-总索引.md`
- Test: `git status --short`, `git diff --name-only`

- [ ] Create a same-day execution record for this documentation rollout so the new workflow is immediately exercised once.
- [ ] Verify every new document is reachable from the relevant README or index.
- [ ] Run `git status --short` and `git diff --name-only` to confirm the exact changed file set matches the intended document-only scope.
- [ ] Re-check the touched Markdown files with UTF-8 output enabled before reporting completion.
