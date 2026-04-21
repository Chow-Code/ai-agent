---
name: bdd-qa
description: 本项目 BDD 与接口测试的单一技能入口：qa/integration 可执行用例、测试用例文档（配合 test-case 命令）、每协议 2～5 条与数据断言、qa/test_reports 双 JSON；接口须从 qa/api/{domain}.yaml 读取，禁止编造。
---

# BDD 与接口测试（bdd-qa）

## 与其它入口的关系（必读）

| 入口 | 是什么 | 要不要重复读 |
|------|--------|----------------|
| **本技能 `bdd-qa`** | **唯一完整操作说明**（跑测、写 BDD、用例数量、JSON 报告、读 API、启动服） | **优先加载本文件** |
| **`.cursor/commands/test-case.md`** | **Cursor 命令**：只负责生成 `docs/design/server/.../*-测试用例.md` 的**文档结构与章节模板** | 仅当要**生成/改测试用例 Markdown** 时打开；BDD 代码规范以本技能 + `qa/README` 为准 |
| **`.cursor/rules/testing.mdc`** | **规则**：编辑 `qa/**/*.go` 等时 IDE 可附带；**仅保留短约束**，细节指向本技能 | 不必与本文逐段对照 |

**结论**：没有三个并列的「技能」——只有 **`bdd-qa` 一个技能**；`test-case` 是**命令**，`testing.mdc` 是**规则**。

## 工具概述

本技能以**可执行 BDD 集成测试**为核心：用例在 `qa/integration/{领域}/`，使用 **Ginkgo v2 + Gomega**，通过 **TCP（PvpCodec）** 与网关通信，**代码即用例**。通用封装在 `qa/integration/testutil/`（env、HTTP 登录取 token、TCP Dial/Login/Call）。API 文档在 `qa/api/`（OpenAPI YAML），接口信息须从 API 文档读取，禁止编造。

## 使用场景

- 需要**运行或编写** BDD 集成测试时（`qa/integration/`）
- 需要调试单个领域或单条用例时
- 需要查看 API 文档时（`qa/api/{domain}.yaml`）
- 需要验证接口功能时

## 前置条件

- **服务器已启动**：根据当前开发环境使用对应启动脚本（见「服务器启动」）
- **integration 测试**：需**登录服（HTTP 20002）**与**网关（TCP 20000）**已启动
- API 文档已准备好（`qa/api/`）

## 服务器启动

⚠️ **重要**：启动脚本不能写死，必须根据当前开发环境动态选择。

### 如何确定当前开发环境

**方法1：根据环境变量 `GAME_INSTANCE` 判断**
- 如果 `GAME_INSTANCE=game_xuhai`，使用 `deploy/start_xuhai.sh`
- 如果 `GAME_INSTANCE=game_zlf`，使用 `deploy/start_zlf.sh`
- 如果 `GAME_INSTANCE=game_pf`，使用 `deploy/start_pf.sh`
- 如果 `GAME_INSTANCE=game_stable`，使用 `deploy/start_stable.sh`

**方法2：根据用户规则中的开发环境判断**
- 查看用户规则中的"开发环境"字段（如 `开发环境: zlf`）
- 对应关系：
  - `zlf` → `deploy/start_zlf.sh`
  - `xuhai` → `deploy/start_xuhai.sh`
  - `pf` → `deploy/start_pf.sh`
  - `stable` → `deploy/start_stable.sh`

**方法3：检查 `deploy/` 目录下的启动脚本**
- 列出 `deploy/start_*.sh` 文件，根据实际存在的脚本选择

### 启动脚本调用方式

**通用格式**：
```bash
cd deploy
./start_{环境名}.sh {服务名}
```

**示例**：
- zlf环境启动游戏服务器：`cd deploy && ./start_zlf.sh game`
- xuhai环境启动所有服务：`cd deploy && ./start_xuhai.sh all`
- pf环境启动游戏服务器：`cd deploy && ./start_pf.sh game`

**可用服务名**：
- `game` - 游戏服务器
- `login` - 登录服务器
- `waypoint` - Waypoint服务
- `gateway` - Gateway服务
- `battle-proxy` - Battle-Proxy服务
- `all` - 启动所有服务

