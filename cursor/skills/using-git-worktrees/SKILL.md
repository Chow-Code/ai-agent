---
name: using-git-worktrees
description: 开始需要与当前工作区隔离的功能开发，或执行实施计划之前使用——创建隔离的 git worktree，并做目录选择与安全检查
---

# 使用 Git Worktree

## 概述

Worktree 在**同一仓库**下提供多个工作目录，可多分支并行，无需频繁切换。

**核心原则：** 系统化选目录 + 安全验证 = 可靠隔离。

**开始时宣告：**「我使用 using-git-worktrees 技能建立隔离工作区。」

## 目录选择顺序

### 1. 查已有目录

```bash
ls -d .worktrees 2>/dev/null   # 优先（隐藏）
ls -d worktrees 2>/dev/null
```

若存在则用该目录；两者都有时优先 `.worktrees`。

### 2. 查 `CURSOR.md` / `AGENTS.md` / 项目约定

```bash
grep -i "worktree.*director" CURSOR.md AGENTS.md 2>/dev/null
```

若写明偏好，直接采用，不必再问。

### 3. 询问用户

若无目录且无约定：

```
未找到 worktree 目录。要在哪里创建？

1. .worktrees/（项目内、隐藏）
2. ~/.config/agents-team/worktrees/<项目名>/（全局）

选哪一项？
```

## 安全验证（项目内目录）

**在创建 worktree 前必须确认目录已被 ignore：**

```bash
git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null
```

**若未 ignore：** 应立刻补 `.gitignore` 并提交，再创建。  
**原因：** 避免误把 worktree 内容提交进仓库。

**全局目录**（`~/.config/...`）无需项目内 gitignore 检查。

## 创建步骤

1. **项目名：** `basename "$(git rev-parse --show-toplevel)"`  
2. **创建：** `git worktree add "<path>" -b "<branch>"`  
3. **依赖安装：** 按 `package.json` / `Cargo.toml` / `go.mod` 等自动检测  
4. **基线测试：** 跑项目标准测试命令；失败则汇报并询问是否继续  
5. **汇报：**  
   ```
   Worktree 就绪：<full-path>
   测试通过（<N> 个，0 失败）
   可开始 <feature-name>
   ```

## 常见错误

- 未验证 ignore 就建项目内 worktree  
- 擅自假设目录位置  
- 基线测试失败仍强行继续  
- 写死安装命令而不自动检测  

## 危险信号

**绝不：** 项目内 worktree 不查 ignore；跳过基线测试；测试失败不问就继续；有歧义时不查项目约定。  
**务必：** 现有目录 > 项目约定 > 询问；项目内必须 ignore；自动检测依赖与测试命令。

## 集成

**调用方：** brainstorming（实现前）、subagent-driven-development、executing-plans、任何需要隔离工作区的技能。  
**配对：** finishing-a-development-branch — 完成后清理 worktree。
