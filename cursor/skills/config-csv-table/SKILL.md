---
name: config-csv-table
description: 在根据策划案新建或补全服务端配置表、需生成或维护 excel/csv、需核对列类型与注释和变量命名、或需对照现有表与枚举及多态列定义做复用时使用。须遵守列名规范、枚举命名与类型扩展路径（proto 枚举 vs createtype，见正文）。涉及「定义表」「建表」「配表」「新表」或明确交付 excel/csv 时优先加载。策划表/截图仅为建议，落地须符合 ParseType 与评审结论。面向 TL3Server excelgen；默认交付物为 excel/csv（及 excelgen 产物）。
---

# 策划案 → 配置表（CSV）

## 本技能解决什么

在 **TL3Server** 仓库中**新建或扩展一张策划配置表**，并正确落地 **`excel/csv`**（以及管线所需的 `excel/excel` xlsx、`excel/createtype` 等）。**「建表」与「CSV」是主目标**。

**多态列（CreateType）** 只是 Excel **类型列**里可能出现的一种写法（`[CreateType]Xxx`），与 `int`、`EMsgXxx` 等并列；仅在列需要结构化多态时再查 `excel/createtype`。

## 术语与默认交付物

在 TL3Server 中，用户或文档若出现 **「定义表」「建表」「配表」「新表」**，**默认指**：

- 维护 **[`excel/excel/{TableName}.xlsx`](../../../excel/excel)** 与 **[`excel/csv/{TableName}.csv`](../../../excel/csv)**（二者与团队流程二选一或同源维护）；
- 运行 excelgen 生成 **`excel/code/Ct{TableName}.go`** 与 **`srv/game/bin/Ct{TableName}.bytes`**（命令与参数见 [`.cursor/skills/sync-client-config/SKILL.md`](../sync-client-config/SKILL.md) 与 [`excel/README.md`](../../../excel/README.md)）。

**`docs/developdoc/**/配置表结构.md`**：**可选**，用于评审或与策划对齐说明；**不能**替代 `excel/csv` 作为「表已在本仓库落地」的唯一证据。

| 交付物 | 说明 |
|--------|------|
| **`excel/csv/{TableName}.csv`** | **主交付物**：四行表头 + 数据行；与策划案列一致时可视为「表已定义」。 |
| **`excel/excel/{TableName}.xlsx`** | 若团队从 Excel 维护，与 CSV **同源**；改表后应用 excelgen 回写 CSV/二进制/Go。 |
| **`excel/code/Ct{TableName}.go`、`srv/game/bin/Ct{TableName}.bytes`** | excelgen 生成物，供服务端加载。 |

**常见误区（避免）**：

- **仅**在 `docs/developdoc/.../配置表结构.md` 或策划原文里写列说明，**没有**对应 `excel/csv` 文件 → **不算**完成「在本仓库定义配置表」。文档可作为补充说明，但 **CSV 是服务端配表的事实来源**。
- 引用 `docs/developdoc/Y-某系统/` 时，若目录或策划原文尚未同步，仍应 **以现有 `excel/csv` 同领域表为基准**（在仓库内搜表名/前缀），再 diff 策划案补列。

## 策划参考与落地原则（重要）

- **策划案、截图、表格、口头需求多为「建议」**：列名、类型、是否拆表 **以可落地为准**；若与 [`schema.go`](../../../tools/sync-client-config/excelgen/schema.go) 的 `ParseType`、已有 `EMsg*`、现网同类表 **冲突**，或设计明显不合理（例如 **主表引用列类型与关联表主键不一致**），应先 **评审或与客户/策划确认** 再改 CSV，**禁止**不经核对直接照搬。
- **「全局」参数放在哪张表**：与**单业务线**强相关、且仅服务该线的全局项（上限、清理、次数等），可用 **专用单行表**（例如邮件上限放在 `Email` 等独立表）承载，便于独立维护与导出；是否与 **项目内统一的全局常量/大表** 合并、或拆字段，**无唯一标准**，以评审与团队约定为准。
- **关联表与引用列**：若某类数据需 **独立成表**，主表引用列类型须与 **关联表主键**一致；策划稿常见「外键写 string、关联表主键为 int」等情形，落地前应 **评审后统一类型**（常用 `int` / `int[]`），或 **书面约定** 外部编码格式；**本技能不绑定具体某张业务表名或列名**，以仓库内实际 CSV 与评审结论为准。

