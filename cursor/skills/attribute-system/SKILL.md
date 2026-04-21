---
name: attribute-system
description: 任意业务接入服务端属性前须对照 docs/design/server 下该功能的 *服务器需求*.md 中的属性/生效范围/推送描述；角色树、宠物单宠树、玩家全局树 GlobalTree、战力与战斗合成、AttrModelType、扣旧加新、MsgCtrNtf* 推送、登录重建与双算排查。
---

# 属性系统（服务端）Skill

## 何时加载本 Skill

- 新玩法需要**写入属性**或**同步客户端/战斗**
- 不确定属性应落在**角色树 / 单宠树 / 玩家全局树**哪一棵
- 排查**属性未推送、双算、登录后不一致**
- 涉及 `EMsgAttrModelType`、`ChangeData`、`RemoveAttrChanges`、`ApplyAttrTreeOverlay` 等实现

---

## 属性需求识别（先读设计，再落代码）

**目的**：各功能在 [docs/design/server](docs/design/server) 下通常有 **服务器需求**（文件名多为 `*服务器需求*.md`，如 `C-宠物-服务器需求.md`、`装备-服务器需求.md`；具体以目录内实际文件名为准），其中常有 **属性加成、生效范围（仅角色 / 单宠 / 全员）、是否推送、与战力或战斗的关系** 等描述。**实现前应先定位并阅读本功能需求文档中的相关章节**，再对照本 Skill 第 4～6 节与 [S-属性系统](docs/design/server/S-属性系统/属性系统业务逻辑详解.md)，避免凭口头或猜枚举。

**建议步骤**：

1. **定位文档**：在 `docs/design/server/{功能目录}/` 下查找 `*服务器需求*.md`；若存在 `*-开发文档.md` 且含「属性树 / SR-6 / DD-1.2」等专章（如宠物），**属性落地规则以开发文档与需求交叉为准**。
2. **检索关键词**：在需求/开发文档中搜 **属性、Attr、战力、推送、生效、全体、角色、宠物、全局** 等，摘录：**写哪棵树**、**升级/换档是否终值行（需扣旧加新）**、**须下发的消息类型**。
3. **与通用规范对齐**：需求写的「全体加成」是否等价于本仓库的 **GlobalTree**（玩家维度）？「仅上阵生效」是否与宠物阵位等现有一致？**冲突时以评审过的需求/开发文档为准**，并回写开发文档避免歧义。
4. **配置对账**：属性条目上的 **`AttrModelType`、表名、行级终值** 以 `excel/csv` 与对应《配置使用》为准，**禁止**仅按需求段落手造模块类型。

**说明**：`docs/developdoc/` 多为策划向摘录；**服务端实现与属性树语义**以 `docs/design/server` 的需求/开发文档为主，策划原文作辅助。

---

## 1. 三棵树（核心心智模型）

| 树 | 挂载实体 | 业务主键 | 典型用途 | 持久化 |
|----|-----------|----------|----------|--------|
| **角色属性树** | `Role` | `playerRoleId` | 等级、武学、绝学、装备等**按角色**的来源 | **整棵树不落库**；依赖登录与各玩法从**配置 + 业务状态**重算 |
| **宠物单宠本地树（Pet tree）** | 宠物实例存储 | `petId` | 单宠养成、**阵位**（仅生效阵容已上阵槽）等 | **不落 Redis**；按需 `GetOrBuildLocalAttrTree` 等构建 |
| **玩家全局树（GlobalTree）** | `Player` | 玩家维度（非 roleId） | **所有角色 + 所有宠物**共享的「全员池」（当前以宠物全员贡献为主） | **仅内存**；登录必须**重建**，无法从存储自愈 |

**易错点（与口头「所有角色都加一份」区分）**：

- **不是**把同一份属性复制到每个角色的树上。
- **「全员生效」** → 写入 **`Player` 上的 GlobalTree**；角色树仍**每角色一棵**，互不影响。
- **总属性合成**（宠物侧）：**总属性 = 单宠本地树 + 玩家全局树**（见 [docs/design/server/C-宠物/C-宠物-开发文档.md](docs/design/server/C-宠物/C-宠物-开发文档.md) DD-1.2）。

通用实现见 [srv/game/shared/attribute/README.md](srv/game/shared/attribute/README.md)：`AttributeManager` 与客户端 `RoleAttributeManager` 同构，**不绑定**「角色」主键。

