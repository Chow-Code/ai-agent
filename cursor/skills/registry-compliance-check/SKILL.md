---
name: registry-compliance-check
description: 对指定领域执行 Registry 与持久化模式合规检查：Registry（ServiceFactory、Loader、CreateByXXX、DI、CacheInvalidator）及持久化（PersistableEntity、markModified/ChangeTracker、禁止 Factory 暴露 GetRepository + AppService 大量手动 repo.Save）。在新增领域、涉及玩家数据设计、检查 Registry/落库路径合规、用户请求 registry-compliance-check 或 /registry-compliance-check 时使用。
---

# Registry 使用规范检查 Skill

## 使用场景

- **涉及玩家数据设计**：项目功能开发时，若设计到玩家数据（如新增/修改领域实体、仓储、缓存），应触发本检查
- 用户请求检查某领域的 Registry 合规性（如「检查绝学领域是否符合 Registry 规范」）
- 新增领域后，需验证是否按规范实现 Registry
- 用户执行 `/registry-compliance-check` 命令
- 代码评审时需确认领域服务是否遵循 Registry 模式

## 执行流程

### Step 1: 定位领域代码

根据用户提供的领域名称（如 `peerlessskill`、`backpack`），查找：

- 领域层：`srv/game/domain/{subdomain}/`
- 基础设施层：`srv/game/domain/{subdomain}/infrastructure/`
- 应用层（持久化合规）：`srv/game/application/service/{subdomain}/`
- DI 层：`srv/game/infrastructure/di/`

使用 `Glob` 搜索 `*service_factory.go`、`*cache_invalidator.go`。

### Step 2: 执行 10 项检查

按顺序执行并记录每项结果（✅通过、❌失败、⚠️警告）。前 8 项侧重 Registry；第 9～10 项侧重 **ChangeTracker / 手动 Save**。

| # | 检查项 | 关键文件/位置 |
|---|--------|---------------|
| 1 | 领域类型定义 | `registry/domain_type.go` 中是否有 `DomainType{Subdomain}` |
| 2 | 领域类型注册 | `domain_manager_registry.go` 的 `u64DomainTypes` 是否包含该类型 |
| 3 | ServiceFactory 实现 | `domain/{subdomain}/infrastructure/*_service_factory.go`：Loader 接口、Load 方法、registry 字段 |
| 4 | CreateByXXX 方法 | 必须使用 `persist.GetOrCreate`，禁止手动 GetInstance/SetInstance |
| 5 | CreateFromEntity 方法 | 可选；若存在需先查缓存、创建后写入缓存 |
| 6 | DI 注入 | `application_factory.go`/`repository_factory.go` 中是否获取 Registry 并注入 Factory |
| 7 | 缓存清理器 | `*_cache_invalidator.go` 及 `playerEventManager.RegisterHandler` 注册 |
| 8 | Repository Factory | `repository_factory.go` 中是否创建 ServiceFactory 并注入 Registry |
| 9 | 持久化模式（实体/Port） | `domain/{subdomain}/entity/`：`PersistableEntity` + `markModified` → `persist.MarkModified`；`port/*repository*` 是否含 `Save`（标准域通常无，走 ChangeTracker）；README 可声明已知例外 |
| 10 | AppService 持久化合规 | `application/service/{subdomain}/`：禁止多处 `repo.Save`/`GetRepository().Save`；Factory **禁止**暴露 `GetRepository`（对照 backpack）；AppService import `infrastructure` 记 ⚠️ |

### Step 3: 生成检查报告

完成检查后，生成 Markdown 报告并保存到：

```
docs/操作记录/{YYYY-MM-DD}-{领域名称}-Registry规范检查报告.md
```

报告必须包含：基本信息、检查结果概览、详细检查结果、问题清单（按优先级）、修复建议、参考实现。

## 常见错误模式

### 错误 1：手动实现缓存逻辑

```go
// ❌ 错误
func (f *XxxServiceFactory) CreateByPlayerID(ctx context.Context, playerID uint64) (*XxxService, error) {
    if svc, ok := f.registry.GetInstance(playerID); ok {
        return svc.(*XxxService), nil
    }
    svc, err := f.Load(ctx, playerID)
    f.registry.SetInstance(playerID, svc)
    return svc, nil
}

// ✅ 正确
func (f *XxxServiceFactory) CreateByPlayerID(ctx context.Context, playerID uint64) (*XxxService, error) {
    return persist.GetOrCreate(ctx, f.registry, playerID, f)
}
```

### 错误 2：未实现 Loader 接口

Factory 必须声明：`var _ persist.Loader[uint64, *XxxService] = (*XxxServiceFactory)(nil)`，并实现 `Load(ctx, key uint64)`。

### 错误 3：DI 中未注入 Registry

Factory 构造函数必须接收 `registry persist.InstanceRegistry[uint64]`，在 `repository_factory.go` 中通过 `GetPlayerInstanceRegistry(DomainTypeXxx)` 获取并传入。

### 错误 4：Factory 暴露 `GetRepository()` 供 AppService 手动 Save

标准域 Factory **不**对外暴露仓储；AppService 不应 `GetRepository().Save` 反复落库，应走实体 `markModified` + ChangeTracker。

### 错误 5：AppService 每个写用例末尾重复 `repo.Save`

与 backpack/skill 等「变更注册 → 定时提交」不一致；易全量多 Key `SaveData`。应对齐 `PersistableEntity` + Port 无 `Save`（或 Save 为 no-op）。

### 错误 6：聚合根无 `PersistableEntity` / `markModified`

玩家数据变更未注册到 ChangeTracker，仅靠 AppService 显式 Save，属高优先级持久化路径问题。

## 参考实现

- **Backpack（Registry + ChangeTracker）**：`domain/backpack/infrastructure/backpack_service_factory.go`（按 playerID，**无** `GetRepository`）；`domain/backpack/entity/backpack.go`；`domain/backpack/port/backpack_repository.go`（**无** `Save`）
- **Skill**：`domain/skill/infrastructure/skill_service_factory.go`（按 playerRoleID）
- **Role**：`domain/role/infrastructure/role_service_factory.go`
- **Player**：`domain/player/infrastructure/player_service_factory.go`

## 特殊情况：纯 Repository 模式

若领域**未使用 Registry**（如绝学当前实现），检查结果将全部为 ❌ 或 ⚠️。报告中应说明：

- 当前采用纯 Repository 模式，每次请求直接读 Redis
- 若需符合规范，需引入 ServiceFactory + Registry；若保持现状，需在领域 README 中说明设计决策

## 完整规范与报告模板

完整检查步骤、输出格式、报告模板见：`.cursor/commands/registry-compliance-check.md`

## 相关文档

- **Registry 规范**：`.cursor/rules/ddd-architecture.mdc`（Registry 部分）
- **DDD 架构**：`.cursor/rules/ddd-architecture.mdc`
- **ChangeTracker**：`common/persist/persist.go`（`MarkModified`、`ChangeTracker`）
