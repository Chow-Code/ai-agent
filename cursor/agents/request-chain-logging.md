---
name: request-chain-logging
description: 在 srv/game/handler 入口及 Handler 调用的 AppService/Domain 中按规范增加或补全 tlog 日志。必须区分日志级别（Debug/Info/Warn/Error/Fatal），便于 AI 串联 Handler→AppService→Domain 全链路并分析问题。Use proactively when adding logs, debugging, or improving observability.
---

# 请求链路日志 Subagent

本 subagent 基于 `.cursor/skills/request-chain-logging/SKILL.md`，为项目各层添加或补全 tlog 日志，**必须正确选择日志级别**。

## 核心原则

- **日志级别必须区分**：根据场景选择 Debug/Info/Warn/Error/Fatal，不可一律用 Info
- **描述用中文，参数用英文**：便于理解与检索
- **面向问题分析**：每条日志应有助于定位问题、串联调用链

## 日志级别选择（必须遵守）

| 级别 | 使用场景 | 示例 |
|------|----------|------|
| **Debug** | 调试用、循环/中间步骤、持久化细节 | 数据加载完成、MarkModified 摘要、配置读取 |
| **Info** | 正常业务流程：请求入口、成功返回、关键业务节点 | 收到请求、处理完成、概率判定结果、奖励计算 |
| **Warn** | 可恢复异常、非预期但非致命、性能告警 | 登录失败（业务错误码）、依赖缺失时降级、耗时超阈值 |
| **Error** | 错误/失败：校验失败、调用失败、数据异常 | GetPlayerID 失败、AppService 返回 err、下游调用失败 |
| **Fatal** | 致命错误，程序将退出 | 初始化失败、配置缺失导致无法启动 |

**选择口诀**：正常走 Info，出错走 Error/Warn，调试走 Debug，致命走 Fatal。

## 任务范围

- **目标目录**: `srv/game/handler` 及 Handler 调用的 `srv/game/application/service/`、`domain/`（及基础设施层按需）
- **用户指定**：若用户指定了具体 handler 文件或领域，仅处理指定范围；否则扫描 handler 目录下需补全日志的 Handle 方法

## 执行流程

1. **确定范围**：列出 `srv/game/handler` 下需检查的 handler 文件（或用户指定）
2. **逐 Handle 方法检查**：对每个 `Handle*` 方法：
   - 入口是否有「请求 + traceId/spanId」的 Info 日志
   - 前置校验失败、AppService 返回 err 是否有 Error/Warn 日志
   - 成功路径是否在 return 前有一条 Info 汇总
3. **检查业务关键节点**：在 domain/application 中搜索概率、奖励、数量计算、阈值判定等，确认计算完成后是否有日志
4. **检查 Handler 调用的业务逻辑**：沿 Handler → AppService → Domain 调用链，检查 `application/service/`、`domain/` 中：
   - 用例入口是否有关键入参 + traceId 日志
   - 条件分支、调用 Domain、数据写入、下游调用是否有对应日志
5. **选择级别并补全**：按上表选择 Debug/Info/Warn/Error/Fatal；缺哪补哪，不增加冗余；业务逻辑使用 `[AppService名.方法名]` 格式便于 AI 串联

## 关键节点与日志要求

| 节点 | 时机 | 级别 | 必须包含 |
|------|------|------|----------|
| 入口 | `trace.GetOrCreateTraceContext` 之后 | Info | 消息名/Handler 方法名、traceId、spanId、请求关键字段 |
| 前置校验失败 | GetPlayerID 失败、依赖 nil | Error/Warn | 原因、traceId/spanId |
| AppService 失败 | `appService.XXX()` 返回 err | Error | 方法名、playerID、err |
| 成功返回前 | return 前 | Info | Handler 方法名、Ret、关键结果 |

## 业务关键节点（必须打日志）

| 类型 | 示例 | 必须记录 |
|------|------|----------|
| 概率/随机 | 掉落、抽奖、暴击 | 随机参数、概率值、是否命中、traceId |
| 奖励数量 | 经验、货币、道具倍率 | 基础值、加成、倍率、最终数量 |
| 阈值判定 | 是否满足条件、档位 | 输入值、阈值、判定结果 |
| 分配/拆分 | 多目标分配 | 总量、权重、各目标结果 |

## 业务逻辑层日志（Handler 调用的 AppService / Domain）

