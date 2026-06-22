#!/usr/bin/env python3
"""测试 MCP Server 的抓取功能"""

import asyncio
import sys
sys.path.insert(0, '/Users/wujing/QingZhen/Tiktok/TikTokShop/mcp-rag')

from server import scrape_page, store_document, collection

async def test_scrape():
    """测试抓取单个页面"""
    url = "https://seller.tiktokglobalshop.com/university/essay?knowledge_id=7347389669721857&role=1&course_type=1&from=search&identity=1"
    
    print("正在抓取页面...")
    result = await scrape_page(url)
    
    print(f"\n标题: {result['title']}")
    print(f"内容长度: {result['content_length']} 字符")
    print(f"\n内容预览 (前 500 字):\n{result['content'][:500]}")
    
    # 存入数据库
    print("\n正在存入向量库...")
    n_chunks = store_document(url, result['title'], result['content'])
    print(f"已分块: {n_chunks} 块")
    
    # 测试检索
    print("\n测试语义检索...")
    query = "如何管理订单"
    results = collection.query(
        query_texts=[query],
        n_results=3,
        include=["documents", "metadatas", "distances"]
    )
    
    print(f"\n检索结果 (query: '{query}'):")
    for i, (doc, meta, dist) in enumerate(zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    )):
        score = 1 - dist
        print(f"\n[{i+1}] 相关度: {score:.3f}")
        print(f"    标题: {meta.get('title', '未知')}")
        print(f"    内容: {doc[:100]}...")

if __name__ == "__main__":
    asyncio.run(test_scrape())