## 管线与命令

**执行 excelgen、from-xlsx / from-csv、默认目录与前置缓存**：只读 [`.cursor/skills/sync-client-config/SKILL.md`](../sync-client-config/SKILL.md) 与 [`excel/README.md`](../../../excel/README.md)，本技能不重复命令与参数表。

**列类型与行列跳过规则**：以 [`tools/sync-client-config/excelgen/schema.go`](../../../tools/sync-client-config/excelgen/schema.go) 的 `ParseType`、`ShouldSkipColumn`、`ShouldSkipDataRow` 为准。

## 策划案 → 表结构检查清单

在动手写表头或 CSV 前，建议整理：

| 维度 | 内容 |
|------|------|
| 表名 | 与 `excel/excel/{TableName}.xlsx` 一致；生成类名为 `Ct{TableName}` |
| 表用途 | 一句话，便于评审 |
| 主键 | 通常为 `Id` 及类型（多为 `int`） |
| 每列 | **列名**（须符合下文「列名规范」）、**类型**（须被 `ParseType` 识别）、**第 3 行配置标签**（如 `key`、`notEmpty`、`[NotSave]` 等，对齐同类现网表）、**第 4 行备注** |
| 枚举列 | 见下文「**枚举列（EMsgXxx）与 int 的取舍**」；新增枚举须走 proto / `message/enum_registry.go` 等生成链，**不能**仅靠手填 CSV「发明」一套取值 |
| 多态列 | 是否必须用 `[CreateType]XxxBase` / `[CreateTypeArray]XxxBase`；能否复用 `excel/createtype` 已有定义 |
| 子表 | 是否需要 `{主表名}_Sub_*.xlsx`（与主表同目录） |

## 表头四行与数据起始（与 excelgen 一致）

定义见 [`tools/sync-client-config/excelgen/xlsx.go`](../../../tools/sync-client-config/excelgen/xlsx.go) 常量：

| 行（1-based） | 含义 |
|---------------|------|
| 1 | 列名（变量名） |
| 2 | Excel 类型字符串 |
| 3 | 配置标签（如 key、跳过规则相关） |
| 4 | 备注（策划说明） |
| 5 起 | 数据行 |

导出的 CSV 通常第一行含 `FileName:` / `Sheet:`，随后为上述四行表头再跟数据；可在 `excel/csv` 中任选一张与 excelgen 对齐的现网表对照表头格式。

## 列名（变量名）规范

excelgen 将 **第 1 行列名** 原样写入生成的 **`Ct{Table}Data` 结构体字段名**（见 [`templates/main_table.tmpl`](../../../tools/sync-client-config/excelgen/templates/main_table.tmpl)），因此列名须是 **合法 Go 标识符**，并符合项目习惯：

| 规则 | 说明 |
|------|------|
| **PascalCase（大驼峰）** | 多单词组合时首字母及后续单词首字母大写，如 `PlayerDailySendLimit`、`MailListDefaultPageSize`；**禁止**中文、空格、`-`、`.` 等非法标识符字符。 |
| **首列主键** | 多数表主键列名为 **`Id`**（类型多为 `int`），与 `TryGetValue`、子表引用习惯一致；不要随意改成 `ID`、`key`（除非全项目约定且工具链支持）。 |
| **与现网对齐** | 新增列时与同领域已有表 **词缀、语义、大小写** 保持一致（如 `Type`、`XxxLimit`、`ArrXxx` 等），避免同义不同名。 |
| **枚举/多态** | 类型行写 `EMsgXxx`、`[CreateType]XxxBase` 等；**列名**仍用业务含义英文，不必把枚举名整段贴进列名。 |
| **缩写** | 团队内统一即可（如 `Cfg`、`Id`），新增缩写宜先对照同目录表。 |

**中文说明只放在第 4 行备注**，不要写进第 1 行列名。

## 列跳过与数据行跳过（配表时必对）

与 [`schema.go`](../../../tools/sync-client-config/excelgen/schema.go) 及现网表一致，避免把**注释**当**数据**：

