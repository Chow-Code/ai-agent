#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cursor 事件 beforeReadFile：将文件内容送入模型上下文前。"""
from __future__ import annotations

from . import probe_support
from .base import HookEventStrategy, HookInvocation, MainCallableEventStrategy
from .hook_event_names import BEFORE_READ_FILE
from .registry import register_strategy


def main() -> None:
    """记录执行、排空 stdin，并输出允许读文件的 JSON（可在此按路径做黑名单等）。"""
    probe_support.run_probe(BEFORE_READ_FILE)


def build(_invocation: HookInvocation) -> HookEventStrategy:
    return MainCallableEventStrategy(main)


register_strategy(BEFORE_READ_FILE, build)