---

## 2. 计算模型（与配置一致）

- 单属性类型内分量：**Base / Factor / Fixed**（`EMsgAttrCalculateType`）。
- 聚合语义（概念）：**最终分量遵循 `Base × Factor + Fixed` 系**；具体模块层级与顺序以 **`CtAttributeModel`** 与 [docs/design/server/S-属性系统/属性系统业务逻辑详解.md](docs/design/server/S-属性系统/属性系统业务逻辑详解.md) 为准。
- **子模块类型**：以配置条目上的 **`AttrModelType`** 为准，**禁止**在业务代码里写死「某玩法=某枚举」；策划改表后须同步建树逻辑。

---

## 3. 变更模式：「终值贡献」与代码写法

**业务语义**：多数表/玩法给出的是**当前等级/当前行**下的**完整贡献**（终值），而不是「相对上一级的差值」。

**落地方式**（等价于「lv1 → lv2：先扣 lv1 再加 lv2」）：

1. **增量 API**：`AttributeModel.ChangeData` / `AttributeManager.ChangeData` 对 Base/Factor/Fixed 做 **`+=`**。
2. **状态变更时**：对旧状态 **`RemoveAttrChanges`**（内部常等价于取反再 Apply），再对新状态 **`ApplyAttrChanges`** / `ChangeData`。
3. **整模块替换**：`SetData`：**先 `clearData` 再按条 Set**，用于某模块整体重写。
4. **登录/对齐快照**：`ApplyAttrTreeOverlay`：对消息中出现的节点 **先 clear 再 Set**，用于与客户端树对齐；**勿与日常重复 `ChangeData` 混用**，否则易双算（登录路径注释中常见「避免重复执行」类说明）。

**反模式**：在已有「当前行」仍生效时，又对同一模块**重复 `+=` 同一份贡献**（未先 Remove 旧行）。

---

## 4. 玩法 → 写哪棵树（决策表）

| 生效范围（语义） | 写入 |
|------------------|------|
| 仅当前**角色** | **角色属性树**（该 `playerRoleId`） |
| **宠物自身**（单宠面板/进战单宠等） | **单宠本地树** |
| **所有角色 + 所有宠物** | **玩家 GlobalTree** |
| **阵位等级**（`CtPetSlotLevelUp`） | **仅单宠本地树**；且仅 **当前生效阵容** 中该槽**已上阵**的宠物；**不写 GlobalTree** |

宠物玩法与表映射的权威说明见 [docs/design/server/C-宠物/C-宠物-开发文档.md](docs/design/server/C-宠物/C-宠物-开发文档.md)（DD-1.2 表「玩法 → 生效范围」）。

---

## 5. 推送规范（协议名须完整）

| 场景 | 消息（完整名） | 要点 |
|------|----------------|------|
| 角色树某模块节点变更 | `MsgCtrNtfRoleAttributeNodeChanged` | 含 **`PlayerRoleId`** + `AttrNodes` |
| 玩家全局树节点变更 | `MsgCtrNtfPlayerGlobalAttributeNodeChanged` | 无 roleId；连接上下文表示玩家 |
| 玩家全局树全量 | `MsgCtrNtfPlayerGlobalAttributeTree` | 登录等；顺序上常与登录包编排相关（须遵守现有 `login` 注释顺序） |
| 单宠整树（如登录、激活后全量） | `MsgCtrNtfPetAttrTrees` | `petId -> MsgDataRoleAttrTree` |
| 单宠节点（如阵位/生效阵容变更） | `MsgCtrNtfPetAttributeNodeChanged` | 含 **`PetId`** + `AttrNodes`；类型集合来自配表显式类型，缺数据可用空节点占位 |

定义见 [proto/CtrSvr.proto](proto/CtrSvr.proto)。推送封装见 [srv/game/application/attrpush/player_pet_attr_nodes.go](srv/game/application/attrpush/player_pet_attr_nodes.go)。角色变更事件 → 推送链路见 [srv/game/application/event_handler/role_attribute_changed_handler.go](srv/game/application/event_handler/role_attribute_changed_handler.go)。

---

## 6. 登录「重建」流程（不是从 Redis 读树）

