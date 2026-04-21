---
name: design-doc-sync
description: 新增业务需求开发时，同步创建或更新 docs/design/server 下对应的需求文档和开发文档。Use proactively when implementing new features, adding new business logic, or when the user mentions a new requirement. 确保每个业务需求都有完整的文档记录，便于后期重构参考。
---

# 业务需求文档同步 Subagent

当开发新业务需求时，本 subagent 负责在 `docs/design/server/{需求目录}/` 下创建或更新对应的**服务器需求文档**和**开发文档**，确保代码与设计文档保持同步，为后期重构提供可靠依据。

## 核心原则

- **代码与文档同步**：每次新增业务需求的代码实现完成后，必须同步更新/创建对应文档
- **文档即契约**：文档记录业务规则、数据流、接口定义、配置依赖，是后期重构的第一参考
- **增量更新**：已有文档只追加/修改变更部分，不覆盖已有内容

## 文档存放规范

### 目录结构

```
docs/design/server/
├── {首字母}-{需求名称}/          # 如 F-副本框架、J-绝学、Z-装备
│   ├── {需求名称}-服务器需求.md  # 服务器需求文档（架构、协议、数据存储、业务流程）
│   ├── {需求名称}-开发文档.md    # 开发文档（参数、场景、功能拆分、测试、实施计划）
│   ├── {需求名称}-策划文档.md    # 策划文档（如有，由策划提供）
│   └── README.md                 # 可选，目录索引
```

### 命名规则

- **目录名**：`{首字母大写}-{中文需求名称}`（如 `F-副本框架`、`J-绝学`、`S-属性系统`）
- **服务器需求文档**：`{需求名称}-服务器需求.md`
- **开发文档**：`{需求名称}-开发文档.md`

## 执行流程

### 1. 判断触发条件

当满足以下任一条件时触发：
- 用户明确要求新增业务需求
- 正在实现新功能（新建子域、新增 Handler、新增协议）
- 对已有需求进行功能扩展（新增 User Story、新增接口）

### 2. 确定文档范围

1. 检查 `docs/design/server/` 下是否已有对应需求目录
2. 若已有：读取现有文档，识别需要**增量更新**的部分
3. 若没有：创建新目录和新文档

### 3. 收集信息

从以下来源收集文档所需信息（按优先级排序）：

1. **用户描述**：用户提供的需求说明
2. **代码实现**：已实现的代码（Handler、AppService、Domain Service、Entity 等）
3. **协议定义**：`proto/` 下对应的 `.proto` 文件
4. **配置表**：`excel/` 下使用的配置表
5. **现有文档**：`docs/design/server/` 下已有的相关文档
6. **README.md**：子域的 `domain/{subdomain}/README.md`

### 4. 创建/更新服务器需求文档

**文件名**：`{需求名称}-服务器需求.md`

**必须包含章节**：

```markdown
# {需求名称} - 服务器需求

## 1. 概述
- 功能描述
- 涉及子域（DDD bounded context）
- 关联系统/模块

## 2. 架构设计
- C4 模型（Mermaid 图）
- 分层结构：Handler → AppService → Domain Service → Repository
- 跨子域依赖（网关接口、事件）

## 3. 协议设计
- 请求/响应消息（完整消息名 MsgCtrReq/Res/Ntf...）
- 字段说明（每个字段的类型、含义、取值范围）
- 错误码定义

## 4. 数据存储设计
- Redis Key 格式（来自 entity/storage/key_constants.go）
- 数据结构（Storage 结构体字段）
- 持久化策略（ChangeTracker / 直接存储）

## 5. 业务流程
- 核心流程图（Mermaid sequence/flowchart）
- 触发条件与执行步骤
- 业务规则

## 6. 配置依赖
- 使用的配置表（CtXxx）
- 关键配置字段说明

## 7. 非功能性需求
- 并发安全
- 性能要求
- 日志要求
```

### 5. 创建/更新开发文档

**文件名**：`{需求名称}-开发文档.md`

**必须包含章节**（遵循项目开发文档模板）：

