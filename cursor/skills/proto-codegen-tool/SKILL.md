---
name: proto-codegen-tool
description: 当修改.proto文件后需要重新生成Protobuf代码时使用此工具。必须使用此工具，不能直接使用protoc命令。
---

# Proto代码生成工具Skill

## 工具概述

Proto代码生成工具是基于DDD架构的Protobuf代码生成增强工具。虽然`protoc`本身可以生成标准的`.pb.go`文件，但本工具在此基础上提供了额外的代码生成和整理功能。

**⚠️ 重要提示**: **每次protobuf代码生成都必须使用本工具**，不要直接使用`protoc`命令。

## 使用场景

- 修改`.proto`文件后需要重新生成代码
- 新增协议消息后需要生成对应的Go代码
- 修改枚举定义后需要重新生成枚举代码
- 需要生成消息类型枚举文件时

## 前置条件

- Go环境已配置
- 项目依赖已安装（`go mod download`）
- `.proto`文件已准备好（位于`proto/`目录）

## 命令格式

### 方式一：使用go run（推荐）

```bash
cd tools/proto/cmd
go run main.go -proto ../../../proto -output ../../../message
```

### 方式二：编译后使用

```bash
cd tools/proto
go build -o proto-gen.exe ./cmd
./proto-gen.exe -proto ../proto -output ../../message
```

### 参数说明

- `-proto`: proto文件目录（默认：`../proto`）
- `-output`: 输出目录（默认：`../../message`）

## 输出说明

工具会生成以下文件：

1. **每个.proto文件对应的.pb.go文件**: 使用protoc自动生成的Protobuf Go代码
   - 例如：`CtrSvr.proto` → `CtrSvr.pb.go`
   - 例如：`BtlSvr.proto` → `BtlSvr.pb.go`

2. **整理后的代码文件**:
   - **EMsgToServerType.go**: 客户端到服务器的消息类型枚举
   - **EMsgToClientType.go**: 服务器到客户端的消息类型枚举
   - **EMsgType.go**: 消息类型方法实现

## 工具特性

1. **枚举值冲突处理**：自动处理Protobuf的枚举值全局唯一性要求（使用临时目录方案）
2. **代码后处理**：对生成的`.pb.go`文件进行类型名称映射，确保类型名称符合项目规范
3. **消息类型枚举生成**：自动生成`EMsgToServerType.go`和`EMsgToClientType.go`
4. **消息类型方法生成**：自动生成`EMsgType.go`，为每个消息类型生成`GetMsgType()`和`GetMsgTypeInt32()`方法
5. **消息ID生成**：使用与Unity C#客户端一致的hash算法（C# GetHashCode()）生成消息ID

## 工作流程

工具使用职责链模式，按照以下4个Handler执行：

1. **PreprocessProtoHandler** - Proto文件预处理（创建临时目录、拷贝文件、解析枚举冲突）
2. **GeneratePbFilesHandler** - 生成并修复Pb文件（生成.pb.go文件、映射修复）
3. **ParseAndGenerateHandler** - 解析并生成代码（解析proto文件、生成整理后的代码）
4. **CleanupTempDirHandler** - 清理临时目录

## 常见问题

### Q: 为什么不能直接使用protoc？

A: 因为本工具提供了以下额外功能：
- 自动处理枚举值冲突（使用临时目录方案）
- 自动修复生成的代码中的重复前缀问题
- 生成消息类型枚举文件（`EMsgToServerType.go`、`EMsgToClientType.go`、`EMsgType.go`）
- 使用与Unity C#客户端一致的hash算法生成消息ID

### Q: 枚举值冲突如何处理？

A: 工具使用临时目录方案自动处理：
1. 创建临时目录并拷贝所有`.proto`文件
2. 在临时目录中为枚举值添加类型前缀（如`None` → `EMsgSectType_None`）
3. 使用临时目录中的文件生成代码
4. 自动修复protoc生成的重复前缀
5. 程序结束时自动删除临时目录

### Q: 生成的代码在哪里？

A: 生成的代码位于`message/`目录下：
- `.pb.go`文件：与`.proto`文件对应的位置
- `EMsgToServerType.go`、`EMsgToClientType.go`、`EMsgType.go`：在`message/`根目录

## 最佳实践

1. **修改协议后立即生成**：修改`.proto`文件后，立即运行此工具生成代码
2. **检查生成结果**：生成后检查是否有编译错误
3. **提交变更**：同时提交`.proto`和生成的`.pb.go`文件
4. **不要手动修改生成文件**：`message/`目录下的`.pb.go`文件都是自动生成的，禁止手动修改

## 相关文档

- **工具README**: `tools/proto/README.md`
- **协议与生成文件**: `.cursor/rules/proto-and-handler.mdc`
