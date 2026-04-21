---
name: deploy-tool
description: 当需要编译打包、重启服务器、查看日志、查看状态、停止服务器时使用。修改代码后测试须按「编译 + 区服启动」规则执行；区服入口为 start_XXX.sh，底层为 start-runtime.sh → start.sh。
---

# 部署工具 Skill

## 工具概述

`deploy/` 下脚本负责：**编译并打 dist**、**按区服启动（从 dist）**、**停服**、**状态/日志**。区服差异写在各 `start_XXX.sh` 内（`game_id`、`OVERRIDE_*`、`GAME_INSTANCE` 等），不再使用已删除的 `deploy/env/` 模板文件。

## 核心规则（编译与启动）

### 编译（build）

- 在仓库根下：`cd deploy && ./build.sh`
- **作用**：编译各 `srv/*` 服务，并打包到 `deploy/dist/<linux-amd64|windows-amd64>/<服务>/`（可执行文件 + `bin/`，含 yaml/toml/bytes 等）。
- **常用环境变量**（见 `build.sh` / `functions/pack_dist.sh`）：
  - `ENABLE_DIST_PACK=false` — 只编译、不打 dist
  - `ENABLE_CROSS_DIST=false` — 不交叉编译另一平台
  - `DIST_PACK_PLATFORMS=windows|linux|all` — 控制打哪些平台（可与 `./build.sh [windows|linux|all]` 一致）
- **验收**：对应平台目录下同时有二进制与 `bin/`。

### 启动（区服入口 → 运行时）

- **日常推荐**：`cd deploy` 后执行 **`./start_<区服>.sh [game|login|all]`**  
  例如：`./start_zlf.sh all`、`./start_pf.sh game`、`./start_xuhai.sh game`
- **调用链**：`start_XXX.sh` 内 `export` 区服默认环境 → **`start-runtime.sh`**（默认 `DEPLOY_USE_DIST=true`、`ENABLE_BUILD=false`）→ **`start.sh`**（停服、清日志、再拉起进程）。**Consul 默认不检查/不自动启动**（`ENABLE_CONSUL_CHECK` 默认 `false`）；连远程注册中心时自行保证 `OVERRIDE_REGISTRY_ADDRS`；本机 Consul 请单独 `start_consul.sh`。
- **含义**：
  - **不单独再跑编译**；须**先** `./build.sh` 保证 `deploy/dist` 与代码一致。
  - 覆盖某变量：启动前在同一 shell 里 `export game_id=...` 等（白名单见 `common/config/env_overrides.go`）。
- **区服脚本默认示例**（脚本内可改，以各文件为准）：
  - `start_zlf.sh`：`game_id=2`、`OVERRIDE_REDIS_DB=10`、`GAME_INSTANCE=game_zlf`
  - `start_pf.sh`（鹏飞唯一入口）：`game_id=3`、`OVERRIDE_REDIS_DB=2`、`GAME_INSTANCE=game_pf`
  - `start_stable.sh`：`game_id=1`、`OVERRIDE_REDIS_DB=0`、`GAME_INSTANCE=game_stable`
  - `start_xuhai.sh` / `start_222.sh` / `start_223.sh`：见脚本内 export；成员区服为 `deploy` 根目录各中文名 `.sh`

### 完整流水线（开发改代码后要「编译 + 启」）

1. `cd deploy && ./build.sh`
2. `./start_<区服>.sh all`（或 `game` / `login`）

若需 **停服 → 编译 → 启动** 单命令：可对 **`./start.sh`** 设 `ENABLE_BUILD=true`（默认即编译），第一个参数为服务名：`game`、`login`、`waypoint`、`gateway`、`battle-proxy`、`social`、`all`（见 `start.sh` 顶部注释）。区服变量仍需先 `export` 或走 `start_XXX.sh`。

### 停止

- `./stop.sh [game|login|waypoint|gateway|battle-proxy|social|all]`  
  无「xuhai」等区服名参数；实例相关依赖当前环境里的 `GAME_INSTANCE` 等。

### 管理（不编译）

- `./start_server.sh status`
- `./start_server.sh logs game`
- `./start_server.sh stop game` / `restart game`

（命令格式：`start_server.sh <子命令> [服务名]`，**不要**再写 `xuhai` 前缀。）

## 使用场景

- 改代码后：先 **`build.sh`**，再用 **`start_XXX.sh`** 启服验证
- 查状态、日志、停服
- 只编译：`./build.sh`
- 手动上传 Consul KV（仍保留，但不在流水线里自动跑）：`./functions/sync_config.sh`

## 前置条件

- 在 **`deploy`** 目录执行上述脚本（路径以项目根为准）
- `.sh` 需 Bash 环境（Windows 用 **Git Bash** 或 **WSL**）
- `chmod +x` 可用 `./chmod.sh`
- **启动参数**：仅 `-config bin` 及需实例的服务 `-instance`（与 `common/config/center/flag_params.go` 一致）；不向进程传 `-config-center-*` / `-config-version` / `-config-service-dir` 等。配置以 `srv/<服务>/bin` 或 `deploy/dist/.../bin` 为准；需上传 KV 时手动 `functions/sync_config.sh`

## 常用命令示例

```bash
cd deploy

./build.sh
./start_zlf.sh all

./start_server.sh status
./start_server.sh logs game

./stop.sh all
```

## 其它脚本

| 路径 | 说明 |
|------|------|
| `functions/pack_dist.sh` | 由 `build.sh` 引用，打 dist |
| `functions/start_*.sh` | 被 `start.sh`、`compose/*` 调用，单服务启动 |
| `functions/generate_proto.sh` / `generate_handler.sh` | 代码生成 |
| `functions/sync_config.sh` / `sync_excel.sh` | 手动同步 |
| `compose/start_all_basic.sh`、`start_core.sh` | 多服务组合启动 |

## 日志

- 各服务 `logs/`；从 dist 跑时日志位置与 `common.sh` 中 `DEPLOY_USE_DIST` 逻辑一致

## 相关文档

- `deploy/README.md` — 权威说明
- `common/config/env_overrides.go` — 可注入环境变量白名单
- `tools/config-sync/DEPRECATED.md` — 配置同步工具状态
