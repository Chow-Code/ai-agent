---
description: 业务实现完整性检查命令
alwaysApply: false
---

# 业务实现完整性检查命令

## 命令用途

执行此命令时，AI应该对指定的业务模块进行完整性检查，验证代码实现是否完整符合开发文档中的需求定义。

## 与 `dev-implement.md` 的衔接

- **`/dev-implement {功能名}`** 按 DD-7.1 做「单协议 → BDD → codereview」闭环，容易在**模块整体**上留下缺口（例如：某协议从未写集成用例、文档要求扣费但 App 层未接背包、FR 级属性/存储要求未对账）。
- **本命令**在 **FR / 全协议 / 参数 / 存储 / 测试覆盖 / 经济闭环** 等维度做横切，产出 **`docs/操作记录/{日期}-{功能名}-业务实现完整性检查报告.md`**。
- **约定**：`dev-implement` 的 **Phase 6 收尾** 与 **「完成验证」** 中已将本命令列为**必做步骤**；生成报告后主 Agent 须按 **`dev-implement` → Phase 6 续** 分析报告并**补开发/补测**、**重跑本检查**，直至高优问题关闭或已书面分期；仅此时才可输出「✅ 开发完成」类最终结论。
- 用户可单独执行 **`/business-implementation-check {功能名}`** 做中期体检，不必等 dev-implement 全部结束。

## 执行步骤

### 本项目结构约定（TL3Server · 中心服 game）

执行 **Step 3** 时须按下列**真实路径**核对（勿使用已废弃的 `interfaces/handler`、`excel.GetXXX` 等写法）：

| 层级 | 路径模式 | 说明 |
|------|----------|------|
| 设计文档 | `docs/design/server/{模块名称}/` | `*-服务器需求.md`、`*-开发文档.md`、可选 `*-配置使用.md` |
| 领域层 | `srv/game/domain/{subdomain}/` | 常见子目录：`entity/`、`entity/storage/`、`service/`、`port/`（仓储等端口）、`infrastructure/`（仓储实现、`pet_service_factory`、事件等） |
| 仓储 | `srv/game/domain/{subdomain}/port/*.go` + `.../infrastructure/repository/` | **多数子域无**独立的顶层 `domain/.../repository/` 目录，接口在 `port/` |
| 应用层 | `srv/game/application/service/{module}/` | `*_app_service.go`；部分模块含 `dto/` 子目录（**非强制**） |
| 接口层（Handler） | **`srv/game/handler/{module}/`** | 如 `pet_handler.go`、`dungeon_handler.go`（**不是** `srv/game/interfaces/handler/`） |
| 集成测试（BDD） | `qa/integration/{domain}/` | 规范见 `.cursor/rules/testing.mdc`；契约 **`qa/api/{domain}.yaml`** |
| 配置读取 | `excel/code` 生成表 + 运行时 **`excel.CfgManager.CtXxx`** | 搜索配置使用：`excel.CfgManager`、`CtPet` 等，**不要**写已不存在的 `excel.GetXXX` |
| 协议与错误码 | `proto/`（源）→ `message/*.pb.go` | `EMsgErrorType` 等在 `message/` |
| Redis Key | 子域 `entity/storage/key_constants.go` 或实体 `GetRedisKey()` | 全仓库**未必**存在统一 `rediskey` 包；检查以**设计文档 Key 与代码常量/格式化是否一致**为准，避免「未找到某工具包」误判 |

**`{subdomain}` / `{module}` / `{domain}` 映射**：通常与功能对应（如宠物：`subdomain=pet`，`module=pet`，集成测试 `domain=pet`）。若文档与目录不一致，以**实际代码目录**为准并在报告中说明。

### Step 1: 定位开发文档

**操作**：根据用户提供的业务模块名称，查找对应的开发文档

**查找位置**：
- 开发文档：`docs/design/server/{模块名称}/` 目录
- 服务器需求：`*-服务器需求.md`
- 开发文档：`*-开发文档.md`

**操作方法**：
```bash
# 搜索开发文档
find docs/design/server -name "*{模块名称}*" -type f
glob_file_search
glob_pattern
**/{模块名称}*.md
```

### Step 2: 读取并解析开发文档

