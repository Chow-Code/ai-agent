---
name: tlog-codegen-tool
description: 当修改log_config.xml后需要生成日志代码时使用此工具。基于XML配置生成多语言日志接口代码（Go、SQL、C、Lua）。
---

# TLog日志代码生成工具Skill

## 工具概述

TLog工具是一个强大的日志代码生成器，基于XML配置文件自动生成多语言的日志接口代码。支持Go、SQL、C和Lua等多种输出格式，为分布式系统提供统一的日志记录解决方案。

## 使用场景

- 新增或修改日志结构定义（`log_config.xml`）后需要重新生成代码
- 需要生成ClickHouse建表语句时
- 需要生成DLL导出函数时
- 需要生成C语言接口或Lua包装层时

## 前置条件

- Go环境已配置
- XML配置文件已准备好（`tools/tlog/log_config.xml`）
- 项目依赖已安装

## 命令格式

```bash
cd tools/tlog
go run main.go [options]
```

### 参数说明

- `-input string`: XML配置文件路径（默认`"log_config.xml"`）
- `-go-output string`: Go代码输出路径（默认`"../../common/tlog/generated.go"`）
- `-sql-output string`: SQL建表语句输出路径（默认`"../../common/tlog/generated_tables.sql"`）
- `-dll-output string`: DLL导出函数输出路径（默认`"../dll/tlog.go"`）
- `-sidecar-output string`: C语言接口输出路径（默认`"../dll/tlog.c"`）
- `-lua-output string`: Lua包装层输出路径（默认`"../dll/tlog.lua"`）

### 使用示例

```bash
# 使用默认参数
cd tools/tlog
go run main.go

# 指定输入和输出路径
go run main.go -input log_config.xml -go-output ../../common/tlog/generated.go
```

## 输出说明

工具会生成以下文件：

1. **Go代码** (`generated.go`):
   - 日志结构体定义
   - 日志记录方法（Logger结构体方法）
   - 包级别便捷函数（简化调用，推荐使用）
   - 自动字段对齐
   - 单例模式的Logger实现

2. **SQL语句** (`generated_tables.sql`):
   - ClickHouse建表语句
   - 包含字段注释
   - 自动设置表引擎和排序键

3. **DLL导出函数** (`tlog.go`):
   - Go导出函数定义
   - C类型转换
   - 错误处理

4. **C语言接口** (`tlog.c`):
   - Lua C API实现
   - 参数检查
   - 内存管理

5. **Lua包装层** (`tlog.lua`):
   - 友好的Lua接口
   - 错误处理
   - 返回值处理

## XML配置格式

### 基本结构

```xml
<metalib tagsetversion="1" name="Log" version="2">
    <struct name="CommonLog" version="1" desc="通用日志结构">
        <entry name="t2Time" type="datetime" desc="日志日期" />
        <entry name="logLevel" type="string" size="10" desc="日志等级" />
        <entry name="trace_id" type="string" size="64" desc="链路追踪ID" />
        <entry name="message" type="string" size="256" desc="日志消息内容" />
    </struct>
</metalib>
```

### 数据类型映射

| XML类型   | Go类型  | ClickHouse类型 | C类型     | Lua类型  |
|----------|---------|----------------|-----------|----------|
| datetime | string  | DateTime       | *C.char   | string   |
| string   | string  | String(size)   | *C.char   | string   |
| int      | int     | Int32          | C.int     | number   |
| int64    | int64   | Int64          | C.longlong| number   |
| bool     | bool    | UInt8          | C.int     | boolean  |

## 使用示例

### Go代码使用

**推荐方式（简化调用）**:
```go
import (
    "context"
    "fmt"
    "server/common/config"
    "server/common/tlog"
)

tlog.LogCommonLogWithContext(ctx, config.GetGameID(), tlog.LogLevelInfo, config.GetServiceName(),
    fmt.Sprintf("user %d login successfully", userID))
```

### Lua代码使用

```lua
local tlog = require "tlog"

local ok, msg = tlog.log_common_log(0, "INFO", "trace123", "span456", "Test message")
if not ok then
    print("Log failed:", msg)
end
```

## 常见问题

### Q: 如何添加新的日志类型？

A: 在XML文件中添加新的struct定义，指定字段类型和描述，然后重新运行工具生成代码。

### Q: 生成的代码会被覆盖吗？

A: 是的，生成的代码文件会自动添加"DO NOT EDIT"警告，工具会直接覆盖这些文件。

### Q: 如何自定义模板？

A: 模板文件位于`templates`目录：
- `go.tmpl`: Go代码模板
- `sql.tmpl`: SQL语句模板
- `dll.tmpl`: DLL导出函数模板
- `tlog.tmpl`: C语言接口模板
- `tloglua.tmpl`: Lua包装层模板

## 最佳实践

1. **修改XML后立即生成**：修改`log_config.xml`后，立即运行工具生成代码
2. **检查生成结果**：生成后检查是否有编译错误
3. **使用包级别便捷函数**：推荐使用`tlog.LogCommonLogWithContext`等包级别便捷函数
4. **注意内存管理**：在C和Lua接口中注意内存管理

## 相关文档

- **工具README**: `tools/tlog/README.md`
- **XML日志定义规范**: `tools/tlog/.cursorrules`
- **日志使用规范**: `.cursor/rules/code-quality.mdc`