**integration 测试**：运行 `qa/integration/` 下的用例前，需启动**登录服**与**网关**（默认 HTTP 20002、TCP 20000），通常通过 `./start_{环境}.sh all` 或分别启动 `login` 与 `gateway`。

### 启动前检查

执行测试前，应该：
1. **确认当前开发环境**：检查环境变量或用户规则
2. **选择对应的启动脚本**：根据环境选择 `start_{环境名}.sh`
3. **启动服务器**：使用选定的脚本启动服务器（integration 需登录服 + 网关）
4. **验证服务器状态**：确认服务器已成功启动

### 战斗服 Mock 与环境变量（自测不必连真实战斗服）

本地或自测时，若只需验证 **game 侧战斗相关逻辑**（不要求真实战斗服、真实 battle-proxy 连战斗进程），应在启动 **game** 前通过环境变量打开 **战斗 Mock**，避免依赖真实战斗服地址。

**优先级**：环境变量覆盖 `srv/game/bin/game.yaml` 中 `battle` 段（与 Sidecar 的 `OVERRIDE_*` 一致）。

| 环境变量 | 作用 |
| -------- | ---- |
| `OVERRIDE_BATTLE_MOCK_MODE` | 是否启用战斗 Mock：`true`/`false`、`1`/`0`、`yes`/`no`、`on`/`off`（不区分大小写） |
| `OVERRIDE_MOCK_BATTLE_ADDR` | Mock 模式下下发给客户端的战斗地址（`host:port`） |

**示例**（在调用 `start-runtime.sh` / `start.sh` 或启动 game 进程前 `export`）：

```bash
export OVERRIDE_BATTLE_MOCK_MODE=true
export OVERRIDE_MOCK_BATTLE_ADDR=127.0.0.1:6200
```

**区服启动脚本（`deploy/start_*.sh`）**：多数区服默认 `OVERRIDE_BATTLE_MOCK_MODE=true`（自测 Mock），并导出双地址等（见各脚本注释）。**例外：`start_stable.sh`（稳定服）默认 `OVERRIDE_BATTLE_MOCK_MODE=false`**，走真实战斗链路；若要在稳定服临时开 Mock，可 `export OVERRIDE_BATTLE_MOCK_MODE=true` 再启动。涉及脚本示例：`start_xuhai.sh`、`start_zlf.sh`、`start_stable.sh`、`start_222.sh`、`start_pf.sh`、`start_223.sh`；成员区服见 `deploy/` 下各人中文名 `.sh`。

```bash
cd deploy
export OVERRIDE_BATTLE_MOCK_MODE=false   # 非稳定服脚本若需关 Mock
./start_xuhai.sh all
# 稳定服已默认关 Mock；若要开：export OVERRIDE_BATTLE_MOCK_MODE=true
```

若仍启动 **battle-proxy** 且希望 **不维护长 `battle.toml`**，可用 `OVERRIDE_BATTLE_PROXY_BATTLE_ADDR`、`OVERRIDE_BATTLE_PROXY_CLIENT_ADDR` 覆盖默认战斗服地址，并用 `OVERRIDE_BATTLE_PROXY_DEFAULT_SERVER` + `OVERRIDE_BATTLE_PROXY_GAME_IDS` 或 `OVERRIDE_BATTLE_GAME_MAPPING` 补全 `game_id` 映射。完整白名单与常量名见 **`common/config/env_overrides.go`** 顶部注释。

**说明**：integration 用例是否依赖真实战斗链路取决于业务；上述变量用于**服务端配置**，与 `qa/integration/testutil` 里网关地址、`SERVER_ID` 等配置相互独立。

## 目录结构

```
qa/
├── api/                          # API文档目录
│   ├── account.yaml              # 账号相关接口
│   ├── skill.yaml                # 技能相关接口
│   ├── backpack.yaml            # 背包相关接口
│   ├── role.yaml                 # 角色相关接口
│   ├── player.yaml               # 玩家相关接口
│   ├── default.yaml              # 未按领域注解的接口
│   └── README.md                 # API文档说明
├── integration/                  # 按领域组织的 BDD 集成测试（代码即用例）
│   ├── testutil/                 # 通用测试封装（TCP、登录、GM、环境配置）
│   │   ├── env.go                # 环境配置（test_config.yaml + 环境变量）
│   │   ├── login_http.go         # GetLoginToken、GetSessionToken（两步登录）
│   │   ├── tcp_client.go         # Dial、Login、Call、CallExpect（PvpCodec）
│   │   ├── gm.go                 # GMCommand、GMCommandOptional
│   │   ├── testing_t.go          # TestingT 接口（兼容 Ginkgo）
│   │   ├── test_config.yaml.example  # 配置示例
│   │   └── README.md             # testutil 使用说明
│   ├── account/
│   │   └── account_test.go       # 账号领域用例
│   ├── backpack/
│   │   └── backpack_test.go      # 背包领域用例（Ginkgo + Gomega）
│   ├── role/
│   ├── skill/
│   └── ...                       # 其他领域
└── test_reports/                 # BDD 跑完后的 JSON 报告（汇总 + 详细），见 qa/test_reports/README.md
```