**必须提取的信息**：
1. **功能需求清单（FR-001 到 FR-XXX）**：列出所有功能需求编号和描述
2. **用户场景（User Story）**：列出所有用户场景和验收场景
3. **参数定义清单（DD-1.1）**：列出所有配置参数（PARAM_XXX）
4. **协议设计**：列出所有协议消息（MsgCtrReqXXX、MsgCtrResXXX）
5. **数据存储设计**：列出所有Redis Key格式
6. **错误处理设计**：列出所有错误码定义

**操作方法**：使用 `read_file` 工具读取开发文档，提取关键信息

### Step 3: 执行代码检查

按照以下顺序执行检查，每项检查完成后记录结果：

#### 3.1 架构检查

**检查目标**：验证代码是否符合 DDD 分层与**本仓库**目录习惯

**检查操作**：
1. 使用 `list_dir` 检查：
   - `srv/game/domain/{subdomain}/`（`entity/`、`service/`、`port/`、`infrastructure/` 等）
   - `srv/game/application/service/{module}/`
   - **`srv/game/handler/{module}/`**（Handler 按**业务子目录**划分，与 `handler/registrar.go` 注册一致）

2. 验证要点（**按存在即合理**，缺项需对照设计文档判断是否真缺）：
   - 领域：`entity/`（及常见 `entity/storage/`）、`service/`、**`port/`**（端口）
   - 基础设施：`**domain/{subdomain}/infrastructure/**`（仓储实现、Factory、事件等）
   - 应用层：`*_app_service.go`；`dto/` 仅部分模块具备
   - **不要求**存在顶层 `domain/.../repository/` 或 `interfaces/handler/`

**检查命令**：
```bash
list_dir srv/game/domain/{subdomain}
list_dir srv/game/handler/{module}
list_dir srv/game/application/service/{module}
```

**记录结果**：记录架构是否符合规范；若与设计文档目录图不一致，注明**以仓库为准**或**待文档修订**

#### 3.2 功能需求检查

**检查目标**：验证开发文档中列出的所有功能需求（FR-001 到 FR-XXX）是否都已实现

**检查操作**：
1. 从开发文档中提取所有功能需求编号（FR-001, FR-002, ...）
2. 对每个功能需求，使用 `codebase_search` 搜索相关实现：
   - 搜索实体实现：`codebase_search "How is FR-001 implemented?"`
   - 搜索应用服务：`codebase_search "Where is FR-001 business logic handled?"`
   - 搜索 Handler：`grep -r "Handle" srv/game/handler/{module}/`（本仓库多为 `HandlePetXxx`、`HandleDungeonXxx` 等，**未必**以 `HandleMsgCtrReq` 前缀命名）

3. 记录每个FR的实现状态：
   - ✅ 已实现：记录代码位置
   - ❌ 未实现：记录缺失的部分

**必须检查的层次**：
- 实体层（Entity）
- 仓储接口（Repository Interface）
- 仓储实现（Repository Implementation）
- 应用服务（Application Service）
- Handler层（Handler）
- 协议处理（Message Handler）

**输出格式**：
```markdown
### FR-001: {功能名称}
- ✅ 实体实现：`srv/game/domain/{subdomain}/entity/...`
- ✅ 仓储端口：`srv/game/domain/{subdomain}/port/...`
- ✅ 仓储实现：`srv/game/domain/{subdomain}/infrastructure/repository/...`
- ✅ 应用服务：`srv/game/application/service/{module}/..._app_service.go`
- ✅ Handler：`srv/game/handler/{module}/..._handler.go`
- ❌ 测试文件：缺失（注明 `qa/integration/{domain}/` 或 `*_test.go`）
```

#### 3.3 用户场景检查

**检查目标**：验证开发文档中的所有用户场景（User Story）和验收场景是否实现

**检查操作**：
1. 从开发文档中提取所有User Story
2. 对每个User Story，提取所有Given-When-Then验收场景
3. 使用 `codebase_search` 搜索对应实现：
   - `codebase_search "How is User Story 1 implemented?"`
4. 记录每个场景的实现状态

**输出格式**：
```markdown
### User Story 1: {场景描述}
- ✅ Given-When-Then 场景1：已实现
- ❌ Given-When-Then 场景2：缺失（缺少XXX验证）
```

