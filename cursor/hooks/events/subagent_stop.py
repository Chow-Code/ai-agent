#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cursor 事件 subagentStop：解析 workflow-gate 合并 workflow-state；可手动对 .md 落盘。

契约：.cursor/docs/workflow-gate-contract.md
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from . import hook_debug_log
from . import ten_round_state

from .base import HookInvocation, HookEventStrategy, SubagentStopEventStrategy
from .hook_event_names import SUBAGENT_STOP
from .registry import register_strategy

START = re.compile(r"^```[Ww]orkflow-gate\s*$")
END = re.compile(r"^```\s*$")


def default_state_path() -> Path:
    return ten_round_state.repo_root() / ".cursor" / "workflow-state.json"


def extract_workflow_gate_block(markdown: str) -> str | None:
    lines = markdown.replace("\r\n", "\n").splitlines()
    in_block = False
    out: list[str] = []
    for line in lines:
        if START.match(line):
            in_block = True
            continue
        if in_block and END.match(line):
            break
        if in_block:
            out.append(line)
    text = "\n".join(out).strip()
    return text if text else None


def merge_state(state_path: Path, gate: dict) -> None:
    phase = gate.get("phase") or ""
    outcome = gate.get("outcome") or ""
    subagent = gate.get("subagent") or ""

    state: dict = {}
    if state_path.is_file():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            state = {}

    if not phase:
        return

    state["current_phase"] = phase
    state["last_gate_result"] = outcome
    if subagent:
        state["last_subagent"] = subagent
    abp = state.setdefault("attempts_by_phase", {})
    if outcome == "success":
        abp[phase] = 0
    else:
        abp[phase] = abp.get(phase, 0) + 1

    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"workflow-gate-apply：已更新状态文件 {state_path}（阶段={phase} 结果={outcome}）",
        file=sys.stderr,
    )


def apply_from_text(markdown: str, state_path: Path | None = None) -> bool:
    sp = state_path or default_state_path()
    block = extract_workflow_gate_block(markdown)
    if not block:
        print(
            "workflow-gate-apply：未找到 ```workflow-gate 代码块",
            file=sys.stderr,
        )
        return False
    try:
        gate = json.loads(block)
    except json.JSONDecodeError as e:
        print(f"workflow-gate-apply：JSON 无效: {e}", file=sys.stderr)
        return False
    if not isinstance(gate, dict):
        return False
    merge_state(sp, gate)
    return True


def walk(obj):
    if isinstance(obj, str):
        if "workflow-gate" in obj and "```" in obj:
            return obj
    if isinstance(obj, dict):
        for v in obj.values():
            r = walk(v)
            if r is not None:
                return r
    if isinstance(obj, list):
        for v in obj:
            r = walk(v)
            if r is not None:
                return r
    return None


def run_subagent_stop_hook(stdin_text: str) -> None:
    if not stdin_text.strip():
        print("{}")
        return
    try:
        data = json.loads(stdin_text)
    except json.JSONDecodeError:
        print("{}")
        return

    cand = walk(data)
    if not cand:
        print("{}")
        return

    state_path = default_state_path()
    try:
        apply_from_text(cand, state_path)
    except Exception as e:
        print(e, file=sys.stderr)
    print("{}")


def main() -> None:
    hook_debug_log.log_event(SUBAGENT_STOP)
    if len(sys.argv) > 1:
        text = Path(sys.argv[1]).read_text(encoding="utf-8")
        ok = apply_from_text(text)
        sys.exit(0 if ok else 1)

    raw = sys.stdin.read()
    if not raw.strip():
        print("{}")
        return

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        ok = apply_from_text(raw)
        sys.exit(0 if ok else 1)

    if isinstance(data, (dict, list)):
        run_subagent_stop_hook(raw)
        return

    ok = apply_from_text(raw)
    sys.exit(0 if ok else 1)


def build(invocation: HookInvocation) -> HookEventStrategy:
    return SubagentStopEventStrategy(invocation.extra_args)


register_strategy(SUBAGENT_STOP, build)
