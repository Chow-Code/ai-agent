---
description: 自动化测试命令，统一调用test-server和gm规则进行服务器测试和GM指令测试
---

# 自动化测试命令

本命令用于统一执行服务器自动化测试，整合了以下规则：
- **test-server和gm规则** (`.cursor/rules/deployment-testing.md`): 服务器测试配置、参数生成、HTTP请求规范、GM指令系统使用规范和指令列表

## User Input

```text
$ARGUMENTS
```

用户输入可以包含以下内容：
- 测试类型：`api`（API接口测试）、`gm`（GM指令测试）、`all`（全部测试）
- 服务器名称：`xuhai`、`zlf`、`pengfei`、`11` 等
- 测试范围：具体的接口或GM指令名称
- 其他参数：账号、道具ID、货币类型等

示例：
- `test api xuhai login backpack` - 测试xuhai服务器的登录和背包接口
- `test gm xuhai additem 1001 10` - 在xuhai服务器上执行GM指令添加道具
- `test all zlf` - 在zlf服务器上执行所有测试

## 执行流程

### 1. 解析用户输入

解析用户输入参数，提取：
- **测试类型**: `api` / `gm` / `all`
- **服务器名称**: 用于读取配置文件
- **测试范围**: 具体的接口列表或GM指令列表
- **测试参数**: 其他必要的测试参数（账号、道具ID等）

### 2. 读取服务器配置

根据**test-server规则**读取服务器配置：

**配置读取步骤**:
1. **登录服务器地址**: 
   - `{{loginServerAddr}}` = `http://172.16.3.55:6000` （固定地址）
   - `{{loginConsoleAddr}}` = `http://172.16.3.55:6001` （固定地址）

2. **读取配置中心配置**:
   - 从配置中心（Consul）读取 `login/login.toml` 配置
   - 遍历 `[[GameServers]]` 数组
   - 根据服务器名称（Name）或服务器ID（ServerId）匹配游戏服务器
   - 获取 `Ip` 和 `Port`

3. **读取游戏服务器配置**:
   - 从配置中心读取 `game_{服务器名}/config.yaml` 配置
   - 获取游戏服务器外部端口（默认: `:6100`）
   - 获取游戏服务器后端端口（默认: `:6101`）

4. **组合地址**:
   - `{{gameServerAddr}}` = `{GameServers[].Ip}:{ExtNet端口}`
   - `{{gameServerConsoleAddr}}` = `{GameServers[].Ip}:{BackNet端口}` （HTTP API地址，用于接口测试）

### 3. 获取Session Token

如果需要测试API接口或GM指令，需要先获取Session Token：

**步骤**:
1. 生成或使用指定的测试账号（默认使用随机账号）
2. 调用登录接口获取Session Token：
   ```
   GET http://{{loginServerAddr}}/login?channel={{channel}}&account={{account}}
   ```
3. 提取Session Token，后续所有请求使用该Token

### 3.1 使用 HTTP MCP 工具发起请求

可以使用 **HTTP MCP** 工具（`user-mcphttp`）来辅助发起 HTTP 请求，简化测试流程。

**工具说明**:
- **工具名称**: `http_request`
- **服务器标识**: `user-mcphttp`
- **支持方法**: GET、POST、PUT、DELETE、PATCH
- **功能**: 执行 HTTP 请求，支持请求头、查询参数、请求体等完整功能

**工具参数**:
- `method` (必需): HTTP 方法（GET、POST、PUT、DELETE、PATCH）
- `url` (必需): 请求的 URL
- `headers` (可选): HTTP 请求头（键值对对象）
- `params` (可选): URL 查询参数（键值对对象）
- `body` (可选): 请求体（JSON 字符串或普通文本）

**使用场景**:
- 获取 Session Token（登录接口）
- 调用 API 接口进行测试
- 执行 GM 指令
- 验证接口响应

**使用示例**:

1. **GET 请求 - 登录获取 Session**:
   ```json
   {
     "method": "GET",
     "url": "http://172.16.3.55:6000/login",
     "params": {
       "channel": "pc",
       "account": "test123"
     }
   }
   ```

