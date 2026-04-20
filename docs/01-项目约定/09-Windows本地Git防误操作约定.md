# Windows 本地 Git 防误操作约定

## 1. 文档用途

- 固定 `cntrandingagents` 在 Windows 本地镜像中的 Git 保护规则。
- 从机制上防止误把 Windows 本地目录当成正式提交与发布面。

## 2. 为什么需要这层保护

- 当前正式主工作树在 Ubuntu，不在 Windows。
- Windows 本地目录只是镜像和应急副本。
- 若继续在 Windows 本地常态提交与推送，容易形成双主线。

## 3. 当前保护目标

- 默认阻止在 Windows 本地镜像直接 `git commit`
- 默认阻止在 Windows 本地镜像直接 `git push`
- 强制把日常 Git 动作收口到 Ubuntu 主工作树

## 4. 建议钩子策略

建议在 Windows 本地 `cntrandingagents` 仓库中安装：

- `pre-commit`
- `pre-push`

并默认阻止本地常态提交与推送。

## 5. 推荐环境变量命名

- `CNTRANDINGAGENTS_ALLOW_WINDOWS_LOCAL_GIT=1`

仅在极少数应急场景下，临时允许放开本地 Git 保护。

## 6. 推荐钩子提示口径

- 提示当前 Windows 本地仓库只是镜像 / 应急副本
- 提示正式 Git 动作应在 Ubuntu `~/projects/cntrandingagents` 执行
- 提示如需临时放开，必须先明确原因和风险

## 7. 临时放开条件

- 只用于极少数应急排障场景
- 只用于离线或远程机暂不可用场景
- 放开前必须明确说明原因
- 放开后应尽快重新收口到 Ubuntu 主工作树

## 8. 放开后的收口要求

- 记录本地操作原因
- 尽快把结果整理并同步到 Ubuntu 主工作树
- 不把“临时放开”变成默认工作流

## 9. 如何验证钩子生效

在 Windows 本地镜像执行：

```powershell
git commit --allow-empty -m "test"
git push
```

预期：

- 被 `pre-commit` 或 `pre-push` 拦截
- 提示应切换到 Ubuntu 主工作树执行正式 Git 动作

## 10. 一句话结论

Windows 本地镜像之所以加 Git 防误操作保护，不是为了增加流程，而是为了防止 `cntrandingagents` 重新回到双主线失控状态。
