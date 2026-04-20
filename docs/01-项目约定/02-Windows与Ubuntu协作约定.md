# Windows 与 Ubuntu 协作约定

## 1. 文档用途

- 固定 `cntrandingagents` 当前的开发协作模式。
- 明确 Windows 与 Ubuntu 各自负责什么。
- 固定默认编辑、Git、构建、测试与发布动作在哪一侧执行。

## 2. 当前协作模式

当前默认模式不是“双端本地开发”，而是：

- `Windows IDE + Remote SSH + Ubuntu 开发机`

具体含义：

- Windows 负责 IDE 界面、文档入口、代码浏览和远程终端入口。
- Ubuntu 开发机承担唯一正式主工作树与正式 Git / 构建 / 发布执行面。
- Windows 本地目录只保留为镜像、副本和应急参考。

## 3. Ubuntu 主工作树规则

- 正式工作树：`~/projects/cntrandingagents`
- 该工作树是默认编辑对象。
- 该工作树是默认 Git 操作对象。
- 该工作树是默认构建、测试、校验与发布对象。

## 4. Windows 本地目录规则

- 本地路径：`D:\tranding\tranding_agents_cn\cntrandingagents`
- 角色：本地镜像、应急副本、脱机参考目录
- 不再作为默认日常编辑面
- 不再作为默认正式 Git 提交面
- 不再作为默认构建或发布面

## 5. Windows 的职责

- 作为 IDE 入口
- 作为 Remote SSH 入口
- 作为文档查看与审阅入口
- 作为本地镜像与应急参考目录
- 在必要时做离线查看、Diff、搜索和比对

## 6. Ubuntu 的职责

- 作为唯一正式主工作树
- 作为唯一正式 Git 执行面
- 作为唯一正式构建和测试执行面
- 作为唯一正式发布与同步执行面
- 作为同步上游与准备 release 的默认环境

## 7. 默认在 Ubuntu 上执行的动作

- `git status`
- `git add / commit / push / tag`
- 文档构建验证
- CLI 运行验证
- 上游同步检查
- GitHub / Gitee 同步
- release 相关命令

## 8. 默认不在 Windows 上执行的动作

- 正式 `git commit`
- 正式 `git push`
- 正式 release tag 推送
- 正式 release 创建
- 正式构建和发布链路验证

## 9. 同步规则

- 日常同步首选 Git。
- 不做 Windows 和 Ubuntu 的长期双向目录镜像。
- 不把两边都维护成“主工作树”。
- 需要同步时，通过 Git 把 Ubuntu 主工作树的结果推送到 GitHub，再镜像到 Gitee。

## 10. 明确禁止的做法

- 不把 Windows 本地镜像继续当默认主工作树。
- 不在 Windows 本地目录上常态执行 `git commit` 或 `git push`。
- 不把 Windows 与 Ubuntu 维护成两套不同事实源。
- 不在本机 WSL 与远程 Ubuntu 之间再制造第三套主线。

## 11. 推荐日常工作流

1. 在 Windows IDE 中通过 Remote SSH 连接 Ubuntu 开发机。
2. 打开 `~/projects/cntrandingagents`。
3. 在 Ubuntu 主工作树中修改文档或代码。
4. 在 Ubuntu 主工作树执行 Git、验证和同步命令。
5. 需要时再回看 Windows 本地镜像目录做比对。

## 12. 一句话结论

`cntrandingagents` 当前固定采用“Windows 只是入口，Ubuntu 才是正式主工作树”的单主线协作模式。
