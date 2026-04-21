#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 Hook stdin JSON 或环境变量解析会话标识，供 lifecycle 等按会话分文件。"""
from __future__ import annotations

import json
import os
import re
from typing import Any

_ENV_OVERRIDE = "CURSOR_HOOK_SESSION_ID"

# 小写、去连字符后匹配（与 JSON 里 camelCase 对应）
_CANDIDATE_KEYS = frozenset(
    {
        "sessionid",
        "session_id",
        "conversationid",
        "conversation_id",
        "composerid",
        "threadid",
        "chatid",
        "cursor_session_id",
        "chat_session_id",
    }
)

_effective_id: str = "default"


def _normalize_key(key: str) -> str:
    return str(key).lower().replace("-", "_")


def _walk_for_session_id(obj: Any, depth: int) -> str | None:
    if depth > 14 or obj is None:
        return None
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = _normalize_key(k)
            if isinstance(v, str) and v.strip():
                if nk in _CANDIDATE_KEYS or nk.endswith("_session_id"):
                    return v.strip()
            found = _walk_for_session_id(v, depth + 1)
            if found:
                return found
    elif isinstance(obj, list):
        for item in obj:
            found = _walk_for_session_id(item, depth + 1)
            if found:
                return found
    return None


def extract_session_id_from_payload(payload: str) -> str | None:
    """从 stdin 文本解析 JSON 并查找会话类字段；失败返回 None。"""
    raw = (payload or "").strip()
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    found = _walk_for_session_id(data, 0)
    return found if found else None


def sanitize_session_id(raw: str) -> str:
    """目录名安全：仅保留常见安全字符，限制长度。"""
    s = raw.strip()
    if not s:
        return "default"
    s = re.sub(r"[^a-zA-Z0-9._-]+", "_", s)
    s = s.strip("._-") or "default"
    if len(s) > 120:
        s = s[:120]
    if s in (".", ".."):
        return "default"
    return s


def init_from_stdin_payload(payload: str) -> None:
    """在 run_hook 捕获 stdin 后调用，设置本进程内生效的会话目录名。"""
    global _effective_id
    env_val = (os.environ.get(_ENV_OVERRIDE) or "").strip()
    if env_val:
        _effective_id = sanitize_session_id(env_val)
        return
    extracted = extract_session_id_from_payload(payload)
    _effective_id = sanitize_session_id(extracted) if extracted else "default"


def get_effective_session_id() -> str:
    return _effective_id
