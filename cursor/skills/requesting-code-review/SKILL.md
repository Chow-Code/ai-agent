---
name: requesting-code-review
description: 完成任务、实现较大功能或合并前需要验证工作是否符合要求时使用
---

# 请求代码评审

派发 code-reviewer 子代理（模板见本目录 `code-reviewer.md`，属 `requesting-code-review` 技能），在问题扩散前拦截。评审者只获得**精心裁剪的上下文**——不要塞满会话历史。这样评审聚焦产物，你也保留上下文继续工作。

**核心原则：** 早评审、常评审。

## 何时请求

**必须：**
- subagent-driven-development 中**每个任务后**  
- 重大功能完成后  
- 合并进 main 前  

**建议：**
- 卡住时（换视角）  
- 重构前（基线检查）  
- 修完复杂 bug 后  

## 如何请求

**1. 取 git SHA：**
```bash
BASE_SHA=$(git rev-parse HEAD~1)  # 或 origin/main
HEAD_SHA=$(git rev-parse HEAD)
```

**2. 按 `code-reviewer.md` 模板派发评审子代理**

占位符：
- `{WHAT_WAS_IMPLEMENTED}` — 你刚做了什么  
- `{PLAN_OR_REQUIREMENTS}` — 应该达成什么  
- `{BASE_SHA}` / `{HEAD_SHA}` — 提交范围  
- `{DESCRIPTION}` — 简短摘要  

**3. 处理反馈：**
- Critical：立即修  
- Important：继续前先修  
- Minor：可记 backlog  
- 评审有误：有理有据反对  

## 与工作流集成

**子代理驱动开发：** 每任务后评审（任务来自 **BDD** 计划，对照 Then）。  
**执行计划：** 可按批次（如每 3 个任务）评审；计划须为 **BDD**。  
**临时开发：** 合并前或卡住时评审。  

## 危险信号

**绝不：**
- 因「很简单」跳过评审  
- 忽略 Critical  
- Important 未修就继续  
- 对有效技术反馈抬杠  

**评审有误：** 用技术理由与测试/代码证明。  

模板见：`requesting-code-review/code-reviewer.md`
