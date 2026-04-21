#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cursor Hook 生命周期轨迹：按会话追加 UTF-8 日志。

- 路径：`.cursor/hook-logs/sessions/<会话目录>/lifecycle.log`（会话标识来自 stdin JSON 或环境变量 `CURSOR_HOOK_SESSION_ID`；缺失时为 `default`）
- 每次经 `run_hook.py` 执行任意事件 → 一行 `hook\\t<事件名>`
- `sessionStart` / `sessionEnd` 内再写里程碑行
- `sessionEnd` 结束时将 **本会话 lifecycle.log 快照** 写入 `user_message`，并 **stderr 打印**
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from .hook_session_id import get_effective_session_id
from .paths import repo_root

_HOOK_LOGS_SUBDIR = "hook-logs"
_SESSIONS_SUBDIR = "sessions"
_LIFECYCLE_NAME = "lifecycle.log"
# 每次 sessionEnd / stop 覆盖写入，便于 IDE 不展示 hook stdout 时仍可查
_LAST_EXIT_NOTICE_NAME = "LAST_EXIT_NOTICE.txt"

# 嵌入 user_message 的长度上限（避免 JSON 过大）
_USER_MESSAGE_MAX_CHARS = 48_000
# stderr 可放宽，仍设上限防止极端大文件拖死终端
_STDERR_MAX_CHARS = 1_000_000


def hook_logs_dir() -> Path:
    return repo_root() / ".cursor" / _HOOK_LOGS_SUBDIR


def lifecycle_log_path() -> Path:
    sid = get_effective_session_id()
    return hook_logs_dir() / _SESSIONS_SUBDIR / sid / _LIFECYCLE_NAME


def lifecycle_relative_posix() -> str:
    """相对仓库根，用于 user_message / README。"""
    sid = get_effective_session_id()
    return f".cursor/{_HOOK_LOGS_SUBDIR}/{_SESSIONS_SUBDIR}/{sid}/{_LIFECYCLE_NAME}"


def last_exit_notice_path() -> Path:
    return hook_logs_dir() / _LAST_EXIT_NOTICE_NAME


def last_exit_notice_relative_posix() -> str:
    return f".cursor/{_HOOK_LOGS_SUBDIR}/{_LAST_EXIT_NOTICE_NAME}"


def write_last_exit_notice(full_message: str) -> None:
    """将结束摘要落盘；不依赖 Cursor 是否把 hook stdout 显示在聊天里。"""
    try:
        p = last_exit_notice_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        header = f"{_now_iso()}\tpid={os.getpid()}\twritten_by=hook\n\n"
        p.write_text(header + full_message, encoding="utf-8")
    except OSError:
        pass


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="milliseconds")


def _append_line(line: str) -> None:
    try:
        p = lifecycle_log_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as f:
            f.write(line.rstrip() + "\n")
    except Exception:
        pass


def log_hook_invoked(cursor_event: str) -> None:
    """由 `run_hook.py` 在 `strategy.execute()` 前调用。"""
    _append_line(f"{_now_iso()}\tpid={os.getpid()}\thook\t{cursor_event}")


def log_session_milestone_start() -> None:
    """`sessionStart` 内：标记新会话边界。"""
    _append_line(
        f"{_now_iso()}\tpid={os.getpid()}\tmilestone\tsession\t"
        f"begin（本轮 hook 顺序见 {lifecycle_relative_posix()}）"
    )


def log_session_milestone_end() -> None:
    """`sessionEnd` 内：标记关闭会话，便于对照轨迹文件。"""
    _append_line(
        f"{_now_iso()}\tpid={os.getpid()}\tmilestone\tsession\t"
        f"end（打开 {lifecycle_relative_posix()} 查看本轮全部 hook）"
    )


def read_lifecycle_log_text() -> str:
    """读取当前 lifecycle.log 全文；不存在或失败则返回说明文本。"""
    p = lifecycle_log_path()
    if not p.is_file():
        return (
            "（尚无本会话的 lifecycle.log，或尚未经 run_hook 写入任何事件；"
            f"期望路径：`{lifecycle_relative_posix()}`）\n"
        )
    try:
        return p.read_text(encoding="utf-8")
    except OSError:
        return "（读取 lifecycle.log 失败）\n"


