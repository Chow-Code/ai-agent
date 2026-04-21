---
name: sync-client-config
description: 同步客户端配置（策划表）。当用户说「同步客户端配置」「使用 Excel 同步」「使用 csv 生成配置」时使用。从 Excel 或 CSV 生成 .bytes、.go、.csv。上传到 Consul 的 config-sync 链路已废弃，勿再作为推荐步骤。
---

# 客户端配置同步 Skill（非 config-sync 工具）

## 使用场景

- 用户说「同步客户端配置」「同步所有的配置」「使用 Excel 同步」→ 从 Excel 生成全部配置
- 用户说「使用 csv 生成配置」→ 从 CSV 生成配置（可指定表或全部）
- **完整「表定义」含列设计、类型与表头四行**时，优先按 [`.cursor/skills/config-csv-table/SKILL.md`](../config-csv-table/SKILL.md) 核对 [`schema.go`](../../../tools/sync-client-config/excelgen/schema.go)，避免只跑 excelgen 同步却未校验列类型与跳过规则

## 流程说明

### 场景一：同步客户端配置（使用 Excel）

**数据源**：仓库内 `excel/excel`（xlsx）、`excel/createtype`（CreateType `.txt`）  
**输出**：`.bytes` → `srv/game/bin/`（与 game 服务 `configDir/bin` 加载路径一致），`.go` → `excel/code`，`.csv` → `excel/csv`

**执行**（在 TL3Server 项目根目录）：

```bash
go run ./tools/sync-client-config/cmd/excelgen
```

**可选**：

- 遇无效行停止：`go run ./tools/sync-client-config/cmd/excelgen -skip-invalid-rows`
- 自定义路径：`-xlsx-dir`、`-createtype-dir`（旧客户端布局可将 `-createtype-dir` 指向 `.../Excel/CreateType`）

**与配置中心**：不再通过自动化流程上传 Consul。Excel/CSV 生成产物请按工具输出路径落盘，并**直接维护** `srv/<服务>/bin`（或执行 `deploy/build.sh` 将 `srv/*/bin` 打进 `deploy/dist`）。若仍需旧版上传，可**手动**运行 `tools/config-sync` 或 `deploy/functions/sync_config.sh`（代码保留，无 Cursor Skill）。

### 场景二：使用 CSV 生成配置

**数据源**：`excel/csv`  
**输出**：`.bytes`、`.go`（不写 csv）

**执行**（在 TL3Server 项目根目录）：

```bash
# 同步所有 CSV 表
go run ./tools/sync-client-config/cmd/excelgen -mode=from-csv

# 指定表（逗号分隔，表名按实际）
go run ./tools/sync-client-config/cmd/excelgen -mode=from-csv -tables=YourTable,AnotherTable
```

**前置**：需先执行一次 from-xlsx 生成 CSV 及 CreateType 缓存。

## 命令行参数速查

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `-mode` | `from-xlsx` | `from-xlsx` 或 `from-csv` |
| `-xlsx-dir` | `excel/excel` | xlsx 所在目录 |
| `-createtype-dir` | `excel/createtype` | CreateType `*.txt` 所在目录 |
| `-tables` | 空 | 指定表名，逗号分隔；空则处理全部 |
| `-skip-invalid-rows` | `false` | 遇无效行即停止写入 |

## 快速入口

- **VSCode 调试**：运行「同步客户端所有 Excel」配置（launch.json）可一键执行 from-xlsx 全量同步

## 相关技能

- **根据策划案建配置表、维护 `excel/csv` 形态与列类型**：见 [`.cursor/skills/config-csv-table/SKILL.md`](../config-csv-table/SKILL.md)。用户说「**定义表**」「**建表**」「**配表**」「**新表**」时，**权威交付物是 `excel/csv` 中的表文件**（及 excelgen 生成的 `excel/code`、`srv/game/bin`），不要只写 developdoc 而不落 CSV；列设计与 `ParseType` 合法性以 **config-csv-table** 为准，勿仅执行本 Skill 的同步命令。
