# TikTok Shop Coach 技能优化设计文档

**版本**: 1.1.0  
**日期**: 2026-06-22  
**状态**: 已批准实施

---

## 一、优化目标

对 `/Users/wujing/QingZhen/Tiktok/.trae/skills/tiktok-shop-coach` 进行全面优化，解决以下问题：

1. **结构问题**：SKILL.md 过于臃肿（469行），职责混杂
2. **维护问题**：模板、参数、流程耦合在一起，难以单独修改
3. **健壮性问题**：缺少数据验证和错误处理机制
4. **知识管理问题**：SKILL.md 与 knowledge/ 文件内容重复，缺少索引

---

## 二、目标架构

```
tiktok-shop-coach/
├── SKILL.md                    # 精简入口（<80行）
├── config/
│   ├── triggers.yaml           # 触发条件与角色识别
│   ├── parameters.yaml         # 关键参数表
│   └── templates/              # 输出模板
│       ├── daily-tasks.md
│       ├── product-analysis.md
│       ├── data-report.md
│       └── monthly-plan.md
├── workflows/
│   ├── daily-guide.md          # 每日运营指导
│   ├── product-select.md       # 选品分析
│   ├── data-analysis.md        # 数据分析
│   └── link-learn.md           # 链接学习
├── data/
│   ├── schema.json             # 数据结构规范
│   └── validation.md           # 验证规则说明
├── knowledge/                  # 保持不变（11个文件）
│   └── INDEX.md                # 新增：知识库索引
├── CHANGELOG.md                # 版本记录
└── DESIGN.md                   # 本设计文档
```

---

## 三、核心组件设计

### 3.1 SKILL.md（精简入口）

**职责**：
- 元数据定义（name, description）
- 路由逻辑（根据意图分发到对应 workflow）
- 快速参考（关键参数摘要）

**行数目标**：<80行

**内容结构**：
```yaml
---
name: tiktok-shop-coach
description: ...
---

# TikTok Shop 越南站运营助手

## 快速使用
（3行说明如何触发）

## 角色路由
（表格：角色 → workflow 文件映射）

## 关键参数速查
（最核心的5个参数，详细内容指向 parameters.yaml）

## 知识库链接
（指向 knowledge/INDEX.md）

## 错误处理
（简要说明回退策略）
```

### 3.2 config/triggers.yaml

**职责**：定义触发条件和角色识别规则

**结构**：
```yaml
triggers:
  positive:
    - pattern: "今天该做什么|每日任务"
      role: coach
    - pattern: "选品|卖什么|利润分析"
      role: product-expert
    # ...
  
  negative:
    - pattern: "你好|谢谢|再见"
    - pattern: "与TikTok Shop无关"

roles:
  coach:
    name: 运营教练
    workflow: workflows/daily-guide.md
    template: config/templates/daily-tasks.md
  
  product-expert:
    name: 选品专家
    workflow: workflows/product-select.md
    template: config/templates/product-analysis.md
  
  # ...
```

### 3.3 config/parameters.yaml

**职责**：统一管理所有关键参数

**结构**：
```yaml
selection_rules:
  weight_limit: 200g
  volume_limit: "20×15×10cm"
  price_range: "$5-$15"
  profit_margin: "≥30%"
  competition_threshold: 100

platform_metrics:
  shop_rating: "≥4.5"
  nrr: "<5%"
  ldr: "<10%"
  sfcr: "<2.5%"

cost_parameters:
  shipping_rate: "2.3-3元/kg"
  commission_rate: "6%"
  exchange_rate: "1 CNY ≈ 3,872 VND"

# ...
```

### 3.4 config/templates/

**职责**：独立管理输出模板

**文件列表**：
- `daily-tasks.md` - 每日任务清单模板
- `product-analysis.md` - 选品分析报告模板
- `data-report.md` - 数据分析报告模板
- `monthly-plan.md` - 月度规划模板

**设计原则**：
- 每个模板独立文件，便于单独修改
- 使用占位符 `{变量名}` 标记动态内容
- 包含使用说明和示例

### 3.5 workflows/

**职责**：定义详细工作流程

**文件列表**：
- `daily-guide.md` - 每日运营指导流程
- `product-select.md` - 选品分析流程
- `data-analysis.md` - 数据分析流程
- `link-learn.md` - 链接学习流程

