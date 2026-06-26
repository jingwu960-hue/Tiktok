#!/usr/bin/env python3
"""
TikTok 卖家大学 - 批量收集 knowledge_id
通过 Playwright 自动化点击菜单项，收集所有文章 knowledge_id
"""
import asyncio
import json
import os
import re
import sys
from pathlib import Path

# 输出目录
OUTPUT_DIR = Path(__file__).parent.parent
PROGRESS_FILE = OUTPUT_DIR / ".knowledge_ids_progress.json"
FAILED_FILE = OUTPUT_DIR / ".failed_records.json"

# 原始 URL
ORIG_URL = "https://seller.tiktokglobalshop.com/university/essay?knowledge_id=7347389669721857&role=1&course_type=1&from=search&identity=1"

async def main():
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        await page.goto(ORIG_URL, wait_until="networkidle")
        await page.wait_for_timeout(3000)
        
        # 加载进度
        progress = {"collected": {}, "last_global_index": 0, "total_collected": 0}
        if PROGRESS_FILE.exists():
            with open(PROGRESS_FILE) as f:
                progress = json.load(f)
        
        all_kids = progress.get("collected", {})
        global_index = progress.get("last_global_index", 0)
        
        print(f"已收集 {len(all_kids)} 个 knowledge_id，从索引 {global_index} 继续")
        
        max_items = 644
        batch_size = 20
        
        while global_index < max_items:
            try:
                # 检查菜单项数量
                items = await page.query_selector_all('.theme-arco-menu-item')
                items_count = len(items)
                print(f"\n当前菜单项: {items_count}，全局索引: {global_index}")
                
                if items_count == 0:
                    print("菜单为空，重新导航...")
                    await page.goto(ORIG_URL, wait_until="networkidle")
                    await page.wait_for_timeout(3000)
                    continue
                
                # 收集当前批次
                batch_collected = 0
                for i in range(min(batch_size, items_count)):
                    idx = i  # 当前菜单中的索引
                    
                    try:
                        item = items[idx]
                        text = await item.text_content()
                        text = text.strip()[:80]
                        
                        # 滚动到可见
                        await item.scroll_into_view_if_needed()
                        await item.click()
                        await page.wait_for_timeout(1500)
                        
                        url = page.url
                        kid = None
                        is_course = '/course?' in url
                        
                        if not is_course:
                            match = re.search(r'knowledge_id=(\d+)', url)
                            if match:
                                kid = match.group(1)
                        
                        if kid and kid not in all_kids:
                            all_kids[kid] = text
                            batch_collected += 1
                            print(f"  [{len(all_kids)}] {text[:50]} -> {kid}")
                        
                        # 检查菜单是否缩小
                        new_items = await page.query_selector_all('.theme-arco-menu-item')
                        if len(new_items) < items_count:
                            print(f"  菜单缩小: {items_count} -> {len(new_items)}，重新导航...")
                            await page.goto(ORIG_URL, wait_until="networkidle")
                            await page.wait_for_timeout(3000)
                            global_index += 1
                            break
                        
                    except Exception as e:
                        print(f"  错误 (索引 {idx}): {e}")
                        continue
                
                global_index += batch_size
                
                # 保存进度
                progress["collected"] = all_kids
                progress["last_global_index"] = global_index
                progress["total_collected"] = len(all_kids)
                with open(PROGRESS_FILE, 'w') as f:
                    json.dump(progress, f, ensure_ascii=False, indent=2)
                
                print(f"进度: {len(all_kids)} 个已收集，全局索引: {global_index}")
                
            except Exception as e:
                print(f"批次错误: {e}")
                await page.goto(ORIG_URL, wait_until="networkidle")
                await page.wait_for_timeout(3000)
        
        # 最终保存
        output_file = OUTPUT_DIR / ".all_knowledge_ids.json"
        with open(output_file, 'w') as f:
            json.dump(all_kids, f, ensure_ascii=False, indent=2)
        
        print(f"\n完成！共收集 {len(all_kids)} 个 knowledge_id")
        print(f"保存到: {output_file}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())