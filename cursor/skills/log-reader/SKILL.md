---
name: log-reader
description: 读取、查询、分析 logs 目录下的业务日志。使用场景：读取日志、按 TraceID 查询请求链路、排查游戏业务问题、分析 game/battle-proxy/social 日志。
---

# 日志读取技能

## 使用场景

- 需要读取、查询或分析 `logs/` 目录下的业务日志时
- 需要按 TraceID 查询完整请求链路时
- 排查登录、背包、技能、地图等游戏业务问题时
- 分析 game、battle-proxy、social 等服务的日志时

## 日志目录与服务映射

日志位于项目根目录下的 `logs/` 目录，各服务日志文件命名规则：

| 日志文件前缀 | 服务 | 业务说明 |
|-------------|------|----------|
| `game_startup_*.log` | game | 玩家核心玩法业务（登录、背包、技能、地图等） |
| `battle-proxy_startup_*.log` | battle-proxy | 战斗代理、与战斗服通信 |
| `social_startup_*.log` | social | 社交业务 |
| `gateway_startup_*.log` | gateway | 网关连接与转发 |
| `login_startup_*.log` | login | 登录服 |
| `waypoint_startup_*.log` | waypoint | 路由 |
| `consul_*.log` | consul | 配置中心 |

## 日志格式（tlog）

日志采用 tlog 标准格式（来源：`common/tlog/generated.go`）：

```
source:path LogType|timestamp|gameId|logLevel|serverName|traceId|parentId|spanId|message
```

- **LogType**：如 `CommonLog`、`MapEnterLog` 等
- **链路信息**：`|traceId|parentId|spanId|` 三个字段，其中 **traceId（第一个）为主 ID**
- **主 TraceID**：用于串联同一请求的完整调用链，如 `0875072e70002802` 可找到一次登录请求从 Handler → AppService → Domain 的全链路

示例：

```
CommonLog|2026-03-06 01:37:12.805|2|INFO|default_module|0875072e70002802|0875072e70062802|0875072e70072802|[LoginHandler.HandleLogin] request: ...
CommonLog|2026-03-06 01:37:12.842|2|INFO|default_module|0875072e70002802|0875072e70062802|0875072e70072802|[LoginAppService.CompleteLogin] 完成登录流程成功: ...
```

## 查询方法

### 按主 TraceID 查询

使用 ripgrep（`rg`）或 grep 搜索主 TraceID，可获取该请求的完整链路：

```bash
rg "0875072e70002802" logs/
rg "0875072e70002802" logs/game_startup_*.log
```

### 按服务筛选

指定日志文件前缀，缩小搜索范围：

```bash
rg "关键词" logs/game_startup_*.log
rg "关键词" logs/battle-proxy_startup_*.log
rg "关键词" logs/social_startup_*.log
```

### 按关键词查询

```bash
rg "LoginAppService" logs/game_startup_*.log
rg "MapAppService.EnterMap" logs/game_startup_*.log
```

## 最佳实践

1. **玩家核心玩法问题**：优先查看 `logs/game_startup_*.log`
2. **战斗相关问题**：查看 `logs/battle-proxy_startup_*.log` 和 `logs/game_startup_*.log`
3. **链路追踪**：从错误日志或客户端获取主 TraceID，用 `rg "TraceID" logs/` 串联全链路
4. **大文件**：可先用 `Read` 读取部分内容，再用 `Grep` 按 TraceID 或关键词精确搜索

## 相关文档

- 详细格式说明与示例见 [reference.md](reference.md)
- 提交 Bug 报告（选择 TraceID）见 report-tool 技能
