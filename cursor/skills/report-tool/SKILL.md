---
name: report-tool
description: 当需要解析日志文件并选择TraceID提交Bug报告时使用此工具。用于日志TraceID选择器客户端和服务器。
---

# 报告工具Skill

## 工具概述

报告工具包含日志TraceID选择器客户端和服务器，用于解析游戏日志文件并选择TraceID提交Bug报告。客户端提供Web界面，支持日志解析、智能筛选、TraceID选择、Bug报告提交等功能。

## 使用场景

- 需要解析日志文件并选择TraceID提交Bug报告时
- 需要搜索和筛选日志记录时
- 需要批量选择TraceID时

## 前置条件

- Go 1.21+环境已配置
- 日志文件目录可访问
- 报告服务器已启动（如果需要提交报告）

## 命令格式

### 启动客户端

**方法一：使用批处理文件（推荐）**

```bash
cd tools/report/client
start.bat
```

**方法二：直接运行**

```bash
cd tools/report/client
go run main.go
```

### 启动服务器

```bash
cd tools/report/server
go run main.go
```

## 配置说明

配置文件：`tools/report/client/config.yaml`

```yaml
# 日志文件目录
log_directory: "D:\\DSGamePackage\\project_wt_Q2\\FromTheForgotten\\Saved\\Logs\\Net"

# 报告服务器配置
server_ip: "192.168.61.85"
server_port: "8082"
report_url: "http://192.168.61.85:8082/report"

# 客户端服务器端口
client_port: "8083"
```

## 工具功能

### 客户端功能

1. **日志解析**:
   - 自动扫描指定目录下的所有`.log`文件
   - 解析日志中的TraceID、消息名称、时间戳等信息
   - 支持ProtoReq和ProtoRsp两种消息类型
   - 按时间排序显示日志记录

2. **智能筛选**:
   - 搜索功能：支持按TraceID、消息名称、文件名搜索
   - 方向过滤：可筛选请求(Req)或响应(Rsp)消息
   - 文件过滤：可按日志文件名筛选
   - 时间过滤：支持最近1小时、6小时、24小时筛选

3. **TraceID选择**:
   - 支持单选和多选TraceID
   - 点击TraceID可快速单选
   - 勾选复选框可多选
   - 实时显示选中的TraceID详细信息

4. **Bug报告提交**:
   - 输入问题描述（限制100字符）
   - 自动提交到报告服务器
   - 支持中文描述
   - 提交成功后自动清除选择

## 使用流程

1. **启动工具**：运行`go run main.go`
2. **打开界面**：访问`http://localhost:8083`
3. **查看日志**：工具自动扫描并显示日志记录
4. **筛选数据**：使用搜索和过滤功能找到相关日志
5. **选择TraceID**：点击或勾选需要的TraceID
6. **输入描述**：在问题描述框中输入Bug描述
7. **提交报告**：点击"提交Bug报告"按钮
8. **查看结果**：系统会显示提交成功或失败信息

## 日志格式支持

工具支持解析以下格式的日志：

```
2025.07.09-16.26.41: ProtoReq ---> MsgName: PreLobby.ReqEnterLobby , TraceID: 777145184084114176 , MsgBody: None
2025.07.09-16.26.41: ProtoRsp <--- MsgName: PreLobby.RspEnterLobby , TraceID: 777145184084114176 , MsgBody: PlayerInfo {...}
```

- **时间格式**：`YYYY.MM.DD-HH.MM.SS`
- **消息类型**：`ProtoReq`（请求）或`ProtoRsp`（响应）
- **方向标识**：`--->`（请求）或`<---`（响应）
- **TraceID**：数字ID，跳过"None"值

## API接口

- **GET /**：主页面，显示日志选择界面
- **GET /api/logs**：获取解析后的日志数据（JSON格式）
- **GET /api/config**：获取当前配置
- **POST /api/config**：更新配置

## 常见问题

### Q: 没有显示日志数据？

A: 检查`config.yaml`中的`log_directory`路径是否正确，确认目录下有`.log`文件，检查文件权限是否允许读取。

### Q: 提交失败？

A: 检查报告服务器是否运行，确认`report_url`配置是否正确，检查网络连接。

### Q: 解析错误？

A: 确认日志文件格式符合要求，检查日志文件编码（建议UTF-8）。

## 最佳实践

1. **配置日志目录**：确保`log_directory`路径正确且有读取权限
2. **使用筛选功能**：利用搜索和过滤功能快速找到相关日志
3. **批量选择**：支持同时选择多个TraceID进行批量报告
4. **检查配置**：确保报告服务器地址可访问

## 相关文档

- **客户端README**: `tools/report/client/README.md`
- **服务器README**: `tools/report/server/README.md`
