#!/usr/bin/env python3
"""检查 MCP RAG 项目所需依赖"""

modules = {
    'playwright': 'Playwright (浏览器抓取)',
    'chromadb': 'ChromaDB (向量数据库)',
    'faiss': 'FAISS (向量数据库)',
    'tiktoken': 'Tiktoken (文本分块)',
    'openai': 'OpenAI (Embedding API)',
    'requests': 'Requests (HTTP)',
    'bs4': 'BeautifulSoup4 (HTML解析)',
    'markdownify': 'Markdownify (HTML转MD)',
}

for mod, desc in modules.items():
    try:
        __import__(mod)
        print(f"  OK  {desc} ({mod})")
    except ImportError:
        print(f"  MISSING  {desc} ({mod})")
