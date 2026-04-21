#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cursor 事件 subagentStart：Subagent（Task）启动时。"""
from __future__ import annotations

from . import probe_support
from .base import HookEventStrategy, HookInvocation, MainCallableEventStrategy
from .hook_event_names import SUBAGENT_START
from .registry import register_strategy


def main() -> None:
    """记录执行、排空 stdin，并输出观测 JSON（可在此扩展子代理配额等）。"""
    probe_support.run_probe(SUBAGENT_START)


def build(_invocation: HookInvocation) -> HookEventStrategy:
    return MainCallableEventStrategy(main)


register_strategy(SUBAGENT_START, build)
