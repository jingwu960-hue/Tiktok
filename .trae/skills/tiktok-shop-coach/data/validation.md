# 数据验证规则

## 概述

本文档定义 `shop-metrics.json` 数据文件的验证规则和自动修复策略。

## 验证流程

```
读取数据文件
  ↓
文件存在？ → 否 → 创建默认结构 → 记录警告
  ↓ 是
JSON格式正确？ → 否 → 尝试修复 → 失败 → 使用默认值 → 记录错误
  ↓ 是
Schema验证 → 失败 → 填充缺失字段 → 记录警告
  ↓ 通过
数据完整性检查
  ↓
返回验证结果
```

## 验证规则

### 1. 必填字段检查

| 字段 | 类型 | 必填 | 默认值 |
|------|------|------|--------|
| shop_info.market | string | ✅ | "越南" |
| shop_info.start_date | date | ✅ | - |
| shop_info.shop_code | string | ✅ | - |
| daily_metrics | array | ✅ | [] |

### 2. 数据类型检查

| 字段 | 期望类型 | 修复策略 |
|------|----------|----------|
| day_number | integer | 从字符串转换 |
| products_listed | integer | 从字符串转换，默认0 |
| orders | integer | 从字符串转换，默认0 |
| gmv | number | 从字符串转换，默认0 |
| ctr | number/string | 统一为number |

### 3. 数据范围检查

| 字段 | 最小值 | 最大值 | 异常处理 |
|------|--------|--------|----------|
| day_number | 1 | 365 | 超出范围则重新计算 |
| products_listed | 0 | 10000 | 超出范围标记异常 |
| orders | 0 | 10000 | 超出范围标记异常 |
| gmv | 0 | 100000000 | 超出范围标记异常 |
| ctr | 0 | 100 | 超出范围重新计算 |

### 4. 数据一致性检查

- `day_number` 应与 `date` 和 `start_date` 一致
- `ctr` 应等于 `clicks / impressions × 100`（允许误差）
- `daily_metrics` 数组应按日期排序

## 自动修复策略

### 策略1：缺失字段填充
当字段缺失时，使用默认值填充并记录警告。

### 策略2：类型转换
当字段类型不匹配时，尝试自动转换。

### 策略3：数据重算
当计算字段（如ctr）与实际值不符时，重新计算。

### 策略4：日期补全
当 `day_number` 缺失时，根据 `start_date` 和 `date` 计算。

## 默认数据结构

当数据文件不存在时，使用以下默认结构创建：

```json
{
  "shop_info": {
    "market": "越南",
    "start_date": "2026-06-19",
    "shop_code": "CNVNCBBRL4FX"
  },
  "daily_metrics": [],
  "tasks_completed": [],
  "warnings": []
}
```

## 错误日志格式

```
[时间] [级别] [模块] 消息
[2026-06-22 10:00:00] [WARN] [data-validation] 字段 shop_info.budget 缺失，使用默认值
[2026-06-22 10:00:01] [ERROR] [data-validation] daily_metrics[0].ctr 类型错误，已从字符串转换
```