#### 3.4 参数配置检查

**检查目标**：验证所有配置参数是否从配置表读取，而非硬编码

**检查操作**：
1. 从开发文档中提取所有参数定义（PARAM_XXX）及对应配置表/字段名
2. 使用 `grep` 在 `srv/game/domain/{subdomain}/`、`srv/game/application/service/{module}/` 搜索 **`excel.CfgManager.CtXxx`**、`TryGetValue`、`GetList` 等
3. 验证与 DD-1.1 /《配置使用》一致；禁止仅凭「魔法数」推断，需对照表名
4. 对可疑字面量结合业务再判断（排除测试文件）

**检查命令**：
```bash
# 配置读取（本仓库典型形态）
grep -r "excel\.CfgManager\.Ct" srv/game/domain/{subdomain}/ srv/game/application/service/{module}/ --include="*.go"

# 辅助：硬编码嫌疑（需人工结合上下文排除枚举/常量）
grep -rE "\b150\b|\b360\b" srv/game/domain/{subdomain}/ --include="*.go" | grep -vE "test|Test|_test\.go"
```

**输出格式**：
```markdown
### 参数配置检查
- ✅ PARAM_XXX：从 `ConfigTable.Field` 读取
- ❌ PARAM_YYY：硬编码为 150（应改为从配置读取）
```

#### 3.5 协议接口检查

**检查目标**：验证所有协议消息是否都有对应的Handler实现

**检查操作**：
1. 从开发文档中提取所有协议消息（MsgCtrReqXXX、MsgCtrResXXX）
2. 在 Handler 中搜索（**按模块子目录**）：
   - `grep -r "Handle" srv/game/handler/{module}/ --include="*.go"`
   - 或 `codebase_search "Where is MsgCtrReqXXX handled?"`
3. 与 `handler/registrar.go`（或各模块注册处）交叉核对是否挂载
4. 与 **`qa/api/{domain}.yaml`** 路径与消息名一致

**输出格式**：
```markdown
### 协议接口检查
- ✅ MsgCtrReqXXX：已实现（Handler: `srv/game/handler/{module}/xxx_handler.go`）
- ❌ MsgCtrReqYYY：未实现
```

#### 3.6 数据存储检查

**检查目标**：验证 Redis Key 与设计文档一致，且生成方式可维护（常量或 `GetRedisKey()`）

**检查操作**：
1. 从开发文档中提取 K-1、K-2 等 Key 格式说明
2. 在子域中搜索：
   - `grep -r "RedisKey\|redis\|KeyFormat" srv/game/domain/{subdomain}/ --include="*.go"`
   - 常见位置：`entity/storage/key_constants.go`、各 `*Storage.GetRedisKey()`
3. **说明**：本仓库**不一定**存在全局 `rediskey` 包；若某模块使用实体内常量格式化，在报告中记为「符合本子域约定」，并对比《服务器需求》中的 Key 模板是否一致
4. 若项目另有统一 Key 工具包，再补充检索该包（以实际路径为准）

**输出格式**：
```markdown
### 数据存储检查
- ✅ K-1：`srv/game/domain/{subdomain}/entity/storage/key_constants.go` 与文档一致
- ⚠️ 与 `rediskey` 包：本子域未使用统一包（若规范要求迁移，记入中优建议）
```

#### 3.7 错误处理检查

**检查目标**：验证错误码定义和处理逻辑是否完整

**检查操作**：
1. 从开发文档中提取业务相关错误码（及 `EMsgErrorType` 枚举名）
2. 枚举定义：`proto/*.proto` 源文件；生成代码：`grep -r "EMsgErrorType_" message/ --include="*.go"`
3. 业务返回：在 `srv/game/domain/{subdomain}/`、`srv/game/application/service/{module}/`、`srv/game/handler/{module}/` 中检索具体错误枚举使用是否与文档一致
4. `codebase_search` 辅助定位某错误码首次返回位置

#### 3.8 日志记录检查

**检查目标**：验证日志使用是否符合规范

**检查操作**：
1. 搜索不符合规范的日志：
   - `grep -r "fmt.Println\|fmt.Printf" srv/game/domain/{subdomain}/ --include="*.go" | grep -v "test"`
