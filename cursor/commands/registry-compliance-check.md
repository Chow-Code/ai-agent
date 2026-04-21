---
description: Registry 使用规范检查命令
alwaysApply: false
---

# Registry 使用规范检查命令

## 命令用途

执行此命令时，AI应该对指定的领域服务进行 **Registry 缓存** 与 **持久化模式** 两类规范检查：前者验证 `GetOrCreate`、Loader、DI、下线清理等；后者验证是否按项目标准接入 `ChangeTracker` / `persist.MarkModified`，避免 AppService 大量手动 `repo.Save`、Factory 暴露 `GetRepository` 等与 backpack 等标准域不一致的路径。

## 执行步骤

### Step 1: 定位领域代码

**操作**：根据用户提供的领域名称，查找对应的领域代码

**查找位置**：
- 领域层：`srv/game/domain/{subdomain}/`
- 基础设施层：`srv/game/domain/{subdomain}/infrastructure/`
- 应用层（持久化合规）：`srv/game/application/service/{subdomain}/`
- DI 层：`srv/game/infrastructure/di/`

**操作方法**：
```bash
# 搜索领域目录
list_dir srv/game/domain/{subdomain}
glob_file_search glob_pattern **/{subdomain}*service_factory.go
glob_file_search glob_pattern **/{subdomain}*cache_invalidator.go
```

### Step 2: 执行规范检查（共 10 项）

按以下顺序执行检查，每项完成后记录结果（前 8 项侧重 Registry，第 9～10 项侧重持久化与 AppService）：

#### 2.1 领域类型定义检查

**检查目标**：验证领域类型常量是否在 `domain_type.go` 中定义

**检查操作**：
1. 读取 `srv/game/infrastructure/technical/cache/registry/domain_type.go`
2. 搜索是否存在 `DomainType{Subdomain}` 常量（如 `DomainTypeBackpack`）
3. 验证常量命名是否符合规范（首字母大写，驼峰命名）

**检查命令**：
```bash
grep -r "DomainType.*{subdomain}" srv/game/infrastructure/technical/cache/registry/domain_type.go -i
```

**输出格式**：
```markdown
### 1. 领域类型定义检查
- ✅ DomainType{Subdomain}：已定义（`domain_type.go:7`）
- ❌ DomainType{Subdomain}：未定义（需要添加常量定义）
```

#### 2.2 领域类型注册检查

**检查目标**：验证领域类型是否在 `u64DomainTypes` 数组中注册

**检查操作**：
1. 读取 `srv/game/infrastructure/technical/cache/registry/domain_manager_registry.go`
2. 搜索 `u64DomainTypes` 数组
3. 验证是否包含 `DomainType{Subdomain}`

**检查命令**：
```bash
grep -A 10 "var u64DomainTypes" srv/game/infrastructure/technical/cache/registry/domain_manager_registry.go
```

**输出格式**：
```markdown
### 2. 领域类型注册检查
- ✅ DomainType{Subdomain}：已在 u64DomainTypes 中注册
- ❌ DomainType{Subdomain}：未在 u64DomainTypes 中注册（需要添加到数组）
```

#### 2.3 ServiceFactory 实现检查

**检查目标**：验证 ServiceFactory 是否正确实现 `persist.Loader` 接口

**检查操作**：
1. 查找 ServiceFactory 文件：`domain/{subdomain}/infrastructure/{subdomain}_service_factory.go`
2. 检查是否声明实现 `persist.Loader` 接口：
   ```go
   var _ persist.Loader[uint64, *xxxService.XxxService] = (*XxxServiceFactory)(nil)
   ```
3. 检查是否实现了 `Load(ctx context.Context, key uint64)` 方法
4. 检查 Factory 结构体是否包含 `registry persist.InstanceRegistry[uint64]` 字段

**检查命令**：
```bash
# 搜索 Loader 接口声明
grep -r "persist.Loader" srv/game/domain/{subdomain}/infrastructure/*service_factory.go

# 搜索 Load 方法实现
grep -A 10 "func.*Load.*context.Context" srv/game/domain/{subdomain}/infrastructure/*service_factory.go

# 搜索 registry 字段
grep -r "registry.*persist.InstanceRegistry" srv/game/domain/{subdomain}/infrastructure/*service_factory.go
```

