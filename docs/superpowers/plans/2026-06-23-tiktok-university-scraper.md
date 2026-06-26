# TikTok 卖家大学文章抓取实施计划

> **For agentic workers:** 本计划使用 Playwright MCP + AI 处理，非传统代码编写。步骤使用 checkbox (`- [ ]`) 跟踪。

**Goal:** 从 TikTok 卖家大学抓取所有文章，经双层过滤后保存到本地知识库

**Architecture:** Playwright MCP 浏览器自动化提取菜单和文章内容，AI 执行关键词匹配 + 角色视角提炼，最终保存为 Markdown 文件到知识库目录

**Tech Stack:** Playwright MCP（浏览器自动化）、AI 文本处理、Markdown 文件存储

## Global Constraints

- 知识库保存路径：`/Users/wujing/QingZhen/Tiktok/TikTokShop/知识库/`
- 文件命名：`卖家大学-{分类}-{文章标题}.md`
- 每篇文章头部需包含 HTML 注释元信息（source、categories、roles、crawled_at）
- 需更新 `index.json` 的 entries 数组
- 11 个知识库类目 + 6 个角色作为过滤标准
- 所有输出使用中文

---

### Task 1: 菜单提取 — 打开页面并提取左侧菜单树

**MCP 工具：**
- `mcp_Playwright` / `playwright_navigate`
- `mcp_Playwright` / `playwright_evaluate`
- `mcp_Playwright` / `playwright_screenshot`

**产出：** 菜单树 JSON（含层级、名称、链接/article_id）

- [ ] **Step 1: 导航到目标页面**

```json
// 调用 playwright_navigate
{
  "server_name": "mcp_Playwright",
  "tool_name": "playwright_navigate",
  "args": {
    "url": "https://seller.tiktokglobalshop.com/university/essay?knowledge_id=7347389669721857&role=1&course_type=1&from=search&identity=1",
    "wait_until": "networkidle"
  }
}
```

预期：页面加载成功，左侧菜单栏可见

- [ ] **Step 2: 截图确认页面状态**

```json
// 调用 playwright_screenshot
{
  "server_name": "mcp_Playwright",
  "tool_name": "playwright_screenshot",
  "args": {}
}
```

预期：截图显示页面正常加载，左侧菜单可见

- [ ] **Step 3: 提取菜单 DOM 结构**

```json
// 调用 playwright_evaluate，执行 JS 提取菜单树
{
  "server_name": "mcp_Playwright",
  "tool_name": "playwright_evaluate",
  "args": {
    "script": "() => { const buildMenuTree = (container) => { const items = []; const menuItems = container.querySelectorAll(':scope > li, :scope > .menu-item, :scope > [class*=\"menu\"], :scope > [class*=\"sidebar\"] > *'); if (menuItems.length === 0) { const allItems = container.children; for (const el of allItems) { const text = el.textContent?.trim().substring(0, 100); const link = el.querySelector('a'); const isExpandable = el.querySelector('ul, [class*=\"sub\"], [class*=\"child\"]'); items.push({ label: text, href: link?.href || null, articleId: link?.href?.match(/knowledge_id=(\\d+)/)?.[1] || null, hasChildren: !!isExpandable, children: isExpandable ? buildMenuTree(isExpandable) : [] }); } } else { for (const el of menuItems) { const text = el.textContent?.trim().substring(0, 100); const link = el.querySelector('a'); const isExpandable = el.querySelector('ul, [class*=\"sub\"], [class*=\"child\"]'); items.push({ label: text, href: link?.href || null, articleId: link?.href?.match(/knowledge_id=(\\d+)/)?.[1] || null, hasChildren: !!isExpandable, children: isExpandable ? buildMenuTree(isExpandable) : [] }); } } return items; }; const sidebar = document.querySelector('aside, .sidebar, [class*=\"sidebar\"], [class*=\"menu\"], .nav, nav'); if (!sidebar) return { error: 'sidebar not found', selectors: document.body.innerHTML.substring(0, 2000) }; return buildMenuTree(sidebar); }"
  }
}
```

预期：返回菜单树 JSON，包含所有菜单项及其层级

- [ ] **Step 4: 如果菜单在 iframe 中，用 iframe 方式提取**

```json
// 先检测 iframe
{
  "server_name": "mcp_Playwright",
  "tool_name": "playwright_evaluate",
  "args": {
    "script": "() => { const iframes = document.querySelectorAll('iframe'); return Array.from(iframes).map(f => ({ src: f.src, id: f.id, className: f.className })); }"
  }
}
```

如果检测到 iframe 包含菜单，则使用 `playwright_iframe_click` 系列工具操作。

- [ ] **Step 5: 展开所有折叠菜单项，获取完整树**

对于菜单树中 `hasChildren: true` 的节点，逐个点击展开，重新提取以获得完整结构。

- [ ] **Step 6: 保存菜单树到临时文件**

将菜单树 JSON 保存到 `/Users/wujing/QingZhen/Tiktok/TikTokShop/知识库/.menu_tree.json`

---

### Task 2: 文章抓取 — 遍历菜单树抓取每篇文章

**MCP 工具：**
- `mcp_Playwright` / `playwright_click`
- `mcp_Playwright` / `playwright_navigate`
- `mcp_Playwright` / `playwright_get_visible_text`
- `mcp_Playwright` / `playwright_get_visible_html`

**产出：** 每篇文章的原始文本，保存为 `.raw.md`

