# 工作流门禁契约（workflow-gate）

本文件为 **bdd_qa / hook / 状态机** 的**可执行约定**来源；`.cursor/rules` 中长流程仅作索引，**以本文 + `.cursor/hooks/` 脚本为准**（若已配置）。

## 门禁如何「处理」（本仓库约定）

| 层级 | 作用 |
|------|------|
| **契约（本文）** | 定义 `workflow-gate` 块长什么样、`phase`/`outcome` 含义、bdd_qa 命令、回退表、状态文件字段。 |
| **Hook 落地** | **`subagentStop`** 经 **`run_hook.py subagentStop`** → **`.cursor/hooks/events/subagent_stop.py`**（解析与合并）→ **`.cursor/workflow-state.json`**（本仓库 **`hooks.json`** 注册；主 Agent 回合若需落盘可手动 **`run_hook.py subagentStop` + Markdown**）。 |
| **助手输出** | Subagent 在回复末尾带 **`workflow-gate`** 块，**供回合结束时的 Hook 抓取**；**不以**模型口头「过了」为准。 |

**厘清（易混）**：**不是** Hook 脚本**拉起**主流程、Task 或 Subagent。流程由对话、主 Agent、Cursor Task 等**先**跑完；**仅在** Cursor 触发 **`subagentStop`**（子代理本轮**已结束**）时，本仓库注册的入口才执行 **`events/subagent_stop.py`** 做**侧车**：解析 payload、写状态。**本条用户输入进模型前**由 **`beforeSubmitPrompt`** → **`events/before_submit_prompt.py`**（与 **`sessionStart`** 新开会话**不是**同一事件）。**Hook 是侧车，不是流程入口。**

**边界**：Hook **不**向模型注入规则文本；**不**保证「未过门禁」时自动禁止发送。**人 / 主 Agent** 以 **`.cursor/workflow-state.json`** 与本文 §4、§6 为准做阶段判断与回退。

## 1. 助手消息末尾块（强制）

每个参与交付流的 Subagent 在**最后一次助手回复**末尾输出 **JSON** 代码块，围栏语言名固定为 **`workflow-gate`**：

````markdown
```workflow-gate
{ "subagent": "...", "phase": "...", "outcome": "...", ... }
```
````

### 1.1 必填字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `subagent` | string | 与 `.cursor/agents/*.md` 的 YAML `name` **完全一致** |
| `phase` | string | 见 §2 |
| `outcome` | string | `success` \| `failure` \| `needs_revision`（后者多用于计划/架构类） |

### 1.2 可选字段

| 字段 | 说明 |
|------|------|
| `next_action` | 建议下一动作（枚举，便于人读） |
| `evidence` | 简短证据：如 `go test` 最后一行、失败用例名 |

---

## 2. phase 枚举

| phase | 含义 | 通常 subagent |
|-------|------|----------------|
| `requirement_split` | 需求拆分产出/修订计划 | `requirement-splitter` |
| `architect_review` | 架构师审核计划 | `architect` |
| `pb_align` | 阶段0 PB 与客户端对齐 | 主 Agent / 约定 |
| `code` | 编码阶段结束 | `executor` |
| `bdd_qa` | BDD 集成测试阶段结束 | `qa-tester` |
| `codereview` | 代码评审结束 | `codereview` |
| `pr` | PR 收尾 | 约定 |

**编码 vs 测试**：用 `phase`=`code` 与 `bdd_qa` 区分；若与 `subagent` 不一致，以 **`phase`** 定回退（见 §4）。

---

## 3. bdd_qa（测试门禁）

### 3.1 默认范围（强制）

- **仅** `qa/integration/` 下 Go 测试包。
- **默认命令**（全量）：`go test -v ./qa/integration/...`（在仓库根目录执行）。
- **按领域**：`go test -v ./qa/integration/{领域}/...`（领域名与目录一致，如 `account`）。
- **不包含**：`srv/`、`domain/` 等**单元测试**不作为本门禁；**不包含** `qa/api/`（YAML 文档，非测试包）。
- **禁止**用 `go test ./...` 全仓库代替本门禁。

### 3.2 本领域路径（与仓库对齐）

| 类型 | 路径示例 |
|------|----------|
| BDD | `qa/integration/{领域}/`（如 `qa/integration/account/`） |
| API 文档 | `qa/api/{领域}.yaml` |
| 领域代码 | `domain/<子域>/...`（分层见 `ddd-architecture.mdc`） |

