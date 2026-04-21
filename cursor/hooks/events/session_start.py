#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cursor 事件 sessionStart：新开会话/Composer，初始化十轮计数。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from . import hook_debug_log
from . import ten_round_state
from .hook_event_names import SESSION_START
from .hook_lifecycle_log import log_session_milestone_start
from .registry import register_strategy

from .base import HookInvocation, MainCallableEventStrategy, HookEventStrategy


def main() -> None:
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

    hook_debug_log.log_event(SESSION_START)
    ten_round_state.drain_stdin()
    log_session_milestone_start()

    root = ten_round_state.repo_root()
    cfg = _read_target_from_config(root)
    target = cfg if cfg is not None else ten_round_state.DEFAULT_TARGET
    ten_round_state.init_session(target_rounds=target)

    st_after = ten_round_state.load_state()
    tr = int(st_after.get("target_rounds", target)) if st_after else target
    exit_total = int(st_after.get("exit_total", 0)) if st_after else 0
    exit_cap = int(st_after.get("exit_total_cap", ten_round_state.DEFAULT_EXIT_CAP)) if st_after else ten_round_state.DEFAULT_EXIT_CAP

    ctx = (
        f"【十轮侧车 · 会话已开始】本轮发送计数已重置；**第 1 次发送**对应「第 1/{tr} 次」（`session_round_begin=1`，`user_submits` 从 0 起算）。"
        f"目标 **{tr} 次**用户发送（每条消息算一次）；每次发送前注入「第 n/{tr} 次」。"
        f"**sessionEnd** 时：默认未满 {tr} 次会 **拦截结束**（`continue:false`）；满 {tr} 次后允许关闭并 **累计退出** `exit_total` +1（当前已累计 {exit_total}/{exit_cap} 次退出）。"
    )
    hook_debug_log.emit_hook_json({"continue": True, "additional_context": ctx})


def _read_target_from_config(root: Path) -> int | None:
    p = root / ".cursor" / "ten-round-config.json"
    if not p.is_file():
        return None
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        t = d.get("target_rounds")
        if isinstance(t, int) and t >= 1:
            return t
    except (OSError, json.JSONDecodeError):
        pass
    return None


def build(_invocation: HookInvocation) -> HookEventStrategy:
    return MainCallableEventStrategy(main)


register_strategy(SESSION_START, build)
