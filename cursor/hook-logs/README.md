# Cursor Hook 调试日志目录

| 路径 | 说明 |
|------|------|
| **`sessions/<id>/lifecycle.log`** | 按**会话**分目录追加：每次经 `run_hook.py` 触发的事件一行；`sessionStart` / `sessionEnd` 另有里程碑行。`<id>` 来自 Hook **stdin JSON** 中的会话类字段（如 `conversationId`、`sessionId` 等，实现会递归查找），或通过环境变量 **`CURSOR_HOOK_SESSION_ID`** 覆盖；若均无法得到则使用 **`default`**。**`sessionEnd`**：快照在返回 JSON 的 **`user_message`/`userMessage`**。**`stop`**：官方 schema 仅用 **`followup_message`/`followupMessage`**（`user_message` 无效）。二者均 **stderr** 打印快照。 |
| **`LAST_EXIT_NOTICE.txt`** | **每次 `sessionEnd` 或 `stop` 覆盖写入**：与上条快照相同的正文。当 Cursor **不在聊天里展示** hook stdout 时，仍可在仓库根相对路径 **`.cursor/hook-logs/LAST_EXIT_NOTICE.txt`** 打开查看（强制可观察）。 |

- 编码：**UTF-8**
- 建议**不入库**：根目录 `.gitignore` 已忽略 `hook-logs/sessions/`
- 与 **`.cursor/hooks-debug.log`** 互补（后者偏单行调试；本文件偏**整轮顺序**）

实现见：`.cursor/hooks/events/hook_lifecycle_log.py`、`.cursor/hooks/events/hook_session_id.py`
