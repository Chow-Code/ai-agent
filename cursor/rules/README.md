# Cursor 规则索引（`.mdc`）

## 始终加载（短）

| 文件 | 说明 |
|------|------|
| `harness-always.mdc` | Harness 底线；门禁与 Hook 说明见内文 |
| `requirement-plan-before-code.mdc` | 改仓库前确认需求 + `docs/plans/` 计划（新建/更新）再执行 |
| `temporal-data.mdc` | 问「当前时间」等须用工具取实时时间 |
| `subagent-dispatch.mdc` | 可拆任务优先 Task 派发 Subagent |

## 按需 / 按路径（`alwaysApply: false` + `globs`）

编辑或上下文涉及匹配路径时，由 Cursor 按条件挂上；**改 `.go` 时**会带上 `code-style`、`code-quality`、`ddd-architecture`（均为 `**/*.go`）。未挂上时可 `@` 对应 `.mdc`。

| 文件 | 说明 |
|------|------|
| `testing.mdc` | qa/integration、BDD |
| `proto-and-handler.mdc` | proto、handler、生成 |
| `deployment-testing.mdc` | deploy、跑测试前启服 |
| `gm.mdc` | GM |
| `storage.mdc` | Redis、仓储 |
| `code-style.mdc` | Go 风格、DDD 配套 |
| `code-quality.mdc` | tlog、WorkPool |
| `ddd-architecture.mdc` | DDD 分层 |
| `domain-cache-registry.mdc` | Registry（domain/application/infrastructure） |
| `development-documentation.mdc` | docs/design/server |
| `specify-rules.mdc` | Specify |

## 工作流契约（非 `.mdc`）

| 文件 | 用途 |
|------|------|
| `.cursor/docs/workflow-gate-contract.md` | `workflow-gate` JSON、phase、bdd_qa 仅 `qa/integration`、白名单与 hook |

## Cursor 命令（`.cursor/commands/*.md`）

对话中可 **`@命令名`**（与文件名一致，不含 `.md`）。与成员私服/deploy 相关：

| 命令 | 用途 |
|------|------|
| `private-server` | 新增成员私服：`deploy/{姓名}.sh`、`login.toml`、战斗服地址、冲突检查（详见该文件） |

## Skill

| Skill | 用途 |
|-------|------|
| `deploy-tool` | 启停服、配置中心 |
| `gm-command` | GM 列表 |
| `proto-codegen-tool` / `handler-generator-tool` | 生成 |
| `bdd-qa` | qa/integration、BDD 全文 |

## 已合并（勿引用旧名）

- `bdd` + `api-testing` → `testing.mdc`
- `protocols` + `game-concepts` → `proto-and-handler.mdc`