**输出格式**：
```markdown
### 3. ServiceFactory 实现检查
- ✅ Loader 接口声明：已声明 `var _ persist.Loader[uint64, *XxxService] = (*XxxServiceFactory)(nil)`
- ✅ Load 方法实现：已实现 `Load(ctx context.Context, key uint64) (*XxxService, error)`
- ✅ Registry 字段：Factory 结构体包含 `registry persist.InstanceRegistry[uint64]` 字段
- ❌ Loader 接口声明：缺失（需要添加接口声明）
- ❌ Load 方法实现：缺失或签名不正确（需要实现 Load 方法）
- ❌ Registry 字段：缺失（需要在 Factory 结构体中添加 registry 字段）
```

#### 2.4 CreateByXXX 方法检查

**检查目标**：验证 `CreateByXXX` 方法是否使用 `persist.GetOrCreate`，而非手动实现缓存逻辑

**检查操作**：
1. 搜索 `CreateByPlayerID`、`CreateByRoleID` 等方法
2. 检查方法实现是否使用 `persist.GetOrCreate`
3. 检查是否存在手动实现缓存逻辑（如手动调用 `GetInstance`、`SetInstance`）

**检查命令**：
```bash
# 搜索 CreateByXXX 方法
grep -A 5 "func.*CreateBy" srv/game/domain/{subdomain}/infrastructure/*service_factory.go

# 检查是否使用 persist.GetOrCreate
grep -r "persist.GetOrCreate" srv/game/domain/{subdomain}/infrastructure/*service_factory.go

# 检查是否存在手动缓存逻辑（错误示例）
grep -r "registry.GetInstance\|registry.SetInstance" srv/game/domain/{subdomain}/infrastructure/*service_factory.go | grep -v "CreateFromEntity"
```

**输出格式**：
```markdown
### 4. CreateByXXX 方法检查
- ✅ CreateByPlayerID：使用 `persist.GetOrCreate(ctx, f.registry, playerID, f)`
- ❌ CreateByPlayerID：手动实现缓存逻辑（应改为使用 persist.GetOrCreate）
- ❌ CreateByPlayerID：未使用 persist.GetOrCreate（需要修改实现）
```

**错误示例识别**：
```go
// ❌ 错误：手动实现缓存逻辑
func (f *XxxServiceFactory) CreateByPlayerID(ctx context.Context, playerID uint64) (*XxxService, error) {
    if svc, ok := f.registry.GetInstance(playerID); ok {
        return svc.(*XxxService), nil
    }
    // ... 加载逻辑
    f.registry.SetInstance(playerID, svc)
    return svc, nil
}

// ✅ 正确：使用 persist.GetOrCreate
func (f *XxxServiceFactory) CreateByPlayerID(ctx context.Context, playerID uint64) (*XxxService, error) {
    return persist.GetOrCreate(ctx, f.registry, playerID, f)
}
```

#### 2.5 CreateFromEntity 方法检查（可选）

**检查目标**：验证 `CreateFromEntity` 方法是否正确处理缓存

**检查操作**：
1. 搜索 `CreateFromEntity` 方法
2. 检查是否先查询缓存
3. 检查创建后是否写入缓存

**检查命令**：
```bash
grep -A 15 "func.*CreateFromEntity" srv/game/domain/{subdomain}/infrastructure/*service_factory.go
```

**输出格式**：
```markdown
### 5. CreateFromEntity 方法检查
- ✅ CreateFromEntity：先查缓存，未命中则创建并写入缓存
- ⚠️ CreateFromEntity：方法不存在（可选，如不需要可忽略）
- ❌ CreateFromEntity：未写入缓存（需要添加 SetInstance 调用）
```

#### 2.6 DI 注入检查

**检查目标**：验证 Registry 是否在 DI 中正确获取和注入

**检查操作**：
1. 在 `application_factory.go` 中搜索领域服务组装函数（如 `new{Subdomain}Services`）
2. 检查是否通过 `GetPlayerInstanceRegistry` 获取 Registry
3. 检查是否将 Registry 注入到 ServiceFactory 或 AppService

**检查命令**：
```bash
# 搜索领域服务组装函数
grep -A 20 "func new{Subdomain}Services" srv/game/infrastructure/di/application_factory.go

# 搜索 Registry 获取
grep -r "GetPlayerInstanceRegistry.*DomainType{Subdomain}" srv/game/infrastructure/di/

# 搜索 Registry 注入
grep -r "New.*ServiceFactory.*registry\|New.*AppService.*registry" srv/game/infrastructure/di/application_factory.go
```

**输出格式**：
```markdown
### 6. DI 注入检查
- ✅ Registry 获取：在 `new{Subdomain}Services` 中通过 `GetPlayerInstanceRegistry(DomainType{Subdomain})` 获取
- ✅ Registry 注入：Registry 已注入到 ServiceFactory 或 AppService
- ❌ Registry 获取：未在 DI 中获取 Registry
- ❌ Registry 注入：Registry 未注入到 ServiceFactory 或 AppService
```

