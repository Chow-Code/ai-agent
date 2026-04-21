# Gemini CLI 工具映射

技能正文若出现「Claude Code / Cursor 侧工具名」，在 **Gemini CLI** 上使用等价能力：

| 技能中的说法 | Gemini CLI 等价 |
|-------------|-----------------|
| `Read` | `read_file` |
| `Write` | `write_file` |
| `Edit` | `replace` |
| `Bash` | `run_shell_command` |
| `Grep` | `grep_search` |
| `Glob` | `glob` |
| `TodoWrite` | `write_todos` |
| `Skill` | `activate_skill` |
| `WebSearch` | `google_web_search` |
| `WebFetch` | `web_fetch` |
| `Task`（子代理） | **无等价** —— Gemini CLI 不支持子代理 |

## 无子代理时

Gemini CLI 没有与 `Task` 等价的子代理派发。依赖子代理的技能应退化为**单会话**执行（例如 `executing-plans`）。

**在 Cursor：** 使用 **Task 子代理**（若环境提供）或本会话内逐步执行。

## Gemini 独有工具（无 Cursor 直接对应）

| 工具 | 用途 |
|------|------|
| `list_directory` | 列目录 |
| `save_memory` | 跨会话写入 GEMINI.md |
| `ask_user` | 结构化询问用户 |
| `tracker_create_task` | 任务管理 |
| `enter_plan_mode` / `exit_plan_mode` | 改动前只读调研模式 |
