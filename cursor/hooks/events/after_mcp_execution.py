#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cursor 事件 afterMCPExecution：MCP 工具调用结束后。"""
from __future__ import annotations

from . import probe_support
from .base import HookEventStrategy, HookInvocation, MainCallableEventStrategy
from .hook_event_names import AFTER_MCP_EXECUTION
from .registry import register_strategy


def main() -> None:
    """记录执行、排空 stdin，并输出观测用 JSON（可在此扩展审计/埋点）。"""
    probe_support.run_probe(AFTER_MCP_EXECUTION)


def build(_invocation: HookInvocation) -> HookEventStrategy:
    return MainCallableEventStrategy(main)


register_strategy(AFTER_MCP_EXECUTION, build)