## 用例数量与数据断言（与测试用例文档一致）

- **每业务协议 2～5 条 `It`**：`qa/api/{domain}.yaml` 中每个 `MsgCtrReq*` 应有 **≥2 且 ≤5** 个场景（失败/边界/成功等），**禁止**仅断言「收到响应」而不校验 `qa/api` 中的业务字段。
- **测试完成交付**：跑完或汇报验证时，在 **`qa/test_reports/`** 生成 **`bdd-report-summary.json`**（汇总）与 **`bdd-report-detail.json`**（逐用例消息收发与断言摘要），结构见 **`qa/test_reports/README.md`**，用于防幻觉；**测试用例 Markdown 文档**的章节与流程见 **`.cursor/commands/test-case.md`**（命令，非技能）。

## BDD 集成测试与 testutil

### 框架与入口

- **框架**：Ginkgo v2 + Gomega（Describe/Context/It、BeforeEach/AfterEach、Expect 断言）
- **入口**：每个领域一个 `TestXxx(t *testing.T)`，内部 `gomega.RegisterFailHandler(ginkgo.Fail)` 与 `ginkgo.RunSpecs(t, "Suite 名")`
- **前置两种模式**：（1）仅 TCP 登录：BeforeEach 中 Dial + Login。（2）需 GM 造数：先 GetSessionTokenOptional、再按需 GMCommandOptional、最后 Dial + Login；`AfterEach` 中 Close；每个 `It` 内 Call/CallExpect + Expect

### testutil 使用

- **环境配置**：`GetGatewayTCPAddr()`、`GetLoginServerAddr()`、`GetGameServerConsoleAddr()`、`GetServerID()`；支持配置文件 `qa/integration/testutil/test_config.yaml`（复制自 `test_config.yaml.example`）与环境变量（`GATEWAY_TCP_ADDR`、`LOGIN_SERVER_ADDR`、`GAME_SERVER_CONSOLE_ADDR`、`SERVER_ID`），优先级：环境变量 > 配置文件 > 默认值。
- **TCP**：`testutil.Dial(t, addr)` 建立连接；`testutil.Login(t, conn, account)` 在连接上完成登录（HTTP 取 token + TCP 发 MsgCtrReqLogin）。
- **一发一收**：`testutil.Call(t, conn, reqMsgId, req)` 一发一收；若服务端先推通知再推响应，用 `testutil.CallExpect(t, conn, reqMsgId, req, expectedMsgId)` 循环收包直到目标 MsgId；响应用 `net.UnmarshalPb(msg.MsgId, msg.Data)` 得到 proto。
- **需 GM 造数**：先 `testutil.GetSessionTokenOptional(t, account)` 两步登录取网关 SessionToken，再 `testutil.GMCommandOptional(sessionToken, ",,additem,itemId,count")`，最后 Dial + Login；GM 失败可继续，依赖道具的 It 内可 Skip。

**Session/登录**：仅 TCP 登录用 `testutil.Login`；需控制台 HTTP 或 GM 时用 `testutil.GetSessionToken`/`GetSessionTokenOptional`。

### 运行命令

- **强制**：集成 BDD 须加 **`-ginkgo.v`**，否则 Ginkgo 不逐条输出 `It` 名称、`ginkgo.Skip` 文案与 `t.Logf`，汇总里只见「N Skipped」难以定位。
- 只跑某一领域：`go test -v -ginkgo.v ./qa/integration/backpack/`
- 跑所有领域：`go test -v -ginkgo.v ./qa/integration/...`
- 部分套件对 `go test -short` 使用 `Expect(testing.Short()).To(BeFalse())`（**直接失败**）或 `ginkgo.Skip`（**显式跳过**）；以各领域 `*_test.go` 为准；无环境时勿假定「-short 一定跳过全部 TCP」

