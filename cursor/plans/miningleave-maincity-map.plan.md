---
name: MiningLeave 回主城 MapChange
overview: 在 map 应用端口新增「确保回主城并推送 MapChange」的接口；实现内查有效主城则 sendMapChange，否则 EnterMap。Mining Leave 与 Player ReturnToMainCity 均通过该能力组合调用，避免 Handler 重复逻辑。
todos:
  - id: port-method
    content: appPort.MapAppService 新增 EnsureMainCityMapChange（命名可评审）；MapAppService 实现并抽离 sendMapChange+EnterMap 逻辑
    status: completed
  - id: refactor-return
    content: ReturnToMainCity 改为宗师殿退出后调用 EnsureMainCityMapChange（行为与现网一致）
    status: completed
  - id: mining-leave
    content: HandleMiningLeave 成功分支调用 EnsureMainCityMapChange（或按需调用完整 ReturnToMainCity）
    status: completed
  - id: player-handler
    content: PlayerHandler 改为依赖接口方法（若当前为具体类型，可改为 appPort.MapAppService + 新方法）
    status: completed
  - id: bdd-doc
    content: mining Leave BDD 与 domain/map README 补充说明（可选）
    status: completed
isProject: false
---

# Mining Leave 与 Map 端口「回主城」接口

## 需求（迭代）

在 **map 层新增正式接口**：用于回到主城；接口内检查是否仍有**有效、在使用的主城**地图记录，有则**直接推送 changemap**（`MsgCtrNtfMapChange` / `sendMapChangeNotification`），没有则**创建新的**（`EnterMap` 主城）。

## 与现有代码关系

`[MapAppService.ReturnToMainCity](srv/game/application/service/mapdomain/map.go)`（约 874–988 行）已包含：

1. 可选：退出宗师殿
2. 查主城 → 有效则 `sendMapChangeNotification` → 否则 `EnterMap`

本次将 **第 2 段**抽成端口方法，便于：

- **Mining Leave** 只关心「回主城 + MapChange」，不必依赖具体 `*MapAppService` 或未在接口上声明的方法  
- **Player `ReturnToMainCity`** 保持「先退宗师殿再回主城」，内部复用同一套主城逻辑

## 建议 API 命名（可评审）

在 `[appPort.MapAppService](srv/game/application/port/service_interfaces.go)` 增加例如：

```go
// EnsureMainCityMapChange 若存在有效主城地图记录则推送 MsgCtrNtfMapChange；否则 EnterMap 创建主城并走现有进图推送。
EnsureMainCityMapChange(ctx context.Context, playerId uint64) error
```

实现放在 `[mapdomain/map.go](srv/game/application/service/mapdomain/map.go)`：

- 从 `ReturnToMainCity` 中复制/移动「`FindAllByMapType` 主城 + `IsValid` + `sendMapChangeNotification` + 失败分支 `EnterMap`」到 `EnsureMainCityMapChange`  
- `ReturnToMainCity` 保留宗师殿循环 `ExitMap`，然后调用 `EnsureMainCityMapChange(ctx, playerId)`

## Mining Leave

`[HandleMiningLeave](srv/game/handler/mining/mining_handler.go)` 在 `Leave` 成功且 `Ret==None` 后调用：

- `**EnsureMainCityMapChange**`（不自动退宗师殿；矿场场景通常不在宗师殿）

若产品要求与「回到主城」按钮**完全一致**（含退宗师殿），可改为调用 `ReturnToMainCity`；默认按「仅主城」更贴合矿场 Leave 语义。

## Player Handler

`[HandleReturnToMainCity](srv/game/handler/player/player.go)` 继续调用 `**ReturnToMainCity`**（内部已复用 `EnsureMainCityMapChange`）。  

若希望 Handler 仅依赖 `appPort.MapAppService`，将 `PlayerHandler.mapAppService` 类型改为接口，并保证接口包含 `ReturnToMainCity` 与 `EnsureMainCityMapChange`（或仅 `ReturnToMainCity` 若 Player 不直接用新方法）。

## 错误与日志

- `EnsureMainCityMapChange` 失败：`EnterMap` 失败时返回 `error`，与现 `ReturnToMainCity` 一致打日志。  
- Mining：`Leave` 已成功时，`Ret` 是否仍为 `None` 仅因回主城失败——按前次计划可选：**仍 Ret=0 + 打日志**，或对齐 Player **返回业务错误**（需与策划/客户端约定）。

## BDD / 文档

- Mining Leave 用例：若先推 `MsgCtrNtfMapChange` 再回 `MsgCtrResMiningLeave`，需 `CallWithOptions` 与 Enter 用例一致。  
- 可选：`[domain/map/README.md](srv/game/domain/map/README.md)` 增加 `EnsureMainCityMapChange` 说明。

## 不涉及

- 修改矿场进图 `pushMapChange`（MiningMapId）逻辑。  
- 在 map 仓储层新增类型；仅应用服务端口 + 实现重构。

