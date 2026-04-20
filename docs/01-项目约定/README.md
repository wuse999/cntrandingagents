# 项目约定总入口

## 1. 文档用途

- 作为 `cntrandingagents` 项目约定类文档的总入口。
- 帮助任何进入本项目的人先理解边界，再开始修改。
- 避免把本仓误做成“功能增强仓”或“双主线仓”。

## 2. 当前约定总览

- 本仓只做汉化，不做功能增强。
- `raw` 只负责官方上游镜像，不承载汉化主线。
- `cntrandingagents` 才是正式汉化仓。
- Windows 只负责本地镜像、应急副本和文档入口。
- Ubuntu 是唯一正式主工作树。
- GitHub 是主仓与主发布仓。
- Gitee 是镜像仓与国内发布源。
- AI 或自动化执行默认按 `11-AI自动执行文档与检查清单.md` 启动。

## 3. 必读文档列表

1. [01-汉化范围与非目标.md](d:/tranding/tranding_agents_cn/cntrandingagents/docs/01-项目约定/01-汉化范围与非目标.md)
2. [02-Windows与Ubuntu协作约定.md](d:/tranding/tranding_agents_cn/cntrandingagents/docs/01-项目约定/02-Windows与Ubuntu协作约定.md)
3. [03-仓库角色与同步策略说明.md](d:/tranding/tranding_agents_cn/cntrandingagents/docs/01-项目约定/03-仓库角色与同步策略说明.md)
4. [04-仓库与远端清单.md](d:/tranding/tranding_agents_cn/cntrandingagents/docs/01-项目约定/04-仓库与远端清单.md)
5. [05-SSH与令牌迁移说明.md](d:/tranding/tranding_agents_cn/cntrandingagents/docs/01-项目约定/05-SSH与令牌迁移说明.md)
6. [06-上游同步与汉化分层规则.md](d:/tranding/tranding_agents_cn/cntrandingagents/docs/01-项目约定/06-上游同步与汉化分层规则.md)
7. [07-允许修改的文件类型与改动边界.md](d:/tranding/tranding_agents_cn/cntrandingagents/docs/01-项目约定/07-允许修改的文件类型与改动边界.md)
8. [08-翻译术语表与风格约定.md](d:/tranding/tranding_agents_cn/cntrandingagents/docs/01-项目约定/08-翻译术语表与风格约定.md)
9. [09-Windows本地Git防误操作约定.md](d:/tranding/tranding_agents_cn/cntrandingagents/docs/01-项目约定/09-Windows本地Git防误操作约定.md)
10. [10-发布与镜像规则.md](d:/tranding/tranding_agents_cn/cntrandingagents/docs/01-项目约定/10-发布与镜像规则.md)
11. [11-AI自动执行文档与检查清单.md](d:/tranding/tranding_agents_cn/cntrandingagents/docs/01-项目约定/11-AI自动执行文档与检查清单.md)

## 4. 新成员阅读顺序

1. 先看“本仓到底做什么，不做什么”。
2. 再看“默认在哪台机器上工作，在哪台机器上执行 Git”。
3. 再看“`raw` 和 `cntrandingagents` 的关系”。
4. 再看“哪些文件允许改，哪些不允许改”。
5. 再看“Windows 本地 Git 为什么默认禁止直接提交/推送”。
6. 最后再看“发布怎么做、GitHub/Gitee 怎么同步，以及 AI 默认如何自动执行整套流程”。

## 5. 后续文档维护规则

- 规则类文档只写长期有效约定，不写一次性动作。
- 一次性动作写进 `docs/02-执行记录`。
- 每轮官方同步的细节写进 `docs/03-上游同步`。
- 如某条约定已过时，优先更新原文，不新增冲突版本。

## 6. 一句话结论

`cntrandingagents` 的文档顺序不是“想到什么写什么”，而是先锁边界，再锁协作，再锁同步，最后才进入具体执行。
