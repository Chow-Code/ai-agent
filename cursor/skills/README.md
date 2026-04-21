# `.cursor/skills` 说明

- 本仓库将 **Agents Team**（代理协作技能套件）与业务技能混放在此目录。  
- 入门技能目录：**`using-agents-team/`**（旧文档或社区资料中可能写作 Superpowers、**superstarts**，系同一套理念）。  
- **BDD / `qa/integration`**：技能 **`bdd-qa/`**。  
- 技能间引用使用命名空间前缀 **`agents-team:<技能目录名>`**（与文件夹名对应，例如 `agents-team:writing-plans`）。**`writing-plans` 产出的实施计划一律 BDD**（Given-When-Then）。  
- **Cursor 插件包名**（`package.json` 的 `name`）仍为 **`superpowers`**，因此 `.cursor/settings.json` 必须使用 **`plugins.superpowers`**，不能改成 `agents-team`（否则插件可能无法启用）。详见：[`../plugins-settings-note.md`](../plugins-settings-note.md)。
- 本仓库对套件的**称呼**为 **Agents Team**，与插件包名无关。