## 测试执行流程

1. **启动登录服与网关**（及涉及 GM 时的 game 服）：见「服务器启动」（默认 HTTP 20002、TCP 20000、控制台 20001）
2. **可选配置**：复制 `qa/integration/testutil/test_config.yaml.example` 为 `test_config.yaml` 并按本机环境修改；或设环境变量 `GATEWAY_TCP_ADDR`、`LOGIN_SERVER_ADDR`、`GAME_SERVER_CONSOLE_ADDR`、`SERVER_ID`（须与 login.toml 及 game 配置匹配）
3. **运行测试**：
   - 单领域：`go test -v -ginkgo.v ./qa/integration/{domain}/`
   - 全量：`go test -v -ginkgo.v ./qa/integration/...`
   - 无真实环境：部分领域可用 `go test -short ...`（行为因套件而异）；**仍建议加 `-ginkgo.v`** 便于看清跳过/失败原因

编写新用例时：确定领域后读取 `qa/api/{domain}.yaml` 获取接口定义，在 `qa/integration/{domain}/` 下编写 BDD 代码（Describe/It + Expect），使用 testutil 完成连接、登录及可选 GM。

## 如何读取API文档

⚠️ **重要规则**：**必须从`qa/api/{domain}.yaml`读取接口信息，禁止编造！**

**执行步骤**：
1. 确定要测试的领域（如`account`、`skill`、`backpack`）
2. **必须读取API文档**：`qa/api/{domain}.yaml`
3. 从API文档中查找接口定义：
   - 在`paths`部分查找接口路径（如`/api/MsgCtrReqLogin`）
   - 在`components/schemas`部分查找请求和响应的数据结构
4. **禁止**：不要编造接口路径、参数或返回值，必须严格按照API文档中的定义

## 接口路径规则

**格式**：`POST {{gameServerConsoleAddr}}/api/{MessageName}`

**重要规则**：
- 路径必须使用**完整的消息名称**（如`MsgCtrReqLogin`），而不是简化名称（如`login`）
- 所有接口都使用`POST`方法
- 接口地址：`{{gameServerConsoleAddr}}/api/{MessageName}`

**示例**：
- ✅ 正确：`POST {{gameServerConsoleAddr}}/api/MsgCtrReqLogin`
- ❌ 错误：`POST {{gameServerConsoleAddr}}/api/login`

## Session Token获取

**integration 中**：由 `testutil.Login(t, conn, account)` 完成（HTTP 取 token，再 TCP 发 MsgCtrReqLogin）。

**手工验证时**：
1. 调用登录服 `GET {LOGIN_SERVER_ADDR}/login?channel=pc&account=xxx` 获取 session
2. 调用网关 `POST {{gameServerConsoleAddr}}/api/MsgCtrReqLogin`，Header `Session-Token: {session}`
3. 从响应中提取 `SessionToken`，后续接口 Header 使用 `Session-Token: {SessionToken}`

## 接口依赖关系

### 基础依赖（必须先执行）

1. **登录接口** (`MsgCtrReqLogin`) - 所有接口的基础，获取SessionToken和PlayerGuid
2. **创建角色接口** (`MsgCtrReqCreateRole`) - 获取PlayerRoleId，大部分业务接口都需要

### 业务依赖

- **技能相关接口**：需要PlayerRoleId（从创建角色接口获取）
- **背包相关接口**：需要PlayerRoleId（从创建角色接口获取）
- **玩家相关接口**：需要PlayerGuid（从登录接口获取）或PlayerRoleId（从创建角色接口获取）

## 数据流转

**关键数据字段**：
- `SessionToken` - 从登录接口响应中提取，用于后续所有接口的Header
- `PlayerGuid` - 从登录接口响应中提取，用于玩家相关接口
- `PlayerRoleId` - 从创建角色接口响应中提取，用于角色相关接口

**数据流转示例**：
```
登录接口响应
  └─> SessionToken: "abc123"
      └─> 传递给后续所有接口的Header: Session-Token: abc123

登录接口响应
  └─> PlayerGuid: 88888
      └─> 传递给玩家相关接口

创建角色接口响应
  └─> PlayerRoleId: 99999
      └─> 传递给技能、背包等角色相关接口
```

