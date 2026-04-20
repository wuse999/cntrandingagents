# cntrandingagents Bootstrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bootstrap `cntrandingagents` as the formal Chinese translation repository with Windows local mirror protections, Ubuntu canonical worktree, and GitHub/Gitee remotes.

**Architecture:** Seed the new repository from the official `raw` mirror to preserve upstream history, then layer the governance docs on top. Treat Ubuntu as the only canonical working tree and install guard hooks in the Windows local mirror to keep Git actions on the Ubuntu side.

**Tech Stack:** Git, PowerShell, SSH, GitHub REST API, Gitee REST API

---

### Task 1: Verify external repository state and create missing remotes

**Files:**
- Modify: `d:\tranding\tranding_agents_cn\cntrandingagents\docs\01-项目约定\04-仓库与远端清单.md`
- Test: remote availability via `git ls-remote`

- [ ] Check whether `wuse999/cntrandingagents` exists on GitHub.
- [ ] Check whether `frpnat/cntrandingagents` exists on Gitee.
- [ ] Create the missing GitHub repository if absent.
- [ ] Create the missing Gitee repository if absent.
- [ ] Re-run `git ls-remote` against both remotes and confirm reachability.

### Task 2: Seed the local Windows repository from `raw`

**Files:**
- Modify: `d:\tranding\tranding_agents_cn\cntrandingagents\**`
- Test: `git status --short --branch`, `git remote -v`

- [ ] Back up the already-created governance docs from `cntrandingagents`.
- [ ] Replace the empty local directory with a clone seeded from `raw`.
- [ ] Restore the governance docs into the cloned repository.
- [ ] Reconfigure remotes to `origin`, `gitee`, and `upstream`.
- [ ] Commit the governance docs as the first `cntrandingagents` change.

### Task 3: Push bootstrap state and provision the Ubuntu canonical worktree

**Files:**
- Modify: Ubuntu `~/projects/cntrandingagents`
- Test: remote `git status --short --branch`, `git remote -v`

- [ ] Push the Windows-seeded repository to GitHub.
- [ ] Mirror the same state to Gitee.
- [ ] Create or refresh `~/projects/cntrandingagents` on Ubuntu from GitHub.
- [ ] Configure `origin`, `gitee`, and `upstream` on Ubuntu.
- [ ] Verify Ubuntu is on `main` and clean.

### Task 4: Install Windows local Git guard hooks

**Files:**
- Create: `d:\tranding\tranding_agents_cn\cntrandingagents\.git\hooks\pre-commit`
- Create: `d:\tranding\tranding_agents_cn\cntrandingagents\.git\hooks\pre-push`
- Test: hook file existence and message content

- [ ] Add `pre-commit` hook that blocks local Windows commits by default.
- [ ] Add `pre-push` hook that blocks local Windows pushes by default.
- [ ] Reference `CNTRANDINGAGENTS_ALLOW_WINDOWS_LOCAL_GIT=1` as the temporary override.
- [ ] Verify both hooks exist and contain the expected guidance.

### Task 5: Update docs to reflect real created state

**Files:**
- Modify: `d:\tranding\tranding_agents_cn\cntrandingagents\docs\01-项目约定\04-仓库与远端清单.md`
- Modify: `d:\tranding\tranding_agents_cn\cntrandingagents\docs\01-项目约定\05-SSH与令牌迁移说明.md`
- Test: document spot-check

- [ ] Replace “planned” remote wording with actual repository state.
- [ ] Record that the GitHub/Gitee repositories now exist.
- [ ] Record that Ubuntu worktree is provisioned and verified.
- [ ] Confirm the credential and remote instructions still match reality.