2. **POST 请求 - 调用 API 接口**:
   ```json
   {
     "method": "POST",
     "url": "http://172.16.3.55:20001/api/MsgCtrReqGetBackpack",
     "headers": {
       "Session-Token": "c7fdf87d3ca341b3a26d7a2688a83cde",
       "Content-Type": "application/json"
     },
     "body": "{}"
   }
   ```

3. **POST 请求 - 执行 GM 指令**:
   ```json
   {
     "method": "POST",
     "url": "http://172.16.3.55:20001/api/command",
     "headers": {
       "Session-Token": "c7fdf87d3ca341b3a26d7a2688a83cde",
       "Content-Type": "application/json"
     },
     "body": "{\"Command\": \",,additem,1001,10\"}"
   }
   ```

**响应格式**:
```json
{
  "status_code": 200,
  "headers": {
    "Content-Type": "application/json; charset=utf-8"
  },
  "body": "{\"Ret\": 0, \"Data\": {...}}",
  "url": "http://..."
}
```

**注意事项**:
- 使用 HTTP MCP 工具可以简化 HTTP 请求的发送和响应处理
- 响应中的 `body` 字段是字符串格式，需要根据 `Content-Type` 进行解析（通常是 JSON）
- 所有请求地址必须使用从配置文件读取的实际地址，不要硬编码
- Session Token 需要从登录接口获取，并在后续请求的 `Session-Token` 请求头中使用

### 4. 执行测试

根据测试类型执行相应的测试：

#### 4.1 API接口测试

根据**test-server规则**执行API接口测试：

**接口定义**（路径、参数、返回值、接口名称等）以 `qa/api/` 为准。可执行用例在 `qa/integration/{领域}/`。

**测试流程**:
1. 确定要测试的领域，读取 `qa/api/{领域}.yaml` 获取接口定义
2. 运行可执行测试：`go test -v ./qa/integration/{领域}/` 或 `go test -v ./qa/integration/...`
3. 或使用 **HTTP MCP 工具**（`http_request`）按接口定义执行 HTTP 请求
4. 验证响应是否符合预期（检查 `status_code`、解析 `body` 字段、`Ret` 为 0 等）

#### 4.2 GM指令测试

根据**gm规则**执行GM指令测试：

**GM指令调用方式**:
- 接口地址: `POST {{gameServerConsoleAddr}}/api/command`
- 请求头: `Session-Token: {{session}}`、`Content-Type: application/json`
- 请求体格式:
  ```json
  {
      "Command": ",,命令名,参数1,参数2,..."
  }
  ```

**查找可用GM指令**:
1. 查看 `srv/game/handler/gm_command/` 目录
2. 查找所有 `*_command.go` 文件
3. 每个文件的 `GetCommandName()` 方法返回命令名称
4. `Execute()` 方法包含命令的参数说明和执行逻辑

**已注册的GM指令**:
- `additem` - 添加道具（参数: itemId, count）
- `addcurrency` - 添加货币（参数: currencyType, amount）
- `drop` - 触发掉落（参数: dropID, [monsterID], [mapID]）

**GM指令测试流程**:
1. 根据用户输入或测试场景确定要执行的GM指令
2. 构造GM命令字符串：`,,命令名,参数1,参数2,...`
3. 使用 **HTTP MCP 工具**（`http_request`）发送 POST 请求到 `{{gameServerConsoleAddr}}/api/command`
4. 验证响应中的 `Result` 字段（解析响应 `body` 中的 JSON）

### 5. 测试结果处理

#### 5.1 测试结果汇总

测试完成后，在聊天窗口中展示测试结果，格式如下：

```
## 测试结果汇总

### API接口测试
- **测试用例**: 登录接口
- **用例来源**: `qa/integration/`（可执行 BDD 测试）
- **测试结果**: ✅ 通过 / ❌ 失败 / ⊘ 跳过
- **简要说明**: [测试结果简要说明]

### GM指令测试
- **测试用例**: 添加道具
- **指令**: `,,additem,1001,10`
- **测试结果**: ✅ 通过 / ❌ 失败
- **简要说明**: [测试结果简要说明]

---
**测试统计**: 总用例数: 2 | 通过: 1 | 失败: 1 | 跳过: 0
**成功率**: 50.0%
```

#### 5.2 测试完成后的操作选项

