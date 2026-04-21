#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""十轮会话侧车：状态文件读写与 beforeSubmit 计数。"""
from __future__ import annotations

import json
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .paths import repo_root

STATE_NAME = "ten-round-state.json"
DEFAULT_TARGET = 10
DEFAULT_EXIT_CAP = 10


def drain_stdin() -> None:
    """排空 Cursor 可能传入的 stdin JSON；避免在交互式终端上对 stdin.read() 无限阻塞。"""
    try:
        if sys.stdin.isatty():
            return
    except Exception:
        return

    container: list[str] = []

    def _read() -> None:
        try:
            container.append(sys.stdin.read())
        except Exception:
            pass

    t = threading.Thread(target=_read, daemon=True)
    t.start()
    t.join(timeout=0.5)


def state_path() -> Path:
    return repo_root() / ".cursor" / STATE_NAME


def load_state() -> dict[str, Any] | None:
    p = state_path()
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def save_state(data: dict[str, Any]) -> None:
    p = state_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _read_ten_round_config(root: Path) -> dict[str, Any]:
    p = root / ".cursor" / "ten-round-config.json"
    if not p.is_file():
        return {}
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def init_session(target_rounds: int = DEFAULT_TARGET) -> dict[str, Any]:
    """新会话：重置本轮 user_submits；累计 exit_total 默认保留（可在 ten-round-config.json 中每次重置）。"""
    now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    root = repo_root()
    cfg = _read_ten_round_config(root)
    prev = load_state()

    tr = int(cfg["target_rounds"]) if isinstance(cfg.get("target_rounds"), int) and cfg["target_rounds"] >= 1 else target_rounds
    exit_cap = int(cfg["exit_total_cap"]) if isinstance(cfg.get("exit_total_cap"), int) and cfg["exit_total_cap"] >= 1 else DEFAULT_EXIT_CAP

    exit_total = int(prev.get("exit_total", 0)) if prev else 0
    if cfg.get("reset_exit_total_on_session_start") is True:
        exit_total = 0

    data: dict[str, Any] = {
        "version": 2,
        "target_rounds": tr,
        "user_submits": 0,
        "session_round_begin": 1,
        "exit_total": exit_total,
        "exit_total_cap": exit_cap,
        "started_at": now,
    }
    save_state(data)
    return data


def _reached_target(got: int, target: int) -> bool:
    """是否已达本轮目标（发送次数不少于目标即视为可结束本轮）。"""
    return got >= target


def apply_session_end() -> dict[str, Any]:
    """会话结束：校验发送次数；默认未达标时不累计 exit_total，并由 session_end 返回 continue:false。

    ten-round-config.json：
    - block_session_end_until_target（默认 true）：未达标时阻止结束会话（不增加 exit_total）。
    - 为 false 时恢复旧行为：任意结束都 +exit_total。
    """
    st = load_state()
    if not st:
        return {"ok": False, "reason": "no_state"}

    root = repo_root()
    cfg = _read_ten_round_config(root)
    strict = cfg.get("block_session_end_until_target")
    if strict is None:
        strict = True
    else:
        strict = bool(strict)

    target = int(st.get("target_rounds", DEFAULT_TARGET))
    got = int(st.get("user_submits", 0))
    reached = _reached_target(got, target)
    cap = int(st.get("exit_total_cap", DEFAULT_EXIT_CAP))
    exit_now = int(st.get("exit_total", 0))

    if strict and not reached:
        return {
            "ok": True,
            "reached": False,
            "match_exact": got == target,
            "target": target,
            "user_submits": got,
            "exit_total": exit_now,
            "exit_cap": cap,
            "at_cap": exit_now >= cap,
            "block_exit": True,
        }

    exit_total = exit_now + 1
    st["exit_total"] = exit_total
    st["last_session_end_at"] = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    save_state(st)

    return {
        "ok": True,
        "reached": reached,
        "match_exact": got == target,
        "target": target,
        "user_submits": got,
        "exit_total": exit_total,
        "exit_cap": cap,
        "at_cap": exit_total >= cap,
        "block_exit": False,
    }


def increment_user_submits() -> tuple[str, dict[str, Any] | None]:
    """每次用户本条输入将送入模型前调用：user_submits += 1，返回 (追加注入文本, 新状态或 None)。"""
    st = load_state()
    if not st:
        return "", None
    target = int(st.get("target_rounds", DEFAULT_TARGET))
    st["user_submits"] = int(st.get("user_submits", 0)) + 1
    save_state(st)
    n = st["user_submits"]
    inject = (
        f"【十轮侧车】第 {n}/{target} 次用户发送（默认满 {target} 次才允许结束会话；"
        f"未达标时 sessionEnd 会尝试拦截关闭）。\n"
    )
    return inject, st
