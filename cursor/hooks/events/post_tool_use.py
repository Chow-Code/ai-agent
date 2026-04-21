#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cursor 事件 postToolUse：任意工具调用成功后。"""
from __future__ import annotations

from . import probe_support
from .base import HookEventStrategy, HookInvocation, MainCallableEventStrategy
from .hook_event_names import POST_TOOL_USE
from .registry import register_strategy


def main() -> None:
    """记录执行、排空 stdin，并输出观测 JSON（可在此扩展结果后处理）。"""
    probe_support.run_probe(POST_TOOL_USE)


def build(_invocation: HookInvocation) -> HookEventStrategy:
    return MainCallableEventStrategy(main)


register_strategy(POST_TOOL_USE, build)
