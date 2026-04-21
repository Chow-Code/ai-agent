---
name: kafkatoclick-tool
description: 当需要从Kafka消费消息并写入ClickHouse时使用此工具。用于日志数据同步到ClickHouse。
---

# Kafka到ClickHouse数据同步工具Skill

## 工具概述

Kafka到ClickHouse数据同步工具是一个从Kafka消费消息并写入ClickHouse的高性能同步工具，专为大规模日志数据处理设计，支持实时数据同步和批量写入优化。

## 使用场景

- 需要将Kafka中的日志数据同步到ClickHouse时
- 需要实时处理大量日志数据时
- 需要批量写入优化时

## 前置条件

- Go 1.22+环境已配置
- ClickHouse服务器已启动并可访问
- Kafka集群已启动并可访问
- 配置文件已准备好（`tools/kafkatoclick/config.yaml`）

## 命令格式

```bash
cd tools/kafkatoclick
go run main.go
```

## 配置说明

配置文件：`tools/kafkatoclick/config.yaml`

### ClickHouse配置

```yaml
clickhouse:
  address: "192.168.220.56:30090"
  username: "digisky"
  password: "A7dzk3Lx9B2"
  database: "wtserver"
  bufferSize: 100000
  flushinterval: 10
```

### Kafka配置

```yaml
kafka:
  brokers:
    - "192.168.220.55:30093"
  topic: "lobby-inner"
  group_id: "test-group"
  auto_offset_reset: "latest"
  acks: "all"
  compression_type: "gzip"
  partition: 10
```

## 工具特性

1. **高性能批量写入**：默认批次大小50000
2. **并发处理**：200个处理协程
3. **消息缓冲**：200000容量的消息通道
4. **定时刷新**：30秒自动检查未满批次数据
5. **完整的监控统计**：处理消息数、跳过消息数、插入记录数
6. **异常处理**：SQL注入防护、字段校验等

## 性能调优

### 关键参数

1. **批量写入**:
   - `batchSize`: 默认50000，可根据内存调整
   - `bufferSize`: 影响写入缓冲区大小
   - `flushinterval`: 影响写入频率

2. **并发处理**:
   - 处理协程数：默认200
   - 消息通道容量：200000

### 监控指标

- `processedMessages`: 已处理消息总数
- `skippedMessages`: 跳过的异常消息数
- `insertedRecords`: 成功写入记录数

## 常见问题

### Q: 如何调试？

A: 使用VSCode的"Debug KafkaToClick Tool"配置启动调试。

### Q: 如何调整性能参数？

A: 修改`config.yaml`中的`batchSize`、`bufferSize`、`flushinterval`等参数。

### Q: 如何处理异常消息？

A: 工具会自动跳过异常消息并记录到`skippedMessages`统计中。

## 最佳实践

1. **监控统计指标**：定期查看处理消息数、跳过消息数、插入记录数
2. **调整批次大小**：根据内存情况调整`batchSize`参数
3. **检查配置**：确保ClickHouse和Kafka配置正确
4. **处理异常**：关注`skippedMessages`统计，及时处理异常消息

## 相关文档

- **工具README**: `tools/kafkatoclick/README.md`
