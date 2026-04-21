# Codex 工具映射

技能正文若出现「Claude Code / Cursor 侧工具名」，在 **Codex** 上使用等价能力：

| 技能中的说法 | Codex 等价 |
|-------------|------------|
| `Task`（派子代理） | `spawn_agent` |
| 多次并行 `Task` | 多次 `spawn_agent` |
| Task 返回结果 | `wait` |
| Task 自动结束 | `close_agent` 释放槽位 |
| `TodoWrite` | `update_plan` |
| `Skill` / 读技能 | 按各产品加载技能的方式 |
| `Read` / `Write` / `Edit` | 使用本机文件工具 |
| `Bash` | 使用本机 shell |

**在 Cursor 本仓库：** 优先使用编辑器内置 **Read / 终端 / 子代理**，不必强行对应上表。

## 多代理（Codex）

在 Codex 配置 `~/.codex/config.toml` 中启用：

```toml
[features]
multi_agent = true
```

启用后方可使用 `spawn_agent` 等，以支持并行排查、子代理驱动开发等技能。