#### 2.7 缓存清理器检查（可选）

**检查目标**：验证是否实现了缓存清理器，用于玩家下线时清理缓存

**检查操作**：
1. 查找缓存清理器文件：`domain/{subdomain}/infrastructure/{subdomain}_cache_invalidator.go`
2. 检查是否实现了 `RemoveInstance` 方法
3. 检查是否在 `newPlayerEventManager` 中注册了事件处理器

**检查命令**：
```bash
# 搜索缓存清理器
glob_file_search glob_pattern **/{subdomain}*cache_invalidator.go

# 搜索事件处理器注册
grep -r "{Subdomain}CacheInvalidator\|{Subdomain}EventHandler" srv/game/infrastructure/di/application_factory.go
```

**输出格式**：
```markdown
### 7. 缓存清理器检查
- ✅ 缓存清理器：已实现 `{Subdomain}CacheInvalidator`
- ✅ 事件处理器：已在 `newPlayerEventManager` 中注册
- ⚠️ 缓存清理器：未实现（可选，如不需要下线清理可忽略）
- ❌ 事件处理器：未注册（如实现了清理器，需要注册事件处理器）
```

#### 2.8 Repository Factory 检查（如适用）

**检查目标**：验证 ServiceFactory 是否在 `repository_factory.go` 中正确创建

**检查操作**：
1. 在 `repository_factory.go` 中搜索 ServiceFactory 创建
2. 检查是否获取了对应的 Registry
3. 检查是否将 Registry 注入到 Factory

**检查命令**：
```bash
grep -A 10 "New.*ServiceFactory" srv/game/infrastructure/di/repository_factory.go | grep -A 10 "{subdomain}"
```

**输出格式**：
```markdown
### 8. Repository Factory 检查
- ✅ ServiceFactory 创建：在 `newRepositories` 中创建，并注入 Registry
- ⚠️ ServiceFactory 创建：在 `application_factory.go` 中创建（如适用）
- ❌ ServiceFactory 创建：未创建或未注入 Registry
```

#### 2.9 持久化模式检查（实体层与 Port）

**检查目标**：验证玩家数据变更是否走项目标准 **`persist.MarkModified` → `ChangeTracker` → 定时 `SaveData`** 路径（参考 [common/persist/persist.go](common/persist/persist.go) 与 backpack），而非仅依赖 AppService 末尾显式 `repo.Save`。

**检查操作**：
1. 在 `domain/{subdomain}/entity/` 中搜索聚合根是否声明 `var _ persist.PersistableEntity = (*Xxx)(nil)`
2. 搜索实体中是否有私有 `markModified()`，且内部调用 `persist.MarkModified(...)`
3. 读取 `domain/{subdomain}/port/*repository*.go`：标准域的 Repository **port 通常不提供 `Save`**（持久化由 ChangeTracker 提交）；若 port 含 `Save(ctx, ...)`，记为 **⚠️ 可能未走 ChangeTracker**
4. 若领域在 `domain/{subdomain}/README.md` 中**明确记载**采用手动 Save、不走 ChangeTracker，可在报告中标注为 **已知例外**（不将 port 的 `Save` 判为失败，但须写明与标准域差异及后续对齐建议）

**检查命令**：
```bash
grep -r "PersistableEntity\|MarkModified\|markModified" srv/game/domain/{subdomain}/entity/ 2>/dev/null
grep -r "Save(" srv/game/domain/{subdomain}/port/
```

**输出格式**：
```markdown
### 9. 持久化模式检查（实体层与 Port）
- ✅ 聚合根实现 `persist.PersistableEntity` 且存在 `markModified` → `persist.MarkModified`
- ✅ Port 无 `Save`（与 backpack 一致，落库走 ChangeTracker）
- ⚠️ Port 含 `Save`：可能为显式落库路径，需对照 README 是否已知例外
- ❌ 无 `PersistableEntity`/`markModified` 且无文档说明例外：与标准持久化路径不一致（高优先级）
```

**标准参考**（backpack `domain/backpack/entity/backpack.go`）：
```go
var _ persist.PersistableEntity = (*Backpack)(nil)

func (b *Backpack) markModified() {
    persist.MarkModified(b)
}
```

#### 2.10 AppService 持久化合规检查

**检查目标**：验证应用层是否通过 **领域实体变更 + ChangeTracker** 落库，而非在 `application/service/{subdomain}/` 中反复 `GetRepository().Save` / `repo.Save`。

