# 计划：创建知识抓取技能 (knowledge-harvester)

## 摘要

创建一个新的Skill，接收URL作为输入，使用Playwright自动化抓取网页内容，参考tiktok-shop-coach的角色信息提取关键知识，并保存到知识库目录。

---

## 现状分析

### 现有技能结构
- **tiktok-shop-coach** 位置：`.trae/skills/tiktok-shop-coach/SKILL.md`
- **知识库目录**：`/Users/wujing/QingZhen/Tiktok/TikTokShop/知识库/`
- **现有知识分类**：选品策略、商品上架、短视频制作、冷启动策略、平台政策、定价策略、达人合作、账号运营、广告投放、直播带货、常见问题

### 知识库文件格式规范
```markdown
# 标题

> 更新时间：2026年6月20日
> 版本：v1.0

---

## 一、章节内容
...
---

*文档版本：v1.1*
*更新时间：2026年6月20日*
*学习来源：URL*
```

### Playwright MCP工具（已启用）
- `playwright_navigate` - 导航到URL
- `playwright_get_visible_text` - 获取页面可见文本
- `playwright_get_visible_html` - 获取页面HTML
- `playwright_click` - 点击元素
- `playwright_screenshot` - 页面截图
- `playwright_evaluate` - 执行JavaScript
- `playwright_fill` - 填写表单
- `playwright_select` - 选择下拉选项

---

## 实施步骤

### 步骤1：创建技能目录和SKILL.md文件

**目录**：[`.trae/skills/knowledge-harvester/`](file:///Users/wujing/QingZhen/Tiktok/.trae/skills/knowledge-harvester/)

**SKILL.md内容**：

```markdown
---
name: "knowledge-harvester"
description: "从URL自动抓取TikTok/电商相关知识。输入URL后使用Playwright自动化提取内容，参考运营角色信息整理知识，保存到知识库。用于用户发送链接希望学习或保存知识时。"
---

# 知识抓取助手

## 触发条件

**何时使用**：
- 用户发送URL并要求"学习"、"抓取"、"保存知识"
- 用户发送TikTok Shop相关链接（seller.tiktokglobalshop.com、university.tiktokglobalshop.com、1688.com等）
- 用户请求"分析这个页面"

**触发关键词**：
- "抓取"
- "学习这个链接"
- "保存到知识库"
- "提取知识"

---

## 核心工作流程

### 流程1：URL验证与导航

```
1. 验证URL域名是否在允许列表
2. 使用 playwright_navigate 打开URL
3. 等待页面加载完成（waitUntil: networkidle）
4. 截图保存当前页面状态
```

### 流程2：内容提取

```
1. 使用 playwright_get_visible_text 获取页面可见文本
2. 使用 playwright_get_visible_html 获取完整HTML
3. 使用 playwright_evaluate 提取关键信息（标题、描述、关键词）
4. 识别页面类型（课程页、商品页、学习中心页等）
```

### 流程3：智能遍历（可选）

```
1. 如果页面包含目录/导航链接
2. 按优先级最多遍历10个相关链接
3. 每抓取一个链接休息2秒（避免封禁）
```

### 流程4：知识提取与整理

```
1. 分析内容类型，对应知识分类
2. 提取关键知识点：
   - 标题/概念
   - 操作步骤/方法
   - 注意事项/规则
   - 数据/指标
3. 按照知识库格式整理
```

### 流程5：保存到知识库

```
1. 确定保存文件路径
   - 知识库主目录：/Users/wujing/QingZhen/Tiktok/TikTokShop/知识库/
2. 命名规范：{分类名}.md
3. 更新 index.json 添加新条目
4. 保存文件
5. 返回确认信息
```

---

## 内容分类映射

| URL类型/关键词 | 保存到 |
|---------------|--------|
| 选品、爆款、品类 | 选品策略.md |
| 上架、标题、主图 | 商品上架.md |
| 视频、剪辑、内容 | 短视频制作.md |
| 冷启动、破零、新店 | 冷启动策略.md |
| 政策、规则、考核 | 平台政策.md |
| 定价、成本、利润 | 定价策略.md |
| 达人、KOL、网红 | 达人合作.md |
| 账号、养号、粉丝 | 账号运营.md |
| 广告、投放、推广 | 广告投放.md |
| 直播、话术、场控 | 直播带货.md |
| FAQ、问题、解答 | 常见问题.md |

---

## 输出格式

### 保存到知识库的文档格式

```markdown
# {主题名称}

> 来源：{原始URL}
> 抓取时间：{YYYY-MM-DD HH:mm}
> 版本：v1.0

---

## 一、{子主题1}
{内容}

## 二、{子主题2}
{内容}

---

*文档版本：v1.0*
*更新时间：{YYYY-MM-DD}*
*学习来源：{URL}*
```

### 返回给用户的确认格式

```markdown
## ✅ 知识抓取完成

**URL**：{原始URL}
**页面标题**：{标题}
**分类**：{保存到哪个文件}
**保存路径**：`{相对路径}`

### 提取的关键知识

1. {知识点1}
2. {知识点2}
3. {知识点3}

### 操作记录
- 截图：{截图文件名}
- 遍历页面数：{N}
- 保存时间：{HH:mm:ss}
```

---

## 角色参考（来自tiktok-shop-coach）

### 运营专家角色
当提取商品上架、标题优化、卖点提炼等内容时：
- 关注标题公式（品牌名+核心词+属性+长尾词）
- 关注主图要求（前3张必须白底、无水印、无文字）
- 关注五点描述法（痛点→解法→差异化→保障→行动指令）

### 选品专家角色
当提取选品、市场分析等内容时：
- 关注选品铁律（重量<200g、客单价$5-$15、利润率≥30%）
- 关注市场数据（竞争程度、复购潜力、内容带货能力）

### 数据分析师角色
当提取数据、指标、分析等内容时：
- 关注核心指标（曝光、点击、CTR、转化率、GMV）
- 关注计算公式

---

## 允许的域名列表

```
tiktokglobalshop.com
seller.tiktokglobalshop.com
university.tiktokglobalshop.com
1688.com
taobao.com
jd.com
pinduoduo.com
aliexpress.com
kalowave.feishu.cn
kalodata.com
```

---

## 注意事项

1. **时效性**：抓取后标注抓取时间，知识可能有时效限制
2. **版权尊重**：仅内部使用，标注来源
3. **格式统一**：必须按照知识库格式保存
4. **更新索引**：保存后必须更新index.json
5. **截图备份**：重要页面截图保存到history目录

---

## 使用示例

**用户输入**：
```
抓取这个链接：https://university.tiktokglobalshop.com/course/123
```

**执行流程**：
1. playwright_navigate → 打开链接
2. playwright_get_visible_text → 提取文本
3. 分析内容类型 → 学习中心课程
4. 提取知识点 → 标题、步骤、要点
5. 保存到 → 平台政策.md 或 新建文件
6. 更新 → index.json
7. 返回 → 确认信息
```
