# Windows Mirror Backup Retention Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 Windows 本地镜像备份建立默认保留最近 3 份的长期规则与清理脚本。

**Architecture:** 先补一份长期规则文档与本轮执行留痕，再新增 PowerShell 清理脚本，最后把索引、README、AI 检查清单与长期踩坑台账接上，并用 `-WhatIf` 与临时测试目录验证脚本行为。

**Tech Stack:** Markdown, PowerShell, Git

---

### Task 1: 落地治理文档与执行留痕

**Files:**
- Create: `docs/01-项目约定/12-Windows镜像备份保留策略.md`
- Create: `docs/02-执行记录/2026-04-21-Windows镜像备份保留策略执行记录.md`
- Create: `docs/superpowers/specs/2026-04-21-windows-mirror-backup-retention-design.md`
- Modify: `docs/00-总索引.md`
- Modify: `docs/01-项目约定/README.md`

- [ ] 写入长期规则文档，明确路径、前缀、默认保留数量和安全边界。
- [ ] 写入本轮设计与执行留痕。
- [ ] 更新总索引与项目约定入口，确保新文档可被发现。

### Task 2: 新增 Windows 备份清理脚本

**Files:**
- Create: `tools/cleanup_windows_mirror_backups.ps1`

- [ ] 实现 `BackupRoot`、`RetainCount`、`Prefix` 参数。
- [ ] 仅管理带有 `mirror-snapshot.tgz` 的完整快照目录。
- [ ] 支持 `-WhatIf` 演练，并输出保留/跳过/删除结果。

### Task 3: 把规则接入检查清单与长期台账

**Files:**
- Modify: `docs/01-项目约定/11-AI自动执行文档与检查清单.md`
- Modify: `docs/02-执行记录/00-长期踩坑与经验回收.md`

- [ ] 在 AI 检查清单中加入 Windows 镜像备份清理入口。
- [ ] 在长期踩坑台账中固化“镜像备份无限增长”的处理办法。

### Task 4: 验证脚本并回填结果

**Files:**
- Modify: `docs/02-执行记录/2026-04-21-Windows镜像备份保留策略执行记录.md`

- [ ] 运行 `powershell -ExecutionPolicy Bypass -File .\tools\cleanup_windows_mirror_backups.ps1 -WhatIf`
- [ ] 在临时测试根目录构造超过 3 份模拟快照并执行脚本验证。
- [ ] 回填本轮验证结果与结论。
