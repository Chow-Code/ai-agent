---
name: gm-command
description: GM 指令调用方式、已注册指令列表与参数；开发与接口测试造数时使用
---

# GM 指令（Skill）

详细列表在此；规则层仅保留摘要见 `.cursor/rules/gm.mdc`。

## 调用

- **POST** `{{gameServerConsoleAddr}}/api/command`
- **Header**：`Session-Token`（必需）、`Content-Type: application/json`
- **Body**：`{ "Command": ",,命令名,参数1,参数2,..." }`（命令以 `,,` 开头）

## 查找新指令

目录：`srv/game/handler/gm_command/`；`*_command.go` → `GetCommandName()` → `RegisterStrategy()`。

## 已注册指令（以代码为准，表为常见集合）

| 指令 | 说明 | 参数 |
|------|------|------|
| addpet | 一键激活宠物（不扣激活道具，等同正式激活数据） | petId |
| additem | 添加道具 | itemId, count |
| additemtotemp | 临时背包 | itemId, count |
| clearbackpack | 清空背包 | 无 |
| addcurrency | 货币 | currencyType, amount |
| drop | 掉落 | dropID, [monsterID], [mapID] |
| getplayerroles | 所有角色 | 无 |
| setmainrole | 主控角色 | roleId |
| setrolesessiontimes | 写入 **账号** `LastLoginUnix` / `LastOfflineUnix`（`MsgDataPlayerStorage`，BDD 造数；G-挂机 OfflinePopup 读此字段；**不再写** `MsgDataRoleStorage`） | `lastLoginUnix,lastOfflineUnix`（玩家须有角色，取第一个做参数占位/校验）或 `roleId,lastLoginUnix,lastOfflineUnix`（`roleId>0` 且须属于当前玩家，仅校验） |
| mockplayerofflineseconds | 相对秒模拟离线：仅 **玩家账号**（`LastLoginUnix=now`，`LastOfflineUnix=now-D`） | `D`（秒） |
| setrolelevel | 角色等级 | roleId, level |
| addroleattr | 加属性 | roleId, attrModelType, attrType, calculateType, value |
| getroleattr | 查属性 | roleId |
| getpetattr | 查指定宠物本地属性树（JsonData：`petId`+`treeStructure`+`totalAttributes`） | petId |
| getglobalattr | 查玩家全局属性树（JsonData：`playerID`+`treeStructure`+`totalAttributes`） | 无 |
| mockmonsterdeath | 模拟怪死亡 | mapId, mapKeyInBtl, siteId… |
| mockmonstergroupdeath | 怪组死亡 | mapId, mapKeyInBtl, groupId |
| mockmapstepfinish | 阶段结算 | mapId, mapKeyInBtl, mapStep |
| mockmapfinish | 地图结束 | mapId, mapKeyInBtl, isSuccess |
| getdungeonprogress | 副本进度 | dungeonId |
| getplayermapentries | 当前进图列表 | 无（返回 mapId、mapType、index、mapKeyInBattle，供 mockmapfinish 等使用） |
| resetminingbdd | 重置当前角色采矿数据（会话/今日次数/铁镐与锻造），供矿场 BDD 稳定跑全量 | 无 |
| resetminingcount | 仅恢复矿场每日次数（挖矿/购买/掠夺/协助清零），不改会话、分组、铁镐、锻造 | 无 |
| addminingexp | 增加累计采矿获得（`TotalReward`），与领取奖励时 `AddTotalReward`+`CheckLevelUp` 一致，不发道具 | amount（正整数） |
| miningprimecrossday | 矿场 BDD：将 LastResetDate 置为昨日并耗尽当日免费挖矿次数，用于验证 Enter 等路径触发惰性跨日重置 | 无 |
| spawnminingaihelp | 立即执行一次协助列表 AI 投放（与定时任务同一路径）；模板须为 **战力榜在线真人** 且能生成 `MirrorPlayerPayload`，否则不投放；返回文案含实际投放条数或未投放原因 | 无 |
| spawnminingairob | 立即执行一次掠夺列表 AI 投放（与定时任务同一路径）；模板须为 **战力榜在线真人** 且能生成 `MirrorPlayerPayload`，否则不投放；返回文案含实际投放条数或未投放原因 | 无 |
| setminingsessionstatus | 设置当前挖矿会话 `EMsgMiningSessionStatus`（0=None,1=InProgress,2=Completed,3=Claimed）；设为 2 时会将 `EndTime` 置为过去，便于 `MsgCtrReqMiningClaim` 测试 | status（0-3） |
| seedminingrevengesettle | 矿场 BDD 造数：夺回 mapKey 索引 | mapKeyInBtl |
| seedmininghelpsettle | 矿场 BDD 造数：协助 mapKey 索引 | mapKeyInBtl |
| pushstoreself | 向当前玩家推送 MsgCtrNtfStoreDataChange（商城全量快照） | 无 |
| pushstoreall | 向所有在线玩家推送 MsgCtrNtfStoreDataChange（配置热更/运维同步） | 无 |
| jixiongbossresetdaily | 缉凶BOSS：将 LastResetTime 回拨为 now-86400 并落库；每日重置由下次 Open/Challenge/结算等业务触发 CheckAndResetDaily | 无 |
| jixiongbosssetgroup | 缉凶BOSS：将 PassedGroupId 设为指定分组，清空其它分组进度；该组全部 BOSS 条目 FirstCleared=false、DailyChallengeUsed=0，并清除进行中战斗登记 | groupId（缉凶表 GroupId） |
| leaderboard_seed | （GM-1）排行榜 BDD 造数：**当前玩家**在指定榜单种入指定分数（实时榜走 ZSet+Display；历史榜走 peak），不发奖、不消耗额度、不发推送 | LeaderboardId, Score |
| leaderboard_seed_other | （GM-2）排行榜 BDD 造数：为**指定 MemberId** 种入分数（**注意 INF-2**：history 分支以 caller playerID 为 peak key，无法独立支持「为他人写历史榜」） | LeaderboardId, TargetMemberId, Score |
| leaderboard_set_quota | （GM-3）排行榜 BDD 造数：覆写当前玩家点赞额度（`DailyLikeQuotaTotal/Used`，`used>total` 自动夹紧） | DailyTotal, DailyUsed |
| leaderboard_force_reset | （GM-4）排行榜 BDD 造数：强制跨日重置（`LastDailyResetTime=0`），下次访问触发 `LeaderboardResetService.EnsureDaily` 清空当日额度与已赞 key | 无 |
| leaderboard_set_history_peak | （GM-5）排行榜 BDD 造数：当前玩家在历史榜直接写 peak（不触发 ZSet sync），用于验证 EnsureHistoryPeakSynced 的 peak>SyncedZSetScore（**注意 INF-3**：当前为强制覆盖，与 SR-2.4「历史峰值不回退」语义冲突） | LeaderboardId, Score |
| leaderboard_clear | （GM-6）排行榜 BDD 初始化：清空指定 LeaderboardId 的全部公共数据（ZSet + 所有 Entry Display Hash），不动玩家维度数据 | LeaderboardId |
| leaderboard_full_reset | （GM-7）排行榜 BDD BeforeEach：清空当前玩家所有排行榜相关持久化数据（玩家级 Storage、所有历史榜 peak、所有榜单 ZSet 中该玩家的 memberId） | 无 |
| leaderboard_query_self | （GM-8）排行榜排查辅助：返回当前玩家在指定榜的 rank/score/peak 等字段（JsonData 形式），纯读、不触发 sync | LeaderboardId |

**注意**：不同环境 `deployment-testing` / GM 表里若与代码不一致，以 `gm_command` 下实现为准。

## 测试流程

1. 部署脚本启动 game 等 → 2. 登录拿 Session → 3. 调 `/api/command` → 4. 看 `Result`。
