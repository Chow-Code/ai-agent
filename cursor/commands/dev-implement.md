---
description: 按独立 `{功能}-开发任务清单.md`（与 development.md DD-7.1 结构一致）全程通过 Task 派发 subagent 完成实现与验证（Phase 1 写代码须 executor；Phase 2～6 禁止主 Agent 替代）；主 Agent 仅编排、对账、勾选任务清单、抽检编译测试；白名单修补后不得交接式停步，须继续派发下一 Task；收尾 business-implementation-check 与 Phase 6 续闭环后方可宣称交付完成。
---

## 用户输入

```text
$ARGUMENTS
```

必须考虑用户输入（若非空）。用户输入通常为功能名，如 `C-宠物`、`J-绝学`。

## 概述

### 任务清单文件（独立维护，强制）

本命令的 **checkbox 任务区**以**单独 Markdown 文件**为唯一真源，**不**放在 `{功能}-开发文档.md` 正文中维护（避免与 DD-2/设计叙述混排、难独立 diff）：

- **路径**：`FEATURE_DIR/{功能}-开发任务清单.md`（与 `{功能}-开发文档.md` 同目录，命名与功能前缀一致）
- **内容**：与 `.cursor/commands/development.md` **DD-7.1** 相同的 Phase 结构、`[Setup]` / 协议三步 / `[E2E]` / 收尾等 `- [ ]` / `- [x]` 列表
- **开发文档中的 DD-7.1**：仅保留**一行引用**至本文件即可（例如「实现进度勾选见：`{功能}-开发任务清单.md`」）；若历史文档仍含完整 DD-7.1 列表，应**迁移**到本文件后删除开发文档内重复列表，避免双处勾选

主 Agent 须读取 **`{功能}-开发任务清单.md`** 中自文件首（或首个 `##` 任务标题）至文末的 checkbox 区，按 Phase 和依赖关系逐步派发给 **subagent** 执行。核心循环为：

```
业务开发(executor) → BDD 测试(qa-tester) → 代码检查(codereview)
     ↑                      |                        |
     |                      | 不通过                  | 不通过
     +←←←←修复代码←←←←←←←←←+                        |
     +←←←←修复代码←←←←←←←←←←←←←←重新BDD←←←←←←←←←←←+
```

**成功条件**：BDD 测试通过 **且** 代码检查通过；**模块收尾**还须通过下文「与 business-implementation-check 衔接」中的完整性核对（或用户书面确认分期例外）。

**与 `business-implementation-check.md` 的关系（推荐升级为强制门禁）**：

| 维度 | dev-implement（本命令） | business-implementation-check |
|------|-------------------------|--------------------------------|
| 粒度 | 按**任务清单**单协议闭环 + E2E + 收尾 | 按模块 **横切**：FR、全协议、参数、存储、错误、日志、**测试覆盖缺口**、经济闭环等 |
| 时机 | 开发过程中持续执行 | **Phase 5～6 之后**、宣称「本模块开发完成」**之前** |
| 产出 | 任务清单勾选、BDD 绿、codereview 结论 | `docs/操作记录/{日期}-{功能名}-业务实现完整性检查报告.md` |
| **报告之后** | — | **必须解析报告「问题清单」**；属**功能/经济/协议缺失**的须**补开发**（非仅改文档）；属**缺测**的须 **qa-tester** 补 BDD；然后**重跑**本检查直至高优清零或已备注分期（见 Phase 6 续） |

二者互补：**单协议都勾 `[x]` 仍可能出现「某协议无 BDD」「P-5 未扣道具」类横切缺口**；完整性检查专门抓这类问题。主 Agent 在 **完成验证** 中须：**生成报告 → 分析 → 缺则补 → 再验证**，禁止把报告当作流程终点而不处理缺项。

**闭环失效典型原因（主 Agent 须主动规避）**：
- **Subagent**：prompt 过短、只贴**任务清单**一行任务、未要求读取 **DD-2 P-{N} 整节**与 **`{功能}-服务器需求.md`** 中该协议对应段落 → 执行方按「简化版」改字段即交差。
- **BDD**：未为本协议新增/补齐 `It`，或 DD-2 中的失败场景未写成**会先失败、实现正确后变绿**的用例 → 测试全绿但不覆盖需求。
- **代码检查**：仅看风格与编译，未做 **文档 vs 代码对账**，或文档已写「扣道具/上限」而代码无对应路径仍判通过。
- **骨架遗漏**：Setup 创建的 Service/Repository **含占位注释**的骨架文件，后续 Phase 2～4 executor 未被要求填充 → Phase 6 时搜索 `TODO` 关键词但占位注释写的是 `// Phase X 实现` → 绕过扫描 → 空壳文件遗留至交付。**防范**：Setup executor 回报中须列出骨架文件；Phase 2～4 executor prompt 须逐个点名骨架；Phase 6 强制搜索 `// Phase|// 待实现` 等模式。
- **目录与包路径漂移**：《服务器需求》已写「新增的文件和目录」或包路径附录，但 executor 仅按「分层」抽象落盘（如把 AppService 放在 `domain/{domain}/appservice/` 而需求写明 `srv/game/application/service/{domain}/`）→ BDD/流程对账仍可能判通过。**防范**：Setup / executor / codereview / Phase 6 须按本文「工程目录与《服务器需求》一致」与占位扫描路径执行；主 Agent 对 executor 回报须核对**差异表**或已登记分期。
- **主 Agent 越权**：在应派发 Subagent 的环节**亲自改业务代码 / 写集成 BDD / 出具正式 codereview 对账表**以「加速」→ Phase 1 后静默停步、无映射表与可审计回报。
- **主 Agent 交接式停步**：用户意图为 **`/dev-implement` 跑通任务清单**（含「用 subagent 做完任务」）时，主 Agent 完成用户**点名**的白名单修补（如 **`GameCfgManager` 补表、编译/生成物修复**）后，以「进度说明 + **若要继续请回复 T0xx / 继续某协议**」作为**本轮终点**，而 **`TASKLIST_FILE` 仍有 Phase 2～6 的 `- [ ]`**、且**不属于**proto 未合并/外部服务未就绪等**明确阻塞** → **视为未执行本命令**。正确做法：**修补完成后不经用户二次口令**，立即扫描任务区下一项并 **派发 Task**（通常为首个未完成的 **executor**）。

若 **`{功能}-开发任务清单.md` 不存在**：提示用户**新建该文件**（按 **`development.md` DD-7.1** 的结构与 Phase 填写 checkbox）；并在 `{功能}-开发文档.md` 的 **DD-7.1** 中**只写一行**指向该文件，**勿**在开发文档内再放一份完整任务表。

