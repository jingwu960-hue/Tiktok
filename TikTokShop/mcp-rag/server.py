#!/usr/bin/env python3
"""
TikTok Seller University RAG MCP Server
========================================
将 TikTok 卖家大学知识页面抓取、分块、向量化，提供语义检索能力。

架构：
  Playwright 抓取 → HTML 解析 → Markdown 转换 → 文本分块 → ChromaDB 向量化 → 语义检索

MCP 工具：
  - ingest: 抓取指定 URL 并存入向量库
  - search: 语义检索知识库
  - list_knowledge: 列出已入库的知识条目
"""

import asyncio
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional

# MCP SDK
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# 抓取 & 解析
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from markdownify import markdownify as md

# 向量数据库
import chromadb

# ── 路径配置 ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "chroma_db"
CATALOG_FILE = BASE_DIR.parent / "知识库" / "卖家大学文章目录.json"

# ── ChromaDB 初始化 ──────────────────────────────────────
chroma_client = chromadb.PersistentClient(path=str(DB_DIR))
collection = chroma_client.get_or_create_collection(
    name="tiktok_university",
    metadata={"hnsw:space": "cosine"}
)

# ── MCP Server ────────────────────────────────────────────
server = Server("tiktok-university-rag")


# ══════════════════════════════════════════════════════════
#  工具定义
# ══════════════════════════════════════════════════════════

TOOLS = [
    Tool(
        name="ingest",
        description="抓取 TikTok 卖家大学页面并存入向量知识库。支持单个 URL 或从目录文件批量导入。",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "要抓取的页面 URL（单个模式）"
                },
                "batch": {
                    "type": "boolean",
                    "description": "是否从卖家大学文章目录批量导入",
                    "default": False
                },
                "category": {
                    "type": "string",
                    "description": "批量导入时指定分类名称（如 '跨境功能指南'），不填则导入全部"
                },
                "limit": {
                    "type": "integer",
                    "description": "批量导入时限制数量（每分类），0 或 -1 表示不限制，默认 0（全部）",
                    "default": 0
                }
            }
        }
    ),
    Tool(
        name="search",
        description="在 TikTok 卖家大学知识库中进行语义检索，返回最相关的知识片段。",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "检索查询内容"
                },
                "top_k": {
                    "type": "integer",
                    "description": "返回结果数量，默认 5",
                    "default": 5
                },
                "category": {
                    "type": "string",
                    "description": "按分类过滤（可选）"
                }
            },
            "required": ["query"]
        }
    ),
    Tool(
        name="list_knowledge",
        description="列出已入库的知识条目，可按分类筛选。",
        inputSchema={
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "按分类过滤（可选）"
                }
            }
        }
    ),
    Tool(
        name="catalog",
        description="查看卖家大学文章目录结构（分类和文章列表），不需要抓取。",
        inputSchema={
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "指定分类名称（可选），不填则列出所有分类"
                }
            }
        }
    ),
]


# ══════════════════════════════════════════════════════════
#  核心功能
# ══════════════════════════════════════════════════════════

async def scrape_page(url: str, max_retries: int = 2) -> dict:
    """用 Playwright 抓取页面，返回结构化内容（带重试）"""
    last_err = None
    for attempt in range(max_retries + 1):
        try:
            return await _scrape_once(url)
        except Exception as e:
            last_err = e
            if attempt < max_retries:
                await asyncio.sleep(2)
    return {"url": url, "title": "", "content": "", "content_length": 0, "error": str(last_err)}


