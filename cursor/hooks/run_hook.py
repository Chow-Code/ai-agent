#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cursor Hooks 唯一 CLI 入口。各事件实现见 `events/` 目录。

用法（仓库根为 cwd）：
  python3 .cursor/hooks/run_hook.py sessionStart
  echo '{}' | python3 .cursor/hooks/run_hook.py beforeSubmitPrompt
  python3 .cursor/hooks/run_hook.py subagentStop path/to/reply.md
"""
from __future__ import annotations

import sys
from pathlib import Path

_HOOKS_DIR = Path(__file__).resolve().parent
if str(_HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(_HOOKS_DIR))


def _configure_win32_stdio() -> None:
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass


def main() -> None:
    _configure_win32_stdio()

    from events.hook_session_id import init_from_stdin_payload
    from events.stdin_capture import read_stdin_with_timeout, replace_stdin_with

    _stdin_payload = read_stdin_with_timeout()
    replace_stdin_with(_stdin_payload)
    init_from_stdin_payload(_stdin_payload)

    from events import EVENT_STRATEGY_FACTORIES
    from events.base import HookInvocation

    if len(sys.argv) < 2:
        sys.stderr.write("usage: run_hook.py <EventName> [subagentStop 可选: .md 路径]\n")
        sys.stderr.write(
            "完整事件列表见 .cursor/hooks/events/__init__.py 中 EVENT_STRATEGY_FACTORIES。\n"
        )
        sys.exit(2)

    invocation = HookInvocation(
        event=sys.argv[1].strip(),
        extra_args=tuple(sys.argv[2:]),
    )
    factory = EVENT_STRATEGY_FACTORIES.get(invocation.event)
    if factory is None:
        sys.stderr.write(f"run_hook.py: unknown event {invocation.event!r}\n")
        sys.exit(2)

    strategy = factory(invocation)

    from events.hook_lifecycle_log import log_hook_invoked

    log_hook_invoked(invocation.event)
    strategy.execute()


if __name__ == "__main__":
    main()
