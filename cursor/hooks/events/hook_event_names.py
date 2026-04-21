#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cursor hooks 事件名字符串（与 `.cursor/hooks.json`、IDE 约定一致）。单一来源，避免手写拼错。"""
from __future__ import annotations

# 会话
SESSION_START = "sessionStart"
SESSION_END = "sessionEnd"

# Prompt
BEFORE_SUBMIT_PROMPT = "beforeSubmitPrompt"

# Subagent（Task）
SUBAGENT_START = "subagentStart"
SUBAGENT_STOP = "subagentStop"

# 通用工具
PRE_TOOL_USE = "preToolUse"
POST_TOOL_USE = "postToolUse"
POST_TOOL_USE_FAILURE = "postToolUseFailure"

# Shell
BEFORE_SHELL_EXECUTION = "beforeShellExecution"

# MCP
BEFORE_MCP_EXECUTION = "beforeMCPExecution"
AFTER_MCP_EXECUTION = "afterMCPExecution"

# 文件（Agent）
BEFORE_READ_FILE = "beforeReadFile"
AFTER_FILE_EDIT = "afterFileEdit"

# 上下文
PRE_COMPACT = "preCompact"

# Agent 结束 / 追踪
STOP = "stop"
AFTER_AGENT_RESPONSE = "afterAgentResponse"
AFTER_AGENT_THOUGHT = "afterAgentThought"

# Tab 行内补全
BEFORE_TAB_FILE_READ = "beforeTabFileRead"
AFTER_TAB_FILE_EDIT = "afterTabFileEdit"