**情况1: 有失败的测试用例**
- **A** - 分析失败原因并尝试修复
- **B** - 生成完整测试报告（包含失败详情）
- **C** - 生成简易测试报告
- **D** - 修复 + 生成完整报告
- **E** - 修复 + 生成简易报告
- **F** - 跳过修复，仅生成报告

**情况2: 全部测试通过**
- **A** - 生成完整测试报告
- **B** - 生成简易测试报告
- **C** - 都生成

### 6. 日志分析

如果测试失败，根据**test-server规则**分析日志：

**日志位置**:
- 日志目录: `srv/game/logs/` 或 `srv/{service}/logs/`
- 日志文件名: `game_{服务器名字}_{服务启动时间}.log`
- 读取最后一个日志文件（最新启动的服务）

**日志分析时机**:
- 接口执行报错
- 需要分析日志，确认接口是否正确执行
- 其他需要日志分析的场景

### 7. Redis 数据库日志读取

可以使用 **Redis MCP** 工具读取 Redis 数据库中的日志数据，用于验证测试结果或排查问题。

#### 7.1 确定游戏服使用的 Redis DB

**配置位置（优先）**: `srv/game/bin/config.yaml`（当前运行/集成环境实际使用的配置）。历史模板路径 `tools/config-sync/resources/versions/v1.0.0/game_{实例}/config.yaml` 可作参考；**config-sync 上传已废弃**，不必以该目录为唯一真相。

**读取步骤**:
1. 根据服务器名称（如 `xuhai`、`zlf`、`pengfei` 等）确定配置文件路径
2. 读取配置文件中的 `redis.db` 字段，该字段指定了游戏服使用的 Redis DB 编号
3. 不同环境使用不同的 DB：
   - `game_xuhai`: DB = 4（`OVERRIDE_REDIS_DB`；`game_id`/ServerID 为 26，Redis 库号 0–15）
   - `game_zlf`: DB = 10
   - `game_pf`: 查看对应配置文件
   - `game_223`（172.16.3.53）: `redis.db` = 6，与 `login.toml` 中 `ServerID=5` 的 `RedisDB` 一致
   - `game_stable`: 查看对应配置文件

**配置示例**:
```yaml
# game_zlf/config.yaml
redis:
  addresses:
    - "172.16.3.55:6379"
  password: "Ee12ws4"
  db: 10  # GameRedisDB = 10

# game_xuhai/config.yaml
redis:
  addresses:
    - "172.16.3.55:6379"
  password: "Ee12ws4"
  db: 4  # 徐海默认 OVERRIDE_REDIS_DB；login 徐海区显式 RedisDB（game_id 仍为 26）
```

#### 7.2 使用 Redis MCP 读取数据

**可用工具**:
- `redis.get` - 根据 Key 获取单个值
- `redis.list` - 根据模式匹配列出所有 Key

**使用场景**:
- 验证玩家数据是否正确保存到 Redis
- 检查背包、角色、技能等游戏数据
- 排查数据不一致问题
- 验证 GM 指令执行结果

**使用示例**:
1. **读取单个 Key**:
   ```
   使用 redis.get 工具，传入 Redis Key（如 playerrole:{roleId}:skills:{skillId}）
   ```

2. **列出匹配的 Key**:
   ```
   使用 redis.list 工具，传入模式（如 playerrole:{roleId}:skills:*）
   ```

**注意事项**:
- ⚠️ **重要**: 游戏服数据存储有 **5秒延迟**，数据不会立即保存到 Redis。执行操作后需要等待至少 5 秒再使用 Redis MCP 读取数据验证
- Redis MCP 会自动使用配置的 Redis 地址和密码
- 需要根据配置文件中的 `redis.db` 字段确定正确的 DB 编号
- Redis Key 命名规范参考 `.cursor/rules/storage.mdc`
- 所有 Redis Key 必须使用 `srv/game/adapters/technical/cache/rediskey/` 包中的函数生成

## 使用示例

### 示例1: 测试API接口

```
/test-automation api xuhai login backpack
```

执行流程：
1. 读取xuhai服务器配置
2. 使用 HTTP MCP 工具获取Session Token（GET 请求登录接口）
3. 使用 HTTP MCP 工具测试登录接口
4. 使用 HTTP MCP 工具测试背包接口（POST 请求）
5. 展示测试结果

