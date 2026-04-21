#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""本包位于 `.cursor/hooks/events/`：向上三级到仓库根。"""
from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]
