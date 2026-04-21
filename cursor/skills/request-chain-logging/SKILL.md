---
name: request-chain-logging
description: 检查 srv/game/handler 作为入口的客户端请求，在请求处理的关键节点及业务重要节点（概率参数、奖励计算等）增加或补全 tlog 日志，便于问题分析。在新增/修改 handler、排查请求链路、分析问题时使用。
---

# Handler 请求关键节点日志

以 `srv/game/handler` 为入口的客户端请求，在以下关键节点应具备日志，便于按 traceId/spanId 串联请求链路并定位问题。

## 关键节点定义

| 节点 | 时机 | 日志级别 | 必须包含信息 | 说明 |
|------|------|----------|--------------|------|
| **入口** | HandleXxx 内，`trace.GetOrCreateTraceContext` 之后 | Info | 消息名/Handler 方法名、traceId、spanId；请求关键字段（如 session 脱敏、playerID、msg 类型相关 ID） | 收到请求，便于确认请求是否进入 game、串联全链路 |
| **前置校验失败** | GetPlayerIDFromContext 失败、依赖为 nil 等 | Error / Warn | 原因、traceId/spanId | 便于区分“未到业务”的失败 |
| **调用 AppService 后失败** | `appService.XXX()` 返回 err != nil | Error | 方法名、关键参数（如 playerID）、err | 业务或下游失败 |
| **返回前（成功）** | 正常 return 前 | Info | 一条汇总：Handler 方法名、Ret（若有）、关键结果（如数量、ID） | 满足「每函数一行成功日志」，便于确认成功路径 |

## 业务关键节点（必须打日志）

以下节点涉及概率、奖励、数量等核心业务逻辑，出现问题难以复现，**必须在计算完成时打一条日志**，便于分析「为何得到该结果」。出现位置多为 **Domain 层 / Application 层**，少数在 Handler。

| 类型 | 示例场景 | 必须记录的信息 | 日志级别 |
|------|----------|----------------|----------|
| **概率/随机** | 掉落判定、抽奖、暴击、命中等 | 随机种子/参数、概率值、最终是否命中、traceId/spanId | Info / Debug |
| **奖励数量计算** | 经验、货币、道具数量、倍率加成 | 基础值、加成系数、倍率、最终数量、traceId/spanId | Info |
| **阈值/条件判定** | 是否满足条件、分段奖励、档位判断 | 输入值、阈值、判定结果、traceId/spanId | Info / Debug |
| **分配/拆分** | 多目标分配、按权重分配 | 总量、权重/比例、各目标分配结果、traceId/spanId | Info |

**日志示例**：
```go
// 概率判定后
tlog.LogCommonLogWithContext(ctx, config.GetGameID(), tlog.LogLevelInfo, config.GetServiceName(),
	fmt.Sprintf("[DropService.RollDrop] 掉落判定: dropId=%d, roll=%d, rate=%d, hit=%v, traceId=%s",
		dropId, rollValue, dropRate, hit, traceId))

// 奖励数量计算后
tlog.LogCommonLogWithContext(ctx, config.GetGameID(), tlog.LogLevelInfo, config.GetServiceName(),
	fmt.Sprintf("[RewardService.CalcReward] 奖励计算: base=%d, multiplier=%d, final=%d, traceId=%s",
		baseAmount, multiplier, finalAmount, traceId))
```

**注意**：这些属于「业务关键决策点」，不属于冗余日志；每个此类计算点只打**一条**汇总日志，记录入参与结果即可，避免在循环内重复打同类日志。

## 业务逻辑层日志（Handler 调用的 AppService / Domain）

Handler 调用 AppService 后，业务逻辑在 `srv/game/application/service/`、`domain/` 中执行。**应依据业务情况在逻辑内部补充日志**，便于 AI 串联 Handler → AppService → Domain 的全链路、分析执行路径与结果。

### 必须打日志的调用链节点

