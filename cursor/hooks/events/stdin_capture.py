#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性读取 Hook stdin（带超时），并还原为 StringIO，避免下游 drain_stdin 与解析争抢。"""
from __future__ import annotations

import io
import sys
import threading


def read_stdin_with_timeout(timeout: float = 0.5) -> str:
    """非 TTY 时在线程中 read 全量 stdin，最多等待 timeout 秒。"""
    try:
        if sys.stdin.isatty():
            return ""
    except Exception:
        return ""

    container: list[str] = []

    def _read() -> None:
        try:
            container.append(sys.stdin.read())
        except Exception:
            pass

    t = threading.Thread(target=_read, daemon=True)
    t.start()
    t.join(timeout=timeout)
    return container[0] if container else ""


def replace_stdin_with(payload: str) -> None:
    """将 sys.stdin 替换为内存缓冲，供本进程内后续代码再次读取同一内容。"""
    sys.stdin = io.StringIO(payload)
