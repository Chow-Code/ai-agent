---
name: finishing-a-development-branch
description: 实现已完成、测试通过、需要决定如何合并或集成时使用——引导选择合并、PR 或清理等结构化选项
---

# 收尾开发分支

## 概述

用清晰选项引导开发收尾，并执行所选流程。

**核心原则：** 验证测试 → 展示选项 → 执行选择 → 清理。

**开始时宣告：**「我使用 finishing-a-development-branch 技能来收尾。」

## 流程

### 第 1 步：验证测试

**展示选项前必须先确认测试通过：**

```bash
# 按项目选择
npm test / cargo test / pytest / go test ./...
```

**若失败：**
```
测试失败（<N> 个）。须先修复再收尾：

[展示失败]

在测试通过前不能进行合并/PR。
```

停止，不要进入第 2 步。

**若通过：** 进入第 2 步。

### 第 2 步：确定基线分支

```bash
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null
```

或确认：「本分支从 main 分出 — 是否正确？」

### 第 3 步：展示选项

**仅展示以下 4 项：**

```
实现已完成。你希望怎么做？

1. 本地合并回 <base-branch>
2. 推送并创建 Pull Request
3. 保持分支不动（稍后我自己处理）
4. 丢弃本工作

选哪一项？
```

选项保持简短，勿加冗长解释。

### 第 4 步：执行选择

#### 选项 1：本地合并

```bash
git checkout <base-branch>
git pull
git merge <feature-branch>
<测试命令>
# 若通过
git branch -d <feature-branch>
```

然后：工作区清理（第 5 步）

#### 选项 2：推送并建 PR

```bash
git push -u origin <feature-branch>
gh pr create --title "<title>" --body "..."
```

然后：工作区清理（第 5 步）

#### 选项 3：保持

汇报：「保留分支 <name>。工作区保留在 <path>。」  
**不要**清理工作区。

#### 选项 4：丢弃

**先确认：**
```
将永久删除：
- 分支 <name>
- 提交：<commit-list>
- 工作区 <path>

输入 discard 确认。
```

确认后执行删除分支等操作，然后工作区清理（第 5 步）。

### 第 5 步：清理工作树

**选项 1、2、4：**

```bash
git worktree list | grep $(git branch --show-current)
```

若在 worktree 中：
```bash
git worktree remove <worktree-path>
```

**选项 3：** 保留工作树。

## 快速对照

| 选项 | 合并 | 推送 | 保留工作树 | 删分支 |
|------|------|------|------------|--------|
| 1. 本地合并 | ✓ | - | - | ✓ |
| 2. Create PR | - | ✓ | ✓ | - |
| 3. 保持 | - | - | ✓ | - |
| 4. 丢弃 | - | - | - | ✓（强删） |

## 常见错误

- **跳过测试验证** — 合并坏代码、建失败 PR  
- **开放式提问** — 「接下来怎么办？」应改为 4 个固定选项  
- **错误清理 worktree** — 选项 2、3 可能需要保留  
- **丢弃无确认** — 必须输入 `discard` 确认  

## 集成

**由以下调用：**
- **subagent-driven-development**（第 7 步）— 全部任务完成后  
- **executing-plans**（第 5 步）— 全部批次完成后  

**与以下配合：**
- **using-git-worktrees** — 清理该技能创建的工作树  