## Subagent 强制执行与主 Agent 边界（强制）

本命令的交付物应**主要由 Subagent 产出**；主 Agent 负责**读取文档、派发 Task、核对回报、更新 `TASKLIST_FILE`（任务清单）、必要时本地抽检**（如 `go build ./...`、对映射表做 `grep`），**不替代** Subagent 完成下列工作。

### 必须通过 Cursor Task 派发的类型

| 工作类型 | subagent_type | 说明 |
|----------|---------------|------|
| 业务实现（含 Setup 中增删改**仓库内**代码、配置、生成物、DI、Handler 等；proto/codegen 若需人工先决条件由 executor 列阻塞项） | `executor` | Handler/AppService/Domain/infra/DI/GM 等 |
| 集成 BDD 编写与执行 | `qa-tester` | `qa/integration/{domain}/` 下 `It` + `go test` 直至通过 |
| 单协议 / 单批改动审查 | `codereview` | 按 `.cursor/agents/codereview.md` + 本文对账要求 |
| Phase 1 **只读**核查（文件是否存在、表是否入库、目录是否齐） | `explore` 或 `shell` | **不得**用于替代应写代码的 Setup 项 |
| 设计文档与任务清单 / DD-2 同步 | `design-doc-sync` | 若本次实现变更了 DD-2/需求边界，按需派发（含 `{功能}-开发任务清单.md` 与开发文档引用一致性） |

**派发方式**：使用 Cursor **Task** 工具，`subagent_type` 取上表；每条 Task 的 `prompt` 须满足下文「主 Agent 派发 subagent 的共用要求」及对应 Phase 模板。

### 主 Agent 允许亲自执行的操作（白名单）

- 读取 `FEATURE_DIR` 下开发文档、服务器需求、`qa/api`、`development.md` 等，**整理**下一包 Task 的完整 prompt（含 DD-2 整节或明确「须 Read 的路径」）。
- Subagent 返回后：**轻量对账**（对照表、映射表、严重问题是否闭环），再决定是否勾选 **`TASKLIST_FILE`** 中对应项。
- **本地只读或轻量验证**：`go build ./...`、针对单包的 `go test` 抽检、ripgrep 核对 `BDD-P{N}` / 消息名是否存在（**不**因抽检通过就跳过 qa-tester 的正式跑测与映射表回报）。
- 用户阻塞项：**停止并说明**缺什么（如 proto 需人工合并、外部服务未就绪），**不得**在未派发 executor 的情况下自行大包大揽改完 Phase 2+ 代码。
- **用户点名的基础设施小改**（如「在 `GameCfgManager` 补某表加载」、与 Subagent 并行的**极小**接线）：允许主 Agent 亲自改，但**同一 dev-implement 会话中，该改动不得成为停步理由**：改完并验证编译后，**须立即**回到 **`TASKLIST_FILE`** 扫描下一项并派发 Subagent（见下文「禁止交接式停步」），**禁止**以「补丁已交」结束对话。

### 禁止行为（视为未执行本命令）

- **Phase 2～6** 中，主 Agent **自行实现**应对应 **executor** 的代码改动（含「先接线再说的」协议逻辑、占位改真实实现），或**自行撰写**应对应 **qa-tester** 的集成测试并宣称本命令完成。
- **Phase 1** 中，对涉及 **仓库内代码/生成物** 的 Setup（骨架、DI、`srv.go` 注册、Registry、Handler 实现等）**仅用主对话改代码而不派发 executor**（或不分批的单一 executor Setup 任务）。
- **Phase 1 全部 `[x]` 后结束会话**，且未扫描 **`TASKLIST_FILE`** 后续 Phase、未派发下一项 **executor / qa-tester**、未说明「用户待处理阻塞」——视为**流程中断**，须在进度报告中写明 **下一任务 ID 与将派发的 subagent_type**。
- **禁止交接式停步**：在同一会话执行 **`/dev-implement`** 时，若 **`TASKLIST_FILE`** 仍有 Phase 2～6 的 `- [ ]`，且**无**「用户待处理阻塞」，主 Agent **不得以**「若需继续请说 xxx」「回复后继续 T0xx」等**等待用户二次确认**作为回复结尾；**必须**已派发下一项 **Task**，或已按下面第 2 点给出带 **续跑指令**的进度报告（显式原因：上下文用尽 / 用户中止 / 阻塞项）。

### Phase 连续性与中断续跑

1. 每次完成一个任务清单条目并勾选后，**立即**在 **`{功能}-开发任务清单.md`** 内扫描下一个 `- [ ]`，按 Phase 顺序执行：**Phase 1 Setup → Phase 2～4 按协议 → Phase 5 E2E → Phase 6**，**不得**默认停在 Phase 1。
   - **白名单修补之后**（如用户要求补 `GameCfgManager`、主 Agent 本地 `go build` 修编译）：**不得**将该次回复视为 dev-implement 终点；**须在同一轮对话内继续**派发首个未完成的 Phase 2+ **Task**（或在本轮已用尽工具配额时，用第 2 点格式给出**续跑指令**，**禁止**仅用「请用户回复继续」代替续跑指令）。
2. 若因上下文、时间或用户中止无法一次跑完：在回复中给出 **进度报告**（已完成 / 进行中 / 待开始）及 **续跑指令**：「下一项：`Txxx` + 派发 `executor|qa-tester|codereview`，prompt 要点：…」。
3. 同一会话内对 **未标记 `[P]`** 的协议**串行**派发；对 **`[P]`** 协议最多 **4 路**并行 Task（仍遵守「单协议内三步串行」）。

## 主 Agent 派发 subagent 的共用要求（强制）

派发 **executor / qa-tester / codereview** 前，主 Agent **必须**自检并满足：