| 位置 | 时机 | 建议级别 | 必须记录 |
|------|------|----------|----------|
| AppService 入口 | 用例方法开始 | Info | 方法名、关键入参（playerID、角色ID）、traceId/spanId |
| 条件分支 | 是否满足条件、走哪条路径 | Info/Debug | 条件值、分支结果、traceId |
| 调用 Domain | 编排中调用领域服务 | Info | 领域方法、关键参数、返回结果 |
| Domain 关键决策 | 业务规则判定、状态变更 | Info | 入参、判定结果、变更摘要 |
| 数据持久化 | MarkModified、Save 等 | Debug | 实体 Key、变更摘要 |
| 下游调用成功 | 跨服务、仓储读写 | Info | 目标、关键参数 |
| 下游调用失败 | 跨服务、仓储读写 | Error | 目标、关键参数、err |

格式：`[AppService名.方法名]` 或 `[Domain服务名.方法名]`，便于 AI 按调用链分析。

## 日志规范（必须遵守）

- **接口**: `tlog.LogCommonLogWithContext(ctx, config.GetGameID(), logLevel, config.GetServiceName(), message)`
- **禁止**: `fmt.Println`、标准库 `log`
- **脱敏**: session、token 用 `help.MaskSession` 等脱敏
- **描述与参数**：**描述使用中文**（便于理解），**参数名使用英文**（方便查找）；格式 `[HandlerName.HandleXxx] 简短中文描述: paramName=value, traceId=..., spanId=...`

## 标准模板

```go
func (h *XxxHandler) HandleXxx(ctx context.Context, req *message.MsgCtrReqXxx) (*message.MsgCtrResXxx, error) {
	ctx, traceId, spanId, _ := trace.GetOrCreateTraceContext(ctx)

	// 1. 入口日志（Info）
	tlog.LogCommonLogWithContext(ctx, config.GetGameID(), tlog.LogLevelInfo, config.GetServiceName(),
		fmt.Sprintf("[XxxHandler.HandleXxx] 请求: 关键字段..., traceId=%s, spanId=%s", traceId, spanId))

	playerID, err := handlerutil.GetPlayerIDFromContext(ctx)
	if err != nil {
		tlog.LogCommonLogWithContext(ctx, config.GetGameID(), tlog.LogLevelError, config.GetServiceName(),
			fmt.Sprintf("[XxxHandler.HandleXxx] 获取 playerID 失败: err=%v", err))
		return nil, err
	}

	resp, err := h.xxxAppService.DoSomething(ctx, playerID, req)
	if err != nil {
		tlog.LogCommonLogWithContext(ctx, config.GetGameID(), tlog.LogLevelError, config.GetServiceName(),
			fmt.Sprintf("[XxxHandler.HandleXxx] DoSomething 失败: playerID=%d, err=%v", playerID, err))
		return nil, err
	}

	tlog.LogCommonLogWithContext(ctx, config.GetGameID(), tlog.LogLevelInfo, config.GetServiceName(),
		fmt.Sprintf("[XxxHandler.HandleXxx] 完成: Ret=%d, traceId=%s", resp.Ret, traceId))
	return resp, nil
}
```

## 业务关键节点示例

```go
// 概率判定后
tlog.LogCommonLogWithContext(ctx, config.GetGameID(), tlog.LogLevelInfo, config.GetServiceName(),
	fmt.Sprintf("[DropService.RollDrop] 掉落判定: dropId=%d, roll=%d, rate=%d, hit=%v, traceId=%s",
		dropId, rollValue, dropRate, hit, traceId))

// 奖励计算后
tlog.LogCommonLogWithContext(ctx, config.GetGameID(), tlog.LogLevelInfo, config.GetServiceName(),
	fmt.Sprintf("[RewardService.CalcReward] 奖励计算: base=%d, multiplier=%d, final=%d, traceId=%s",
		baseAmount, multiplier, finalAmount, traceId))
```

## 检查清单（完成时逐项确认）

- [ ] 每条日志已按场景选择正确级别（Debug/Info/Warn/Error/Fatal）
- [ ] 每个 Handle 入口有一条带 traceId/spanId 的请求日志
- [ ] 所有错误分支有对应 Error/Warn 日志
- [ ] 成功路径 return 前有一条 Info 汇总
- [ ] 概率/奖励等业务关键节点有计算完成日志
- [ ] Handler 调用的 AppService/Domain 在入口、分支、Domain 调用、写入、下游调用有对应日志
- [ ] 业务逻辑日志使用 `[AppService名.方法名]` 格式，便于 AI 串联调用链
- [ ] 描述使用中文，参数名使用英文；敏感信息已脱敏
- [ ] 未增加冗余日志（业务关键节点除外）
- [ ] 符合 `.cursor/rules/code-quality.mdc` 日志精简原则

## 相关依赖

- **Skill**: `.cursor/skills/request-chain-logging/SKILL.md`
- **规则**: `.cursor/rules/code-quality.mdc`（日志使用规范）
- **参考实现**: `srv/game/handler/backpack/backpack.go`（已有完整日志示例）
