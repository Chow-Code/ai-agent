#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按 Cursor 事件拆分的 Hook 实现。

- 事件名字符串：**`hook_event_names`**（常量，与 `hooks.json` 一致）
- 策略注册：**`registry.register_strategy`**，由各 `events/*.py` 在 import 时调用
- 聚合表：**`EVENT_STRATEGY_FACTORIES`**（所有子模块 import 完毕后生成）
"""
from __future__ import annotations

from . import (
    after_agent_response,
    after_agent_thought,
    after_file_edit,
    after_mcp_execution,
    after_tab_file_edit,
    before_mcp_execution,
    before_read_file,
    before_shell_execution,
    before_submit_prompt,
    before_tab_file_read,
    post_tool_use,
    post_tool_use_failure,
    pre_compact,
    pre_tool_use,
    session_end,
    session_start,
    stop,
    subagent_start,
    subagent_stop,
)
from .base import HookEventStrategy, HookInvocation
from .hook_event_names import (
    AFTER_AGENT_RESPONSE,
    AFTER_AGENT_THOUGHT,
    AFTER_FILE_EDIT,
    AFTER_MCP_EXECUTION,
    AFTER_TAB_FILE_EDIT,
    BEFORE_MCP_EXECUTION,
    BEFORE_READ_FILE,
    BEFORE_SHELL_EXECUTION,
    BEFORE_SUBMIT_PROMPT,
    BEFORE_TAB_FILE_READ,
    POST_TOOL_USE,
    POST_TOOL_USE_FAILURE,
    PRE_COMPACT,
    PRE_TOOL_USE,
    SESSION_END,
    SESSION_START,
    STOP,
    SUBAGENT_START,
    SUBAGENT_STOP,
)
from .registry import (
    StrategyFactory,
    get_event_strategy_factories,
    register_strategy,
)

# 子模块 import 副作用已完成 register_strategy
EVENT_STRATEGY_FACTORIES = get_event_strategy_factories()

__all__ = [
    "EVENT_STRATEGY_FACTORIES",
    "HookInvocation",
    "HookEventStrategy",
    "StrategyFactory",
    "get_event_strategy_factories",
    "register_strategy",
    "SESSION_START",
    "SESSION_END",
    "BEFORE_SUBMIT_PROMPT",
    "SUBAGENT_START",
    "SUBAGENT_STOP",
    "PRE_TOOL_USE",
    "POST_TOOL_USE",
    "POST_TOOL_USE_FAILURE",
    "BEFORE_SHELL_EXECUTION",
    "BEFORE_MCP_EXECUTION",
    "AFTER_MCP_EXECUTION",
    "BEFORE_READ_FILE",
    "AFTER_FILE_EDIT",
    "PRE_COMPACT",
    "STOP",
    "AFTER_AGENT_RESPONSE",
    "AFTER_AGENT_THOUGHT",
    "BEFORE_TAB_FILE_READ",
    "AFTER_TAB_FILE_EDIT",
]
