#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cursor 事件 stop：Agent 本轮任务结束（completed / aborted / error）。

与 **sessionEnd**（关 Composer）不同，用户点「停止」或本轮跑完时通常会走 **stop**。
stdout 使用 Cursor 规定的 **`followup_message`**（不是 user_message）；全文仍落盘 **LAST_EXIT_NOTICE.txt**。
"""
from __future__ import annotations

import sys

from . import hook_debug_log
from . import ten_round_state
from .hook_event_names import STOP
from .hook_lifecycle_log import (
    format_lifecycle_followup_summary,
    lifecycle_attachment_for_session_end,
    print_lifecycle_dump_to_stderr,
    write_last_exit_notice,
)
from .registry import register_strategy

from .base import HookInvocation, MainCallableEventStrategy, HookEventStrategy

# Cursor StopOutput 官方仅有 followup_message（见 Cursor / hookshot 文档）；user_message 对该事件无效。


def main() -> None:
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

    hook_debug_log.log_event(STOP)
    ten_round_state.drain_stdin()

    print_lifecycle_dump_to_stderr()
    head = (
        "【Hook · stop】Agent **本轮任务**已结束（具体 status 见 stdin 的 `status` 字段："
        "completed / aborted / error）。\n"
        "若需「关对话窗口」时的十轮统计，仍以 **sessionEnd** 为准；以下为当前会话 **lifecycle** 快照（与 sessionEnd 同格式）。\n\n"
    )
    full = head + lifecycle_attachment_for_session_end(when_label="stop")
    write_last_exit_notice(full)
    hook_debug_log.emit_hook_json(
        {"followup_message": format_lifecycle_followup_summary()},
    )


def build(_invocation: HookInvocation) -> HookEventStrategy:
    return MainCallableEventStrategy(main)


register_strategy(STOP, build)