| 位置 | 时机 | 必须记录 | 日志级别 |
|------|------|----------|----------|
| **AppService 入口** | 用例方法开始，重要分支前 | 方法名、关键入参（playerID、角色ID、业务ID）、traceId/spanId | Info |
| **AppService 分支** | 条件分支（如是否满足条件、走哪条路径） | 条件值、分支结果、traceId | Info/Debug |
| **调用 Domain 前/后** | 编排中调用领域服务 | 调用的领域方法、关键参数、返回的关键结果 | Info |
| **Domain 关键决策** | 领域内业务规则判定、状态变更 | 入参、判定结果、变更前/后状态 | Info |
| **数据持久化前** | MarkModified、Save 等写入前 | 实体 Key、变更摘要 | Debug |
| **下游调用** | 跨服务调用、仓储读写 | 目标、关键参数、成功/失败 | Info/Error |

### 业务逻辑日志格式

```go
// AppService 用例入口
tlog.LogCommonLogWithContext(ctx, config.GetGameID(), tlog.LogLevelInfo, config.GetServiceName(),
	fmt.Sprintf("[BackpackAppService.GetBackpack] start: playerID=%d, traceId=%s, spanId=%s", playerID, traceId, spanId))

// 分支判定后
tlog.LogCommonLogWithContext(ctx, config.GetGameID(), tlog.LogLevelInfo, config.GetServiceName(),
	fmt.Sprintf("[RoleLevelupAppService.RoleLevelup] 条件判定: playerRoleId=%d, levelCount=%d, 满足条件=%v, traceId=%s", roleId, count, ok, traceId))

// 调用 Domain 后
tlog.LogCommonLogWithContext(ctx, config.GetGameID(), tlog.LogLevelInfo, config.GetServiceName(),
	fmt.Sprintf("[MartialArtsAppService.HandleMartialArtsLearn] 学习完成: roleId=%d, stanceId=%d, martialArtsId=%d, traceId=%s", roleId, stanceId, maId, traceId))
```

### 执行步骤中业务逻辑检查

在「执行步骤」第 3 步后增加：

- **追踪 Handler 调用的 AppService**：对每个 `h.xxxAppService.XXX(ctx, ...)`，进入对应 `application/service/` 方法。
- **逐业务方法检查**：入口是否有关键入参 + traceId 日志；条件分支、调用 Domain、写入数据、下游调用等是否有对应日志。
- **补全**：缺哪补哪，保持 `[AppService名.方法名]` 或 `[Domain服务名.方法名]` 格式，便于 AI 按调用链分析。

## 日志级别选择（必须遵守）

| 级别 | 使用场景 |
|------|----------|
| **Debug** | 调试用、循环/中间步骤、持久化细节 |
| **Info** | 正常业务流程：请求入口、成功返回、关键业务节点 |
| **Warn** | 可恢复异常、非预期但非致命、性能告警 |
| **Error** | 错误/失败：校验失败、调用失败、数据异常 |
| **Fatal** | 致命错误，程序将退出 |

**选择口诀**：正常走 Info，出错走 Error/Warn，调试走 Debug，致命走 Fatal。

## 日志规范（必须遵守）

- **统一接口**：使用 `tlog.LogCommonLogWithContext(ctx, config.GetGameID(), logLevel, config.GetServiceName(), message)`，禁止 `fmt.Println`/标准库 `log`。
- **精简原则**：每个 Handle 方法内，入口一条、错误分支各一条、成功路径一条；不在循环、无关中间步骤打冗余 Info。**业务关键节点**（概率、奖励计算等）除外，每个此类计算点打一条汇总日志。
- **敏感信息**：session、token 等使用 `help.MaskSession` 等脱敏后再写入日志。
- **描述与参数**：**日志描述使用中文**（便于开发人员快速理解），**参数名/key 使用英文**（方便按参数查找）；格式 `[HandlerName.HandleXxx] 简短中文描述: paramName=value, traceId=..., spanId=...`。

## 标准模板（每个 Handle 方法）

