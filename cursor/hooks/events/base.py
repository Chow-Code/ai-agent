#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hook 策略基类型与可复用策略（具体事件逻辑在同级各模块）。"""
from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class HookInvocation:
    """一次调用：Cursor 事件名 + `run_hook.py` 之后的附加参数（如 subagentStop 的 .md 路径）。"""

    event: str
    extra_args: tuple[str, ...] = ()


class HookEventStrategy(ABC):
    """与单个 Cursor hook 事件对应的策略。"""

    @abstractmethod
    def execute(self) -> None:
        pass


class MainCallableEventStrategy(HookEventStrategy):
    """委托给本事件模块内的 `main()`（无 argv 魔术）。"""

    def __init__(self, main_fn: Callable[[], None]) -> None:
        self._main_fn = main_fn

    def execute(self) -> None:
        self._main_fn()


class SubagentStopEventStrategy(HookEventStrategy):
    """subagentStop：`main()` 依赖 `sys.argv` 区分 Cursor stdin 与手动文件路径。"""

    def __init__(self, extra_args: tuple[str, ...]) -> None:
        self._extra_args = list(extra_args)

    def execute(self) -> None:
        import events.subagent_stop as subagent_mod

        old = sys.argv[:]
        try:
            base = str(Path(subagent_mod.__file__).resolve())
            sys.argv = [base, *self._extra_args]
            subagent_mod.main()
        finally:
            sys.argv = old
