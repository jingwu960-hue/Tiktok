#!/usr/bin/env python3
"""
智能批量导入 - 自动跳过已完成的 URL，每篇文章有独立的 15s 超时
"""
import sys
sys.path.insert(0, '/Users/wujing/QingZhen/Tiktok/TikTokShop/mcp-rag')
import asyncio
import time
import json
from pathlib import Path
from server import scrape_page, store_document, collection, load_catalog

BASE = Path('/Users/wujing/QingZhen/Tiktok/TikTokShop/mcp-rag')
MAX_PER_ARTICLE = 15  # 单篇最大耗时（含重试）


async def scrape_with_timeout(url, timeout):
    """带超时的抓取"""
    try:
        return await asyncio.wait_for(scrape_page(url), timeout=timeout)
    except asyncio.TimeoutError:
        return {"url": url, "title": "", "content": "", "content_length": 0, "error": "timeout"}


async def main(max_articles=0):
    cat = load_catalog().get('catalog', {})
    flat = []
    for cn, arts in cat.items():
        for a in arts:
            flat.append((cn, a))
    total = len(flat)
    print(f"[开始] 总文章: {total}, 目标: {'全部' if max_articles == 0 else max_articles}", flush=True)

    pf = BASE / "ingest_progress.json"
    done = set()
    if pf.exists():
        try: done = set(json.loads(pf.read_text()))
        except: pass
    print(f"[续传] 已完成: {len(done)}", flush=True)

    success = empty = failed = 0
    t0 = time.time()
    target = max_articles if max_articles > 0 else total

    for idx, (cn, a) in enumerate(flat):
        if success + empty + failed >= target:
            break
        url = a.get('url', '')
        title = a.get('title', '')
        if not url or url in done:
            continue

        t_art = time.time()
        r = await scrape_with_timeout(url, MAX_PER_ARTICLE)
        dt = time.time() - t_art

        if r.get('content'):
            n = store_document(url, title, r['content'], category=cn)
            success += 1
            print(f"  [{idx+1}/{total}] ✓ {cn[:6]} | {title[:30]:30s} → {n}块 ({dt:.1f}s) DB={collection.count()}", flush=True)
        elif r.get('error'):
            failed += 1
            print(f"  [{idx+1}/{total}] ✗ {title[:30]:30s} → {r['error']} ({dt:.1f}s)", flush=True)
        else:
            empty += 1
            print(f"  [{idx+1}/{total}] ⊘ {title[:30]:30s} → 空 ({dt:.1f}s)", flush=True)

        done.add(url)

        # 每 3 篇保存进度
        if (success + empty + failed) % 3 == 0:
            pf.write_text(json.dumps(list(done), ensure_ascii=False))

    pf.write_text(json.dumps(list(done), ensure_ascii=False))
    dt = time.time() - t0
    rate = (success + empty + failed) / dt if dt > 0 else 0
    print(f"\n[本轮] 成功:{success} 空:{empty} 失败:{failed} 耗时:{dt:.0f}s 速度:{rate*60:.1f}篇/分", flush=True)
    print(f"[DB] 总分块: {collection.count()}", flush=True)


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    asyncio.run(main(n))