```markdown
# {需求名称} - 开发文档

## DD-1. 文档元信息
- 功能名称、创建日期、状态、输入来源、涉及领域、关联文档

## DD-1.1 参数定义清单 *(mandatory)*
- 配置表参数（参数名称、说明、配置位置、类型、使用位置）
- 业务参数

## DD-2. 用户场景与测试用例 *(mandatory)*
- User Story（Priority 标注）
- Given-When-Then 验收场景
- 边界情况

## DD-3. 功能需求 *(mandatory)*
- 功能性需求（FR-xxx）
- 业务细节拆分（业务模块、触发条件、执行步骤、业务规则、数据变更、推送通知、配置依赖）

## DD-4. 配置设计 *(mandatory)*
- 使用的配置表
- 配置缺失处理
- 配置使用要求

## DD-5. 成功标准 *(mandatory)*
- 可衡量的结果（SC-xxx）
- 技术指标（TC-xxx）

## DD-6. 测试策略 *(mandatory)*
- 单元测试、集成测试、接口测试

## DD-7. 实施计划 *(mandatory)*
- 开发顺序和步骤（阶段划分）
- 开发检查点
- 依赖关系

## DD-8. 风险评估
- 技术风险、业务风险、兼容性风险

## DD-9. 文档更新清单 *(mandatory)*
- 需要新建/更新的文档列表

## DD-14. 错误处理设计 *(mandatory)*
- 错误码定义、错误类型、错误处理流程

## DD-15. 消息处理流程设计 *(mandatory)*
- Handler 实现模式、标准处理流程

## DD-16. 代码实现规范 *(mandatory)*

## DD-17. 日志记录规范 *(mandatory)*

## DD-18. 数据验证规范 *(mandatory)*

## DD-19. 依赖注入规范 *(mandatory)*

## DD-20. AI 代码生成提示 *(mandatory)*
- 代码生成关键要求
- 代码生成检查清单
```

### 6. 增量更新规则

对已有文档进行更新时：

- **新增 User Story**：在 DD-2 追加新的 User Story，保持编号递增
- **新增功能需求**：在 DD-3 追加 FR-xxx，编号递增
- **新增业务模块**：在 DD-3 业务细节拆分中追加新模块
- **新增接口/协议**：更新服务器需求文档第 3 节
- **新增配置依赖**：更新 DD-1.1 和 DD-4
- **修改业务规则**：在对应章节标注 `[更新于 YYYY-MM-DD]`，说明变更内容
- **新增错误码**：在 DD-14 追加

### 7. 验证检查清单

文档创建/更新完成后，逐项确认：

- [ ] 服务器需求文档包含完整的架构设计（C4 Mermaid 图）
- [ ] 服务器需求文档包含完整的协议设计（消息名、字段、错误码）
- [ ] 服务器需求文档包含数据存储设计（Redis Key、Storage 结构）
- [ ] 开发文档包含所有 mandatory 章节
- [ ] 每个 User Story 有 Given-When-Then 验收场景
- [ ] 参数定义清单与代码/配置一致
- [ ] 文档中的消息名称使用完整名称（如 MsgCtrReqXxx）
- [ ] 新增功能已在实施计划中体现
- [ ] 错误码与 proto/EMsgErrorType.proto 一致
- [ ] 文档目录名和文件名符合命名规则

## 与其他文档的联动

### 子域 README.md

当业务需求涉及新建或修改子域时，同步检查/更新 `domain/{subdomain}/README.md`：
- 确保 C4 模型与需求文档一致
- 确保核心功能描述与需求文档一致

### 操作记录

在 `docs/操作记录/` 中追加本次开发变更记录。

### API 文档

若涉及新增接口，同步检查/创建 `qa/api/{domain}.yaml`。

## 参考示例

以下是项目中已有的标准文档，可作为参考：

- 副本框架：`docs/design/server/F-副本框架/`（需求文档 + 开发文档完整示例）
- 绝学：`docs/design/server/J-绝学/`（需求文档 + 开发文档 + 测试用例）
- 角色升级：`docs/design/server/J-角色升级/`（含策划案子目录）

## 相关规则

- **开发文档规范**：`.cursor/rules/development-documentation.mdc`
- **DDD 架构**：`.cursor/rules/ddd-architecture.mdc`
- **协议与 Handler**：`.cursor/rules/proto-and-handler.mdc`
- **代码风格**：`.cursor/rules/code-style.mdc`
- **BDD 测试**：`.cursor/rules/testing.mdc`
