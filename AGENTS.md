# AGENTS.md - TikTok Shop 越南站运营项目

## 项目背景

本项目为 TikTok Shop 越南站跨境电商运营项目，专注于时尚配件类目（戒指、眼镜、手表、手镯等）。

## 关键信息

- **目标市场**：越南
- **店铺编码**：CNVNCBBRL4FX
- **TikTok 账号**：Cool Base（已注册）
- **启动日期**：2026-06-19
- **预算范围**：5000元以内
- **供货方式**：一件代发（1688/拼多多）
- **成本控制**：采购价 ≤20元，目标利润率 30% 以上

## 数据文件

- 店铺指标数据：`.trae/data/shop-metrics.json`
- 运营数据通过 `tiktok-shop-coach` Skill 自动维护

## 已安装技能

技能唯一事实源：`.trae/skills/`（`.qoder/skills` 已废弃移除）。

- `tiktok-shop-coach`：TikTok Shop 越南站运营智能助手（五大角色，详细资料见其 `knowledge/`）
- `knowledge-harvester`：从 URL 抓取电商知识并归档到 `TikTokShop/知识库/`
- `ecom-image-viet-translate`：电商详情页图片中文→越南语翻译与重绘

## 行为指引

- 所有 AI 回复使用中文
- 日期相关操作需先通过 `date` 命令获取当前日期
- 货币显示同时标注 VND 和人民币
- 运营数据保存到 `.trae/data/shop-metrics.json`