1. **上下文不可省**：prompt 中须明确给出（二选一或同时）：① `FEATURE_DIR/{功能}-开发文档.md` 内 **DD-2「P-{N} …」整节**的完整拷贝；② `FEATURE_DIR/{功能}-服务器需求.md` 内**与本协议对应**的小节/流程/验收要点拷贝。**禁止**仅用 **`{功能}-开发任务清单.md`** 里一行 checkbox 文案代替上述全文。若消息名与章节标题不一致，主 Agent 须在 prompt 中写明对应关系。
2. **路径与引用**：每条 subagent prompt 须含 `FEATURE_DIR`、`qa/api/{domain}.yaml`、`qa/integration/{domain}/` 等**可点击路径**，并要求子代理用 Read 工具打开上述文件核对，禁止凭记忆编造接口名或字段。
3. **禁止默许简化**：若子代理回报「先简化实现」，主 Agent 应**拒绝勾选完成**，要求其按文档全量实现；仅当文档明确分期且**任务清单**已拆分时，未完成部分保持 `[ ]`。
4. **回报须可核对**：子代理须列出**修改文件路径**；BDD 须附 **DD-2 BDD 条目 → `It` 标题**映射表；codereview 须附 **DD-2 代码检查条目 → 结论（满足/缺陷）** 对照。
5. **工程目录与《服务器需求》一致（强制）**：若 `FEATURE_DIR/{功能}-服务器需求.md` 中存在「新增的文件和目录」「包路径」或等价树形/列表附录，派发 **executor** 时须在 prompt 中**点名**该附录标题，并要求：**新增或迁移的源码路径、包目录须与附录一致**；若因仓库既有约定必须偏离，须在回报中附 **需求路径 → 实际路径** 差异表，且 **`TASKLIST_FILE` 或开发文档 DD-7 已写明分期/例外**，否则主 Agent 不得勾选对应 Setup/业务开发完成。Phase 1 中「仅验证、盘点」类 Setup 可用 **explore/shell** 对照该附录做路径存在性清单。

## 前置检查

### 1. 定位与加载

1. 从用户输入提取 **功能名**
2. 设置 `FEATURE_DIR = docs/design/server/{功能}/`，**任务清单路径** `TASKLIST_FILE = FEATURE_DIR/{功能}-开发任务清单.md`
3. **必须**：读取 **`TASKLIST_FILE`** 全文；其中所有 `- [ ]` / `- [x]` 所在章节（通常自 `## DD-7.1` 或「开发任务清单」标题起至文件末）为**任务区**（真源）
4. **必须**：读取 `FEATURE_DIR/{功能}-开发文档.md` 内 **DD-2**（协议详情、BDD 条目、代码检查条目）、**DD-7**（实施计划）；**勿**从开发文档内解析 checkbox 作为任务真源
5. **必须**：读取 `FEATURE_DIR/{功能}-服务器需求.md`（与开发文档并列为实现与验收依据；派发 subagent 时须摘入与本协议相关段落）
6. **可选**：读取 `FEATURE_DIR/{功能}-配置使用.md`（配置表字段）

### 2. 检查任务状态

扫描任务区内所有 `- [ ]` 和 `- [x]` 条目：

| 总任务 | 已完成 | 未完成 | 状态 |
|--------|--------|--------|------|
| {N}    | {C}    | {R}    | {R>0 ? "继续" : "全部完成"} |

若有未完成任务，从第一个未完成任务开始执行。

## 执行流程

### Phase 1: 基础设施准备

逐条执行 `[Setup]` 标签的任务：

对每个 Setup 任务：
1. 读取任务描述，判断需要检查/操作的内容
2. **分流派发**（**禁止**主 Agent 独自完成本属 Subagent 的实现类工作）：
   - **仅验证、盘点、路径存在性**（如配置是否已在 `excel/csv`、某文件是否存在）：派 **`explore`** 或 **`shell`**，回报可核对清单后主 Agent 勾选或标阻塞。
   - **涉及修改/新增本仓库代码、生成 Handler、DI、Registry、子域骨架、GM 注册、测试目录创建等**：必须派 **`executor`**（可将同一 Phase 内多个相邻 Setup 合并为 **一条** executor prompt「Setup 批次：T00x～T00y」，但**不得**由主 Agent 直接提交这些改动）。**executor Setup prompt 须含**：若《服务器需求》有目录/包路径附录，则本批次新建目录与文件路径**须与该附录一致**，并在回报中列「附录条目 → 实际路径」对照；无附录则按 DD-7 与 `.cursor/rules/ddd-architecture.md` 落盘。
   - **proto / 外部工具链需人工操作**：executor 在回报中列阻塞项，主 Agent **停止并报告用户**，该项保持 `[ ]`。
3. Subagent 回报通过且主 Agent **核对**与任务描述一致后，在 **`TASKLIST_FILE`** 内将对应行改为 `[x]`（**禁止**仅改开发文档而不改任务清单）
4. **骨架债务登记（强制）**：Setup 中创建的**含占位注释**（如 `// Phase X 实现`、`// 待实现`）的文件，executor 回报须列出**骨架文件清单**；主 Agent 须记录这些文件路径，在后续 Phase 2～4 对应协议的 executor prompt 中**明确要求填充或删除该骨架**。占位注释在 Phase 6 之前必须全部清除——以真实实现替代或删除不需要的文件。
5. 若有问题（如配置表缺失、proto 未更新），**停止并报告**，等待用户处理

**Phase 1 结束后的强制动作**：再次扫描 **`TASKLIST_FILE`**；若仍存在 Phase 2～4 的 `- [ ]`，**必须**继续派发下一任务的 Subagent（通常为首条 **业务开发 executor**），**不得**以「Setup 已完成」作为本轮 `/dev-implement` 的结束语。

**与用户点名修补的叠加**：若用户在同一次输入中要求「dev-implement + 补某配置/编译」等：允许先做白名单内修补；**修补完成后视为 Phase 1 或并行准备已推进，仍须执行本段强制动作**——扫描 **`TASKLIST_FILE`** 并派发下一项 Subagent，**禁止**以「配置已补，若要协议实现请再说」收尾。

### Phase 2~4: 按协议开发（核心循环）

按 Priority 分组（P1 → P2 → P3），组内按协议编号执行。

**同 Priority 内的并行策略**：
- 标记 `[P]` 的任务可并行派发（最多 4 个 subagent 并发）
- 但每个协议内部的 3 步（业务开发 → BDD → 代码检查）必须串行

#### 单协议执行流程（核心闭环）

对每个协议 P-{N}：

**Subagent 完成后的主 Agent 针对性检查（强制）**

可以且**应当**在**每一个** subagent（executor / qa-tester / codereview）完成本协议任务并返回后，由**主 Agent** 针对**该次任务**做一次核对，再在 **`TASKLIST_FILE`** 勾选或进入下一步。此为**轻量对账**，与 Phase 6 全量 `business-implementation-check` 互补：前者保证单协议闭环不断档，后者保证整功能横切一致。