## 验证规则

**响应验证**：
- `Ret`字段为`0`表示成功，其他值表示失败
- 检查响应中的业务字段是否符合预期
- 检查数据一致性（如PlayerRoleId是否正确传递）

## 常见问题

### Q: 如何运行集成测试？

A: 先启动登录服与网关，再执行 `go test -v ./qa/integration/backpack/` 或 `go test -v ./qa/integration/...`。无环境时加 `-short` 跳过需服务器的用例。

### Q: 如何查找接口定义？

A: 
1. 确定要测试的领域（如`account`、`skill`）
2. 读取`qa/api/{domain}.yaml`文件
3. 在`paths`部分查找接口路径
4. 在`components/schemas`部分查找请求和响应结构

### Q: 接口路径格式是什么？

A: 必须使用完整消息名称，格式为`POST /api/{MessageName}`，例如`POST /api/MsgCtrReqLogin`。

### Q: 如何获取Session Token？

A: integration 中由 testutil.Login 自动完成（HTTP 取 token + TCP 登录）。手工验证时：先 GET /login 取 token，再 POST /api/MsgCtrReqLogin 带 Session-Token。

### Q: 如何选择启动脚本？

A: 根据当前开发环境动态选择启动脚本：
1. 检查环境变量`GAME_INSTANCE`（如`game_zlf`、`game_xuhai`）
2. 或查看用户规则中的"开发环境"字段（如`zlf`、`xuhai`）
3. 根据环境选择对应的启动脚本：`deploy/start_{环境名}.sh`
4. 示例：zlf环境使用`deploy/start_zlf.sh game`，xuhai环境使用`deploy/start_xuhai.sh game`

### Q: 自测时不想连真实战斗服怎么办？

A: 使用上述区服 `start_*.sh` 时默认已开 Mock；未走这些脚本时可手动 `export OVERRIDE_BATTLE_MOCK_MODE=true` 等。battle-proxy 侧可选 `OVERRIDE_BATTLE_PROXY_*`，见 `common/config/env_overrides.go`。

### Q: 区服启动脚本怎么关 Mock（连真实战斗服）？

A: 除 **`start_stable.sh` 默认关 Mock** 外，其余区服脚本多为默认开 Mock；关 Mock 时启动前 `export OVERRIDE_BATTLE_MOCK_MODE=false` 再执行对应脚本即可。

### Q: 测试失败怎么办？

A: 
1. 检查响应中的`Ret`字段，查看错误码
2. 检查请求参数是否正确
3. 检查前置条件是否满足（SessionToken是否有效、PlayerRoleId是否存在等）
4. 确认登录服与网关已启动（integration 测试）
5. 查看服务器日志（如果可用）

## 最佳实践

1. **必须从API文档读取**：所有接口信息必须从`qa/api/{domain}.yaml`读取，禁止编造
2. **使用完整消息名称**：接口路径必须使用完整的消息名称（如`MsgCtrReqLogin`）
3. **优先运行 integration**：可执行用例以 `qa/integration/` 为准，用 `go test` 运行
4. **先获取Session**：执行测试前先完成登录（integration 中 BeforeEach 内 Login）
5. **验证响应与数据**：每个接口调用后验证 `Ret`，并断言**关键业务字段**（类型与值、列表内容、推送、必要时全量查询/Redis），**禁止**仅判断收到包
6. **每协议多场景**：每个 `MsgCtrReq*` 尽量覆盖 **2～5 条**用例（与测试用例文档一致）
7. **数据流转清晰**：明确说明数据如何从上一个接口传递到下一个接口
8. **汇报带 JSON**：验收或总结时产出 `qa/test_reports/` 下汇总与详细 JSON，与 `go test` 输出交叉核对

## 相关文档

- **短规则（IDE）**: `.cursor/rules/testing.mdc`
- **测试用例 Markdown 命令**: `.cursor/commands/test-case.md`
- **JSON 报告格式**: `qa/test_reports/README.md`
- **QA 工作主文档**: `qa/README.md`
- **API 说明**: `qa/api/README.md`
- **GM 造数**: `.cursor/skills/gm-command/SKILL.md`
- **部署与测试**: `.cursor/rules/deployment-testing.mdc`
