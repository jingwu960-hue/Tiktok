# TRAE IDE → TRAE Work 任务迁移计划

## 概述

将当前 TRAE IDE（Tiktok 项目）中的 Skill、规则、记忆、智能体配置、Hook 自动化和定时自动化任务迁移到 TRAE Work 中。

## 当前配置盘点

| 配置类型 | 位置 | 内容 |
|---------|------|------|
| **项目 Skill** | `.trae/skills/tiktok-shop-coach/SKILL.md` | TikTok Shop 越南站运营助手（1085行） |
| **项目 Skill** | `.trae/skills/电商图片越南语翻译与重绘/SKILL.md` | 电商图片翻译重绘 |
| **全局规则** | `~/.trae-cn/user_rules/rule-1780363616684.md` | "ai返回内容用中文展示" |
| **项目数据** | `.trae/data/shop-metrics.json` | 店铺指标数据 |
| **MCP Server** | `~/.trae-cn/mcps/s_Tiktok-8bc4dfb8/` | Playwright（dev_agent + solo_agent）、integrated_browser |
| **内置 Skill 开关** | `~/.trae-cn/skill-config.json` | 禁用 TRAE-dynamic-ui，启用 TRAE-code-review |
| **Hook 配置** | 无 | 未配置任何 Hook |
| **项目规则** | 无 `.trae/rules/` | 无项目级规则文件 |
| **AGENTS.md / CLAUDE.md** | 无 | 项目根目录无此类文件 |
| **定时自动化任务** | 无 | TRAE IDE 不支持原生定时任务 |

## 兼容性分析

| 配置类型 | TRAE IDE | TRAE Work | 迁移方式 | 难度 |
|---------|----------|-----------|---------|------|
| **Skill（技能）** | `.trae/skills/` | `.trae/skills/` + 上传导入 | 直接复制/打包上传 | 低 |
| **全局规则** | `~/.trae-cn/user_rules/` | 设置中心 UI | 手动重建 | 低 |
| **项目规则** | `.trae/rules/` | 不支持（用 AGENTS.md 替代） | 转为 AGENTS.md | 中 |
| **Agent（智能体）** | IDE 内部配置 | 不支持（用 Skill+Rule 替代） | 拆解为 Skill + Rule | 中 |
| **Memory（记忆）** | IDE 内部存储 | 不支持（用 Rule 替代） | 转为全局规则 | 中 |
| **Hook** | `hooks.json` | **不支持** | 无直接替代 | 高 |
| **定时自动化** | 不支持 | 原生支持 | 在 Work 中新建 | 低 |
| **MCP Server** | `~/.trae-cn/mcps/` | 需重新配置 | 在 Work 中重新添加 | 中 |

## 迁移步骤

### 步骤 1：迁移 Skill（兼容性最高，优先执行）

**目标**：将 2 个项目 Skill 迁移到 TRAE Work

**操作**：
1. 将 `.trae/skills/tiktok-shop-coach/` 目录打包为 `tiktok-shop-coach.zip`
2. 将 `.trae/skills/电商图片越南语翻译与重绘/` 目录打包为 `ecom-image-translate.zip`
3. 在 TRAE Work 桌面版中，打开同一项目目录（`/Users/wujing/QingZhen/Tiktok`）
4. 由于 TRAE Work 桌面版共享同一套 `.trae/` 目录结构，Skill 文件会自动被识别
5. 如使用网页版，需通过"技能管理中心 → 上传技能"手动导入 zip 包

**验证**：在 TRAE Work 对话中输入相关指令，确认 Skill 能被自动触发

### 步骤 2：创建全局规则

**目标**：将"ai返回内容用中文展示"规则迁移到 TRAE Work

**操作**：
1. 打开 TRAE Work → 设置 → 规则 → 创建规则
2. 输入规则内容："ai返回内容用中文展示"
3. 设置生效方式为"始终生效"

**验证**：在 TRAE Work 中发起对话，确认 AI 回复使用中文

### 步骤 3：创建 AGENTS.md（替代项目规则）

**目标**：为项目创建 AGENTS.md 文件，作为项目级行为指引

**操作**：
1. 在项目根目录 `/Users/wujing/QingZhen/Tiktok/` 创建 `AGENTS.md` 文件
2. 写入项目相关的行为指引（如：项目背景、TikTok Shop 越南站运营上下文、数据文件引用路径等）
3. 在 TRAE Work 设置 → 规则 → 导入设置中，开启"将 AGENTS.md 包含在上下文中"

**验证**：在 TRAE Work 中确认 AGENTS.md 内容被正确加载

### 步骤 4：重新配置 MCP Server

**目标**：在 TRAE Work 中添加 Playwright MCP Server

**操作**：
1. 打开 TRAE Work → 设置 → MCP Server → 添加
2. 查找并添加 Playwright MCP Server（从技能市场或手动配置）
3. 注意：`integrated_browser` 是 TRAE Work 内置的浏览器工具，无需额外配置

**验证**：在 TRAE Work 对话中测试浏览器相关操作

### 步骤 5：配置定时自动化任务（TRAE Work 独有功能）

**目标**：在 TRAE Work 中创建所需的定时自动化任务

**操作**：
1. 打开 TRAE Work → 左栏顶部"自动化"
2. 选择创建方式（推荐"在对话中创建"）
3. 描述任务内容和执行时间
4. 选择运行环境（云端/本地）和输出存储位置
5. 确认创建

**注意**：TRAE IDE 不支持定时自动化任务，此为 TRAE Work 新增能力，需根据实际业务需求定义任务内容

### 步骤 6：Hook 自动化替代方案

**目标**：为未来可能需要的 Hook 功能找到替代方案

**当前状态**：未配置任何 Hook，无需立即迁移

**替代方案备忘**：
- `SessionStart` 初始化逻辑 → 封装为 Skill
- `PreToolUse`/`PostToolUse` 校验逻辑 → 写入 Rule
- `Stop` 产出检查 → 融入 Skill 指令
- `Notification` 通知 → 使用 TRAE Work 的飞书集成

## 假设与决策

1. **假设** TRAE Work 桌面版打开同一项目目录时，`.trae/skills/` 目录下的 Skill 会被自动识别（基于两者共享 `.trae/` 目录结构）
2. **决策** 不迁移 Hook 配置（当前无 Hook 配置，且 TRAE Work 不支持 Hook）
3. **决策** 不迁移 Memory（需在 TRAE Work 中通过规则重新建立偏好）
4. **决策** 使用 AGENTS.md 替代项目级规则（TRAE Work 不支持 `.trae/rules/` 目录）

## 验证清单

- [ ] Skill `tiktok-shop-coach` 在 TRAE Work 中可正常触发
- [ ] Skill `电商图片越南语翻译与重绘` 在 TRAE Work 中可正常触发
- [ ] 全局规则"ai返回内容用中文展示"生效
- [ ] AGENTS.md 内容被正确加载到上下文
- [ ] MCP Server（Playwright）正常工作
- [ ] 定时自动化任务按预期执行（如有配置）
