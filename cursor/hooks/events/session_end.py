#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cursor 事件 sessionEnd：会话结束，校验十轮与累计退出。"""
from __future__ import annotations

import sys

from . import hook_debug_log
from . import ten_round_state
from .hook_event_names import SESSION_END
from .hook_lifecycle_log import (
    lifecycle_attachment_for_session_end,
    log_session_milestone_end,
    print_lifecycle_dump_to_stderr,
    write_last_exit_notice,
)
from .registry import register_strategy

from .base import HookInvocation, MainCallableEventStrategy, HookEventStrategy


def _emit(continue_val: bool, body: str) -> None:
    """统一：stderr 打印 lifecycle；stdout JSON（user_message + userMessage 兼容）；并落盘 LAST_EXIT_NOTICE.txt。"""
    print_lifecycle_dump_to_stderr()
    full = body + lifecycle_attachment_for_session_end()
    write_last_exit_notice(full)
    hook_debug_log.emit_hook_json(
        {"continue": continue_val, "user_message": full},
    )


def main() -> None:
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

    hook_debug_log.log_event(SESSION_END)
    ten_round_state.drain_stdin()
    log_session_milestone_end()

    result = ten_round_state.apply_session_end()
    if not result.get("ok"):
        msg = (
            "【十轮侧车 · 会话结束】未找到 `.cursor/ten-round-state.json`，无法校验本轮次数。"
            "常见原因：**sessionStart 未执行**、状态文件被删、或 **beforeSubmitPrompt** 从未成功跑过。"
            "请在 Cursor 设置中确认 Hooks 已注册 **sessionStart**、**beforeSubmitPrompt**、**sessionEnd**；"
            "本仓库 `hooks.json` 已包含上述事件；若 IDE 仍不触发 **sessionEnd**，需升级 Cursor 或查阅当前版本是否支持该事件。"
        )
        _emit(True, msg)
        return

    if result.get("block_exit"):
        target = int(result["target"])
        got = int(result["user_submits"])
        need = target - got
        msg = (
            "【十轮侧车 · 阻止结束】本轮用户发送 "
            f"{got}/{target} 次，**未满 {target} 次**，请继续对话补满后再结束会话。"
            f"（约还需 {need} 条用户消息；若 Cursor 支持 `continue:false`，本次关闭会被拦截。）"
        )
        _emit(False, msg)
        return

    target = int(result["target"])
    got = int(result["user_submits"])
    reached = bool(result.get("reached", True))
    exit_total = int(result["exit_total"])
    exit_cap = int(result["exit_cap"])
    at_cap = bool(result["at_cap"])

    if reached and got == target:
        line_a = f"本轮用户发送次数 = {got}，与目标 {target} 次一致，允许结束。"
    elif reached and got > target:
        line_a = f"本轮用户发送次数 = {got}，已不少于目标 {target} 次，允许结束。"
    else:
        short = target - got if got < target else 0
        line_a = (
            f"本轮用户发送次数 = {got}，目标 = {target}，**未对齐**（差 {short} 次）。"
            f"（非严格模式或未拦截时仍记录了本次结束。）"
        )

    line_b = f"累计退出次数 exit_total = {exit_total}/{exit_cap}（本次 sessionEnd 已 +1）。"
    if at_cap:
        line_b += " **已达到累计退出上限。**"

    msg = "【十轮侧车 · 会话结束】" + line_a + line_b
    _emit(True, msg)


def build(_invocation: HookInvocation) -> HookEventStrategy:
    return MainCallableEventStrategy(main)


register_strategy(SESSION_END, build)