| 时机 | 针对本步的检查（不通过则不得勾选、不得进入下一步） |
|------|------------------------------------------------------|
| **executor 返回后** | ① 回报中的「DD-2 流程每一步 → 实现位置」是否**逐项**有落点；任一项未覆盖或未说明分期 → **不标**业务开发 `[x]`。<br>② DD-2/服务器需求已写扣道具/货币/上限等：在回报所列文件中**抽查**是否存在真实扣减/校验调用链（禁止仅有日志无行为）。<br>③ 业务主路径是否存在 **TODO 顶替已交付需求** → 有则返工 executor。<br>④《服务器需求》含目录/包路径附录时：回报须含「附录路径 → 实际路径」对照或已登记分期；**无对照且明显偏离附录** → **不标**业务开发 `[x]`，须返工或先补文档分期。 |
| **qa-tester 返回后** | ① **映射表**完整：`BDD-P{N}-xx` → `It("...")` 或文件:行，**缺一条即本步不通过**、不标 BDD `[x]`。<br>② 声明通过但**无映射表** → 视为不通过，要求 qa-tester 补回报。<br>③ 可选：`grep` `BDD-P{N}` 或完整消息名于 `qa/integration/{domain}/` 复核存在性。 |
| **codereview 返回后** | ① 回报中**严重**级问题未闭环 → **不标**代码检查 `[x]`。<br>② 「文档业务流程对账表」：文档已写步骤若标否/TODO 且无 accepted 分期说明 → 不通过，须修代码或修文档后再审。<br>③ BDD 缺测与对账结论一致：缺测须已补或已在**任务清单** / 开发文档登记分期。<br>④《服务器需求》含目录/包路径附录时：回报须含「附录 → 代码树」对账；**附录要求的路径不存在实现且未说明分期** → **不标**代码检查 `[x]`。 |

---

**步骤 1：业务开发**

派发给 **executor** subagent（subagent_type: `executor`）：

```
prompt 内容：
1. 功能名：{功能名}
2. 协议：P-{N} {消息名} — {中文功能名}
3. **必读文件（须用 Read 打开，禁止只依赖本 prompt 摘要）**：
   - FEATURE_DIR/{功能}-开发文档.md：**整段 DD-2「P-{N} …」**（业务描述、业务流程、BDD 列表、代码检查列表）
   - FEATURE_DIR/{功能}-服务器需求.md：**与本协议对应**的协议说明、流程图、验收要点（与 DD-2 取并集，不得遗漏任一侧已写明的行为）
4. **交付标准（禁止简化版）**：
   - 须同时满足《服务器需求》与 DD-2 中已描述的全部业务步骤（校验、消耗、上限、持久化、推送、属性树等）。禁止以「骨架 / 只改内存字段 / TODO 后补」替代已写明的需求。
   - 若确有外部依赖阻塞：须保持**任务清单**对应项未完成并在回报中列阻塞项；禁止未实现却宣称完成。
5. 开发内容（与第 3 步文件内容对账后实现，逐项打勾）：
   - 业务描述
   - 业务流程（完整步骤，与文档一致）
   - 涉及配置（表名+字段）
   - 关联存储 Key（K-1~K-5 等）
   - **骨架文件（若有）**：以下 Setup 阶段创建的骨架文件包含占位注释，本协议须填充其真实实现或删除不需要的文件：{列出骨架文件路径}。**禁止**保留 `// Phase X 实现` 等占位注释。
6. 实施计划（从 DD-7 提取）：
   - 领域层 → 基础设施层 → 应用层 → 接口层
6.1 **工程目录与《服务器需求》一致（强制）**：若 `{功能}-服务器需求.md` 含「新增的文件和目录」或包路径类附录，**本协议涉及的新增/调整文件须落在附录所列路径**（含 AppService、Handler、子域 `port`/`extension` 等子目录名）；禁止仅用「分层」自行选路径。若必须与附录不一致：在**完成回报**中附 **需求路径 → 实际路径** 表，并注明 **`TASKLIST_FILE`/DD-7 已登记分期或仓库约定**，否则不得要求主 Agent 勾选完成。
7. 代码规范引用：
   - .cursor/rules/ddd-architecture.md
   - .cursor/rules/redis.mdc
   - .cursor/rules/code-quality.md
8. 日志规范（必须遵守，见本命令下方「日志与注释规范」）：
   **核心原则：宁可多打不可少打，每一个执行步骤都应有日志，方便开发阶段快速定位问题。**
   - Handler 入口：Info 级别，记录请求全部参数
   - 配置表读取：Info 级别，记录配置项与关键值
   - 前置校验：每个分支有日志（通过 Info/Debug，失败 Warn）
   - 扣道具/扣货币：Info 级别，道具 ID、数量前后（**文档要求扣除则必须有此类日志**）
   - 领域状态变更：Info 级别，前后对比
   - 持久化：Info 级别，Save 与结果
   - 业务失败 Warn，系统失败 Error；中文描述；格式 `[类名.方法名] 描述 k=v`
9. 注释规范：公开方法 GoDoc（含协议编号）；非显而易见规则写清依据；禁止无效叙述注释；TODO 须含前置条件与归属任务。
10. 架构要求：
   - DDD 分层；配置禁止硬编码；Redis Key 用 rediskey；玩家维度 Registry。
11. **完成回报（强制）**：
   - 修改/新增文件路径列表
   - **对照表**：DD-2 业务流程每一步 → 实现位置（文件+函数）是否已覆盖；未覆盖须说明并不得要求主 Agent 勾选完成
   - **（若《服务器需求》含目录附录）目录对账表**：附录中的路径/文件名 → 本协议实际落点路径（一致则写「一致」；偏离则写差异与分期依据）
```

executor 返回后：
- **先**完成上表 **executor 行**针对性检查；不通过则记录原因，派发 executor 返工或要求补充回报，**不得**勾选业务开发 `[x]`
- 若 subagent 声明成功且针对性检查通过，在 **`TASKLIST_FILE`** 中标记该业务开发任务为 `[x]`
- 若 subagent 声明失败，记录失败原因，**停止该协议**，报告用户

---

**步骤 2：BDD 测试**

派发给 **qa-tester** subagent（subagent_type: `qa-tester`）：

```
prompt 内容：
1. 功能名：{功能名}，领域（domain）名：{domain}
2. 协议：P-{N} {消息名}
3. **必读文件**：FEATURE_DIR/{功能}-开发文档.md 中 **DD-2 P-{N} 整节**；qa/api/{domain}.yaml 中本协议请求/响应定义（禁止编造消息名或字段）。
4. BDD 用例条目（从 DD-2 P-{N} 的 BDD 列表**逐条**抄入，不得合并省略）：
   - BDD-P{N}-01: {用例描述}
   - BDD-P{N}-02: {用例描述}
   - ...
