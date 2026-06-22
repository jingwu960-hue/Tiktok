# AGENTS.md — TikTok Shop 越南站运营项目

> 最后更新：2026-06-23 | 版本：2.0.0

---

## 一、项目概述

### 基本信息

| 项目 | 详情 |
|------|------|
| **目标市场** | 越南（Vietnam） |
| **店铺编码** | CNVNCBBRL4FX |
| **TikTok 账号** | Cool Base（已注册） |
| **主营类目** | 时尚配件（戒指、眼镜、手表、手镯等） |
| **启动日期** | 2026-06-19 |
| **预算范围** | 5000 元以内 |
| **供货方式** | 一件代发（1688 / 拼多多） |
| **成本控制** | 采购价 ≤ 20 元，目标利润率 ≥ 30% |
| **运营模式** | 无货源跨境电商，自然流量冷启动 |

### 店铺链接

- 卖家中心：https://seller.tiktok.com/

---

## 二、项目目录结构

```
Tiktok/
├── AGENTS.md                          # 本文件：项目手册（AI 上下文入口）
├── .gitignore                         # Git 忽略规则
├── skills-lock.json                   # 技能锁定文件（brainstorming, writing-plans）
├── 迁移操作指南.md                     # TRAE IDE → TRAE Work 迁移指南
│
├── .agents/                           # 内置技能（obra/superpowers 官方技能）
│   └── skills/
│       ├── brainstorming/             # 头脑风暴与设计评审
│       └── writing-plans/             # 实施计划编写
│
├── .trae/                             # TRAE 技能与数据（主技能目录）
│   ├── data/
│   │   └── shop-metrics.json          # 📊 店铺核心指标数据（单一真相来源）
│   ├── documents/                     # 历史规划文档（11 个计划文件）
│   └── skills/
│       ├── tiktok-shop-coach/         # 🎯 TikTok Shop 运营助手（核心技能）
│       │   ├── SKILL.md               #   技能入口（角色路由）
│       │   ├── DESIGN.md              #   架构设计文档
│       │   ├── CHANGELOG.md           #   版本变更记录
│       │   ├── OPTIMIZATION-REPORT.md #   优化报告
│       │   ├── config/
│       │   │   ├── triggers.yaml      #   触发条件与角色映射
│       │   │   ├── parameters.yaml    #   运营参数表（单一真相来源）
│       │   │   └── templates/         #   输出模板（5 个）
│       │   ├── workflows/             #   工作流定义（7 个）
│       │   ├── data/                  #   数据规范（schema + validation）
│       │   └── knowledge/             #   知识库（11 个文档 + INDEX.md）
│       ├── knowledge-harvester/       # 🔗 知识收割器（URL 自动抓取学习）
│       └── task-planner/              # 📋 任务规划器
│
├── .qoder/                            # ⚠️ 废弃目录（遗留技能，请使用 .trae/）
│   ├── skills/
│   │   ├── tiktok-shop-coach/         #   旧版技能（已废弃）
│   │   ├── ecom-image-viet-translate/ #   电商图片越南语翻译（已废弃）
│   │   └── knowledge-harvester/       #   旧版知识收割器（已废弃）
│   └── data/
│       └── shop-metrics.json          #   旧版数据（已废弃，以 .trae/ 为准）
│
├── TikTokShop/                        # 📁 运营工作目录
│   ├── readme.md                      #   产品列表 API 路径参考
│   ├── products.json                  #   📦 商品数据（TikTok API 导出，19 个商品）
│   ├── products-simple.json           #   📦 商品数据精简版
│   ├── 定价策略指南.md                 #   💰 详细定价策略（含 2026 年平台费率）
│   ├── 越南语评论模板.md               #   💬 养号互动评论模板（48 条，6 大类）
│   ├── 2026/                          #   📅 运营日志（按年份/月份组织）
│   │   └── 6月/
│   │       ├── 6月19日.md              #     第 1 天：上架 20 个商品
│   │       ├── 6月20日.md              #     第 2 天：定价策略制定
│   │       └── 6月22日.md              #     第 4 天：下架侵权商品、视频上传
│   ├── 学习笔记/                       #   📝 平台课程学习记录
│   │   ├── TikTok Shop东南亚新商政策必修课.md
│   │   ├── 卖家学习中心课程资源库.md
│   │   └── 学习进度追踪.md
│   └── 知识库/                         #   📚 本地知识库（含历史版本与工具脚本）
│       ├── index.json                 #   知识库索引
│       ├── config.json                #   知识库配置
│       ├── Kalodata资源与行业白皮书.md
│       ├── 卖家大学文章目录.json
│       ├── 卖家学习中心课程资源库.md
│       ├── metadata/                  #   元数据
│       ├── history/                   #   历史版本
│       └── utils/                     #   工具脚本（Python）
│
├── 选品/                              # 🖼️ 选品参考图片（4 张）
├── 工具/                              # 🛠️ 工具文件
│   └── 东南亚跨境物流运费价格表20260401.xlsx
└── Logistics/                         # 物流计算器子项目（独立）
```

