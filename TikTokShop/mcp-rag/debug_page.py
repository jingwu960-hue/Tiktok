#!/usr/bin/env python3
"""调试：查看 TikTok 卖家大学页面的实际 HTML 结构"""

import asyncio
from playwright.async_api import async_playwright

async def debug_page():
    url = "https://seller.tiktokglobalshop.com/university/essay?knowledge_id=7347389669721857&role=1&course_type=1&from=search&identity=1"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            locale="zh-CN"
        )
        page = await context.new_page()
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(8000)
            
            title = await page.title()
            print(f"标题: {title}")
            
            # 获取页面完整文本（前 2000 字）
            body_text = await page.inner_text("body")
            print(f"\n=== 页面全文 (前 2000 字) ===")
            print(body_text[:2000])
            
            # 分析 HTML 结构
            html = await page.content()
            
            # 查找可能的内容容器
            print("\n=== 可能的内容容器 ===")
            for sel in ["article", "main", "[class*='content']", "[class*='article']", 
                        "[class*='essay']", "[class*='course']", "[class*='lesson']",
                        "[class*='detail']", "[class*='body']", "[class*='text']",
                        "[class*='rich']", "[class*='editor']"]:
                elements = await page.query_selector_all(sel)
                if elements:
                    for el in elements[:2]:
                        text = await el.inner_text()
                        if len(text.strip()) > 50:
                            class_name = await el.get_attribute("class") or ""
                            tag = await el.evaluate("e => e.tagName")
                            print(f"  {tag}.{class_name[:80]} → {len(text)} 字")
            
            # 打印 HTML 结构（class/id）
            print("\n=== HTML 顶层结构 ===")
            structure = await page.evaluate("""() => {
                const result = [];
                const body = document.body;
                for (const child of body.children) {
                    const tag = child.tagName;
                    const id = child.id ? '#' + child.id : '';
                    const cls = child.className ? '.' + String(child.className).split(' ').join('.') : '';
                    const textLen = child.innerText?.length || 0;
                    result.push(`${tag}${id}${cls.substring(0, 60)} [${textLen}字]`);
                }
                return result;
            }""")
            for s in structure:
                print(f"  {s}")
                
        finally:
            await browser.close()

asyncio.run(debug_page())