5. BDD 规范引用：.cursor/rules/bdd.mdc、.cursor/rules/api-testing.mdc
6. 测试目录：qa/integration/{domain}/；testutil：qa/integration/testutil/
7. **红绿与覆盖（强制）**：
   - **无测试则无通过**：若本协议在 `qa/integration/{domain}/` 下**没有任何**针对该消息（或 BDD-P{N}-xx）的 `It`，视为**本步骤失败**，须先补测试再跑。
   - **先红后绿**：对 DD-2 中标注的**失败/异常**场景，须有意编写会先失败的断言（如道具不足 Ret、参数非法 Ret）；实现正确后同一用例应变绿。**禁止**只写「成功路径」导致错误实现仍全绿。
   - **一一映射**：DD-2 中列出的每个 BDD-P{N}-xx 须有对应 `It`（或可等价说明的单一 It 覆盖多条的依据）；**遗漏一条即本步骤不通过**。
   - 成功路径：`Ret` 与关键字段、写操作后全量拉取对比、有推送则验推送、有持久化副作用则按规范验 Redis（见 bdd.mdc）。
8. 执行：编写/修改测试后运行 `go test -v -run {TestSuiteName} ./qa/integration/{domain}/`（或全包），贴出失败输出直至通过。
9. **返回（强制）**：
   - 通过/不通过；失败时附用例名与错误摘要
   - **映射表**：`BDD-P{N}-xx` → `It("...")` 标题（或文件:行）
   - 本协议涉及的测试文件路径列表
```

qa-tester 返回后：
- **先**完成上表 **qa-tester 行**针对性检查；未满足映射表等要求时，**视为不通过**，要求 qa-tester 补全后再判
- **通过**（含针对性检查通过）：在 **`TASKLIST_FILE`** 中标记该 BDD 测试任务为 `[x]`，继续步骤 3
- **不通过**：
  1. 记录失败的用例和错误信息
  2. 将失败信息派发给 **executor** subagent 修复代码：
     ```
     prompt: 以下 BDD 测试用例未通过，请修复代码：
     - 失败用例：{列表}
     - 错误信息：{详情}
     - 测试文件：{路径}
     - 被测代码：{相关文件路径}
     修复后报告修改内容。
     ```
  3. 修复后**重新执行步骤 2**（BDD 测试）
  4. **最多重试 3 次**，超过后停止并报告用户

---

**步骤 3：代码检查**

派发给 **codereview** subagent（subagent_type: `codereview`）：

```
prompt 内容：
1. 功能名：{功能名}
2. 协议：P-{N} {消息名}
3. **必读对账材料（须 Read）**：
   - FEATURE_DIR/{功能}-开发文档.md：**DD-2 P-{N} 整节**（含代码检查列表）
   - FEATURE_DIR/{功能}-服务器需求.md：与本协议相关的消耗、上限、流程描述
   - qa/integration/{domain}/：本协议已存在的测试文件（核对是否覆盖 DD-2 BDD 条目）
4. 代码检查条目（从 DD-2「代码检查」**逐条抄入**）：
   - [硬编码] …
   - [注释] …
   - [日志] …
   - [BDD] …
   - [规范] …
5. 审查规范：.cursor/agents/codereview.md
6. 审查范围：本协议 P-{N} 涉及的所有新增/修改文件（Handler / AppService / Domain / infra）
7. **文档 vs 代码对账（强制，不通过则整体不通过）**：
   - 将 DD-2 **业务流程**与《服务器需求》中本协议步骤，逐条对照代码：**文档已写「扣道具/扣货币/上限/返还/属性树/推送」等，必须在代码中存在对应实现**（含调用链）。若仅有 TODO 或「简化」注释而无行为，**判为不通过（严重）**。
   - **禁止**以「当前代码没写扣道具」为由认定「本协议不涉及经济」——须以**文档为准**。
8. **BDD 对账（强制）**：
   - DD-2 列出的每个 BDD-P{N}-xx 须在 `qa/integration/{domain}/` 中有对应用例；缺测**判不通过（严重）**。
8.1 **目录与包路径对账（强制）**：若《服务器需求》含「新增的文件和目录」或包路径附录，须输出 **附录条目 → 仓库实际路径** 表；附录要求存在而代码树缺失、且未在任务清单/DD-7 分期说明的 → **不通过（严重）**。
9. **工程审查**：分层职责、WorkPool、tlog、clock、Redis Key、命名、并发安全（按 codereview.md）。
10. **日志标准（必检）**：仅凭日志能否还原完整请求路径；Handler 参数、配置读取、各校验分支、**文档要求时的扣道具日志**、状态变更前后、Save、返回 Ret；中文；缺关键节点**不通过**。
11. **注释标准（必检）**：GoDoc 含协议编号；业务规则有依据；无无效叙述；业务路径上 **TODO 顶替已交付需求** → **不通过（严重）**；**`// Phase X 实现` 等空壳占位注释** → **不通过（严重）**，必须以真实实现替代或删除该文件。
12. **经济安全（按文档触发）**：文档/DD-2 写明扣除 → 必须「先校验后扣除」、顺序合理、有 Info 日志；文档未写扣除 → 在回报中注明「经济：N/A」并仍须完成对账表。
13. **返回（强制）**：
   - 通过/不通过
   - **对照表**：DD-2 代码检查每一条 → 满足 / 缺陷（附文件与说明）
   - **对账表**：文档业务流程步骤 → 代码是否实现（是/否/TODO）
   - **（若《服务器需求》含目录附录）目录对账表**：附录路径 → 实际路径（或分期说明）
   - 问题清单：严重程度、修复建议
```

codereview 返回后：
- **先**完成上表 **codereview 行**针对性检查；严重项未闭环或对账不成立时，**不得**视为通过
- **通过**（含针对性检查通过）：在 **`TASKLIST_FILE`** 中标记该代码检查任务为 `[x]`，**该协议完成**
- **不通过**：
  1. 记录审查问题清单
  2. 将问题派发给 **executor** subagent 修复：
     ```
     prompt: 以下代码检查问题需修复：
     - 问题清单：{列表，含文件路径、行号、问题描述、修复建议}
     修复后报告修改内容。
     ```
  3. 修复后**重新执行步骤 2（BDD）+ 步骤 3（代码检查）**
  4. **最多重试 2 次**，超过后停止并报告用户

---

**协议完成判定**：步骤 2（BDD）通过 **且** 步骤 3（代码检查）通过 → 该协议 P-{N} 开发完成。

### Phase 5: E2E 混合验收测试

前置条件：所有单协议任务（Phase 2~4）全部完成。

派发给 **qa-tester** subagent：

```
prompt 内容：
1. 功能名：{功能名}，领域名：{domain}
2. E2E 场景列表（从开发文档 DD-2 E2E-1~E2E-{K} 提取）：
   - E2E-1: {业务链路描述}
   - E2E-2: {业务链路描述}
   - ...
