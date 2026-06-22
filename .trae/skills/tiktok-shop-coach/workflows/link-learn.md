# 链接学习工作流程

## 触发条件

用户发送 TikTok Shop 相关链接（seller.tiktokglobalshop.com、university.tiktokglobalshop.com、1688.com 等）时触发。

## 执行步骤

### 1. 验证链接
检查域名是否在允许列表中：

**允许的域名**：
- tiktokglobalshop.com
- seller.tiktokglobalshop.com
- university.tiktokglobalshop.com
- 1688.com
- taobao.com
- jd.com
- pinduoduo.com
- aliexpress.com

**不在允许列表**：提示用户链接不在支持范围内。

### 2. 获取页面内容
使用 WebFetch 工具抓取页面内容：
- 提取标题
- 提取正文内容
- 提取相关链接

### 3. 智能遍历
根据页面内容，按优先级遍历相关链接（最多10个）：

**优先级**：
1. 同域名下的教程/指南链接
2. 平台官方文档链接
3. 相关产品/政策链接

### 4. 自动分类
根据内容关键词匹配分类：

| 关键词 | 分类 | 保存文件 |
|--------|------|----------|
| 选品、产品、品类 | 选品策略 | knowledge/选品策略.md |
| 上架、标题、主图 | 商品上架 | knowledge/商品上架.md |
| 定价、成本、利润 | 定价策略 | knowledge/定价策略.md |
| 冷启动、破零、新手 | 冷启动策略 | knowledge/冷启动策略.md |
| 政策、规则、考核 | 平台政策 | knowledge/平台政策.md |
| 短视频、视频制作 | 短视频制作 | knowledge/短视频制作.md |
| 账号、运营、粉丝 | 账号运营 | knowledge/账号运营.md |
| 达人、KOL、合作 | 达人合作 | knowledge/达人合作.md |
| 广告、投流、ADS | 广告投放 | knowledge/广告投放.md |
| 直播、livestream | 直播带货 | knowledge/直播带货.md |

### 5. 知识存储
将提取的内容保存到对应的知识库文件：

**存储格式**：
```markdown
## {标题}

**来源**：{URL}
**更新时间**：{日期}

{内容摘要}

### 关键要点
- 要点1
- 要点2
- 要点3

### 相关链接
- {链接1}
- {链接2}
```

### 6. 更新索引
更新 `knowledge/INDEX.md` 中的相关条目。

### 7. 返回确认
告知用户学习完成，总结学到的关键知识点。

## 错误处理

### 场景1：链接无法访问
**处理方式**：
1. 提示用户链接可能已失效
2. 建议用户检查链接是否正确
3. 询问是否有备用链接

### 场景2：页面内容为空
**处理方式**：
1. 尝试使用 Playwright 工具重新抓取
2. 如仍为空，提示用户手动提供内容
3. 记录失败链接，后续重试

### 场景3：无法确定分类
**处理方式**：
1. 询问用户该链接属于哪个主题
2. 根据用户指定分类保存
3. 如用户不确定，保存到 `knowledge/常见问题.md`

### 场景4：内容已存在
**处理方式**：
1. 检查是否已有相同来源的内容
2. 如有，询问用户是否更新
3. 更新时保留原有内容，追加新内容

## 输出格式

**确认消息**：
```
✅ 已学习并保存知识：
- 标题：{标题}
- 分类：{分类}
- 保存位置：{文件路径}
- 关键要点：{要点摘要}
```

## 示例

**用户输入**：
```
https://university.tiktokglobalshop.com/course/selling-on-tiktok-shop
```

**执行流程**：
1. 验证链接：✅ university.tiktokglobalshop.com
2. 获取内容：提取标题和正文
3. 遍历链接：发现5个相关教程链接
4. 自动分类：关键词匹配"冷启动"
5. 知识存储：保存到 knowledge/冷启动策略.md
6. 更新索引：更新 INDEX.md
7. 返回确认

**输出**：
```
✅ 已学习并保存知识：
- 标题：TikTok Shop 新手卖家入门指南
- 分类：冷启动策略
- 保存位置：knowledge/冷启动策略.md
- 关键要点：
  - 冷启动期重点在于测款和素材积累
  - 前15天不建议大量投流
  - 日更3-5条短视频是基础
```

## 相关参数

参考 `config/triggers.yaml` 中的：
- `link_learning.allowed_domains` - 允许的域名列表
- `link_learning.max_links_per_session` - 单次会话最大遍历数
