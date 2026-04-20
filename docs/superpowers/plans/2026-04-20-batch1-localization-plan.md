# cntrandingagents 首批汉化里程碑 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver the first user-facing Chinese localization batch for `cntrandingagents`, covering the repository README, CLI visible copy, execution records, and canonical Git closure on Ubuntu.

**Architecture:** Keep all changes limited to user-visible text. Update governance and execution artifacts locally, translate `README.md` and CLI presentation strings without changing internal values or execution logic, then sync the changed files into the Ubuntu canonical worktree for verification, commit, and push.

**Tech Stack:** Markdown, Python, Typer, Rich, Questionary, Git, PowerShell, SSH

---

### Task 1: Write design and execution records for the batch

**Files:**
- Create: `d:\tranding\tranding_agents_cn\cntrandingagents\docs\superpowers\specs\2026-04-20-batch1-localization-design.md`
- Create: `d:\tranding\tranding_agents_cn\cntrandingagents\docs\02-执行记录\2026-04-20-首批汉化执行记录.md`
- Modify: `d:\tranding\tranding_agents_cn\cntrandingagents\docs\02-执行记录\README.md`
- Test: `Get-Content -Encoding UTF8` spot-check

- [ ] Record the batch scope, chosen approach, risks, and verification strategy in the design document.
- [ ] Create a same-day execution record for the localization batch before code edits.
- [ ] Ensure the execution record structure matches the new automation template.
- [ ] Re-read both files with UTF-8 output enabled and confirm the Chinese content is intact.

### Task 2: Localize the top-level README

**Files:**
- Modify: `d:\tranding\tranding_agents_cn\cntrandingagents\README.md`
- Test: Markdown spot-check via `Get-Content -Encoding UTF8`

- [ ] Translate README headings, explanatory paragraphs, installation guidance, CLI usage text, contribution notes, and citation intro into Chinese.
- [ ] Keep commands, URLs, badges, image paths, file paths, and project names unchanged.
- [ ] Preserve Markdown structure so upstream sync remains manageable.
- [ ] Re-read the translated README and check that code blocks and links remain intact.

### Task 3: Localize CLI user-visible copy

**Files:**
- Modify: `d:\tranding\tranding_agents_cn\cntrandingagents\cli\main.py`
- Modify: `d:\tranding\tranding_agents_cn\cntrandingagents\cli\utils.py`
- Modify: `d:\tranding\tranding_agents_cn\cntrandingagents\cli\announcements.py`
- Modify: `d:\tranding\tranding_agents_cn\cntrandingagents\cli\config.py`
- Test: `python -m compileall cli main.py`, `python -m cli.main --help`

- [ ] Translate Typer help text, welcome copy, step prompts, selection labels, status panels, save-report prompts, and completion messages.
- [ ] Translate Questionary display strings while keeping internal values and provider/model IDs unchanged.
- [ ] Update announcement fallback and attention prompt to Chinese.
- [ ] Run compile/help verification and confirm no syntax or startup regressions were introduced by the text-only changes.

### Task 4: Verify, sync to Ubuntu, and close the batch formally

**Files:**
- Modify: `d:\tranding\tranding_agents_cn\cntrandingagents\docs\02-执行记录\2026-04-20-首批汉化执行记录.md`
- Test: `git status -sb`, `git diff --name-only`, UTF-8 spot-checks, Ubuntu-side Git verification

- [ ] Update the execution record with actual modified files, verification output, and any new pitfalls.
- [ ] Run local UTF-8, Git scope, and sensitive-string checks.
- [ ] Copy the changed files into `~/projects/cntrandingagents` on Ubuntu, re-run verification there, and confirm the canonical worktree state.
- [ ] Commit on Ubuntu with a localization-focused message and push to both `origin` and `gitee`.