def _truncate(text: str, max_chars: int) -> tuple[str, bool]:
    if len(text) <= max_chars:
        return text, False
    return text[:max_chars], True


def format_lifecycle_dump_for_user_message(max_chars: int = _USER_MESSAGE_MAX_CHARS) -> str:
    """供 sessionEnd 拼进 user_message：带边界标记，过长截断。"""
    raw, trunc = _truncate(read_lifecycle_log_text(), max_chars)
    tail = ""
    if trunc:
        tail = (
            f"\n…（已截断，仅保留前 {max_chars} 字符；完整文件见 `{lifecycle_relative_posix()}`）\n"
        )
    return (
        "\n\n【lifecycle.log 快照 · 用于判断 hook 顺序是否正常】\n"
        "```text\n"
        + raw.rstrip()
        + "\n```"
        + tail
    )


def print_lifecycle_dump_to_stderr(max_chars: int = _STDERR_MAX_CHARS) -> None:
    """sessionEnd 时打印到 stderr，终端 / 部分 IDE 可对照 user_message。"""
    raw, trunc = _truncate(read_lifecycle_log_text(), max_chars)
    block = (
        "\n========== hook-lifecycle (stderr) ==========\n"
        + raw.rstrip()
        + ("\n…(stderr 输出已截断)\n" if trunc else "")
        + "\n========== /hook-lifecycle ==========\n"
    )
    try:
        print(block, file=sys.stderr, flush=True)
    except Exception:
        pass


def lifecycle_attachment_for_session_end(when_label: str = "sessionEnd") -> str:
    """sessionEnd / stop 等在 user_message 或落盘全文末尾附加的快照块。"""
    return (
        f"\n\n【Hook 调试】以下为 `{lifecycle_relative_posix()}` 在 **{when_label}** 触发时的内容快照；"
        f"**stderr** 同步打印了同一份（便于命令行对照）。可与 `.cursor/hooks-debug.log` 互证。\n"
        + format_lifecycle_dump_for_user_message()
    )


def format_lifecycle_followup_summary() -> str:
    """供 **stop** 的 `followup_message`：短摘要，避免整份 lifecycle 塞进聊天或被截断。"""
    rel = lifecycle_relative_posix()
    notice = last_exit_notice_relative_posix()
    p = lifecycle_log_path()
    if not p.is_file():
        return (
            "【Hook · stop】本轮任务已结束。\n"
            f"尚无 `{rel}`。\n"
            f"若已落盘提示见 `{notice}`。\n"
            "关对话时的十次发送统计以 **sessionEnd** 为准。"
        )
    try:
        raw = p.read_text(encoding="utf-8")
    except OSError:
        return (
            "【Hook · stop】已结束；读取 lifecycle 失败。\n"
            f"请查看 `{notice}` 或 **输出 → Hooks**。"
        )

    lines = [ln.rstrip() for ln in raw.splitlines() if ln.strip()]
    if not lines:
        return (
            "【Hook · stop】已结束。\n"
            f"`{rel}` 为空；全文见 `{notice}`。"
        )

    pids: set[str] = set()
    hook_rows = 0
    ts_first = ""
    ts_last = ""
    for ln in lines:
        if "\tpid=" in ln:
            try:
                pid_part = ln.split("\tpid=", 1)[1].split("\t", 1)[0]
                pids.add(pid_part)
            except (IndexError, ValueError):
                pass
        if "\thook\t" in ln:
            hook_rows += 1
        if "\t" in ln:
            ts = ln.split("\t", 1)[0]
            if not ts_first:
                ts_first = ts
            ts_last = ts

    return (
        "【Hook · stop】Agent 本轮任务已结束。\n"
        f"- 轨迹：`{rel}`：**{len(lines)}** 行，**{hook_rows}** 次 `hook` 调用，约 **{len(pids)}** 个不同 pid"
        f"（Cursor 多为**每次 hook 起新子进程**，故 pid 数常与调用次数同量级；并行/多窗口时时间会交错；会话目录为 `default` 时会混入多路来源，**正常**）\n"
        f"- 时间跨度：`{ts_first}` → `{ts_last}`\n"
        f"- **完整 lifecycle 快照**：`{notice}`\n"
        "关对话、十轮计数以 **sessionEnd** 为准。"
    )