---

## 三、技能体系

### 技能清单

| 技能 | 位置 | 用途 |
|------|------|------|
| **tiktok-shop-coach** | `.trae/skills/tiktok-shop-coach/` | TikTok Shop 越南站运营核心助手 |
| **knowledge-harvester** | `.trae/skills/knowledge-harvester/` | URL 知识自动抓取与学习 |
| **task-planner** | `.trae/skills/task-planner/` | 任务规划与分解 |
| **brainstorming** | `.agents/skills/brainstorming/` | 头脑风暴与设计评审（官方） |
| **writing-plans** | `.agents/skills/writing-plans/` | 实施计划编写（官方） |

### tiktok-shop-coach 角色路由

核心技能内置 6 个角色，通过关键词自动匹配：

| 角色 | 触发关键词 | 工作流文件 |
|------|-----------|-----------|
| 运营总监 | 月计划、周计划、整体规划 | `workflows/monthly-plan.md` |
| 运营教练 | 今天该做什么、每日任务、第X天 | `workflows/daily-guide.md` |
| 选品专家 | 选品、卖什么、利润分析 | `workflows/product-select.md` |
| 运营专家 | 上架、标题、SEO、卖点 | `workflows/product-listing.md` |
| 数据分析师 | 数据分析、曝光、点击、转化 | `workflows/data-analysis.md` |
| 日志记录员 | 自动触发（对话结束时） | `workflows/log-recorder.md` |

> 详细触发规则见 `.trae/skills/tiktok-shop-coach/config/triggers.yaml`

### 技能架构

```
用户输入 → SKILL.md（路由识别）
              ↓
         读取 triggers.yaml（匹配角色）
              ↓
         加载对应 workflow（执行流程）
              ↓
         读取 parameters.yaml（获取参数）
              ↓
         读取 shop-metrics.json（获取数据）
              ↓
         加载对应 template（格式化输出）
              ↓
         日志记录员自动记录（log-recorder.md）
```

---

## 四、数据文件

### 店铺指标数据

**路径**：`.trae/data/shop-metrics.json`

**结构**：
```json
{
  "shop_info": { ... },       // 店铺基础信息
  "cost_structure": { ... },  // 成本结构
  "cost_control": { ... },    // 成本控制参数
  "daily_metrics": [ ... ],   // 每日运营指标数组
  "product_analysis": { ... },// 商品分析数据
  "tasks_completed": [ ... ], // 已完成任务列表
  "warnings": [ ... ]         // 预警信息
}
```

**每日指标字段**：

| 字段 | 含义 | 单位 |
|------|------|------|
| `date` | 日期 | YYYY-MM-DD |
| `day_number` | 运营天数 | 天 |
| `products_listed` | 已上架商品数 | 个 |
| `orders` | 订单数 | 单 |
| `gmv` | 成交额 | VND |
| `videos` | 已发布视频数 | 个 |
| `followers` | 粉丝数 | 人 |
| `impressions` | 曝光量 | 次 |
| `clicks` | 点击量 | 次 |
| `ctr` | 点击率 | % |
| `add_to_cart` | 加购数 | 次 |
| `refunds` | 退款数 | 单 |
| `notes` | 备注 | 文本 |

### 商品数据

| 文件 | 路径 | 说明 |
|------|------|------|
| products.json | `TikTokShop/products.json` | TikTok API 导出的完整商品数据（含 SKU、价格、库存、分类等） |
| products-simple.json | `TikTokShop/products-simple.json` | 商品数据精简版 |

### 数据规范

- 数据结构定义：`.trae/skills/tiktok-shop-coach/data/schema.json`
- 验证规则说明：`.trae/skills/tiktok-shop-coach/data/validation.md`

---

## 五、日志与记录

### 日志系统

每次对话结束后，**日志记录员**角色自动将运营内容记录到本地文件。

**存储路径**：`TikTokShop/{年份}/{月份}/{M}月{D}日.md`

**示例**：`TikTokShop/2026/6月/6月22日.md`

### 日志格式（模块化）

日志采用**模块化结构**，根据当天内容灵活组合：

