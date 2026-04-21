#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cursor 事件 beforeMCPExecution：调用 MCP 工具前。"""
from __future__ import annotations

from . import probe_support
from .base import HookEventStrategy, HookInvocation, MainCallableEventStrategy
from .hook_event_names import BEFORE_MCP_EXECUTION
from .registry import register_strategy


def main() -> None:
    """记录执行、排空 stdin，并输出允许调用 MCP 的 JSON（可在此扩展鉴权）。"""
    probe_support.run_probe(BEFORE_MCP_EXECUTION)


def build(_invocation: HookInvocation) -> HookEventStrategy:
    return MainCallableEventStrategy(main)


register_strategy(BEFORE_MCP_EXECUTION, build)