**检查操作**：
1. 在 `srv/game/application/service/{subdomain}/` 下搜索 `repo.Save(`、`GetRepository().Save(`、`\.Save(ctx,`
2. 在 `domain/{subdomain}/infrastructure/*service_factory.go` 搜索是否暴露 `func (f *XxxServiceFactory) GetRepository()`
3. 检查 AppService 是否 `import` 了 `domain/{subdomain}/infrastructure`（标准上应用层宜依赖 port/领域服务，不依赖 infrastructure 具体类型；若仅为拿 Factory 具体类型，记 **⚠️ 依赖方向**）

**检查命令**：
```bash
grep -rn "repo\.Save\|GetRepository()\|\.Save(ctx," srv/game/application/service/{subdomain}/
grep -n "GetRepository" srv/game/domain/{subdomain}/infrastructure/*service_factory.go
grep "domain/{subdomain}/infrastructure" srv/game/application/service/{subdomain}/*.go
```

**输出格式**：
```markdown
### 10. AppService 持久化合规检查
- ✅ AppService 无 `repo.Save` / `GetRepository().Save`；Factory 无 `GetRepository()`
- ⚠️ AppService import 了 `domain/.../infrastructure`（建议后续改为 port 接口注入 Factory）
- ❌ Factory 暴露 `GetRepository()` 且 AppService 多处手动 `repo.Save`：与 backpack/skill/role 标准不一致（高优先级）
```

**错误形态说明**：pet 等领域曾出现 `repo := s.xxxServiceFactory.GetRepository(); repo.Save(ctx, aggregate)` 在多个方法末尾重复，且仓储 `Save` 内对多 Key 全量 `store.SaveData`，与 ChangeTracker 批量提交、按变更追踪的模式不一致。

### Step 3: 生成检查报告

**必须执行**：完成所有检查后，生成Markdown格式的检查报告

**报告结构**：
1. **基本信息**：领域名称、检查日期
2. **检查结果概览**：通过/失败/警告统计
3. **详细检查结果**：每个检查项的结果
4. **问题清单**：按优先级列出问题
5. **修复建议**：针对每个问题的修复建议

**保存位置**：
- 文件路径：`docs/操作记录/{YYYY-MM-DD}-{领域名称}-Registry规范检查报告.md`
- 示例：`docs/操作记录/2025-01-20-背包-Registry规范检查报告.md`

## 必须执行的操作

执行此命令时，AI**必须**：

1. ✅ 定位领域代码目录和文件（含 `application/service/{subdomain}/`）
2. ✅ 执行全部 **10 项**检查（前 8 项 Registry；第 9 项持久化实体/Port；第 10 项 AppService 与 Factory `GetRepository`/手动 `Save`）
3. ✅ 记录每个检查项的结果（✅通过、❌失败、⚠️警告）
4. ✅ 识别错误示例（手动缓存、`GetRepository`+手动 `Save`、无 `markModified` 等）
5. ✅ 生成Markdown格式的检查报告
6. ✅ 保存报告到 `docs/操作记录/` 目录
7. ✅ 向用户展示检查结果概览和主要问题

## 报告模板

执行检查后，必须按照以下模板生成报告：

```markdown
# Registry 使用规范检查报告

## 基本信息
- **领域名称**：{subdomain}
- **检查日期**：{YYYY-MM-DD}
- **ServiceFactory 文件**：`srv/game/domain/{subdomain}/infrastructure/{subdomain}_service_factory.go`

## 检查结果概览
- **总检查项**：10
- **通过项**：{数量}
- **失败项**：{数量}
- **警告项**：{数量}
- **合规度**：{百分比}%（可分「Registry 子项」与「持久化子项」分别统计）

## 详细检查结果

### 1. 领域类型定义检查
{检查结果...}

### 2. 领域类型注册检查
{检查结果...}

### 3. ServiceFactory 实现检查
{检查结果...}

### 4. CreateByXXX 方法检查
{检查结果...}

### 5. CreateFromEntity 方法检查
{检查结果...}

### 6. DI 注入检查
{检查结果...}

### 7. 缓存清理器检查
{检查结果...}

### 8. Repository Factory 检查
{检查结果...}

### 9. 持久化模式检查（实体层与 Port）
{检查结果...}

### 10. AppService 持久化合规检查
{检查结果...}

## 问题清单

### 高优先级问题（必须修复）
1. **{问题标题}**：{问题描述}
   - 位置：`{文件路径}:{行号}`
   - 当前代码：
   ```go
   {错误代码示例}
   ```
   - 修复建议：
   ```go
   {正确代码示例}
   ```

### 中优先级问题（建议修复）
{中优先级问题列表...}

### 低优先级问题（可选修复）
{低优先级问题列表...}

## 修复建议

### 必须修复的问题
1. {修复建议1}
2. {修复建议2}

### 可选优化
1. {优化建议1}
2. {优化建议2}

## 参考实现

以下领域的实现可作为参考：
- **Backpack（Registry + ChangeTracker）**：`domain/backpack/infrastructure/backpack_service_factory.go`（Factory **无** `GetRepository`）；`domain/backpack/entity/backpack.go`（`PersistableEntity` + `markModified`）；`domain/backpack/port/backpack_repository.go`（**无** `Save`，落库走 ChangeTracker）
- **Role**：`domain/role/infrastructure/role_service_factory.go`
- **Skill**：`domain/skill/infrastructure/skill_service_factory.go`
- **Player**：`domain/player/infrastructure/player_service_factory.go`
```