**必填模块**：
- 基础信息（店铺状态、成本控制、运营数据）
- 每日复盘（已完成任务、未完成任务）
- 明日计划（任务清单、预期成果、风险预案）

**可选模块**（根据当天内容按需添加）：
- 问题诊断 / 重大发现与问题
- 关键决策记录
- 定价策略分析
- 执行方案
- 视频制作方案
- 知识学习记录

**自媒体素材附加模块**（用于后续抖音视频脚本）：
- 今日一句话（视频钩子）
- 今日故事（视频脚本素材）
- 视频素材标记

> 详细格式规范见 `.trae/skills/tiktok-shop-coach/workflows/log-recorder.md`

---

## 六、知识库体系

### 主知识库

**路径**：`.trae/skills/tiktok-shop-coach/knowledge/`

**索引**：`knowledge/INDEX.md`

### 知识文档清单（11 个）

| 分类 | 文档 | 核心内容 |
|------|------|----------|
| 🎯 选品与定价 | `选品策略.md`、`定价策略.md` | 选品铁律、市场分析、定价公式 |
| 📦 商品运营 | `商品上架.md`、`平台政策.md` | 上架流程、标题优化、平台规则 |
| 🚀 冷启动与增长 | `冷启动策略.md`、`账号运营.md` | 60 天破零计划、粉丝增长 |
| 🎬 内容创作 | `短视频制作.md`、`直播带货.md` | 爆款结构、拍摄技巧、直播流程 |
| 🤝 合作与推广 | `达人合作.md`、`广告投放.md` | KOL 合作、投流策略 |
| ❓ 常见问题 | `常见问题.md` | 新手 FAQ 与应急处理 |

### 本地知识库

**路径**：`TikTokShop/知识库/`

包含知识库的本地副本、历史版本（`history/`）、元数据（`metadata/`）和工具脚本（`utils/`）。

### 学习笔记

**路径**：`TikTokShop/学习笔记/`

包含平台课程学习记录和进度追踪。

---

## 七、关键参数速查

> 完整参数表见 `.trae/skills/tiktok-shop-coach/config/parameters.yaml`

| 类别 | 参数 | 值 |
|------|------|-----|
| 选品 | 重量上限 | < 200g |
| 选品 | 客单价黄金区间 | $5 - $15 |
| 选品 | 目标利润率 | ≥ 30% |
| 成本 | 平台佣金 | 15.5%（时尚配件类目，2026年5月更新） |
| 成本 | 交易手续费 | 6%（2026年5月更新） |
| 成本 | 跨境运费 | 2.3 - 3 元/kg（东南亚专线） |
| 成本 | 采购价上限 | ≤ 20 元 |
| 汇率 | CNY → VND | 1 CNY ≈ 3,872 VND |
| 视频 | 理想时长 | 15 - 25 秒 |
| 视频 | 更新频率 | 日更 3 - 10 条 |
| 视频 | 完播率目标 | > 40% |

---

## 八、行为指引

### 核心规则

1. **所有 AI 回复使用中文**
2. **日期相关操作需先通过 `date` 命令获取当前日期**
3. **货币显示同时标注 VND 和人民币**（示例：126,233 VND ≈ 33 元）
4. **运营数据以 `.trae/data/shop-metrics.json` 为单一真相来源**
5. **文案面向越南市场时使用越南语**
6. **严格遵守 TikTok 平台规则，禁止侵权商品**
7. **新手优先自然流量，谨慎投放广告**
8. **每次对话结束时自动触发日志记录**

### 数据操作规范

| 场景 | 处理方式 |
|------|----------|
| 读取店铺数据 | 优先读取 `.trae/data/shop-metrics.json` |
| 更新店铺数据 | 同步更新 `.trae/data/shop-metrics.json` |
| 数据文件不存在 | 创建默认结构，记录警告 |
| 数据格式错误 | 尝试修复，失败则用默认值 |
| 数据来源 | 必须来自 TikTok Analytics，禁止估算 |

### 目录规范

| 目录 | 状态 | 说明 |
|------|------|------|
| `.trae/` | ✅ 主目录 | 技能和数据的主目录 |
| `.agents/` | ✅ 官方技能 | obra/superpowers 官方技能 |
| `TikTokShop/` | ✅ 工作目录 | 运营文件、日志、知识库 |
| `.qoder/` | ⚠️ 废弃 | 遗留目录，所有功能已迁移到 `.trae/`，请勿使用 |

### 时区

- 越南时间比北京时间慢 1 小时
- 日志记录以北京时间为准

---

*本文件是 AI 助手理解项目上下文的核心入口，请保持更新。*