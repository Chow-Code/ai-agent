#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cursor 事件 preToolUse：任意工具即将被调用前（通用钩子）。"""
from __future__ import annotations

from . import probe_support
from .base import HookEventStrategy, HookInvocation, MainCallableEventStrategy
from .hook_event_names import PRE_TOOL_USE
from .registry import register_strategy


def main() -> None:
    """记录执行、排空 stdin，并输出默认放行 JSON（可在此统一拦截/改写工具调用）。"""
    probe_support.run_probe(PRE_TOOL_USE)


def build(_invocation: HookInvocation) -> HookEventStrategy:
    return MainCallableEventStrategy(main)


register_strategy(PRE_TOOL_USE, build)