- [ ] **Step 1: 读取菜单树**

从 `/Users/wujing/QingZhen/Tiktok/TikTokShop/知识库/.menu_tree.json` 读取菜单树，生成所有叶子节点的抓取队列。

- [ ] **Step 2: 遍历抓取（每批 10 篇）**

对每个叶子节点：

a) 如果是 articleId 类型（同站内文章）：
```json
// 点击菜单项
{
  "server_name": "mcp_Playwright",
  "tool_name": "playwright_click",
  "args": {
    "selector": "包含菜单项文本的选择器"
  }
}
```
等待 2-3 秒内容加载。

b) 如果是外部链接：
```json
// 导航到外部链接
{
  "server_name": "mcp_Playwright",
  "tool_name": "playwright_navigate",
  "args": {
    "url": "外部链接URL"
  }
}
```

- [ ] **Step 3: 提取文章内容**

```json
// 获取可见文本
{
  "server_name": "mcp_Playwright",
  "tool_name": "playwright_get_visible_text",
  "args": {}
}
```

- [ ] **Step 4: 保存原始文章**

将每篇文章保存为：
`/Users/wujing/QingZhen/Tiktok/TikTokShop/知识库/.raw/{序号}-{标题}.raw.md`

内容格式：
```markdown
# {标题}

来源: {URL}
抓取时间: {timestamp}

---

{文章正文}
```

- [ ] **Step 5: 完成后返回菜单页**

如果是外部链接，导航回原始页面，重新定位菜单位置。

---

### Task 3: 内容提炼 — 双层过滤

**处理方式：** AI 直接处理文本，无需 MCP 工具

**产出：** 提炼后的文章内容

- [ ] **Step 1: 第一层过滤 — 关键词匹配**

对每篇原始文章，检查是否包含以下任一关键词（不区分大小写）：

**11 个知识库类目关键词：**
选品、商品选择、上架、商品发布、定价、价格、成本、利润、视频、短视频、内容创作、直播、达人、KOL、网红、合作、联盟、广告、投放、推广、账号、粉丝、冷启动、新店、破零、平台政策、规则、考核、违规、常见问题、FAQ

**店铺相关关键词：**
越南、东南亚、跨境、时尚、饰品、配件、戒指、眼镜、手表、手镯、无货源、一件代发

**不包含任何关键词的文章 → 标记为"丢弃"，记录到报告**

- [ ] **Step 2: 第二层过滤 — 角色视角提炼**

对通过第一层的文章，按 6 个角色视角提取关键信息：

| 角色 | 提取关注点 |
|------|-----------|
| 运营总监 | 战略规划、风险管控、资源分配、长期布局 |
| 运营教练 | 可执行步骤、时间节点、冷启动方法、每日任务 |
| 选品专家 | 选品方法论、品类分析、利润计算、市场洞察 |
| 运营专家 | 上架技巧、标题公式、SEO、卖点提炼、主图要求 |
| 数据分析师 | 指标定义、数据解读、优化策略、ROI 分析 |
| 脚本编剧 | 视频素材、故事案例、痛点场景、钩子灵感 |

提炼规则：
- 同一篇文章可被多个角色复用
- 每个角色只提取与自己相关的段落/要点
- 合并去重，避免重复内容
- 保留原文关键数据、数字、公式

---

### Task 4: 保存入库 — 写入知识库并更新索引

**文件操作：** Write 工具写入 .md 文件，Edit 工具更新 index.json

**产出：** 知识库 .md 文件 + 更新后的 index.json + 抓取报告

- [ ] **Step 1: 为每篇提炼后的文章生成 .md 文件**

保存路径：`/Users/wujing/QingZhen/Tiktok/TikTokShop/知识库/卖家大学-{分类}-{文章标题}.md`

文件格式：
```markdown
<!-- source: {原始URL} -->
<!-- categories: {匹配的知识库类目，逗号分隔} -->
<!-- roles: {关联的角色，逗号分隔} -->
<!-- crawled_at: 2026-06-23 -->

# {文章标题}

> 原始来源：{URL}

{提炼后的内容，按角色分段}
```

- [ ] **Step 2: 更新 index.json**

在 `/Users/wujing/QingZhen/Tiktok/TikTokShop/知识库/index.json` 的 `entries` 数组中新增条目：

```json
{
  "keywords": ["从文章提取的关键词"],
  "file": "卖家大学-{分类}-{文章标题}.md",
  "topics": ["文章涉及的主题"],
  "priority": 2,
  "source": "卖家大学",
  "source_url": "{原始URL}"
}
```

同时更新 `total_entries` 和 `last_updated`。

- [ ] **Step 3: 生成抓取报告**

创建 `/Users/wujing/QingZhen/Tiktok/TikTokShop/知识库/.crawl_report.md`：

```markdown
# TikTok 卖家大学抓取报告

- 抓取时间：2026-06-23
- 菜单项总数：{N}
- 成功抓取：{N}
- 通过第一层过滤：{N}
- 最终保存：{N}
- 丢弃：{N}

## 各类目分布

| 类目 | 数量 |
|------|------|
| 选品策略 | N |
| 商品上架 | N |
| ... | ... |

## 丢弃文章列表

| 标题 | 原因 |
|------|------|
| ... | 无相关关键词 |
```

- [ ] **Step 4: 清理临时文件**

删除 `.menu_tree.json` 和 `.raw/` 目录。