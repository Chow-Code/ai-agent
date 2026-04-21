# 子代理（Subagents）说明

本目录存放 Cursor 的专属子代理配置。每个子代理是一个 Markdown 文件，含 YAML 头（元数据）与正文指令，供主 Agent **Task 派发**专项任务。

## 可用 Subagent

| 名称 | 文件 | 说明 |
|------|------|------|
| requirement-splitter | [requirement-splitter.md](requirement-splitter.md) | 需求拆分为 **BDD** 实施计划（writing-plans，计划一律 G/W/T），输出 `docs/plans/` |
| architect | [architect.md](architect.md) | 只读审核计划是否符合 DDD/Harness 前置；通过或需修订 |
| executor | [executor.md](executor.md) | 按计划编码与本地验证；门禁阶段 **code** |
| qa-tester | [qa-tester.md](qa-tester.md) | 跑 **bdd_qa**（默认仅 `qa/integration/...`） |
| codereview | [codereview.md](codereview.md) | 按 DDD 与代码规范评审；门禁阶段 **codereview** |
| request-chain-logging | [request-chain-logging.md](request-chain-logging.md) | Handler/AppService/Domain 补全 tlog |
| design-doc-sync | [design-doc-sync.md](design-doc-sync.md) | 同步 `docs/design/server/` 需求与开发文档 |

**派发**：主 Agent 见 `.cursor/rules/subagent-dispatch.mdc`。

## 门禁与 Hook（不靠长流程规则）

- **交付门禁**以 **`workflow-gate` JSON** + **`.cursor/docs/workflow-gate-contract.md`** 为准。
- **子代理结束**时 Cursor 调用 **`.cursor/hooks.json`** 里的 **`subagentStop`** → **`run_hook.py subagentStop`**（实现 **`.cursor/hooks/events/subagent_stop.py`**），把助手消息里的 **`workflow-gate`** 合并进 **`.cursor/workflow-state.json`**（**不是** Hook 脚本拉起对话或 Task）。详见 **`.cursor/hooks/README.md`**。
- 各 Subagent 须在**最后一次回复末尾**输出 **`workflow-gate`** 块。

## 使用方式示例

- 「用 architect 审核这份计划」
- 「用 qa-tester 跑 qa/integration」
- 「用 codereview 审这次 diff」

## 为何感觉「Subagent 没自动跑」？

**`.cursor/agents/*.md` 不会自动执行**；须主 Agent **Task 派发**或你**口头指定**子代理。这与「门禁由 Hook 在回合结束时落盘」是两件事：Hook 处理的是**已产生**的回复里的 `workflow-gate`，**不会**替你自动连点 Task。

## 规范

- 每个子代理 YAML 头里须有 `name` 与 `description`
- `name` 与 **workflow-gate** 里 `subagent` 字段须一致（见 `.cursor/docs/workflow-gate-contract.md`）
