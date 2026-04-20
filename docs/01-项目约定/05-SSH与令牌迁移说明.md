# SSH 与令牌迁移说明

## 1. 文档用途

- 固化记录 `cntrandingagents` 项目当前 GitHub / Gitee / Ubuntu 的认证与自动登录基线。
- 明确区分 SSH 公钥指纹与 API Token。
- 把 `cnfrp` 项目现有可复用凭据迁移到 `cntrandingagents` 的方式说明清楚。
- 最后更新时间：2026-04-20

## 2. 当前前提

- 设备与 `cnfrp` 项目相同。
- 远程 Ubuntu 开发机相同。
- GitHub / Gitee 账号体系相同。
- 登录方式可以自动登录，并计划沿用到 `cntrandingagents`。

## 3. 使用规则

- `SSH 指纹` 用于 `git pull`、`git push`、Remote SSH 认证状态核对。
- `API Token` 用于 GitHub Release / Gitee Release / 发布自动化脚本。
- `SSH 指纹` 与 `API Token` 必须分开记录，不再混用。
- 令牌明文不写入 Git 仓库；仓库只记录是否已配置、用途、验证方式与最近使用时间。

## 4. 当前凭据总表

| 平台 | 凭据类别 | 标识/标题 | 明文/指纹 | 用途 | 当前状态 | 最近使用 | 备注 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GitHub | SSH 指纹 | `cnfrp-windows` | `SHA256:89/mJ60fRM/ooQRtz6/tzoYN22YSxGA/W8quQy18sGQ` | Windows 侧仓库 SSH 推送 / 拉取 | 已配置 | 最近一周内已使用 | 沿用到 `cntrandingagents` |
| GitHub | SSH 指纹 | `cnfrp-wuse2060` | `SHA256:Soh119VwsMefPI6DHdM8QLQ1cGnbhhDfuBnEOyl3ikE` | Ubuntu 开发机仓库 SSH 推送 / 拉取 | 已配置 | 最近一周内已使用 | 沿用到 `cntrandingagents` |
| GitHub | API Token | `GitHub PAT` | `已配置，明文不入仓` | GitHub Release / API 自动化 | 已记录 | `2026-04-14` | 从 `cnfrp` 迁移过来，明文沿用本地既有存放位置 |
| Gitee | SSH 指纹 | `cnfrp-windows` | `SHA256:KxFQlVnQt83yEz/tTJGY+wfdvF3ypUpIxZUKFwOZaGU` | Windows 侧仓库 SSH 推送 / 拉取 | 已配置 | `2026-04-14 02:21:52` | 沿用到 `cntrandingagents` |
| Gitee | SSH 指纹 | `cnfrp-wuse2060` | `SHA256:0d6SI/21bvMqZVmwcprFPMEOd4WnVYnlccDdocYekr4` | Ubuntu 开发机仓库 SSH 推送 / 拉取 | 已配置 | `2026-04-14 12:36:26` | 沿用到 `cntrandingagents` |
| Gitee | API Token | `Gitee 私人令牌` | `已配置，明文不入仓` | Gitee Release 创建 / 附件上传 / API 自动化 | 已记录 | `2026-04-14` | 从 `cnfrp` 迁移过来，明文沿用本地既有存放位置 |

## 5. GitHub SSH 公钥迁移结论

- Windows 与 Ubuntu 两侧 SSH 推送能力已在 `cnfrp` 中验证通过。
- `cntrandingagents` 沿用同一账号体系和设备时，无需重新生成新密钥。
- 只需确认新仓库对同一账号可见，并验证 `ls-remote` 与推送权限。

## 6. Gitee SSH 公钥迁移结论

- Windows 与 Ubuntu 两侧 Gitee SSH 推送能力已在 `cnfrp` 中验证通过。
- `cntrandingagents` 沿用同一账号体系和设备时，可直接复用。
- 新仓库创建完成后，补一次 `ls-remote` 即可确认链路。

## 7. API Token 迁移结论

- GitHub PAT 与 Gitee 私人令牌当前均可作为 `cntrandingagents` 发布自动化凭据使用。
- 只要账号权限覆盖新仓库，就不需要重新新建令牌。
- 若后续仓库权限范围不足，再补新令牌并更新本文档。

## 8. 自动登录与认证链路说明

- Windows IDE 通过 Remote SSH 连接 Ubuntu 开发机。
- Ubuntu 负责正式 Git、release 和镜像同步。
- Windows 侧保留 SSH 能力，用于应急和排障。
- GitHub 与 Gitee 发布自动化默认走已有令牌。

## 9. 建议验证命令

在 Ubuntu 主工作树执行：

```bash
git ls-remote origin refs/heads/main
git ls-remote gitee refs/heads/main
git ls-remote upstream refs/heads/main
ssh -T git@github.com || true
ssh -T git@gitee.com || true
```

在 Windows 本地执行：

```powershell
git ls-remote git@github.com:wuse999/cntrandingagents.git refs/heads/main
git ls-remote git@gitee.com:frpnat/cntrandingagents.git refs/heads/main
```

## 10. 令牌使用边界

- GitHub PAT 仅用于 GitHub API、GitHub Release、自动化脚本。
- Gitee 私人令牌仅用于 Gitee API、Gitee Release、附件上传。
- SSH 指纹只负责仓库认证和 Remote SSH 能力核对。

## 11. 当前明确结论

- `cntrandingagents` 可直接继承 `cnfrp` 的 SSH 与 API Token 基线。
- 当前最需要做的不是重新申请凭据，而是把新仓库绑定到既有认证链路并完成验证。

## 12. 一句话结论

`cntrandingagents` 当前默认沿用 `cnfrp` 现成的 GitHub / Gitee SSH 公钥与 API Token 体系，后续只做“绑定新仓库 + 验证可用”。
