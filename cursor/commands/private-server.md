---
description: 新增成员私服：创建 deploy 区服入口脚本、更新 login 区服列表、检查 game_id/GAME_INSTANCE 冲突与 Consul 备忘
alwaysApply: false
---

# 新增成员私服（deploy + login）

## 使用方式（用户）

1. 在 Cursor 对话中 **@private-server**（或通过命令面板选择本命令），并附上参数（见下）。
2. Agent 按下方清单**逐项落实**（创建/修改文件、冲突检查），不要只口头说明。

## 用户输入

```text
$ARGUMENTS
```

**参数约定**（空格或换行分隔均可；缺项须向用户确认后再改仓库）：

| 参数 | 必填 | 说明 |
|------|------|------|
| **姓名** | 是 | 显示名，用于脚本文件名与 `login.toml` 的 `Name`（如 `凌佳`） |
| **game_id**（ServerID） | 建议必填 | 与 `login.toml` 的 `ServerID`、网关 Consul **`Meta.gameid`**、脚本内 `game_id` **必须一致** |
| **GAME_INSTANCE** | 可选 | 进程/实例名，须**全局唯一**；未给时可建议 `game_<拼音>` 或 `game_devXX`（与团队约定一致） |

若用户只给姓名，Agent 应先：**在仓库中检索已占用的 `game_id` / `GAME_INSTANCE`**，再给出下一个可用编号或请用户指定。

---

## Agent 执行清单（按顺序）

### 1. 冲突与范围

- 在 `deploy/` 下检索是否已有同名 `*.sh`（如 `deploy/凌佳.sh`）。
- 在 `deploy/*.sh` 与 `srv/login/bin/login.toml` 的 `[[GameServers]]` 中检索 **`ServerID` / `game_id`** 是否已被占用。
- 检索 **`GAME_INSTANCE`** 字符串是否已出现在其他 `deploy/*.sh` 中。

若有冲突：**列出冲突位置**，请用户改名或换号后再继续。

### 2. 创建 `deploy/{姓名}.sh`

- **若仓库存在** `deploy/common-private-server.sh`：采用薄入口（仅 `source env.sh` + 导出 `game_id`、`OVERRIDE_REDIS_DB`、`GAME_INSTANCE` + `source "$SCRIPT_DIR/common-private-server.sh" "$@"`），与现有成员脚本保持一致。
- **若不存在** `common-private-server.sh`：复制现有成员脚本结构（推荐以 `deploy/古雪.sh` 为模板），至少包含：
  - `source "$SCRIPT_DIR/env.sh"`
  - `export game_id`、`export OVERRIDE_REDIS_DB="${OVERRIDE_REDIS_DB:-$game_id}"`、`export GAME_INSTANCE`
  - `export OVERRIDE_BATTLE_PROXY_GAME_IDS`
  - **战斗服地址（必填）**：在 `OVERRIDE_BATTLE_PROXY_GAME_IDS` 与 `exec start-runtime.sh` 之间增加 `## 战斗服地址` 及下列 `export`（默认本机联调 `127.0.0.1`，与 `srv/battle-proxy/bin/battle.toml` 端口语义一致；**勿漏**，否则 game 下发给客户端的 mock 地址与 battle-proxy 可能不一致）：
    - `OVERRIDE_MOCK_BATTLE_ADDR`（默认 `127.0.0.1:6210`）
    - `OVERRIDE_BATTLE_PROXY_BATTLE_ADDR`（默认 `127.0.0.1:6200`）
    - `OVERRIDE_BATTLE_PROXY_CLIENT_ADDR`（默认 `127.0.0.1:6210`）
    - 注释行与成员脚本**逐行一致**（见 `deploy/古雪.sh` 约第 10–14 行）；若某区需指向远程战斗服，仅改上述默认值或通过环境变量覆盖。
  - `exec "$SCRIPT_DIR/start-runtime.sh" "${1:-all}"`
- 脚本需可执行（必要时提醒用户执行 `chmod +x` 或 `deploy/chmod.sh`）。

### 3. 更新 `srv/login/bin/login.toml`

- 在 `[[GameServers]]` 列表中**新增一段**：

```toml
[[GameServers]]
ServerID = <game_id>
Name = "<姓名>"
Port = 20000
```

- 插入位置：按 `ServerID` **数值顺序**插在合适位置（与现有条目风格一致）。
- 若文件顶部注释写有「开发区服 6–N」类说明，将 **N** 更新为当前最大成员 `game_id`（若适用）。

**说明**（可写入对话，不必重复写进 toml）：Consul 中须有 `Meta.gameid = game_id` 的健康 **gateway**，否则客户端拉服列表/选区可能失败（见 `login.toml` 文件头注释）。

### 4. 文档与备忘（与 `deploy/README` 同步）

- **`deploy/README.md`** 的 **「成员区服（中文名脚本）」** 小节须与本命令约定**一致**（模板脚本、战斗服地址、`login.toml`、`@private-server` 入口等）。若本次变更了本命令中的**硬性步骤**（例如必填项、模板文件名），应**同时检查并更新**该 README 小节，避免两处漂移。
- 若仓库日后引入 **`deploy/common-private-server.sh`**，须在本命令第 2 节与 README 中**同步**说明「薄入口 vs 完整脚本」分支。
- 建议在 `docs/plans/` 增加**极简**计划记录本次新增（遵守仓库「有计划再改」习惯时可选用）。

### 5. 验证（轻量）

- 对新建/修改的 `deploy/{姓名}.sh` 执行 **`bash -n`**，确保语法正确。

---

## 禁止与注意

- **不要**臆造未在仓库出现的路径或变量；成员脚本以现有 `deploy/*.sh` 为准。
- **不要**遗漏 `login.toml`：仅加 `deploy` 脚本会导致登录服**不展示该区**（除非团队另有生成链）。
- `game_id` 与 `ServerID`、`Meta.gameid` 不一致会导致**最难排查**的联调问题，改前务必三方对齐。

---

## 相关路径（速查）

- 团队共用环境：`deploy/env.sh`
- 成员脚本模板（含战斗服地址）：`deploy/古雪.sh`
- 启动链：`deploy/start-runtime.sh`
- 登录区服列表：`srv/login/bin/login.toml`
- 部署说明：`deploy/README.md`（**成员区服**须与本命令对齐；stop 前如何 `source` 环境等）
