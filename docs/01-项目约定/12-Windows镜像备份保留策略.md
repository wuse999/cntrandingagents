# Windows 镜像备份保留策略

## 1. 文档用途

- 固定 Windows 本地镜像对齐前后产生的备份快照应如何保留与清理。
- 避免 `_bootstrap_backup` 长期累积无上限增长。
- 让备份清理动作可复用、可审计、可安全执行。

## 2. 适用范围

- 适用于 `D:\tranding\tranding_agents_cn\_bootstrap_backup` 下的 Windows 镜像对齐快照。
- 当前只管理目录名以 `windows-mirror-align-` 开头的镜像快照目录。
- 不管理其他类型的临时文件、手工备份目录或 Ubuntu 侧任何内容。

## 3. 当前默认规则

- 备份根目录：`D:\tranding\tranding_agents_cn\_bootstrap_backup`
- 快照前缀：`windows-mirror-align-`
- 默认保留数量：最近 `3` 份
- 清理对象：超过保留数量的旧快照目录
- 默认入口脚本：`tools/cleanup_windows_mirror_backups.ps1`

## 4. 完整快照判定

只有同时满足以下条件的目录，才视为可纳入自动保留策略管理的“完整快照”：

- 目录名匹配 `windows-mirror-align-*`
- 目录中存在 `mirror-snapshot.tgz`

若某个同前缀目录不满足完整快照判定，则：

- 不自动删除
- 不计入“最近 3 份”保留数量
- 需要人工检查其是否为中断、失败或半成品备份

## 5. 默认保留与清理规则

1. 每次 Windows 本地镜像执行“对齐前备份”后，可运行一次清理脚本。
2. 脚本按 `LastWriteTime` 从新到旧排序。
3. 默认保留最近 `3` 份完整快照目录。
4. 仅删除更旧的完整快照目录。
5. 不删除不匹配前缀的目录。
6. 不删除不完整快照目录。

## 6. 推荐执行方式

先做演练：

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\cleanup_windows_mirror_backups.ps1 -WhatIf
```

确认无误后再正式执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\cleanup_windows_mirror_backups.ps1
```

如需修改保留数量：

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\cleanup_windows_mirror_backups.ps1 -RetainCount 5
```

## 7. 安全边界

- 脚本只处理 `_bootstrap_backup` 下的目标快照目录。
- 脚本默认不跨目录删除，不处理仓库工作树。
- 若最新快照本身不完整，脚本不会把它当作“完整快照”清理链的一部分。
- 清理前建议先执行 `-WhatIf`。

## 8. 何时执行

- 完成 Windows 本地镜像对齐并确认镜像已恢复干净后。
- 新快照创建完成后。
- `_bootstrap_backup` 中已累计超过 `3` 份完整快照时。

## 9. 不建议的做法

- 不手动随意删除 `_bootstrap_backup` 中不明用途的目录。
- 不把“保留最近 3 份”改成 `0` 或 `1`，以免失去最基本的回退余量。
- 不在未确认最新快照生成完成前直接清理。

## 10. 一句话结论

Windows 本地镜像备份不是永久堆积，而是“默认保留最近 3 份完整快照，其余自动清理”的受控策略。
