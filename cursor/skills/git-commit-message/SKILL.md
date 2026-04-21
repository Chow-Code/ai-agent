---
name: git-commit-message
description: 编写 Git 提交说明时使用；约定 type(scope) 与中文描述，并从当前分支推断 scope。当用户说「帮我提交代码 / 帮我 commit / 提交一下」等表述时，按本 Skill 的「帮我提交代码 工作流」自检已暂存改动 → 生成描述 → 用户确认 → 执行提交
---

# Git 提交信息（Skill）

在生成或润色 **commit message** 时遵循本约定。完整格式：

```text
<type>(<scope>): <description>
```

- **`<type>`**：变更性质，见下表（与 Conventional Commits 对齐，类型表以团队规范为准）。
- **`<scope>`**：**功能域 / 模块简称**，优先由**当前 Git 分支名**解析得到（见「从分支解析 scope」）；无法可靠解析时由执行者根据本次 diff 指定，或使用 `misc`。
- **`<description>`**：**中文**一句话说明「做了什么」，避免模糊词（如「修改了一些东西」）；可带必要上下文，句末一般不加句号。

## 示例

```text
refactor(pet): 更新宠物上阵与下阵响应结构
feat(afk): 挂机结算增加离线收益上限校验
fix(backpack): 修复堆叠道具合并后数量未持久化
```

## 类型 `<type>`（必选其一）

| 类型 | 类别 | 说明 |
|------|------|------|
| `feat` | Production | 新增功能 |
| `fix` | Production | Bug 修复 |
| `perf` | Production | 性能优化 |
| `style` | Development | 代码格式类变更（如 gofmt、仅删空行等），**不改变业务语义** |
| `refactor` | Production | 其余代码类变更且**非** feat/fix/perf/style（如简化结构、重命名、删冗余），**不改变对外约定行为时**优先用 refactor |
| `test` | Development | 新增或更新测试用例 |
| `ci` | Development | CI/CD 相关（Jenkins、GitLab CI、systemd unit 等） |
| `docs` | Development | 文档（用户文档、开发文档、README 等） |
| `chore` | Development | 构建流程、依赖管理、辅助工具等**未落入上述类型**的杂项 |

**区分要点**：

- 分支名里的 `feature` / `fix` 等**只表示分支用途**，**不等于** commit 的 `type`；**每次提交**的 `type` 由**本次改动的实际性质**决定（同一 `feature_xxx` 分支里可以有 `fix`、`docs`、`test` 等提交）。
- 若一次提交混合多类改动，**拆 commit**；必须合并时取**主因**对应类型，并在描述中点出次要变更。

## 范围 `<scope>`：从分支名解析

### 目标

将分支名中的**功能域**映射为小写 **scope**，例如：

- `feature_zlf_pet` → `pet`
- `feature_afk` → `afk`

### 推荐算法（按顺序执行）

1. **取短分支名**：`git rev-parse --abbrev-ref HEAD`；若为 `HEAD`（游离提交）则**无法解析**，scope 由人工指定或使用 `misc`。
2. **去掉远程前缀**（若有）：如 `origin/feature_zlf_pet` → 取最后一段或去掉 `origin/` 后再处理。
3. **去掉路径前缀**（若有）：如 `feature/pet-login` → 先取 `pet-login` 或最后一段，再按下划线规则处理。
4. **去掉常见分支类型前缀**（大小写不敏感，整段匹配前缀后剩余部分进入下一步）：
   - `feature_`、`feat_`、`fix_`、`hotfix_`、`bugfix_`、`release_`、`chore_`、`refactor_`、`dev_`、`test_`
5. **从剩余字符串取 scope**：
   - 若包含下划线 `_`：取**最后一个**下划线之后的段作为 scope（`zlf_pet` → `pet`）。
   - 若不包含下划线：整体作为 scope（`afk` → `afk`）。
6. **规范化**：scope 转为**小写**；仅保留字母、数字、连字符（如有 `pet-v2` 可保留）；去掉首尾 `-`/`_`。

### 非规范分支名的判断与兜底

在以下情况**不要强行编造**模块名，应使用兜底策略：

| 情况 | 建议 scope | 说明 |
|------|----------------|------|
| `main`、`master`、`develop`、`dev`、`release`、纯版本号如 `release-1.2.3` | `misc` 或由 diff 指定 | 无业务域信息 |
| 游离 `HEAD`、临时分支 `tmp`、`wip`、`test`、纯人名 `zhangsan` | `misc` 或由 diff 指定 | 无法表达功能域 |
| 解析结果为空、或只剩单字母/无意义缩写 | `misc` 或由 diff 指定 | 避免 `scope` 无意义 |
| 一次提交跨多个模块 | 用**影响最大**的模块，或 `misc`，描述中列举 | 更好的做法是拆 commit |

