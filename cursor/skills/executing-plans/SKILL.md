---
name: executing-plans
description: 在已有 BDD 书面实施计划、需在独立会话中执行并带评审检查点时使用
---

# 执行计划

## 概述

加载计划 → 批判性审阅 → 执行全部任务 → 完成后汇报。

**计划形态：** 须为 **`writing-plans` 产出的 BDD 实施计划**（Given-When-Then / 可断言 Then）。若发现计划仍是纯 TDD 套话或无 Then，先回到 `writing-plans` 补全，再执行。

**开始时宣告：**「我使用 executing-plans 技能来实施本 **BDD** 计划。」

**说明：** 若有子代理能力，**Agents Team** 工作流效果更好。在 **Cursor** 中若支持 Task 子代理，优先用 `agents-team:subagent-driven-development`，而非本技能。

## 流程

### 第 1 步：加载并审阅计划

1. 读计划文件  
2. 批判性审阅 — 对计划有疑问或顾虑先列出  
3. 有顾虑：与协作者沟通后再开始  
4. 无顾虑：创建 TodoWrite 并继续  

### 第 2 步：执行任务

对每个任务：
1. 标为 in_progress  
2. 严格按步骤执行（计划应已拆成小步；**验收以 BDD Then 为准**）  
3. 按计划运行验证（`qa/integration` 等 BDD 用例，或任务写明的可运行检查）  
4. 标为 completed  

### 第 3 步：完成开发

全部任务完成并验证后：
- 宣告：「我使用 finishing-a-development-branch 技能来收尾。」
- **必选子技能：** `agents-team:finishing-a-development-branch`  
- 按该技能跑测试、展示选项、执行所选路径  

## 何时停并求助

**立即停止执行当：**
- 遇到阻塞（缺依赖、测试失败、指令不清）  
- 计划有关键缺口无法开始  
- 不理解某条指令  
- 验证反复失败  

**先澄清再猜。**

## 何时回到前面步骤

**回到审阅（第 1 步）当：**
- 协作者根据你的反馈更新了计划  
- 根本方向需要重新考虑  

**不要硬扛阻塞** — 问清楚。

## 记住

- 先批判性审阅计划  
- 严格按步骤  
- 不跳过验证  
- 计划要求引用技能时要跟  
- 阻塞就停，不要猜  
- 未经用户明确同意不要在 main/master 上直接开始实现  

## 集成

**相关工作流技能：**
- **agents-team:using-git-worktrees** — 开始前必须：隔离工作区  
- **agents-team:writing-plans** — 本技能所执行的计划由该技能产出  
- **agents-team:finishing-a-development-branch** — 全部任务完成后收尾  
