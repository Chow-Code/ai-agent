#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cursor 事件 postToolUseFailure：任意工具调用失败后。"""
from __future__ import annotations

from . import probe_support
from .base import HookEventStrategy, HookInvocation, MainCallableEventStrategy
from .hook_event_names import POST_TOOL_USE_FAILURE
from .registry import register_strategy


def main() -> None:
    """记录执行、排空 stdin，并输出观测 JSON（可在此扩展失败告警/重试策略）。"""
    probe_support.run_probe(POST_TOOL_USE_FAILURE)


def build(_invocation: HookInvocation) -> HookEventStrategy:
    return MainCallableEventStrategy(main)


register_strategy(POST_TOOL_USE_FAILURE, build)