2. 验证是否使用统一日志库：
   - `grep -r "tlog.LogCommonLogWithContext" srv/game/domain/{subdomain}/ --include="*.go" | head -10`

#### 3.9 测试检查

**检查目标**：验证测试文件是否完整

**检查操作**：
1. **单元测试**：`glob_file_search` → `srv/game/domain/{subdomain}/**/*_test.go`（及同模块其它层若有）
2. **集成测试（BDD）**：`qa/integration/{domain}/*_test.go`；用例与 **`qa/api/{domain}.yaml`**、开发文档 DD-2 BDD 条目对账
3. **勿依赖** `api_test/` 路径（本仓库**无**该目录）；接口说明以 `qa/api` 为准
4. 记录缺测协议或缺 `BDD-Px-yy` 映射的项

#### 3.10 文档检查

**检查目标**：验证子域文档是否更新

**检查操作**：
1. 检查子域README：`read_file srv/game/domain/{subdomain}/README.md`
2. 验证文档内容是否与代码实现一致

### Step 4: 生成检查报告

**必须执行**：完成所有检查后，生成Markdown格式的检查报告并保存到文件

**报告结构**：
1. **基本信息**：业务模块、检查日期、开发文档路径
2. **检查结果概览**：完成度统计
3. **详细检查结果**：每个检查项的结果
4. **问题清单**：按优先级列出问题
5. **建议**：修复建议

**保存位置**：
- 文件路径：`docs/操作记录/{YYYY-MM-DD}-{业务模块名称}-业务实现完整性检查报告.md`（或与 `dev-implement` 约定文件名一致）
- 示例：`docs/操作记录/2026-03-31-C-宠物-业务实现完整性检查报告.md`

**报告模板**：见下方"报告模板"章节

## 必须执行的操作

执行此命令时，AI**必须**：

1. ✅ 读取并解析开发文档
2. ✅ 执行所有10项检查（架构、功能需求、用户场景、参数配置、协议接口、数据存储、错误处理、日志记录、测试、文档）
3. ✅ 记录每个检查项的结果
4. ✅ 生成Markdown格式的检查报告
5. ✅ 保存报告到 `docs/操作记录/` 目录
6. ✅ 向用户展示检查结果概览和主要问题

## 报告模板

执行检查后，必须按照以下模板生成报告：

```markdown
# 业务实现完整性检查报告

## 基本信息
- **业务模块**：{模块名称}
- **检查日期**：{YYYY-MM-DD}
- **开发文档**：`docs/design/server/{模块路径}/{模块名称}-开发文档.md`

## 检查结果概览
- **功能需求总数**：{数量}
- **已实现功能**：{数量}
- **缺失功能**：{数量}
- **完成度**：{百分比}%

## 详细检查结果

### 1. 架构检查
{详细结果...}

### 2. 功能需求检查
{列出所有FR的检查结果...}

### 3. 用户场景检查
{列出所有User Story的检查结果...}

### 4. 参数配置检查
{列出所有参数的检查结果...}

### 5. 协议接口检查
{列出所有协议的检查结果...}

### 6. 数据存储检查
{列出所有Redis Key的检查结果...}

### 7. 错误处理检查
{列出所有错误码的检查结果...}

### 8. 日志记录检查
{列出日志检查结果...}

### 9. 测试检查
{列出测试检查结果...}

### 10. 文档检查
{列出文档检查结果...}

## 问题清单

### 高优先级问题
1. **{问题标题}**：{问题描述}
   - 位置：`{文件路径}:{行号}`
   - 建议：{修复建议}

### 中优先级问题
{中优先级问题列表...}

### 低优先级问题
{低优先级问题列表...}

## 建议
1. {建议1}
2. {建议2}
...
```

## 优先级划分规则

- **高优先级**：功能缺失、硬编码参数、协议未实现
- **中优先级**：错误处理不完整、日志不规范
- **低优先级**：文档未更新、测试缺失

## 相关工具

**推荐使用的工具**：
- `codebase_search`：搜索代码实现
- `grep`：搜索特定模式
- `glob_file_search`：查找文件
- `list_dir`：检查目录结构
- `read_file`：读取文档和代码