**每个文件结构**：
```markdown
# 流程名称

## 触发条件
（何时执行此流程）

## 执行步骤
1. 步骤1
2. 步骤2
...

## 错误处理
- 场景1 → 处理方式
- 场景2 → 处理方式

## 输出格式
（指向对应模板）
```

### 3.6 data/schema.json

**职责**：定义 shop-metrics.json 的数据结构规范

**内容**：
- JSON Schema 定义
- 必填字段标记
- 数据类型约束
- 默认值定义

### 3.7 knowledge/INDEX.md

**职责**：知识库索引和交叉引用

**内容**：
- 按主题分类的文件列表
- 每个文件的摘要说明
- 相关文件交叉引用

---

## 四、数据流设计

```
用户输入
  ↓
SKILL.md（路由）
  ↓
识别角色 → 读取 config/triggers.yaml
  ↓
加载对应 workflow → 读取 workflows/*.md
  ↓
读取参数 → 读取 config/parameters.yaml
  ↓
读取数据 → .trae/data/shop-metrics.json
  ↓
校验数据 → data/schema.json
  ↓
生成输出 → 加载 config/templates/*.md
  ↓
返回结果
```

---

## 五、错误处理机制

### 5.1 数据文件不存在

**处理**：
1. 自动创建默认结构
2. 记录警告日志
3. 使用默认值继续执行

### 5.2 数据格式错误

**处理**：
1. 尝试自动修复（填充缺失字段）
2. 修复失败则使用默认值
3. 提示用户检查数据文件

### 5.3 Schema 验证失败

**处理**：
1. 记录详细错误信息
2. 提供修复建议
3. 不阻断主流程

### 5.4 知识库链接失效

**处理**：
1. 自动扫描 knowledge/ 目录
2. 更新 INDEX.md
3. 提示用户链接已更新

---

## 六、知识库整合策略

### 6.1 去重原则

- SKILL.md 只保留摘要和链接
- parameters.yaml 作为唯一参数源
- templates/ 独立管理输出格式

### 6.2 交叉引用

- knowledge/ 文件头部添加 `related:` 字段
- INDEX.md 提供统一索引

---

## 七、版本管理

### 7.1 CHANGELOG.md 格式

遵循 [Keep a Changelog](https://keepachangelog.com/) 规范：

```markdown
# Changelog

## [1.1.0] - 2026-06-22

### Added
- 数据验证机制（schema.json）
- 错误处理指引

### Changed
- SKILL.md 拆分为模块化结构
- 参数表统一迁移到 parameters.yaml

### Fixed
- 修复数据文件缺失时的崩溃问题
```

---

## 八、优化前后对比

| 指标 | 优化前 | 优化后 |
|------|--------|--------|
| SKILL.md 行数 | 469行 | <80行 |
| 文件数量 | 12个 | 20个 |
| 职责分离 | 混杂 | 清晰 |
| 数据验证 | 无 | 有（schema.json） |
| 错误处理 | 无 | 有（每个workflow） |
| 知识库索引 | 无 | 有（INDEX.md） |
| 版本管理 | 无 | 有（CHANGELOG.md） |

---

## 九、实施计划

### 阶段1：基础设施（Day 1）
- 创建目录结构
- 编写 DESIGN.md
- 编写 CHANGELOG.md

### 阶段2：核心重构（Day 2-3）
- 重构 SKILL.md
- 创建 config/triggers.yaml
- 创建 config/parameters.yaml
- 创建 config/templates/

### 阶段3：流程迁移（Day 4-5）
- 创建 workflows/
- 迁移原有流程逻辑

### 阶段4：数据验证（Day 6）
- 创建 data/schema.json
- 编写验证规则

### 阶段5：知识库整合（Day 7）
- 创建 knowledge/INDEX.md
- 去重和交叉引用

### 阶段6：验证与优化（Day 8）
- 功能测试
- 性能对比
- 生成优化报告

---

## 十、验收标准

1. ✅ SKILL.md 行数 < 80
2. ✅ 所有功能正常工作
3. ✅ 数据验证机制生效
4. ✅ 错误处理覆盖所有场景
5. ✅ 知识库索引完整
6. ✅ 版本记录清晰

---

**文档结束**
