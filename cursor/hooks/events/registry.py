#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hook 策略注册表：各事件模块在 import 时 register_strategy(事件常量, build)。"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from types import MappingProxyType

from .base import HookEventStrategy, HookInvocation

StrategyFactory = Callable[[HookInvocation], HookEventStrategy]

_registry: dict[str, StrategyFactory] = {}


def register_strategy(cursor_event: str, factory: StrategyFactory) -> None:
    """将「Cursor 事件名 → 策略工厂」登记到全局表（每个事件仅允许登记一次）。"""
    if cursor_event in _registry:
        raise ValueError(f"duplicate hook registration: {cursor_event!r}")
    _registry[cursor_event] = factory


def get_event_strategy_factories() -> Mapping[str, StrategyFactory]:
    """返回当前已注册策略的只读视图（在 `events` 包完成所有子模块 import 之后调用）。"""
    return MappingProxyType(dict(_registry))
