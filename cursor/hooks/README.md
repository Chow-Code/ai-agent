# Cursor Hooks 与工作流门禁（workflow-gate）

**`.cursor/hooks.json`** 已注册 **19** 个事件名（见下表）；**以当前 Cursor 版本是否支持为准**——不支持的键可能被 IDE 忽略，可删掉对应条目避免干扰。

**唯一入口**：`hooks.json` 中一律为 **`python3 .cursor/hooks/run_hook.py <事件名>`**。  
**按事件扩展**：每个 Cursor 事件一个 **`events/*.py`**，在模块末尾 **`register_strategy(常量, build)`** 登记到 **`registry`**；**`hook_event_names.py`** 仅存事件名字符串常量（与 **`hooks.json`** 一致）。**`__init__.py`** 在 import 全部子模块后 **`EVENT_STRATEGY_FACTORIES = get_event_strategy_factories()`**。同目录共享：**`paths.py`**、**`hook_debug_log.py`**、**`hook_lifecycle_log.py`**（**`.cursor/hook-logs/sessions/<id>/lifecycle.log`** 按会话整轮轨迹）、**`ten_round_state.py`**、**`probe_support.py`**。

## 目录结构（摘要）

```text
.cursor/
├── hook-logs/               # Hook 调试（见 hook-logs/README.md）
│   ├── README.md
│   └── lifecycle.log        # 按时间追加，gitignore
└── hooks/
    ├── run_hook.py          # 唯一 CLI 入口（每次执行前写 lifecycle.log 一行）
    └── events/
        ├── __init__.py      # import 子模块后生成 EVENT_STRATEGY_FACTORIES
        ├── hook_event_names.py
        ├── registry.py
        ├── paths.py
        ├── hook_debug_log.py
        ├── hook_lifecycle_log.py
        ├── ten_round_state.py
        ├── base.py
        ├── probe_support.py
        ├── session_start.py
        ├── before_submit_prompt.py
        ├── session_end.py
        ├── subagent_stop.py
        └── …（其余事件模块）
```

## 本仓库注册的事件（与 `EVENT_STRATEGY_FACTORIES` 一致）

| 分类 | 事件名 | 说明（摘要） |
|------|--------|----------------|
| 会话 | **`sessionStart`** / **`sessionEnd`** | 会话生命周期 |
| Prompt | **`beforeSubmitPrompt`** | 提交前校验 / 注入 |
| Subagent | **`subagentStart`** / **`subagentStop`** | Task 子代理起止 |
| 通用工具 | **`preToolUse`** / **`postToolUse`** / **`postToolUseFailure`** | 任意工具前后 / 失败 |
| Shell | **`beforeShellExecution`** | 终端命令执行前（未注册 `afterShellExecution`） |
| MCP | **`beforeMCPExecution`** / **`afterMCPExecution`** | MCP 调用前后 |
| 文件（Agent） | **`beforeReadFile`** / **`afterFileEdit`** | 读文件前 / 编辑后 |
| 上下文 | **`preCompact`** | 上下文压缩前 |
| Agent | **`stop`** / **`afterAgentResponse`** / **`afterAgentThought`** | 结束 / 响应与 thought 追踪 |
| Tab | **`beforeTabFileRead`** / **`afterTabFileEdit`** | 行内补全读文件 / 编辑后 |

**业务实现**：`sessionStart`、`beforeSubmitPrompt`、`sessionEnd`、`subagentStop`。其余默认为 **探测**（`probe_support`：一行日志 + 放行类 JSON）。**JSON 形状以 Cursor 版本为准**，见 **`events/probe_support.py`** 中 **`_DEFAULTS`**。

