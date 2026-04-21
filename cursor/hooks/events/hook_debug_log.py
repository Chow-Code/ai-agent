#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""调试日志与 Hook 标准输出 JSON（写入 `.cursor/hooks-debug.log`）。"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

from .paths import repo_root


def log_event(event_name: str, extra: str = "") -> None:
    """写入一行 UTF-8 日志；失败时静默，避免 Hook 本身导致 Agent 失败。"""
    try:
        now = datetime.now(timezone.utc).astimezone().isoformat(timespec="milliseconds")
        line = f"{now}\t{event_name}\tpid={os.getpid()}"
        if extra:
            line += f"\t{extra}"
        line += "\n"
        p = repo_root() / ".cursor" / "hooks-debug.log"
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass


def log_hook_executing(cursor_event: str) -> None:
    """无复杂业务时专用：一行说明「当前在执行哪个 Hook 事件」。"""
    try:
        now = datetime.now(timezone.utc).astimezone().isoformat(timespec="milliseconds")
        line = f"{now}\t[hook]\t执行中\t{cursor_event}\tpid={os.getpid()}\n"
        p = repo_root() / ".cursor" / "hooks-debug.log"
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass


def emit_hook_json(obj: dict) -> None:
    """写出单行 JSON。兼容字段名：user_message/userMessage、additional_context/additionalContext、followup_message/followupMessage。"""
    d = dict(obj)
    um = d.get("user_message")
    uM = d.get("userMessage")
    if um is not None:
        d["userMessage"] = um
    elif uM is not None:
        d["user_message"] = uM
    ac = d.get("additional_context")
    aC = d.get("additionalContext")
    if ac is not None and aC is None:
        d["additionalContext"] = ac
    elif aC is not None and ac is None:
        d["additional_context"] = aC
    fm = d.get("followup_message")
    fM = d.get("followupMessage")
    if fm is not None:
        d["followupMessage"] = fm
    elif fM is not None:
        d["followup_message"] = fM
    line = json.dumps(d, ensure_ascii=False) + "\n"
    sys.stdout.buffer.write(line.encode("utf-8"))
    sys.stdout.buffer.flush()
