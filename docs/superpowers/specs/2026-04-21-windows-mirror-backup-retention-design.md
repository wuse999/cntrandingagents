# Windows 镜像备份保留策略设计

## 1. 背景

`cntrandingagents` 当前采用“Windows 本地镜像 + Ubuntu 正式主工作树”的单主线模式。每次整理 Windows 本地镜像到 `origin/main` 前，都会在工作区外部生成一份镜像对齐备份。若缺少统一保留规则，`_bootstrap_backup` 会随着对齐次数持续膨胀。

## 2. 目标

- 为 Windows 本地镜像备份建立固定保留规则。
- 提供一个可直接执行的 PowerShell 清理脚本。
- 把规则写入治理文档，并接入总索引、README、AI 检查清单与长期踩坑台账。

## 3. 采用方案

采用“长期规则文档 + 本地 PowerShell 清理脚本”的轻量方案。

原因：

- 足够覆盖当前需求，不引入额外系统依赖。
- 可直接复用在现有 Windows 环境。
- 后续若需要再升级为计划任务，不会推翻当前方案。

## 4. 规则边界

- 仅处理 `_bootstrap_backup` 下目录名匹配 `windows-mirror-align-*` 的快照目录。
- 默认保留最近 `3` 份完整快照。
- 完整快照以存在 `mirror-snapshot.tgz` 为判定条件。
- 不完整快照目录默认跳过，留给人工复核。

## 5. 脚本设计

- 参数：
  - `BackupRoot`：备份根目录，默认推导到工作区外层 `_bootstrap_backup`
  - `RetainCount`：默认 `3`
  - `Prefix`：默认 `windows-mirror-align-`
- 行为：
  - 识别符合前缀且带有 `mirror-snapshot.tgz` 的目录
  - 按时间倒序排序
  - 保留最近 `RetainCount` 份
  - 删除更旧目录
  - 支持 `-WhatIf`

## 6. 验证策略

- 先用 `-WhatIf` 验证零破坏演练。
- 再在临时测试根目录构造超过 `3` 份的模拟快照，验证脚本能保留最新 `3` 份并删除更旧目录。
- 最后检查治理文档入口是否补齐。

## 7. 一句话结论

Windows 镜像备份保留策略采用“规则先固化、脚本后执行”的轻量落地方式，默认只保留最近 `3` 份完整快照。