官方/社区文档（如 [Cursor Changelog](https://cursor.com/changelog)、[GitButler · Cursor Hooks](https://blog.gitbutler.com/cursor-hooks-deep-dive)）可能随版本增减事件名；**是否触发以本机 IDE 为准**。

**调试**：**`.cursor/hooks-debug.log`**（已 `.gitignore`）。**`hook-logs/sessions/<id>/lifecycle.log`** 记录整轮 hook 顺序；**`sessionEnd`**：lifecycle 快照写入 **`user_message` / `userMessage`**（及 `continue`），并 **stderr** + **`.cursor/hook-logs/LAST_EXIT_NOTICE.txt`**。**`stop`**（Agent 本轮结束）：Cursor 官方 **StopOutput 只有 `followup_message`**；**`stop`** 的 `followup_message` 为**短统计**（行数、pid 数、时间跨度、路径），**全文快照**仅在 **LAST_EXIT_NOTICE.txt** 与 **stderr**。**输出面板 →「Hooks」** 可看 INPUT/OUTPUT；若仍空对象，多为 **Windows 上已知解析问题**（见 Cursor 论坛）。每个事件文件均有本事件的 **`main()`**（探测类多调用 **`probe_support.run_probe`**；**`stop`** 见 **`events/stop.py`**）。若 IDE 加载 `hooks.json` 报错，可暂时删掉不支持的键或对应 `run_hook.py` 条目。

## 术语（与 Cursor 事件对齐）

| 你想要的语义 | Cursor 事件 | 实现文件（`events/`） |
|-------------|-------------|----------------------|
| **新开会话/Composer** | **`sessionStart`** | **`session_start.py`** |
| **本条用户输入送入模型前** | **`beforeSubmitPrompt`** | **`before_submit_prompt.py`** |
| **子代理本轮结束** | **`subagentStop`** | **`subagent_stop.py`** |
| **会话结束** | **`sessionEnd`** | **`session_end.py`** |

**区分**：**`sessionStart`** 与 **每条发送前**的 **`beforeSubmitPrompt`** 不是同一事件；侧车逻辑见各模块注释。

## 十轮侧车（可选）

| 组件 | 作用 |
|------|------|
| **`events/ten_round_state.py`** | 状态 `.cursor/ten-round-state.json`；**beforeSubmitPrompt** 每次成功提交前 **user_submits += 1**（门禁拦截时不增加）；**sessionEnd** 时 **exit_total += 1**（累计退出次数，默认上限见 `exit_total_cap`） |
| **`events/session_start.py`** | 新会话时重置**本轮** `user_submits`（从第 1 次发送起算）；保留累计 **exit_total**（可选配置见下） |
| **`events/session_end.py`** | 结束时 ① 比对本轮 `user_submits` 与 `target_rounds`；② **exit_total** 加 1，并在 `user_message` 中报告；**无状态文件时也会输出说明**，避免误判 Hook 未执行 |

**无 sessionStart 时**：若 IDE 未触发 **sessionStart**，首次 **beforeSubmitPrompt** 会**懒创建** `.cursor/ten-round-state.json` 并照常计数「第 n/目标 次」。

**设置页**：若显示「已配置 N 个 Hook」但列表未全部展开，请向下滚动查看 **sessionEnd** 等是否已注册。

可选 **`.cursor/ten-round-config.json`** 示例：

```json
{
  "target_rounds": 10,
  "exit_total_cap": 10,
  "reset_exit_total_on_session_start": false,
  "block_session_end_until_target": true
}
```

- **`reset_exit_total_on_session_start`**：为 `true` 时，每次 **sessionStart** 将 **exit_total** 置回 **0**（新对话从零累计退出；默认 `false` 为跨会话累计）。
- **`block_session_end_until_target`**（默认 **`true`**）：**未满** `target_rounds` 条用户发送时，**sessionEnd** 返回 **`continue: false`** 并**不**给 **exit_total** +1；**满**后再结束则 +1。设为 **`false`** 时恢复「任意结束都 +1」的旧行为。若 IDE 忽略 `continue:false`，仍以提示为准（已知部分版本对 Hook 响应支持不完整）。

关闭侧车：删除 **`.cursor/ten-round-state.json`**（或不用 `sessionStart`，且不发消息前无状态文件则不计数）。

## 文件（门禁相关）

| 位置 | 作用 |
|------|------|
| **`events/before_submit_prompt.py`** | 输出 `continue` JSON；可选 **`block_submit`**、**`additional_context`**；合并十轮注入 |
| **`events/subagent_stop.py`** | **`subagentStop`**：从 Cursor JSON 中找 **`workflow-gate`** 并合并状态；亦可经 **`run_hook.py subagentStop <file.md>`** 手动落盘 |

## `.cursor/hooks.json`

| 事件 | 命令 |
|------|------|
| 全部已注册事件 | `python3 .cursor/hooks/run_hook.py <事件名>` |

路径以**仓库根**为当前目录。

### 手动测试（十轮）

```bash
python3 .cursor/hooks/run_hook.py sessionStart
echo '{}' | python3 .cursor/hooks/run_hook.py beforeSubmitPrompt
python3 .cursor/hooks/run_hook.py sessionEnd
```

### 手动落盘（不依赖 Cursor）

```bash
python3 .cursor/hooks/run_hook.py subagentStop reply.md
cat reply.md | python3 .cursor/hooks/run_hook.py subagentStop
```

## 与规则

- 契约：`.cursor/docs/workflow-gate-contract.md`
- Harness 底线：`.cursor/rules/harness-always.mdc`