async def _scrape_once(url: str) -> dict:
    """用 Playwright 抓取页面，返回结构化内容"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            locale="zh-CN"
        )
        page = await context.new_page()

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            # 等待动态内容渲染
            await page.wait_for_timeout(3000)

            # 提取标题
            title = await page.title()

            # 提取正文 - 尝试多种选择器（优先级从高到低）
            content = ""
            selectors = [
                # TikTok 卖家大学实际结构（最精确 → 最宽泛）
                "div[class*='EditorCorePanel']",       # 文章正文区域
                "div[class*='editor-core-panel']",    # 同上（小写）
                "div[class*='articleContent']",        # 文章内容容器
                "div[class*='articleDetailLayout']",   # 文章详情布局
                # 通用选择器
                ".article-content",
                ".course-content",
                ".lesson-content",
                "article",
                "main",
                "#content",
            ]
            for sel in selectors:
                el = await page.query_selector(sel)
                if el:
                    text = await el.inner_text()
                    if len(text.strip()) > 50:
                        content = await el.inner_html()
                        break

            if not content:
                content = await page.content()

            # 转为 Markdown
            md_content = html_to_markdown(content)

            return {
                "url": url,
                "title": title,
                "content": md_content,
                "content_length": len(md_content),
            }
        finally:
            await browser.close()


def html_to_markdown(html: str) -> str:
    """HTML → 干净的 Markdown"""
    soup = BeautifulSoup(html, "html.parser")

    # 移除无关元素
    for tag in soup(["script", "style", "nav", "footer", "header", "iframe", "noscript"]):
        tag.decompose()

    # 转 Markdown
    text = md(str(soup), heading_style="ATX", strip=["img"])

    # 清理
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = "\n".join(line.strip() for line in text.splitlines())
    text = text.strip()

    return text


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """将长文本分成重叠的小块，适合向量化"""
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        # 尝试在句子边界切分
        if end < len(text):
            for sep in ["\n\n", "。", ".", "\n", "；"]:
                last_sep = chunk.rfind(sep)
                if last_sep > chunk_size * 0.5:
                    chunk = chunk[:last_sep + len(sep)]
                    break

        chunks.append(chunk.strip())
        start += len(chunk) - overlap

    return [c for c in chunks if len(c) > 20]


def make_doc_id(url: str, chunk_idx: int) -> str:
    """生成文档 ID"""
    h = hashlib.md5(url.encode()).hexdigest()[:12]
    return f"{h}_{chunk_idx:03d}"


def store_document(url: str, title: str, content: str, category: str = "") -> int:
    """将文档分块后存入 ChromaDB"""
    chunks = chunk_text(content)
    if not chunks:
        return 0

    ids = []
    documents = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        doc_id = make_doc_id(url, i)
        ids.append(doc_id)
        documents.append(chunk)
        meta = {
            "url": url,
            "title": title,
            "chunk_index": i,
            "total_chunks": len(chunks),
        }
        if category:
            meta["category"] = category
        metadatas.append(meta)

    # 去重：删除已有的同 ID 文档
    existing = collection.get(ids=ids)
    if existing and existing["ids"]:
        collection.delete(ids=ids)

    collection.add(ids=ids, documents=documents, metadatas=metadatas)
    return len(chunks)


def load_catalog() -> dict:
    """加载卖家大学文章目录"""
    if not CATALOG_FILE.exists():
        return {}
    with open(CATALOG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ══════════════════════════════════════════════════════════
#  工具处理
# ══════════════════════════════════════════════════════════

@server.list_tools()
async def list_tools() -> list[Tool]:
    return TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "ingest":
            return await handle_ingest(arguments)
        elif name == "search":
            return await handle_search(arguments)
        elif name == "list_knowledge":
            return await handle_list(arguments)
        elif name == "catalog":
            return await handle_catalog(arguments)
        else:
            return [TextContent(type="text", text=f"未知工具: {name}")]
    except Exception as e:
        return [TextContent(type="text", text=f"错误: {type(e).__name__}: {e}")]


async def handle_ingest(args: dict) -> list[TextContent]:
    """处理知识导入"""
    # 处理字符串类型的参数转换
    batch = args.get("batch", False)
    if isinstance(batch, str):
        batch = batch.lower() in ['true', '1', 'yes']

    if batch:
        return await handle_batch_ingest(args)

    url = args.get("url")
    if not url:
        # 如果既没有 url 也没有 batch=True，默认执行批量导入
        return await handle_batch_ingest({})

    result = await scrape_page(url)
    if not result["content"]:
        return [TextContent(type="text", text=f"抓取失败或内容为空: {url}")]

    n_chunks = store_document(url, result["title"], result["content"])
    return [TextContent(type="text", text=(
        f"已入库: {result['title']}\n"
        f"  URL: {url}\n"
        f"  内容长度: {result['content_length']} 字符\n"
        f"  分块数: {n_chunks}"
    ))]


async def handle_batch_ingest(args: dict) -> list[TextContent]:
    """批量从目录导入"""
    catalog = load_catalog()
    if not catalog:
        return [TextContent(type="text", text="未找到卖家大学文章目录文件")]

    catalog_data = catalog.get("catalog", {})
    category = args.get("category", "")
    limit = args.get("limit", 10)

    # 处理字符串类型的 limit 参数
    if isinstance(limit, str):
        try:
            limit = int(limit)
        except ValueError:
            limit = 10

    no_limit = limit <= 0

    # 确定要导入的分类
    if category:
        categories = {category: catalog_data.get(category, [])}
        if not categories[category]:
            available = list(catalog_data.keys())
            return [TextContent(type="text", text=f"未找到分类 '{category}'\n可用分类: {', '.join(available)}")]
    else:
        categories = catalog_data  # 导入所有分类

    results = []
    total_chunks = 0

    for cat_name, articles in categories.items():
        count = 0
        for article in articles:
            if not no_limit and count >= limit:
                break
            url = article.get("url", "")
            title = article.get("title", "")
            if not url:
                continue

            try:
                result = await scrape_page(url)
                if result["content"]:
                    n = store_document(url, title, result["content"], category=cat_name)
                    total_chunks += n
                    results.append(f"  [{cat_name}/{count+1}] {title} → {n} 块")
                else:
                    results.append(f"  [{cat_name}/{count+1}] {title} → 内容为空，跳过")
                count += 1
            except Exception as e:
                results.append(f"  [{cat_name}/{count+1}] {title} → 失败: {e}")

    summary = f"批量导入完成\n总处理: {len(results)}\n总入库分块: {total_chunks}\n\n" + "\n".join(results[:50])
    if len(results) > 50:
        summary += f"\n... (省略 {len(results)-50} 条)"
    return [TextContent(type="text", text=summary)]


async def handle_search(args: dict) -> list[TextContent]:
    """语义检索"""
    query = args.get("query", "")
    top_k = args.get("top_k", 5)
    category = args.get("category", "")

    if not query:
        return [TextContent(type="text", text="请提供 query 参数")]

    where_filter = {"category": category} if category else None

    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        where=where_filter,
        include=["documents", "metadatas", "distances"]
    )

    if not results["documents"] or not results["documents"][0]:
        return [TextContent(type="text", text="未找到相关内容")]

    output_parts = []
    for i, (doc, meta, dist) in enumerate(zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    )):
        score = 1 - dist  # cosine distance → similarity
        output_parts.append(
            f"--- 结果 {i+1} (相关度: {score:.3f}) ---\n"
            f"标题: {meta.get('title', '未知')}\n"
            f"分类: {meta.get('category', '未分类')}\n"
            f"URL: {meta.get('url', '')}\n"
            f"分块: {meta.get('chunk_index', 0)+1}/{meta.get('total_chunks', '?')}\n\n"
            f"{doc}\n"
        )

    return [TextContent(type="text", text="\n".join(output_parts))]


async def handle_list(args: dict) -> list[TextContent]:
    """列出已入库知识"""
    category = args.get("category", "")

    where_filter = {"category": category} if category else None
    results = collection.get(where=where_filter, include=["metadatas"])

    if not results["ids"]:
        return [TextContent(type="text", text="知识库为空")]

    # 按 URL 聚合
    seen_urls = {}
    for meta in results["metadatas"]:
        url = meta.get("url", "")
        if url not in seen_urls:
            seen_urls[url] = {
                "title": meta.get("title", "未知"),
                "category": meta.get("category", "未分类"),
                "chunks": meta.get("total_chunks", 0),
            }

    lines = [f"已入库知识条目 ({len(seen_urls)} 篇):"]
    for url, info in seen_urls.items():
        cat_tag = f"[{info['category']}]" if info['category'] else ""
        lines.append(f"  {cat_tag} {info['title']} ({info['chunks']} 块)")

    return [TextContent(type="text", text="\n".join(lines))]


async def handle_catalog(args: dict) -> list[TextContent]:
    """查看文章目录"""
    catalog = load_catalog()
    if not catalog:
        return [TextContent(type="text", text="未找到卖家大学文章目录文件")]

    catalog_data = catalog.get("catalog", {})
    category = args.get("category", "")

    if category:
        articles = catalog_data.get(category, [])
        if not articles:
            return [TextContent(type="text", text=f"未找到分类 '{category}'\n可用: {', '.join(catalog_data.keys())}")]
        lines = [f"分类: {category} ({len(articles)} 篇)"]
        for a in articles[:20]:
            lines.append(f"  - {a.get('title', '')} (ID: {a.get('knowledge_id', '')})")
        if len(articles) > 20:
            lines.append(f"  ... 还有 {len(articles)-20} 篇")
        return [TextContent(type="text", text="\n".join(lines))]
    else:
        lines = [f"卖家大学文章目录 (共 {catalog.get('total_articles', '?')} 篇):"]
        for cat, articles in catalog_data.items():
            lines.append(f"  [{cat}] {len(articles)} 篇")
        return [TextContent(type="text", text="\n".join(lines))]


# ══════════════════════════════════════════════════════════
#  启动
# ══════════════════════════════════════════════════════════

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
if __name__ == "__main__":
    asyncio.run(main())