```go
func (h *XxxHandler) HandleXxx(ctx context.Context, req *message.MsgCtrReqXxx) (*message.MsgCtrResXxx, error) {
	ctx, traceId, spanId, _ := trace.GetOrCreateTraceContext(ctx)

	// 1. 入口日志（关键请求字段 + traceId/spanId）
	tlog.LogCommonLogWithContext(ctx, config.GetGameID(), tlog.LogLevelInfo, config.GetServiceName(),
		fmt.Sprintf("[XxxHandler.HandleXxx] request: 关键字段..., traceId=%s, spanId=%s", traceId, spanId))

	// 2. 前置校验（若有）
	playerID, err := handlerutil.GetPlayerIDFromContext(ctx)
	if err != nil {
		tlog.LogCommonLogWithContext(ctx, config.GetGameID(), tlog.LogLevelError, config.GetServiceName(),
			fmt.Sprintf("[XxxHandler.HandleXxx] get PlayerID failed: %v", err))
		return nil, err
	}
	// 依赖 nil 检查若失败，同样打 Error 后 return

	// 3. 调用应用服务
	resp, err := h.xxxAppService.DoSomething(ctx, playerID, req)
	if err != nil {
		tlog.LogCommonLogWithContext(ctx, config.GetGameID(), tlog.LogLevelError, config.GetServiceName(),
			fmt.Sprintf("[XxxHandler.HandleXxx] DoSomething failed: playerID=%d, err=%v", playerID, err))
		return nil, err
	}

	// 4. 成功返回前一条汇总日志
	tlog.LogCommonLogWithContext(ctx, config.GetGameID(), tlog.LogLevelInfo, config.GetServiceName(),
		fmt.Sprintf("[XxxHandler.HandleXxx] ok: Ret=%d, 其他关键结果, traceId=%s", resp.Ret, traceId))
	return resp, nil
}
```

## 执行步骤（Agent 使用本 Skill 时）

1. **确定范围**：针对 `srv/game/handler` 下被修改或指定的 handler 文件，及与其关联的 domain/application 逻辑。
2. **逐方法检查 Handler**：对每个 `Handle*` 方法：
   - 入口是否有「请求 + traceId/spanId」的 Info 日志；
   - 前置校验失败、AppService 返回错误是否有 Error/Warn 日志；
   - 成功路径是否在 return 前有一条 Info 汇总。
3. **检查业务关键节点**：在 domain/application 中搜索概率、奖励、数量计算、阈值判定等逻辑，确认是否在计算完成后打了日志（入参 + 结果 + traceId/spanId）。
4. **检查 Handler 调用的业务逻辑**：沿 Handler → AppService → Domain 调用链，在 application/service、domain 中检查：用例入口、条件分支、Domain 调用、数据写入、下游调用等是否有对应日志。
5. **补全或新增**：缺哪补哪，不增加冗余；业务关键节点每个计算点只打一条汇总日志，不在循环内重复；业务逻辑层使用 `[AppService名.方法名]` 格式便于 AI 串联。
5. **符合项目规范**：遵守 `code-quality.mdc` 中「日志使用规范」「日志精简原则」，不破坏现有错误日志。

## 检查清单

- [ ] 每个 Handle 方法入口有一条带 traceId/spanId 的请求日志
- [ ] 所有错误分支（GetPlayerID 失败、依赖 nil、AppService 返回 err）有对应 Error/Warn 日志
- [ ] 成功路径在 return 前有一条 Info 汇总（含 Ret 或关键结果）
- [ ] 概率/随机判定（掉落、抽奖、暴击等）在计算完成后有日志（入参、结果、traceId）
- [ ] 奖励数量计算在完成后有日志（基础值、倍率、最终数量、traceId）
- [ ] Handler 调用的 AppService/Domain 在用例入口、分支、Domain 调用、写入、下游调用等有对应日志
- [ ] 业务逻辑日志使用 `[AppService名.方法名]` 或 `[Domain服务名.方法名]` 格式，便于 AI 串联调用链
- [ ] 仅使用 tlog，未使用 fmt/标准 log；敏感信息已脱敏
- [ ] 未在循环或无关中间步骤增加冗余 Info，业务关键节点除外