**新增领域**：新建 `qa/integration/{新领域}/` 与对应 `qa/api/{新领域}.yaml`。  
**日常开发**：优先只改当前领域目录及对应 integration 用例。

### 3.3 扩展其它 `qa/*` 可测目录（如未来 `qa/e2e`）

须在**本文档**增加白名单（见 §3.4），并更新 hook；**未写入前** hook 与 bdd_qa **仍只认** `qa/integration/...`。

### 3.4 `go_test_path_allowlist`（显式放开）

| 路径（仓库根 `go test` 参数） | 状态 |
|-------------------------------|------|
| `./qa/integration/...` | **默认启用** |

新增一行即表示将该路径纳入 bdd_qa 可选/全量范围；**未列出路径不得**作为门禁替代默认项。

### 3.4 outcome

- `bdd_qa` 的 `outcome=success` **仅当**上述 `go test` **实际退出码为 0**，且建议在 `evidence` 中注明命令摘要。

---

## 4. outcome 与回退（摘要）

| phase | success | failure / needs_revision |
|-------|---------|---------------------------|
| `architect_review` | 进入 `pb_align` 或后续 | `needs_revision` 或 failure → 回到 `requirement_split` |
| `code` | 进入 `bdd_qa` | 回到 `code` |
| `bdd_qa` | 进入 `codereview` | 回到 `code` |
| `codereview` | 进入 `pr` | 回到 `code`，且须**先再跑** `bdd_qa` 再送审 |

---

## 5. 每 phase 最大尝试次数

- 默认 **`max_attempts_per_phase`** = **5**（可在 `.cursor/workflow-state.json` 或单独配置覆盖）。
- 同一 `phase` 连续 `failure` / `needs_revision`（若计次）累加；**成功并离开该 phase** 后该 phase 计数清零。
- **超限**：停止自动进入下一阶段，须人工处理或重置状态。

---

## 6. 状态文件（`.cursor/workflow-state.json`）

**建议不入库**（见根目录 `.gitignore`）。由 **hook 或脚本** 写入；主 Agent 以文件为准，不信口头「通过了」。

首次写入前脚本会生成最小 `{}`；合并后常见字段示例如下（仅作参考，以实际 `jq` 合并结果为准）：

```json
{
  "current_phase": "bdd_qa",
  "last_subagent": "qa-tester",
  "last_gate_result": "success",
  "max_attempts_per_phase": 5,
  "attempts_by_phase": {
    "requirement_split": 0,
    "architect_review": 0,
    "code": 0,
    "bdd_qa": 0,
    "codereview": 0
  },
  "block_submit": false,
  "block_submit_message": ""
}
```

**`block_submit`（可选）**：与 **`beforeSubmitPrompt`** Hook 联动；若未在 **`hooks.json`** 中注册 **`beforeSubmitPrompt`**，则**不会在发送前自动拦截**。

---

## 7. Hook 脚本（门禁落地路径）

- **本条输入进模型前**：**`beforeSubmitPrompt`** → **`run_hook.py`** → **`events/before_submit_prompt.py`**（见 **`.cursor/hooks/README.md`**）。可与 **`workflow-state.json`** 的 **`block_submit`** 联动；并可选合并 **十轮侧车**（`.cursor/ten-round-state.json`，见同目录 README）。
- **新开会话 / 会话结束**：**`sessionStart`** / **`sessionEnd`** → **`run_hook.py`** → **`events/session_start.py`** / **`events/session_end.py`**（十轮计数与结束时校验；以 Cursor 是否触发该事件为准）。
- **子代理结束**：**`subagentStop`** → **`run_hook.py`** → **`events/subagent_stop.py`**（提取 \`\`\`workflow-gate → 合并 **`.cursor/workflow-state.json`**）。注册见 **`.cursor/hooks.json`**。
- 若某次事件的 payload **不含**助手全文，自动解析可能失败；可**手动**将含 `workflow-gate` 的回复存文件后执行 `python3 .cursor/hooks/run_hook.py subagentStop <file>`，仍属同一套**门禁处理**。

---

## 8. 参考

- Harness 底线：`.cursor/rules/harness-always.mdc`
- BDD 与接口测试：`.cursor/rules/testing.mdc`（合并原 bdd、api-testing 等约定）
- bdd-qa：`.cursor/skills/bdd-qa/SKILL.md`
