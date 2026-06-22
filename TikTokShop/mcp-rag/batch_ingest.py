#!/usr/bin/env python3
"""
直接调用 server.py 的核心函数批量导入所有 644 篇知识。
不经过 MCP stdio，避免长任务超时。
"""
import sys
import json
import asyncio
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

# 复用 server 里的核心组件
from server import scrape_page, store_document, collection, load_catalog


async def main():
    catalog = load_catalog()
    catalog_data = catalog.get("catalog", {})
    total_articles = sum(len(v) for v in catalog_data.values())
    print(f"[开始] 总文章数: {total_articles}")
    print(f"[分类] {[(k, len(v)) for k, v in catalog_data.items()]}")
    print(f"[当前知识库] 已存在: {collection.count()} 个分块")
    print("=" * 60)

    start = time.time()
    success = 0
    failed = 0
    empty = 0
    total_chunks = 0

    # 进度文件 - 断点续传
    progress_file = BASE / "ingest_progress.json"
    done_urls = set()
    if progress_file.exists():
        try:
            done_urls = set(json.loads(progress_file.read_text()))
            print(f"[续传] 已完成 {len(done_urls)} 个 URL，将跳过")
        except Exception:
            pass

    save_every = 10

    for cat_name, articles in catalog_data.items():
        print(f"\n[分类] {cat_name} ({len(articles)} 篇)")
        for i, article in enumerate(articles, 1):
            url = article.get("url", "")
            title = article.get("title", "")

            if not url or url in done_urls:
                continue

            try:
                t0 = time.time()
                result = await scrape_page(url)
                dt = time.time() - t0

                if result.get("content"):
                    n = store_document(url, title, result["content"], category=cat_name)
                    total_chunks += n
                    success += 1
                    print(f"  [{i:3d}/{len(articles)}] ✓ {title[:40]:40s} → {n:2d}块 ({dt:.1f}s)")
                else:
                    empty += 1
                    print(f"  [{i:3d}/{len(articles)}) ⊘ {title[:40]:40s} → 空内容")

                done_urls.add(url)

                # 定期保存进度
                if (success + empty) % save_every == 0:
                    progress_file.write_text(json.dumps(list(done_urls), ensure_ascii=False))
                    elapsed = time.time() - start
                    rate = len(done_urls) / elapsed if elapsed > 0 else 0
                    remaining = (total_articles - len(done_urls)) / rate if rate > 0 else 0
                    print(f"  [进度] 已完成 {len(done_urls)}/{total_articles}, "
                          f"速度 {rate*60:.1f} 篇/分, 预计剩余 {remaining/60:.1f} 分钟")

            except Exception as e:
                failed += 1
                print(f"  [{i:3d}/{len(articles)}] ✗ {title[:40]:40s} → {type(e).__name__}: {e}")

    # 最终保存
    progress_file.write_text(json.dumps(list(done_urls), ensure_ascii=False))

    elapsed = time.time() - start
    print("\n" + "=" * 60)
    print(f"[完成] 成功: {success}, 失败: {failed}, 空内容: {empty}")
    print(f"[知识库] 总分块数: {collection.count()}")
    print(f"[耗时] {elapsed/60:.1f} 分钟")


if __name__ == "__main__":
    asyncio.run(main())