3. 覆盖协议：各 E2E 涉及的协议串联列表
4. BDD 规范引用：.cursor/rules/bdd.mdc
5. 测试目录：qa/integration/{domain}/
6. 要求：
   - 编写 E2E 混合验收 BDD 测试；场景须与开发文档 DD-2 中 E2E 描述**可对账**，不得省略异常分支（如文档要求链路中道具不足须断言错误码）
   - 验证多协议串联的完整业务链路
   - 包含掉线重连后数据一致性验证（见 bdd.mdc）
   - 运行全部 E2E 测试并返回结果；返回附 **E2E 场景 → It** 映射
```

E2E 不通过时：与单协议类似，派发修复 → 重新测试，最多重试 3 次。

完成后在 **`TASKLIST_FILE`** 将 `[E2E]` 任务标为 `[x]`。

### Phase 6: 收尾

1. 派发 **executor** subagent 更新子域 README.md 文档
2. 更新开发文档 DD-1 状态为 `Completed`
3. **骨架/占位扫描（强制）**：主 Agent 在**子域**、**域内 appservice（若存在）**、**应用层约定目录（若存在）** 下执行以下扫描，**不得省略**（`{domain}` 为 `qa/api` 与集成测试所用领域名，与《服务器需求》子域名一致时直接使用；不一致时须将三处路径替换为实际包目录）：
   - `rg -n "// Phase|// 待实现|// TODO.*实现|// stub" srv/game/domain/{domain}/ srv/game/domain/{domain}/appservice/ srv/game/application/service/{domain}/`
   - `rg -n "TODO|FIXME|HACK|XXX" srv/game/domain/{domain}/ srv/game/domain/{domain}/appservice/ srv/game/application/service/{domain}/`
   其中 `srv/game/domain/{domain}/appservice/`、`srv/game/application/service/{domain}/` 若目录不存在可跳过该段路径，但**须在收尾说明中写明** AppService 实际所在路径，并与《服务器需求》目录附录对账（不一致须有分期/例外登记）。
   若存在匹配：① 属未完成业务逻辑 → 派发 **executor** 填充或删除；② 属合理 TODO（明确分期、外部依赖阻塞）→ 在报告中标注。**禁止**在代码中留存 `// Phase X 实现` 等空壳注释。
3.1 **目录规划对账（强制）**：若 `{功能}-服务器需求.md` 含「新增的文件和目录」或等价附录，主 Agent 须核对附录中的**关键路径**（如 `srv/game/handler/...`、`srv/game/application/service/...`、`srv/game/domain/...`）在仓库中是否存在或可映射；**未实现且无分期说明**的项须派发 **executor** 迁移/补建或派发 **design-doc-sync** 修订需求与分期，**不得**在 Phase 6 直接勾选收尾完成。
4. 在 **`TASKLIST_FILE`** 中标记所有收尾任务为 `[x]`
5. **（衔接完整性检查）** 执行 **`.cursor/commands/business-implementation-check.md`**：用户输入为当前 **功能名**，生成/更新 **`docs/操作记录/{YYYY-MM-DD}-{功能名}-业务实现完整性检查报告.md`**。

#### Phase 6 续：完整性报告分析 → 缺项补开发（强制）

**报告不是终点**：主 Agent **必须**阅读报告中的 **问题清单**与**建议**，并按下表驱动后续工作（不可仅存档报告即结束）。

| 报告结论类型 | 判定要点 | 主 Agent 动作 |
|--------------|----------|----------------|
| **功能/经济/协议缺失** | 如「应扣费未扣」「协议无 Handler」「FR 与实现不符」「文档流程在代码中无对应路径」 | 派发 **executor**：附上报告中的**问题标题+位置+建议**，要求对照 **`FEATURE_DIR/{功能}-开发文档.md` DD-2** 与 **`{功能}-服务器需求.md`** **补全实现**（禁止再交简化版）；涉及协议则同步 **Handler/AppService/Domain** 与配置读取 |
| **仅缺测试 / BDD 覆盖不足** | 实现已存在但集成测试未覆盖、缺 `BDD-Px-yy` | 派发 **qa-tester**：按 DD-2 与 `qa/api/{domain}.yaml` **补写并跑通** `qa/integration/{domain}/` |
| **工程规范类**（日志、注释、硬编码） | 报告标为中优先级且与交付质量相关 | 派发 **executor** 或 **codereview** 跟进修复 |
| **文档与代码争议** | 报告认为缺功能但实际为文档过时 | 须在报告中**追加修订说明**，或修订设计文档后再关闭该项；**不得**无说明直接忽略 |

**闭环顺序**（每一轮）：

```
business-implementation-check → 分析报告
    → [有功能缺项] executor 补开发 → qa-tester 补/跑 BDD（+ 可选 codereview）
    → 重新执行 business-implementation-check（更新同路径报告或新日期附录）
    → 直至「高优先级问题」为空，或已在报告 / **任务清单** / 开发文档中**明确分期与未完成任务编号**
```

- **重试上限**：完整性检查 **分析→补开发→再检查** 建议 **最多 3 轮**；仍有余项须在最终汇报中列出**未闭环项**与**建议下一迭代任务**，并**不得**输出「✅ 开发完成」除非用户确认接受该残余。
- **禁止**：高优先级问题未修复、未备注分期、未派发补开发，即输出下方「✅ 开发完成」最终报告。

## 进度跟踪

### 实时更新任务勾选

每完成一个任务，立即在 **`TASKLIST_FILE`（`{功能}-开发任务清单.md`）** 内将对应 `- [ ]` 改为 `- [x]`；**勿**在开发文档正文内维护一份并行的 checkbox 列表。

### 进度报告格式

每完成一个协议后，输出进度报告：

```
## 进度报告

### 已完成
- ✅ P-0: MsgCtrNtfPetPlayerInfo — 登录全量推送
- ✅ P-1: MsgCtrReqPetInfo — 获取宠物全量信息
- ✅ P-2: MsgCtrReqPetActivate — 宠物激活

### 进行中
- 🔄 P-3: MsgCtrReqPetLevelUp — 阵位槽升级（BDD 测试中）

### 待开始
- ⏳ P-4 ~ P-17
- ⏳ E2E 混合验收
- ⏳ 收尾文档

### 统计
- 总任务：{N} 条
- 已完成：{C} 条（{C/N*100}%）
- BDD 重试次数：{R} 次
- 代码检查重试次数：{CR} 次
```

## Subagent 派发规则

### 主 Agent 派发前自检（提示词质量）

