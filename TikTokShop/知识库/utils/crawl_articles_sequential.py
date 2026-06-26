#!/usr/bin/env python3
"""
逐篇抓取 TikTok 卖家大学文章
每次点击菜单项后等待 2 秒，提取内容并保存
"""
import json
import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# 配置
KNOWLEDGE_BASE = Path("/Users/wujing/QingZhen/Tiktok/TikTokShop/知识库")
PROGRESS_FILE = KNOWLEDGE_BASE / ".crawl_progress.json"
ORIG_URL = "https://seller.tiktokglobalshop.com/university/essay?knowledge_id=7347389669721857&role=1&course_type=1&from=search&identity=1"

def load_progress():
    """加载进度"""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"completed": [], "failed": [], "last_index": 0}

def save_progress(progress):
    """保存进度"""
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

def extract_article_content(page):
    """提取当前页面的文章内容"""
    try:
        # 等待内容加载
        page.wait_for_timeout(2000)
        
        # 获取 URL 和 knowledge_id
        url = page.url
        kid_match = url.split('knowledge_id=')
        kid = kid_match[1].split('&')[0] if len(kid_match) > 1 else None
        
        # 获取标题
        title = page.title()
        
        # 提取内容区域
        content_section = page.query_selector('section[class*="contentWrapper"]')
        if not content_section:
            return None
        
        text = content_section.inner_text()
        
        return {
            "knowledge_id": kid,
            "title": title,
            "url": url,
            "content": text,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        print(f"  提取内容失败: {e}")
        return None

def save_article(article):
    """保存文章到知识库"""
    if not article or not article.get("knowledge_id"):
        return False
    
    kid = article["knowledge_id"]
    title = article["title"].replace("/", "_").replace("\\", "_").replace(":", "_").replace("*", "_").replace("?", "_").replace('"', "_").replace("<", "_").replace(">", "_").replace("|", "_")
    
    filename = f"{kid}_{title}.md"
    filepath = KNOWLEDGE_BASE / filename
    
    content = f"# {article['title']}\n\n"
    content += f"> knowledge_id: {kid}\n"
    content += f"> URL: {article['url']}\n"
    content += f"> 抓取时间: {article['timestamp']}\n\n"
    content += "---\n\n"
    content += article["content"]
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def main():
    print("开始逐篇抓取 TikTok 卖家大学文章...")
    
    progress = load_progress()
    completed_kids = set(progress["completed"])
    
    print(f"已完成: {len(completed_kids)} 篇")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # 打开原始页面
        print("打开页面...")
        page.goto(ORIG_URL, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)
        
        # 获取所有菜单项
        menu_items = page.query_selector_all('.theme-arco-menu-item')
        total_items = len(menu_items)
        print(f"找到 {total_items} 个菜单项")
        
        # 从上次中断的地方继续
        start_index = progress.get("last_index", 0)
        print(f"从第 {start_index} 项开始")
        
        for i in range(start_index, total_items):
            try:
                # 重新获取菜单项（因为页面可能刷新）
                menu_items = page.query_selector_all('.theme-arco-menu-item')
                if i >= len(menu_items):
                    print(f"菜单项数量变化，跳过第 {i} 项")
                    continue
                
                menu_item = menu_items[i]
                menu_text = menu_item.inner_text().strip()
                
                print(f"\n[{i+1}/{total_items}] 正在处理: {menu_text[:50]}")
                
                # 点击菜单项
                menu_item.scroll_into_view_if_needed()
                menu_item.click()
                
                # 等待页面加载
                page.wait_for_timeout(2000)
                
                # 提取内容
                article = extract_article_content(page)
                
                if article:
                    kid = article["knowledge_id"]
                    
                    # 检查是否已完成
                    if kid in completed_kids:
                        print(f"  已跳过 (已完成)")
                        continue
                    
                    # 保存文章
                    if save_article(article):
                        print(f"  已保存: {kid}")
                        progress["completed"].append(kid)
                        completed_kids.add(kid)
                    else:
                        print(f"  保存失败")
                        progress["failed"].append({"index": i, "text": menu_text, "error": "保存失败"})
                else:
                    print(f"  提取失败")
                    progress["failed"].append({"index": i, "text": menu_text, "error": "提取失败"})
                
                # 更新进度
                progress["last_index"] = i + 1
                save_progress(progress)
                
                # 每 10 篇打印一次统计
                if (i + 1) % 10 == 0:
                    print(f"\n=== 进度统计 ===")
                    print(f"已处理: {i + 1}/{total_items}")
                    print(f"已完成: {len(progress['completed'])}")
                    print(f"失败: {len(progress['failed'])}")
                    print(f"================\n")
                
            except Exception as e:
                print(f"  处理失败: {e}")
                progress["failed"].append({"index": i, "text": menu_text if 'menu_text' in locals() else "unknown", "error": str(e)})
                save_progress(progress)
                continue
        
        print("\n抓取完成！")
        print(f"总共: {total_items}")
        print(f"成功: {len(progress['completed'])}")
        print(f"失败: {len(progress['failed'])}")
        
        browser.close()

if __name__ == "__main__":
    main()
