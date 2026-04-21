#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cursor 事件 beforeShellExecution：Agent 即将执行终端命令前。"""
from __future__ import annotations

from . import probe_support
from .base import HookEventStrategy, HookInvocation, MainCallableEventStrategy
from .hook_event_names import BEFORE_SHELL_EXECUTION
from .registry import register_strategy


def main() -> None:
    """记录执行、排空 stdin，并输出允许执行 Shell 的 JSON（可在此扩展校验/拦截）。"""
    probe_support.run_probe(BEFORE_SHELL_EXECUTION)


def build(_invocation: HookInvocation) -> HookEventStrategy:
    return MainCallableEventStrategy(main)


register_strategy(BEFORE_SHELL_EXECUTION, build)
