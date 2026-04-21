#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cursor 事件 beforeSubmitPrompt：本条用户输入送入模型前（十轮计数与门禁注入）。"""
from __future__ import annotations

import json
import sys

from . import hook_debug_log
from . import ten_round_state
from .hook_event_names import BEFORE_SUBMIT_PROMPT
from .registry import register_strategy

from .base import HookInvocation, MainCallableEventStrategy, HookEventStrategy


def main() -> None:
    hook_debug_log.log_event(BEFORE_SUBMIT_PROMPT)
    ten_round_state.drain_stdin()

    if ten_round_state.load_state() is None:
        ten_round_state.init_session()

    root = ten_round_state.repo_root()
    state_path = root / ".cursor" / "workflow-state.json"
    inject_path = root / ".cursor" / "inject-before-prompt.md"

    out: dict = {"continue": True}

    inject_text = ""
    if inject_path.is_file():
        try:
            inject_text = inject_path.read_text(encoding="utf-8").strip()
            if len(inject_text) > 12000:
                inject_text = inject_text[:12000] + "\n…(truncated)"
        except OSError:
            inject_text = ""

    if state_path.is_file():
        try:
            d = json.loads(state_path.read_text(encoding="utf-8"))
            if d.get("block_submit") is True:
                msg = d.get("block_submit_message")
                if not msg:
                    msg = (
                        "门禁：workflow-state.json 中 block_submit 为 true，已阻止提交。"
                        "处理完毕后请改为 false 或删除该字段。"
                    )
                hook_debug_log.emit_hook_json(
                    {"continue": False, "user_message": str(msg)},
                )
                return
            extra = d.get("inject_before_prompt")
            if isinstance(extra, str) and extra.strip():
                inject_text = (
                    (inject_text + "\n\n") if inject_text else ""
                ) + extra.strip()
        except (OSError, json.JSONDecodeError):
            pass

    tr_inject, _ = ten_round_state.increment_user_submits()
    if tr_inject:
        inject_text = (inject_text + "\n\n") if inject_text else ""
        inject_text += tr_inject

    if inject_text:
        out["additional_context"] = inject_text

    hook_debug_log.emit_hook_json(out)


def build(_invocation: HookInvocation) -> HookEventStrategy:
    return MainCallableEventStrategy(main)


register_strategy(BEFORE_SUBMIT_PROMPT, build)
