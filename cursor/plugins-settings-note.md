# Cursor 项目里 `plugins` 键与插件 ID 的对应关系

## 结论（已在本机缓存核对）

- **Superpowers** 插件解压目录下的 `package.json` 中声明：  
  `"name": "superpowers"`（示例路径：`C:\Users\Administrator\.cursor\plugins\cache\cursor-public\superpowers\<hash>\package.json`）。
- Cursor 项目配置 **`.cursor/settings.json`** 里应使用**同一字符串**作为键：

```json
"plugins": {
  "superpowers": { "enabled": true }
}
```

## 为什么不要改成 `agents-team`

- 配置键需要与已安装插件包的 **`name` 字段**一致；上游未发布 `name: "agents-team"` 的包时，改成 `agents-team` 会导致 Cursor **无法识别/启用**该插件。
- 本仓库对套件的**称呼**为 **Agents Team**（文档、`agents-team:` 技能引用等），与 **插件包名仍为 `superpowers`** 不冲突。

## 若将来改名

若官方插件的 `package.json` 将来改为 `"name": "agents-team"`（或市场提供新 ID），再同步修改 `.cursor/settings.json` 中的键，并在此处更新说明。
