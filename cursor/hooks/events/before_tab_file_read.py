#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cursor 事件 beforeTabFileRead：Tab 行内补全读取文件前。"""
from __future__ import annotations

from . import probe_support
from .base import HookEventStrategy, HookInvocation, MainCallableEventStrategy
from .hook_event_names import BEFORE_TAB_FILE_READ
from .registry import register_strategy


def main() -> None:
    """记录执行、排空 stdin，并输出允许读文件的 JSON（可独立于 Agent 读文件策略）。"""
    probe_support.run_probe(BEFORE_TAB_FILE_READ)


def build(_invocation: HookInvocation) -> HookEventStrategy:
    return MainCallableEventStrategy(main)


register_strategy(BEFORE_TAB_FILE_READ, build)