| 检查项 | 要求 |
|--------|------|
| DD-2 P-{N} | 已整节粘贴或要求子代理必读该节，**非**仅任务清单中一行 checkbox |
| 服务器需求 | 已粘贴或要求必读与本协议对应段落 |
| qa/api | 已写明 `{domain}.yaml`，接口以文档为准 |
| BDD | qa-tester prompt 已列出 DD-2 **全部** BDD-P{N}-xx 文案 |
| codereview | prompt 已列出 DD-2 **全部**代码检查条，并强调文档对账 |
| 目录/包路径 | 《服务器需求》含目录附录时，executor/codereview prompt 已要求 **目录对账表** 或已登记分期；Phase 6 已执行 **3.1 目录规划对账** |

### 角色与 subagent 映射

| 角色 | subagent_type | 说明 |
|------|---------------|------|
| 业务开发 | `executor` | 按《服务器需求》+ DD-2 全量实现，禁止简化 |
| BDD 测试 | `qa-tester` | 红绿覆盖、DD-2 BDD 与 It 一一映射 |
| 代码检查 | `codereview` | 文档对账 + 工程规范 + 硬标准（日志/经济/BDD 覆盖） |
| 基础检查 | `explore` / `shell` | 检查文件存在性、配置状态等 |
| 日志补全 | `request-chain-logging` | 在 Handler/AppService/Domain 补全 tlog 日志 |

### 并行派发限制

- 最多同时运行 **4 个** subagent（Cursor 限制）
- 同一协议内 3 步串行，不同协议间可并行
- 建议同时并行不超过 2 个协议（避免代码冲突）

### 失败处理

| 场景 | 处理 | 最大重试 |
|------|------|----------|
| BDD 测试不通过 | executor 修复 → 重新 BDD | 3 次 |
| 代码检查不通过 | executor 修复 → 重新 BDD + 代码检查 | 2 次 |
| E2E 测试不通过 | executor 修复 → 重新 E2E | 3 次 |
| **完整性检查**报告含未处理 **高优**功能缺项 | executor 补开发 → qa-tester 补 BDD → **重新** business-implementation-check | **3 轮**（见 Phase 6 续） |
| Setup 检查失败 | 停止并报告用户 | 0 次 |
| 重试耗尽 | 停止并报告用户（含失败详情） | — |

## 完成验证

所有任务完成后，执行最终验证：

1. **任务清单完整性**：**`TASKLIST_FILE`** 任务区内所有 `- [ ]` 均已改为 `- [x]`
2. **BDD 全量通过**：运行 `go test -v ./qa/integration/{domain}/...` 确认全部通过；主 Agent 宜抽查：对**任务清单**已勾选 BDD 的每个 P-{N}，在 `qa/integration/{domain}/` 下能检索到对应 `BDD-P{N}-` 或协议消息名相关用例，**防止「未写测却勾选」**
3. **编译检查**：运行 `go build ./...` 确认无编译错误
4. **文档更新**：子域 README.md 已更新、开发文档状态已更新
5. **业务实现完整性检查 + 分析与补开发**：执行 **`.cursor/commands/business-implementation-check.md`** 产出 **`docs/操作记录/{YYYY-MM-DD}-{功能名}-业务实现完整性检查报告.md`** 后，**必须**按 **Phase 6 续** 解析报告：对**功能/经济/协议缺失**派发 **executor** 补开发，对**缺测**派发 **qa-tester**，然后**再次**运行完整性检查更新报告，直至 **高优先级问题** 已关闭或已**书面分期**；**禁止**只生成报告不跟进缺项。

验证通过后输出最终报告：

```
## ✅ {功能名} 开发完成

- 总任务：{N} 条，全部完成
- 单协议 BDD：{M} 条用例全部通过
- E2E 混合验收：{K} 条用例全部通过
- 代码检查：所有协议审查通过
- **业务实现完整性检查报告**：`docs/操作记录/{YYYY-MM-DD}-{功能名}-业务实现完整性检查报告.md`（高优先级问题已闭环或已备注分期）
- 编译状态：通过
- 文档状态：已更新

### 新增/修改文件清单
- domain/{子域}/... ({X} 个文件)
- srv/game/handler/... ({Y} 个文件)
- srv/game/application/service/... ({Z} 个文件)
- qa/integration/{domain}/... ({W} 个文件)
```

## 日志与注释规范

本节为所有 subagent（executor、qa-tester、codereview）的强制要求。

### 日志规范

**核心原则：宁可多打不可少打。看日志就能还原整条请求的完整执行路径，不需要看代码就能判断问题出在哪一步。**

**目的**：开发和运维阶段，仅凭日志即可分析任意一条请求的完整执行过程——走了哪些分支、读了什么配置、扣了什么道具、改了什么数据、最终结果是什么。

**级别使用**：

| 级别 | 场景 | 示例 |
|------|------|------|
| Debug | 循环内部细节、中间变量快照 | 每次循环迭代的值、配置表逐条遍历 |
| Info | **每一个执行步骤**（正常路径） | 请求进入、配置读取、校验通过、扣道具、领域操作、持久化、返回结果 |
| Warn | 业务校验失败、可恢复异常 | 道具不足、参数非法、宠物未激活、重复操作 |
| Error | 系统异常、不可恢复错误 | 持久化失败、依赖服务未注入、Redis 异常 |

**每个方法的日志覆盖要求**（按执行顺序逐步打）：

1. **Handler 入口**：Info，记录请求全部参数
   ```go
   tlog.LogCommonLogWithContext(ctx, config.GetGameID(), tlog.LogLevelInfo, config.GetServiceName(),
       fmt.Sprintf("[PetHandler.HandlePetActivate] 收到激活请求 playerID=%d playerRoleId=%d petId=%d", playerID, playerRoleId, req.GetPetId()))
   ```

2. **配置表读取**：Info，记录读取了什么配置、关键配置值
   ```go
   tlog.LogCommonLogWithContext(ctx, config.GetGameID(), tlog.LogLevelInfo, config.GetServiceName(),
       fmt.Sprintf("[PetAppService.ActivatePet] 读取配置 petId=%d activateItemCount=%d beginChange=%d", petId, len(petConfig.ActivateItem), petConfig.BeginChange))
   ```

3. **数据加载**：Info，记录 Load/Create 调用及加载结果
   ```go
   tlog.LogCommonLogWithContext(ctx, config.GetGameID(), tlog.LogLevelInfo, config.GetServiceName(),
       fmt.Sprintf("[PetAppService.ActivatePet] 加载宠物数据 playerRoleId=%d 已激活数=%d", playerRoleId, len(petService.GetPetPlayer().Base.GetActivatedPetIds())))
   ```

