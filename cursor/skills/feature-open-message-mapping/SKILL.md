---
name: feature-open-message-mapping
description: 维护「消息→功能ID」配置（FeatureOpenGate 鉴权用）。按领域注册、使用 pb 消息类型枚举与功能 ID 常量；新增功能/协议或查询映射时使用。
---

# 功能开放「消息→功能ID」映射维护 Skill

## 触发条件

当用户出现以下任一表述时执行本 skill：

- 「维护 / 更新 / 生成 消息→功能ID 配置」
- 「新增功能开放鉴权」「给某协议加功能开放」
- 「FeatureOpenGate 映射在哪」「消息→功能ID 怎么配」
- 「根据协议和功能系统生成消息功能ID配置」

## 实现方式概览

**映射不由一处手写 map 维护**，而是：

1. **functionopen 子域** 提供注册接口与功能 ID 常量；
2. **各业务领域** 在本域 `infrastructure/feature_open_registration.go` 中实现 `RegisterFeatureOpenMappings(reg)`，用 **pb 消息类型枚举**（如 `message.EMsgToServerType_MsgCtrReqXxx`）和 **功能 ID 常量**（`functionopenEntity.FunctionOpenIdXxx`）调用 `reg.RegisterManyMsgIds(msgTypeIds, systemID)`；
3. **DI** 在 `feature_open_message_mapping.go` 中创建 registry、依次调用各领域注册、通过 `message.MsgIdToNameMap` 将 msgTypeId 转为消息名，最终 `Build()` 得到 `map[string]int32` 供 `FeatureOpenGate` 使用。

这样避免在单一文件中手写消息名字符串，减少拼写错误，且按领域分片、职责清晰。

## 配置与代码位置

| 项目 | 位置 |
|------|------|
| **功能 ID 常量** | `srv/game/domain/functionopen/entity/function_open_system_id.go`（与 AllFuncType 表 Id 列一致） |
| **注册接口** | `srv/game/domain/functionopen/port/feature_open_mapping_registrar_interface.go`（`RegisterManyMsgIds(msgTypeIds []int32, systemID int32)`） |
| **各领域注册实现** | `srv/game/domain/{skill,arena,backpack,role,peerlessskill,equip}/infrastructure/feature_open_registration.go` 中的 `RegisterFeatureOpenMappings(reg)` |
| **DI 组装** | `srv/game/infrastructure/di/feature_open_message_mapping.go` 中 `buildFeatureOpenMessageToSystemID()`：创建 registry → 调用各领域 `XxxInfra.RegisterFeatureOpenMappings(reg)` → `reg.Build()` |
| **功能 ID 来源** | `excel/csv/AllFuncType.csv` 的 **Id** 列；策划在表中配置 FuncCondition / FuncPreviewCondition |
| **使用处** | `srv/game/srv/srv.go` 通过 `ApplicationServices.FeatureOpenMessageToSystemID` 传给 `middleware.NewFeatureOpenGate` |

**约定**：最终 map 的 key 为 **完整消息名**（由 `message.MsgIdToNameMap[msgTypeId]` 得到，如 `MsgCtrReqEquipInfo`），value 为 AllFuncType 的 Id（int32）。仅对出现在此 map 中的请求做功能开放鉴权。

## 维护场景与步骤

### 1. 新增「某协议需要功能开放鉴权」（协议归属已有领域）

1. 确认 AllFuncType 中已有对应功能行（Id），且该行已配置 **FuncCondition**（否则永远不开放，请求会一直被拒）。
2. 确定协议所属领域（如装备→equip、武学→skill、宗师殿→arena、背包→backpack、角色→role、绝学→peerlessskill）。
3. 打开该领域的 **`domain/{subdomain}/infrastructure/feature_open_registration.go`**。
4. 在对应功能 ID 的 `reg.RegisterManyMsgIds([]int32{...}, functionopenEntity.FunctionOpenIdXxx)` 的**切片中追加**一条：`int32(message.EMsgToServerType_MsgCtrReqXxx)`（与 proto/生成的 EMsgToServerType 枚举一致）。若该功能在本领域尚未有块，则新增一组 `reg.RegisterManyMsgIds(...)` 调用，systemID 使用 `functionopenEntity.FunctionOpenIdXxx`。

**不要**在 `di/feature_open_message_mapping.go` 里手写消息名或 map 键值对。

### 2. 新增「新功能」（策划在 AllFuncType 加了一行）

1. 策划在 `excel/csv/AllFuncType.csv` 增加一行（新 Id、FuncCondition 等），导表后确认 `excel` 包能读到（GameCfgManager 已嵌入 CtAllFuncType 并加载）。
2. 在 **`srv/game/domain/functionopen/entity/function_open_system_id.go`** 中增加常量，如：`FunctionOpenIdXxx int32 = 新Id`，注释写明功能含义。
3. 在**归属领域**的 **`domain/{subdomain}/infrastructure/feature_open_registration.go`** 中新增一块：`reg.RegisterManyMsgIds([]int32{ int32(message.EMsgToServerType_MsgCtrReqA), ... }, functionopenEntity.FunctionOpenIdXxx)`，列出该功能需要鉴权的所有请求消息类型枚举。

