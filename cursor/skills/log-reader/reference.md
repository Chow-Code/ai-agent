# 日志读取技能 - 参考文档

## 日志格式详解

### CommonLog 格式

```
source:path CommonLog|timestamp|gameId|logLevel|serverName|traceId|parentId|spanId|message
```

| 字段 | 说明 |
|------|------|
| source:path | 源码位置，如 `srv/game/handler/account/login.go:70` |
| LogType | 日志类型，CommonLog 为通用日志 |
| timestamp | 时间戳，格式 `2006-01-02 15:04:05.000` |
| gameId | 游戏服 ID |
| logLevel | 日志级别：DEBUG、INFO、WARN、ERROR、Fatal |
| serverName | 服务/模块名 |
| traceId | **主 TraceID**，请求链路根 ID |
| parentId | 父 Span ID |
| spanId | 当前 Span ID |
| message | 日志内容 |

### 其他日志类型

- **MapEnterLog**：地图进入日志，格式类似，包含 playerId、mapId、mapType 等
- **MessageProcessingTime**：消息处理耗时日志

## TraceID 说明

- **主 TraceID**：`|traceId|parentId|spanId|` 中第一个字段，16 位十六进制字符串（如 `0875072e70002802`）
- **用途**：同一请求在 Handler、AppService、Domain 各层产生的日志共享同一主 TraceID
- **获取方式**：从错误日志、客户端上报、或业务日志中的 `traceId=` 字段获取

## 查询示例

### 示例 1：查找登录请求全链路

已知主 TraceID `0875072e70002802`：

```bash
rg "0875072e70002802" logs/game_startup_*.log
```

可得到从 `[LoginHandler.HandleLogin] request` 到 `[LoginAppService.CompleteLogin] 完成登录流程成功` 的完整调用链。

### 示例 2：查找地图进入相关日志

```bash
rg "MapAppService.EnterMap" logs/game_startup_*.log
```

### 示例 3：查找某玩家的操作

```bash
rg "playerId=605820762494347266" logs/game_startup_*.log
```

### 示例 4：跨服务查询（同一 TraceID 可能出现在多个服务）

```bash
rg "0875072e70002802" logs/
```

## 日志文件命名规则

- 格式：`{服务名}_startup_{启动时间}.log`，如 `game_startup_20260305173811.log`
- 启动时间格式：`YYYYMMDDHHMMSS`
- 同一服务多次启动会生成多个日志文件，按时间戳区分
