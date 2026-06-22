#!/usr/bin/env python3
"""调试：检查每个选择器实际匹配到什么内容"""
import asyncio
from playwright.async_api import async_playwright

async def debug():
    url = "https://seller.tiktokglobalshop.com/university/essay?knowledge_id=7347389669721857&role=1&course_type=1&from=search&identity=1"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            locale="zh-CN"
        )
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(5000)

        selectors = [
            "section[class*='FrameworkContent']",
            "div[class*='articleDetailLayout']",
            "div[class*='articleContent']",
            "div[class*='EditorCorePanel']",
            "div[class*='editor-core-panel']",
        ]
        for sel in selectors:
            el = await page.query_selector(sel)
            if el:
                text = (await el.inner_text()).strip()
                html_len = len(await el.inner_html())
                print(f"SELECTOR: {sel}")
                print(f"  inner_text 长度: {len(text)}")
                print(f"  inner_html 长度: {html_len}")
                print(f"  前 200 字: {text[:200]}")
                print()
            else:
                print(f"SELECTOR: {sel} → 未匹配到元素\n")

        # 也试试直接用 body inner_text
        body_text = (await page.inner_text("body")).strip()
        print(f"BODY inner_text 长度: {len(body_text)}")
        print(f"BODY 前 300 字: {body_text[:300]}")

        await browser.close()

asyncio.run(debug())