| 树 | 行为 |
|----|------|
| 角色树 | 从 Redis 读**业务状态**（等级、装备、武学等），**属性树在内存中重建**；避免对同一来源重复应用 `ChangeData` |
| GlobalTree | **新建** `AttributeManager`，如 `BuildGlobalAttributeTreeForLogin` → `RebuildGlobalPetEvolveAttributes` 等，再挂到 `Player` |
| 单宠本地树 | 按需构建/缓存；不依赖 Redis 中的「整棵树」 |

参考：

- [srv/game/application/service/player/player_global_attribute_login.go](srv/game/application/service/player/player_global_attribute_login.go)
- [srv/game/domain/pet/service/pet_attribute_tree.go](srv/game/domain/pet/service/pet_attribute_tree.go)（如 `RebuildGlobalPetEvolveAttributes`、`ApplyGlobalPetEvolveForEvolve`）
- [srv/game/domain/player/entity/player.go](srv/game/domain/player/entity/player.go)（`GlobalAttributes()`、`SetGlobalAttributeTreeFromLogin`）
- 设计总览：[docs/design/server/S-属性系统/属性系统业务逻辑详解.md](docs/design/server/S-属性系统/属性系统业务逻辑详解.md)

---

## 7. 关键代码索引（按主题）

| 主题 | 路径 |
|------|------|
| 通用属性树 | [srv/game/shared/attribute/attribute_manager.go](srv/game/shared/attribute/attribute_manager.go) |
| 角色侧别名/入口 | [srv/game/domain/role/valueobject/role_attribute_manager.go](srv/game/domain/role/valueobject/role_attribute_manager.go) |
| 玩家全局树挂载 | [srv/game/domain/player/entity/player.go](srv/game/domain/player/entity/player.go) |
| 宠物全局/本地建树 | [srv/game/domain/pet/service/pet_attribute_tree.go](srv/game/domain/pet/service/pet_attribute_tree.go) |
| 推送封装 | [srv/game/application/attrpush/player_pet_attr_nodes.go](srv/game/application/attrpush/player_pet_attr_nodes.go) |
| 战力叠加全局 | [srv/game/domain/player/infrastructure/combat_power_global_attr_provider.go](srv/game/domain/player/infrastructure/combat_power_global_attr_provider.go)（及领域工厂注入处） |
| 枚举与树结构消息 | [proto/EMsgAttr.proto](proto/EMsgAttr.proto)、[proto/CtrSvr.proto](proto/CtrSvr.proto) |

---

## 8. 新玩法接入 Checklist

1. **需求文档**：已阅读 `docs/design/server` 下本功能的 `*服务器需求*.md`（及含属性专章的 `*开发文档*.md`），并明确生效范围、推送与战力/战斗要求（见上文「属性需求识别」）。
2. **生效范围**：只当前角色 / 单宠 / 全员？→ 选对树（第 4 节）。
3. **模块类型**：只信配置 **`AttrModelType`**，不写死枚举映射。
4. **变更**：状态从 A→B 是否已 **Remove A + Apply B**（或 `SetData` 整模块替换）？禁止重复 `+=`。
5. **推送**：角色 / 全局 / 单宠整树 or 节点？消息名是否与客户端约定一致？
6. **登录**：GlobalTree 是否在登录路径中**重建**？单宠是否在首次需要时构建？角色树是否与 `CompleteLogin` / `loadPlayerRoles` 等路径**避免双算**？
7. **战力/战斗**：若影响战力或进战属性，是否已把 **GlobalTree** 纳入合成（参考 `CombatPowerGlobalAttrProvider` 与宠物开发文档）？
8. **文档**：复杂规则增量请同步 [docs/design/server/S-属性系统/](docs/design/server/S-属性系统/) 或对应领域开发文档，避免仅口头约定。

---

## 9. 与需求澄清话术对照（防误解）

- **「所有角色立刻加属性」** → 澄清是 **每角色各一棵树** 还是 **全员进 GlobalTree**；当前宠物全员池为后者。
- **「登录恢复属性」** → 更正为 **登录重建内存中的属性树**，持久化的是**业务数据**而非整棵 Attr 树。
- **「属性存 Redis」** → 角色/宠物属性树 **默认不落**；以设计文档与 `Player`/`Role` 注释为准。

---

**维护**：属性规则变更时同步更新本节中的路径与消息名；协议以 `proto/CtrSvr.proto` 为准。
