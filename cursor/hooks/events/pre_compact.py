#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cursor 事件 preCompact：上下文窗口即将压缩前。"""
from __future__ import annotations

from . import probe_support
from .base import HookEventStrategy, HookInvocation, MainCallableEventStrategy
from .hook_event_names import PRE_COMPACT
from .registry import register_strategy


def main() -> None:
    """记录执行、排空 stdin，并输出默认放行 JSON（可在此扩展压缩前备份提示等）。"""
    probe_support.run_probe(PRE_COMPACT)


def build(_invocation: HookInvocation) -> HookEventStrategy:
    return MainCallableEventStrategy(main)


register_strategy(PRE_COMPACT, build)