**兜底时**：`<description>` 必须用中文写清**真实模块或路径**（如「宠物上阵协议」「挂机服务」），以弥补 scope 笼统。

### 人工覆盖

当分支名误导或与本次提交无关时（例如在 `feature_pet` 分支上只改了 CI），**以本次改动为准**选择 scope（如 `ci`）或 `misc`，**不必**机械使用分支解析结果。

## AI 执行清单

1. 用 `git rev-parse --abbrev-ref HEAD` 取得当前分支并解析 `scope`；无法解析则用 `misc` 并在描述中写明模块。
2. 根据 **diff / 用户说明** 从类型表中选定 `type`。
3. 输出一行完整 message：`<type>(<scope>): <中文描述>`。
4. 若用户要求英文描述，可额外给一行英文版；**默认以中文描述为准**（与本 Skill 一致）。

## 「帮我提交代码」工作流（用户主动触发）

### 触发表述（任意一条命中即按本流程）

- 「帮我提交代码 / 帮我 commit / 帮我提交 / 提交一下 / 提交代码 / commit 一下」
- 等价中文表述（如「帮我把代码提交了」「这次先提交吧」）

> 仅当用户**明确触发**才执行本流程；未触发时不要自作主张提交。

### 关键约束（与全局 git 安全规范一致）

- **只提交已经 `git add`（staged）的文件**；**禁止**主动 `git add .` 或追加未暂存文件。
- **不修改 git config**；**不**使用 `--no-verify` / `--no-gpg-sign` 跳过 hooks（除非用户显式要求）。
- **不 `git push`**（除非用户显式要求）；不使用 `git rebase -i` / `git add -i` 等交互式命令。
- **可疑文件**（`.env`、`credentials.json`、密钥等）若已被 staged，**先警告用户**再决定是否提交。
- 若发现**没有任何 staged 改动**：提示用户先 `git add <files>`，**不**进入提交步骤。

### 执行步骤

1. **并行收集上下文**（一次发起多条 Shell 调用）：
   - `git status`（查看暂存区与工作区状态、是否跟踪远程）
   - `git diff --cached`（**仅看 staged 改动**，作为生成 message 的唯一事实来源）
   - `git log -n 5 --oneline`（参考本仓库已有的提交风格）
   - `git rev-parse --abbrev-ref HEAD`（解析 `scope`）
2. **判定与生成**：
   - 无 staged → 提示用户 `git add` 后重新触发；流程结束。
   - 有 staged → 按「类型表」选 `type`，按「从分支解析 scope」选 `scope`，写**中文**描述聚焦「为什么 / 主要变化」。
   - 多类改动建议**拆 commit**；用户坚持合并时取主因 `type`，描述里点出次要变更。
3. **请用户确认**：把生成的 message 单独成块展示，并附一段简短「本次将提交的范围」摘要（基于 `git status` 中的 staged 文件清单）。等待用户回复：
   - 「确认 / 可以 / 提交吧」→ 进入步骤 4
   - 「改成 …」→ 按要求调整后再次请确认
   - 「取消 / 先不提交」→ 终止流程，不执行 commit
4. **执行提交**（用户确认后）：使用 HEREDOC 提交，避免引号转义问题：
   ```bash
   git commit -m "$(cat <<'EOF'
   <type>(<scope>): <中文描述>
   EOF
   )"
   ```
5. **验证**：再次 `git status`，确认提交成功（`nothing to commit` 或仅剩未跟踪文件、领先远程 N 个提交）。如失败：
   - **pre-commit hook 失败/拒绝**：根据报错修复后**新建一次 commit**，**不要** `--amend`。
   - **hook 自动修改了文件且 commit 已成功**：按需将这些自动修改的文件 `git add` 后追加一次 commit（同样**不**默认 `--amend`，除非用户明确要求且未推送）。
6. **结束**：把最终 commit hash / 简要结果回报用户；**不主动**推送。

### 失败/异常处理

- 仓库不在 git 控制下、检出为游离 HEAD、`git diff --cached` 为空：按「关键约束」处理，明确告知用户原因。
- 用户在确认环节迟迟未明确表态：**不要默认提交**，等待显式确认。

## 相关

- 项目其他规范见各 `.cursor/rules/*.mdc`；本 Skill 专注 **commit 文案与受用户触发的提交流程**。
- 全局 git 安全规范（不改 config、不跳 hook、不强推、不随意 `--amend` 等）以本仓库 `.cursor/rules/` 与对话系统提示中的 git 协议为准。