- **列跳过**：列名为空；或以 `##`、`0` 开头；或配置行含 `client:false`（仅客户端列）
- **数据行跳过**：`Id` 以 `##` 开头；`Id` 为 `主键`、`配置表主键`、`Key`、与列名相同的 `Id` 备注行等

## 合法列类型（勿在此臆造清单）

**唯一来源**：[`schema.go`](../../../tools/sync-client-config/excelgen/schema.go) 的 `ParseType`。未支持的字符串会报「未知类型」。含：`[CreateType]` / `[CreateTypeArray]`、客户端包装类型（见 [`client_wrapper_types.go`](../../../tools/sync-client-config/excelgen/client_wrapper_types.go)）、基础类型与数组、向量、`EMsgXxx` 及 `EMsgXxx[]` 等。

- **新枚举**：通常需 proto / `message/enum_registry.go` 等生成链，不能单靠 CSV。
- **多态列**：类型列写 `[CreateType]Xxx` / `[CreateTypeArray]Xxx`；`excel/createtype/*.txt` 头部 `//[CreateType]` / `//[CreateTypeArray]`，**新子类型只许在 txt 末尾追加**。

## 枚举列（`EMsgXxx`）与 `int` 的取舍（避免过拟合）

策划稿里常把「类型」「过期规则」等写成 **`int`**；在 TL3Server 中是否升级为 **`EMsgXxx`**，按下面判断，**不要**给每一列「类型」都强行造枚举。

**更适合用 `EMsgXxx`（或 `EMsgXxx[]`）的情况**：

- 取值集合 **有限、稳定**，且在 **协议 / 多端 / 多表** 应对齐同一套语义（分类、状态、策略开关等）；
- 需要在 Go 里 **按枚举分支**，且希望 **配置行与生成代码** 可读（避免裸 `int` 魔法数）；
- 仓库里 **已有** 同名或同领域 `EMsg*`（优先复用），或已安排 **新增 proto 枚举** 再走配表。

**更适合保留 `int` 的情况**：

- **计数、权重、等级、天数、Unix 时间戳** 等连续或大范围数值；
- 规则 **频繁调整**、仅策划内部使用、**不进入协议** 的「档位」；
- 为省改动而 **硬造枚举** 会导致 proto、客户端、历史数据 **全链路升级成本过高** 时，保持 `int` 并在第 4 行备注说明取值约定即可。

**落地约束**：

- 类型列写 **`EMsgXxx`** 时，数据行使用与 excelgen 一致的 **枚举字面量**（与现网表对齐）；**禁止**只在 CSV 里写一套数字约定、却不在 proto 中定义枚举。
- **新增** `EMsgXxx`：**先** proto / 生成 / `enum_registry`，**再**改 CSV；顺序反了会导致类型无法通过 `ParseType` 或与 message 不一致。

**不过拟合**：本技能**不规定**「某业务字段必须枚举」；是否把某列从 `int` 改为 `EMsgXxx` 由 **评审**（语义稳定性、复用面、改造成本）决定，避免为形式统一而批量加枚举。

## 枚举命名、与现网对齐、以及「新类型」走哪条路径

### 枚举类型列（`EMsgXxx`）的命名

- [`ParseType`](../../../tools/sync-client-config/excelgen/schema.go) 要求：枚举类型字符串须匹配 `^E[A-Za-z0-9_]+$`（**以 `E` 开头**），数组写 **`EMsgXxx[]`**。
- **与 proto 一致**：类型列中的名字应与 **`message` 包内由 proto 生成的枚举类型同名**（项目惯例多为 `EMsg` + 领域/语义），避免 CSV 与协议两套名字。
- **数据行**：填 **proto 枚举成员名**（与 `enum_registry` / `*_value` 一致；现网多为**短名**如 `MainCity`、`DailyDungeon`，与 [`enum_resolver.go`](../../../tools/sync-client-config/excelgen/enum_resolver.go) 解析规则一致）；或填 **数字**；勿自造未在 proto 中声明的符号。具体样式在 `excel/csv` 里找 **同类型列**（如 `EMsgMapType`、`EMsgEmailType` 等列）对齐即可。

