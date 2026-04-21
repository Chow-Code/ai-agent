#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""探测类 Hook：无业务逻辑，只打一行「当前执行事件」日志 + Cursor 要求的 JSON。"""
from __future__ import annotations

import sys

from . import hook_debug_log
from . import ten_round_state
from .hook_event_names import (
    AFTER_AGENT_RESPONSE,
    AFTER_AGENT_THOUGHT,
    AFTER_FILE_EDIT,
    AFTER_MCP_EXECUTION,
    AFTER_TAB_FILE_EDIT,
    BEFORE_MCP_EXECUTION,
    BEFORE_READ_FILE,
    BEFORE_SHELL_EXECUTION,
    BEFORE_TAB_FILE_READ,
    POST_TOOL_USE,
    POST_TOOL_USE_FAILURE,
    PRE_COMPACT,
    PRE_TOOL_USE,
    STOP,
    SUBAGENT_START,
)

# 与 Cursor 文档/版本可能不一致处：以本机 IDE 行为为准；未知事件回退为 {"continue": true}
_DEFAULTS: dict[str, dict] = {
    BEFORE_SHELL_EXECUTION: {"continue": True, "permission": "allow"},
    BEFORE_MCP_EXECUTION: {"continue": True, "permission": "allow"},
    AFTER_MCP_EXECUTION: {},
    BEFORE_READ_FILE: {"continue": True, "permission": "allow"},
    AFTER_FILE_EDIT: {},
    PRE_TOOL_USE: {"continue": True, "permission": "allow"},
    POST_TOOL_USE: {},
    POST_TOOL_USE_FAILURE: {},
    SUBAGENT_START: {},
    PRE_COMPACT: {"continue": True},
    STOP: {},
    AFTER_AGENT_RESPONSE: {},
    AFTER_AGENT_THOUGHT: {},
    BEFORE_TAB_FILE_READ: {"continue": True, "permission": "allow"},
    AFTER_TAB_FILE_EDIT: {},
}


def run_probe(cursor_event: str) -> None:
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

    hook_debug_log.log_hook_executing(cursor_event)
    ten_round_state.drain_stdin()
    hook_debug_log.emit_hook_json(_DEFAULTS.get(cursor_event, {"continue": True}))