## 优先级划分规则

- **高优先级**：领域类型未定义/未注册、Factory 未实现 Loader 接口、CreateByXXX 未使用 persist.GetOrCreate、DI 中未注入 Registry；**聚合根未接入 ChangeTracker（无 `PersistableEntity`/`markModified` 且无 README 已知例外）**；**Factory 暴露 `GetRepository` 且 AppService 多处手动 `repo.Save`**
- **中优先级**：CreateFromEntity 未正确处理缓存、缓存清理器未实现；**Port 含 `Save` 且非文档化例外**；**AppService import `domain/.../infrastructure`**
- **低优先级**：代码风格不一致、注释不完整

## 常见错误模式

### 错误 1：手动实现缓存逻辑
```go
// ❌ 错误
func (f *XxxServiceFactory) CreateByPlayerID(ctx context.Context, playerID uint64) (*XxxService, error) {
    if svc, ok := f.registry.GetInstance(playerID); ok {
        return svc.(*XxxService), nil
    }
    svc, err := f.Load(ctx, playerID)
    if err != nil {
        return nil, err
    }
    f.registry.SetInstance(playerID, svc)
    return svc, nil
}
```

### 错误 2：未实现 Loader 接口
```go
// ❌ 错误：缺少接口声明
type XxxServiceFactory struct {
    registry persist.InstanceRegistry[uint64]
}
// 缺少：var _ persist.Loader[uint64, *XxxService] = (*XxxServiceFactory)(nil)
```

### 错误 3：DI 中未注入 Registry
```go
// ❌ 错误：未获取和注入 Registry
func newXxxServices(...) *XxxServices {
    xxxServiceFactory := xxxInfra.NewXxxServiceFactory(repo) // 缺少 registry 参数
}
```

### 错误 4：Factory 暴露 `GetRepository()` 供 AppService 手动 Save
```go
// ❌ 错误：标准域（如 backpack）Factory 不对外暴露仓储，避免应用层绕过 ChangeTracker
func (f *XxxServiceFactory) GetRepository() port.XxxRepository {
    return f.repo
}

// AppService 中反复：
// repo := s.xxxServiceFactory.GetRepository()
// _ = repo.Save(ctx, aggregate)
```

### 错误 5：AppService 每个写用例末尾重复 `repo.Save` 样板
```go
// ❌ 错误：与 backpack/skill 等「实体 markModified → 定时提交」不一致，易全量多 Key 覆盖写
if err := repo.Save(ctx, petService.GetPetPlayer()); err != nil {
    return nil, err
}
// ✅ 方向：聚合根实现 PersistableEntity，变更处 markModified()，Port 去掉 Save 或改为 no-op，由 ChangeTracker 提交
```

### 错误 6：实体未实现 `PersistableEntity` / 无 `markModified`
```go
// ❌ 错误：玩家数据聚合变更后无任何 MarkModified，仅靠 AppService 显式 Save
// ✅ 参考 backpack：var _ persist.PersistableEntity = (*Backpack)(nil)
//    func (b *Backpack) markModified() { persist.MarkModified(b) }
```

## 相关工具

**推荐使用的工具**：
- `grep`：搜索特定模式
- `glob_file_search`：查找文件
- `read_file`：读取代码文件
- `codebase_search`：搜索代码实现

## 参考文档

- **Registry 使用规范**：`.cursor/rules/ddd-architecture.mdc`（Registry 部分）
- **领域驱动设计规范**：`.cursor/rules/ddd-architecture.mdc`
- **代码质量规范**：`.cursor/rules/code-quality.mdc`
- **ChangeTracker / MarkModified**：`common/persist/persist.go`、`common/persist/sharded_change_tracker.go`