### 自定义类型与「照抄现网 CSV」

- **类型列第 2 行** 的字符串必须与 `ParseType` **完全一致**（大小写、括号、`[]` 位置）。新增列时，在 `excel/csv` 中找 **同领域或语义相近** 的列，**对齐写法**（含 `EMsgXxx`、`[CreateType]XxxBase`、`ResourceType<...>`、`int[]` 等），减少「未知类型」。
- **第 3 行配置标签**（`key`、`c`、`s`、`client:false` 等）同样 **对齐同类表**，勿凭空调参。

### 需要「以前仓库里还没有」的类型时——不是都进 createtype

| 诉求 | 应走的路径 |
|------|------------|
| **新的离散取值**，且与 **协议/多端** 对齐 | **在 proto 增加枚举** → 按项目流程生成 `message` → 更新 `enum_registry`（若适用）→ 类型列写 **`EMsgXxx`**。**不要**只在 CSV 里用裸 `int` 约定一套值却不加 proto。 |
| **一列多种结构**（子类型字段不同、多态行） | **`excel/createtype/{BaseName}.txt`** 定义基类与子类型；类型列 **`[CreateType]BaseName`** 或 **`[CreateTypeArray]BaseName`**。见下文与 [`excel/createtype/`](../../../excel/createtype/) 下现有 `*Base.txt`（如多行子类型定义）。**新子类型只许在 txt 末尾追加**。 |
| **新的标量/向量** | 优先使用 `ParseType` 已支持的 **`int`、`float`、`string`、`Vector2`…**；若确需全新基础类型，属于 **改 excelgen `ParseType`**（极少见），须评审。 |
| **ResourceType / UIInterfaceType 等** | 见 [`client_wrapper_types.go`](../../../tools/sync-client-config/excelgen/client_wrapper_types.go)，**不是**在 createtype 里「加枚举」能替代的。 |

**proto 枚举 与 `excel/createtype` 的分工**：

- **`EMsgXxx`**：表达 **有限选项值**（整型枚举），扩展 = **加枚举值**（proto 流程）。
- **`[CreateType]XxxBase`**：表达 **多态结构体**（每种子类型一行、字段组合不同），扩展 = **在对应 txt 末尾追加子类型**（必要时配合生成代码中的 `I*` 接口）。

**误区**：把「需要新枚举分类」的问题做成「新建 createtype 文件」——除非该列真的是多态结构列，否则应走 **proto 枚举**。

## `excel/createtype` 全量核对（多态列时）

列类型含 **`[CreateType]`** 时，在 **[`excel/createtype/`](../../../excel/createtype/)** 查是否已有可复用的 `BaseName.txt`（子类型追加规则见上节）。

**不要**用 **`excel/csv/.createtype_cache/createtype.json`** 当全库列表：它是 excelgen 缓存，多为**当前 xlsx 已引用**子集；全库以 **`excel/createtype/*.txt`** 文件名为准。

## 复用建议

1. **同领域表**：在 `excel/excel`、`excel/csv` 中搜同名或相近前缀，对齐列名与类型、配置标签习惯。
2. **枚举**：在 `message/enum_registry.go` 与现有表中找已有 `EMsg*`；是否新加枚举见上文「枚举列与 int 的取舍」。
3. **多态列**：列出 `excel/createtype` 下已有基类，优先复用再考虑新建 txt。

## 常见错误

- 手搓 CSV 与 xlsx 四行表头不一致 → `from-csv` 失败或二进制与预期不符。
- 在 CreateType txt **中间**插入子类型 → 旧数据子类型索引错位。
- 类型字符串拼写不在 `ParseType` 支持范围内 → 「未知类型」。
- 该用 `EMsgXxx` 的稳定分类却长期裸 `int`、且无备注 → 可读性差、易与协议漂移。
- 为「看起来规范」给大量列强行加 `EMsgXxx` → proto/客户端改动面过大，**过拟合**。
- 需要新「分类枚举」却只在 **`excel/createtype` 加 txt**、不走 proto → 与协议、客户端枚举不一致。
- 需要 **多态结构列** 却只加 proto 枚举、不写 **`[CreateType]`** 与 createtype 定义 → 序列化/子类型无法表达。
