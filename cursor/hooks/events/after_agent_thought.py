#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cursor 事件 afterAgentThought：Agent thought 阶段结束后。"""
from __future__ import annotations

from . import probe_support
from .base import HookEventStrategy, HookInvocation, MainCallableEventStrategy
from .hook_event_names import AFTER_AGENT_THOUGHT
from .registry import register_strategy


def main() -> None:
    """记录执行、排空 stdin，并输出观测 JSON（可在此扩展 thought 追踪）。"""
    probe_support.run_probe(AFTER_AGENT_THOUGHT)


def build(_invocation: HookInvocation) -> HookEventStrategy:
    return MainCallableEventStrategy(main)


register_strategy(AFTER_AGENT_THOUGHT, build)