4. **前置校验**：每个校验分支都打日志（通过打 Info，失败打 Warn）
   ```go
   // 校验通过
   tlog.LogCommonLogWithContext(ctx, config.GetGameID(), tlog.LogLevelInfo, config.GetServiceName(),
       fmt.Sprintf("[PetAppService.ActivatePet] 前置校验通过 petId=%d 未激活", petId))
   // 校验失败
   tlog.LogCommonLogWithContext(ctx, config.GetGameID(), tlog.LogLevelWarn, config.GetServiceName(),
       fmt.Sprintf("[PetAppService.ActivatePet] 宠物已激活 petId=%d", petId))
   ```

5. **扣道具/扣货币**：Info，记录扣除的道具 ID、数量、扣除结果
   ```go
   tlog.LogCommonLogWithContext(ctx, config.GetGameID(), tlog.LogLevelInfo, config.GetServiceName(),
       fmt.Sprintf("[PetAppService.ActivatePet] 扣除道具 playerID=%d itemId=%d count=%d", playerID, itemId, count))
   ```

6. **领域操作**：Info，记录操作名称、输入输出、状态变更值
   ```go
   tlog.LogCommonLogWithContext(ctx, config.GetGameID(), tlog.LogLevelInfo, config.GetServiceName(),
       fmt.Sprintf("[PetService.LevelUpSlot] slotId=%d 增量=%d 升级前level=%d 升级后level=%d exp=%d", slotId, count, oldLevel, sl.GetLevel(), sl.GetExp()))
   ```

7. **持久化**：Info，记录 Save 调用及结果
   ```go
   tlog.LogCommonLogWithContext(ctx, config.GetGameID(), tlog.LogLevelInfo, config.GetServiceName(),
       fmt.Sprintf("[PetAppService.ActivatePet] 持久化完成 playerRoleId=%d petId=%d", playerRoleId, petId))
   ```

8. **方法返回**：Info，记录最终返回的 Ret 值和关键结果
   ```go
   tlog.LogCommonLogWithContext(ctx, config.GetGameID(), tlog.LogLevelInfo, config.GetServiceName(),
       fmt.Sprintf("[PetAppService.ActivatePet] 返回成功 playerRoleId=%d petId=%d ret=%v", playerRoleId, petId, message.EMsgErrorType_None))
   ```

9. **异常/错误**：Warn 或 Error，记录失败原因和全部上下文
   ```go
   tlog.LogCommonLogWithContext(ctx, config.GetGameID(), tlog.LogLevelWarn, config.GetServiceName(),
       fmt.Sprintf("[PetAppService.ActivatePet] 道具不足 playerID=%d itemId=%d count=%d err=%v", playerID, itemId, count, err))
   tlog.LogCommonLogWithContext(ctx, config.GetGameID(), tlog.LogLevelError, config.GetServiceName(),
       fmt.Sprintf("[PetAppService.ActivatePet] 持久化失败 playerRoleId=%d petId=%d err=%v", playerRoleId, petId, err))
   ```

**日志格式统一**：`[类名.方法名] 中文操作描述 key1=value1 key2=value2 err=...`

**判断标准**：如果删掉所有代码只留日志，能否还原出这条请求做了什么、走了哪个分支、结果是什么。如果不能，说明日志不够。

**禁止事项**：
- 禁止在成功路径打 Warn/Error
- 禁止日志中包含敏感信息（密码、token）
- 禁止使用英文日志描述（团队约定中文）

### 注释规范

**目的**：代码注释服务于团队协作和后续维护，解释「为什么」而非复述「做什么」。

**必须添加注释的场景**：

1. **公开方法 GoDoc 注释**：每个公开方法/类型必须有注释，说明用途和对应协议编号
   ```go
   // ActivatePet P-2：校验可激活 → 扣除激活道具 → 领域激活 → 持久化
   func (s *PetAppService) ActivatePet(ctx context.Context, ...) { ... }
   ```

2. **业务规则注释**：非显而易见的校验逻辑、计算公式、业务约束需说明来源
   ```go
   // 先校验是否可激活，避免扣道具后发现已激活导致错扣
   if ret := petService.CanActivate(petId); ret != message.EMsgErrorType_None {
   ```

3. **关键设计决策**：为什么选择某种实现方式
   ```go
   // 使用 roleIDs[0] 作为主角色，当前产品设计每个玩家仅有一个角色
   return roleIDs[0], nil
   ```

4. **TODO 注释**：标记未完成功能，必须说明待完成内容和前置条件
   ```go
   // TODO: 全局属性树集成，待属性系统提供 ChangeData 接口后对接
   ```

5. **存储 Key 说明**：Redis Key 常量必须注释对应的数据结构和用途
   ```go
   // RedisKeyFormatPetBase K-1 宠物基础数据（已激活列表、阵位槽等级、阵容列表）
   RedisKeyFormatPetBase = "playerrole:%d:pet:base"
   ```

**禁止的注释**：
- 禁止纯叙述型注释：`// 获取玩家ID`、`// 返回结果`、`// 循环处理`
- 禁止注释掉的代码长期留存（临时调试后须清理）
- 禁止与代码不一致的过时注释

## 注意事项

- **禁止把「交接话术」当合规收尾**：用户跑 **`/dev-implement`** 时，只要还有未勾的 Phase 2+ 且无阻塞，**默认动作是派发下一 Task**，不是请用户打字「继续」。
- **Task 派发是默认动作**：对 executor / qa-tester / codereview（及 Phase 1 中写代码的 Setup），主 Agent **必须先派发 Task**，再基于回报对账；例外仅见上文「主 Agent 允许亲自执行的操作（白名单）」。
- 每个 subagent 的 prompt 必须包含足够的上下文（开发文档路径、协议详情、规范引用）
- BDD 测试的接口信息必须从 `qa/api/{domain}.yaml` 读取，禁止编造
- 代码检查必须使用完整的 `codereview.md` 规范，不能简化
- 修复代码后必须重新运行 BDD 测试，确保修复不引入新问题（由 **qa-tester** Task 执行并贴结果；主 Agent 抽检不能替代）
- 进度实时更新到 **`TASKLIST_FILE`（`FEATURE_DIR/{功能}-开发任务清单.md`）**，方便中断后继续、独立 diff；开发文档 **DD-7.1** 仅保留指向该文件的链接即可。**勿**在开发文档内与任务清单**双份**维护 checkbox；也**勿**再使用已废弃的 `docs/design/server/{功能}/tasks.md` 作为第三份真源
- **日志和注释是必检项**：codereview 不通过如果日志或注释不符合规范，必须修复后重新检查