### 示例2: 测试GM指令

```
/test-automation gm xuhai additem 1001 10
```

执行流程：
1. 读取xuhai服务器配置
2. 使用 HTTP MCP 工具获取Session Token
3. 使用 HTTP MCP 工具执行GM指令：`,,additem,1001,10`（POST 请求到 `/api/command`）
4. 验证执行结果（解析响应 body 中的 JSON）
5. 展示测试结果

### 示例3: 完整测试

```
/test-automation all zlf
```

执行流程：
1. 读取zlf服务器配置
2. 使用 HTTP MCP 工具获取Session Token
3. 使用 HTTP MCP 工具执行所有API接口测试
4. 使用 HTTP MCP 工具执行所有GM指令测试
5. 生成完整测试报告

### 示例4: 使用 Redis MCP 验证数据

```
/test-automation api zlf backpack
```

执行流程：
1. 读取zlf服务器配置（确定 Redis DB = 10）
2. 使用 HTTP MCP 工具获取Session Token
3. 使用 HTTP MCP 工具测试背包接口（如添加道具）
4. ⚠️ **等待至少 5 秒**（游戏服数据存储有 5 秒延迟）
5. 使用 Redis MCP 验证数据：
   - 使用 `redis.list` 列出背包相关的 Key（如 `playerrole:{roleId}:backpack:*`）
   - 使用 `redis.get` 读取具体道具数据
6. 验证 Redis 中的数据是否与接口返回一致
7. 展示测试结果

## 注意事项

1. **配置读取**: 必须从配置文件读取服务器地址，不要硬编码
2. **Session管理**: 测试前必须先获取有效的Session Token
3. **参数验证**: 执行GM指令前验证参数格式和有效性
4. **错误处理**: 测试失败时自动分析日志并提供修复建议
5. **报告生成**: 测试完成后可选择生成测试报告
6. **HTTP MCP 工具**: 推荐使用 HTTP MCP 工具（`http_request`）发起 HTTP 请求，简化测试流程。响应中的 `body` 字段是字符串格式，需要根据 `Content-Type` 进行解析（通常是 JSON）
7. **Redis DB 确定**: 使用 Redis MCP 前，必须从**当前游戏服实际使用的配置**读取 `redis.db`（优先 `srv/game/bin/config.yaml`，或与测试环境一致的实例目录）；勿仅依赖已废弃的 config-sync 资源树路径。
8. **Redis Key 规范**: 使用 Redis MCP 读取数据时，必须使用 `srv/game/adapters/technical/cache/rediskey/` 包中的函数生成 Key，禁止硬编码 Key 字符串
9. **Redis 数据保存延迟**: ⚠️ **重要** - 游戏服数据存储有 **5秒延迟**，执行操作后需要等待至少 5 秒再使用 Redis MCP 读取数据验证，否则可能读取不到最新数据

## 相关规则文档

- **test-server和gm规则**: `.cursor/rules/deployment-testing.md`
  - 服务器配置读取
  - 参数生成规范
  - HTTP请求规范
  - 测试报告结构

  - GM指令系统概述
  - 指令列表和参数说明
  - 指令注册机制
  - 测试指南

## 参考文档

- **API接口文档**: `qa/api/` 目录
- **可执行用例**: `qa/integration/` 目录（BDD 集成测试）
- **GM指令文档**: `.cursor/rules/gm.mdc`
- **登录流程文档**: `docs/zhanglifan/登录流程.md`
- **Redis存储规范**: `.cursor/rules/storage.mdc` - Redis Key 命名规范和工具包使用规范
- **配置文件位置**: 优先 `srv/game/bin/config.yaml`；资源模板见 `tools/config-sync/resources/...`（**config-sync 已废弃**，该树不等同于运行中唯一配置）

## 可用 MCP 工具

本命令支持使用以下 MCP 工具辅助测试：

- **HTTP MCP** (`user-mcphttp`): 用于发起 HTTP 请求（GET、POST、PUT、DELETE、PATCH），简化接口测试和 GM 指令执行
- **Redis MCP** (`user-redis`): 用于读取 Redis 数据库中的数据，验证测试结果和排查问题