### 3. 新增「新领域」需要参与功能开放鉴权

1. 在该领域的 **`domain/{subdomain}/infrastructure/`** 下新建 **`feature_open_registration.go`**，实现包级函数：  
   `func RegisterFeatureOpenMappings(reg functionopenPort.FeatureOpenMappingRegistrarInterface)`，内部按功能分块调用 `reg.RegisterManyMsgIds(msgTypeIds, systemID)`，msgTypeIds 使用 `message.EMsgToServerType_*`，systemID 使用 `functionopenEntity.FunctionOpenId*`。
2. 在 **`srv/game/infrastructure/di/feature_open_message_mapping.go`** 的 **`buildFeatureOpenMessageToSystemID()`** 中：  
   - 增加对 `{新领域}Infra` 的 import；  
   - 在现有 `XxxInfra.RegisterFeatureOpenMappings(reg)` 列表里**追加一行**：`新领域Infra.RegisterFeatureOpenMappings(reg)`。

### 4. 某协议不再需要鉴权

在**对应领域**的 **`feature_open_registration.go`** 中，从该功能对应的 `RegisterManyMsgIds` 的 **切片里删除**该消息类型枚举即可（若删除后该功能无任何协议，可整块删除该 `RegisterManyMsgIds` 调用）。

### 5. 查询当前「消息→功能ID」映射

- **生成逻辑**：见 `di/feature_open_message_mapping.go` 的 `buildFeatureOpenMessageToSystemID()`；实际内容由各领域 `RegisterFeatureOpenMappings` 汇总而成。
- **消息名来源**：运行时通过 `message.MsgIdToNameMap[msgTypeId]` 得到，与 proto 定义一致。

## 数据对应关系参考（功能 ID 常量 → 典型协议）

| 常量（function_open_system_id.go） | Id | 功能描述 | 注册所在领域 | 典型协议（枚举） |
|-----------------------------------|----|----------|---------------|------------------|
| FunctionOpenIdMartialArts         | 1  | 武学     | skill         | MsgCtrReqPlayerSkillList, MsgCtrReqMartialArtsLearn/Upgrade/Awaken/Reset, MsgCtrReqRedDotStatus, MsgCtrReqGetMartialArtsAllData |
| FunctionOpenIdArena               | 2  | 宗师殿竞技场 | arena      | MsgCtrReqArenaChallengeInfo/ChallengeStart/RefreshOpponents |
| FunctionOpenIdArenaDaily          | 3  | 宗师殿每日奖励 | arena    | MsgCtrReqArenaDailyReward, MsgCtrReqArenaDailyRewardReceive |
| FunctionOpenIdArenaSeason        | 4  | 宗师殿赛季排名 | arena    | MsgCtrReqArenaSeasonRank |
| FunctionOpenIdArenaLastSeason    | 5  | 宗师殿历史赛季 | arena    | MsgCtrReqArenaLastSeasonRank |
| FunctionOpenIdKnapsack           | 6  | 背包     | backpack      | MsgCtrReqOpenKnapsack 等 |
| FunctionOpenIdMartialArtsEquip   | 7  | 绝学和武学装配 | skill    | MsgCtrReqMartialArtsEquip/Unequip, MsgCtrReqRecommendEquip, MsgCtrReqSchemeTagUpdate |
| FunctionOpenIdRoleLevelup        | 11 | 角色升级 | role          | MsgCtrReqRoleLevelup, MsgCtrReqExpPoolInfo 等 |
| FunctionOpenIdPeerlessSkill      | 12 | 绝学     | peerlessskill | MsgCtrReqPeerlessSkill* |
| FunctionOpenIdEquipStrengthen    | 13 | 装备养成-强化 | equip     | MsgCtrReqEquipEnhance/Breakthrough/Evolve |
| FunctionOpenIdEquipStar          | 14 | 装备养成-升星 | equip     | MsgCtrReqEquipEnchant/EnchantAdvance/Awaken |

（8 角色属性、9 属性详情、10 属性对比 等若无独立 Req 协议可暂不注册，待有入口协议再在对应领域补。）

## 禁止与注意

- **禁止**在 `di/feature_open_message_mapping.go` 中手写 `map[string]int32` 或 `"MsgCtrReqXxx": id` 形式的键值对；映射仅通过各领域 `RegisterFeatureOpenMappings` + registry.Build() 生成。
- **禁止**使用 AllFuncType 中不存在的 Id；新增 Id 必须先配置表增加行、再在 `function_open_system_id.go` 增加常量。
- **推荐**始终使用 `message.EMsgToServerType_MsgCtrReqXxx` 枚举注册，避免手写消息名字符串导致拼写或大小写错误。
- 若某 Id 在 AllFuncType 中**未配置 FuncCondition**，该功能永远不会开放，对应请求会始终被鉴权拒绝；先让策划在表中配好条件再挂鉴权。

## 相关文档

- 需求与设计：`docs/design/server/X-新功能开启/X-新功能开启-服务器需求.md`（SR-2.1「消息→功能ID」配置方式）
- 开发文档：`docs/design/server/X-新功能开启/X-新功能开启-开发文档.md`
