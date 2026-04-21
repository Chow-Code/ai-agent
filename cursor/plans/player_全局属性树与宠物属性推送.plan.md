# Player 全局树 + 宠物本地树 + 属性推送（计划迭代）

## 架构澄清（回应「为什么调用 RoleAttribute」）

**不应**在宠物应用服务里通过 **`RoleAttribute.ApplyAttributeDelta` / `ChangeData`** 去维护「宠物全员池」或「宠物本地树」。

- **`Role` 领域 + `RoleAttributeManager`**：语义是 **单个角色** 的属性树（武学、绝学、装备、等级等），推送走 **`MsgCtrNtfRoleAttributeNodeChanged`**（带 `PlayerRoleId`），见 [CtrSvr.proto](proto/CtrSvr.proto) 与 [role_attribute_changed_handler.go](srv/game/application/event_handler/role_attribute_changed_handler.go)。
- **`Player` 领域**：应挂载 **账号/玩家级全局属性树**（SR-6 全员池），与 **任一 Role 解耦**；多角色时避免「池子绑主控角色树」的歧义。
- **`Pet` 领域**：只维护 **每只宠物自己的本地属性树**（及 K-1~K-5 数据）；全员池 **不属于** Pet 聚合内「本地树」的语义，应写 **Player 全局树**。

因此：**宠物领域不调用 `RoleAttribute`**；**Player 领域也不应把全局池塞进 Role 树**。两域各自有 **属性变更结构 + 下发通道**。

## 目标公式（不变）

| 对象 | 公式 |
|------|------|
| 角色总属性 | `Role` 本地 `RoleAttributeManager` **+** `Player` 全局树（全员池） |
| 宠物总属性 | 该宠 **本地树** **+** 同一 `Player` 全局树 |

合成可在 **读侧/战斗桥接** 统一做；写侧严格分流 **谁改哪棵树**。

## 推送设计（对齐 `MsgCtrNtfRoleAttributeNodeChanged` 模式）

角色侧现有：

```protobuf
// CtrSvr.proto
message MsgCtrNtfRoleAttributeNodeChanged {
  uint64 PlayerRoleId = 1;
  repeated MsgDataRoleAttrNode AttrNodes = 2;
}
```

**建议新增（命名可评审后定稿）**：

1. **玩家全局属性节点变化**（中心服 → 客户端）  
   - 字段示例：`uint64 PlayerGuid`（或账号侧 ID，与现有协议一致）+ `repeated MsgDataRoleAttrNode AttrNodes`（**仅全局树节点**，`AttrModelType` 仍为 `PetBasics` / `PetFate` / `PetEvolve` / `PetSlotLevelUp` 等枚举，或单独约定 Global 子树根类型）。  
   - 语义：**所有角色 + 所有宠物** 依赖的全员池变更时推送；客户端可刷新「全局块」并参与本地合成。

2. **单宠属性节点变化**（中心服 → 客户端）  
   - 字段示例：`uint64 PlayerRoleId`（当前上下文角色）+ `int32 PetId` + `repeated MsgDataRoleAttrNode AttrNodes`（**仅该宠本地树**）。  
   - 语义：洗炼/资质/仅宠战斗相关模块变更时推送，**不**与全局通知混用（避免客户端难 diff）。

**原则**：与 `MsgCtrNtfRoleAttributeNodeChanged` 一样，**增量节点替换**（`AttrNodes` 携带变化节点，客户端替换对应模块）；三种通知 **并列存在**，各司其职。

## 领域侧职责

| 领域 | 维护内容 | 变更时动作 |
|------|----------|------------|
| **Player** | 全局属性树（全员池） | 更新树 → 持久化 → 发 **玩家全局属性 Ntf** → 按需触发战力/战斗相关事件 |
| **Pet** | 每宠本地属性树 | 更新树 → 持久化 → 发 **单宠属性 Ntf**（带 PetId） |
| **Role** | 角色本地树（现有） | 不变；仍走 `MsgCtrNtfRoleAttributeNodeChanged` |

**可选技术复用**：全局树/本地树的 **内存结构** 可与 `RoleAttributeManager` **同构**（复用 [role_attribute_manager.go](srv/game/domain/role/valueobject/role_attribute_manager.go) 的模块树与 `ChangeData` 语义），但这是 **代码复用**，不是 **领域调用**——不要在 Pet 里依赖 `RoleAttribute` 服务。

## 实现顺序（任务级，执行阶段再做）

1. **Proto + 注册**：新增两条 Ntf、`EMsgToClientType`、handler 映射、 [qa/api](qa/api) 与 BDD 约定。  
2. **Player**：全局树字段 + Repository/Redis Key + 变更 API + 封装「发玩家全局 Ntf」。  
3. **Pet**：每宠本地树 + 变更 API +「发单宠 Ntf」。  
4. **PetAppService / PlayerAppService**：按 SR-6 把写操作路由到正确树 + 正确推送。  
5. **合成查询**：战斗/GM/全量接口读取「Role 树 + Player 全局」「Pet 本地 + Player 全局」。

## 与前一版计划的修正

- **删除**「宠物写全员池走 `RoleAttribute`」的路径描述。  
- **增加** 与 `MsgCtrNtfRoleAttributeNodeChanged` **对称的两类新通知** 作为需求与协议的正式交付物。
