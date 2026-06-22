import sys
sys.path.insert(0, '/Users/wujing/QingZhen/Tiktok/TikTokShop/mcp-rag')
import asyncio
import time
import json
from pathlib import Path
from server import scrape_page, store_document, collection, load_catalog

BASE = Path('/Users/wujing/QingZhen/Tiktok/TikTokShop/mcp-rag')

async def main(start, count):
    cat = load_catalog().get('catalog', {})
    flat = []
    for cn, arts in cat.items():
        for a in arts:
            flat.append((cn, a))
    total = len(flat)
    end = min(start + count, total)

    pf = BASE / "ingest_progress.json"
    done = set()
    if pf.exists():
        try: done = set(json.loads(pf.read_text()))
        except: pass

    success = empty = failed = 0
    t0 = time.time()
    for idx in range(start, end):
        cn, a = flat[idx]
        url = a.get('url','')
        title = a.get('title','')
        if not url or url in done:
            continue
        try:
            r = await scrape_page(url)
            if r.get('content'):
                # 用 H1 替换默认标题
                real_title = a['title']  # 保留目录中的标题
                n = store_document(url, real_title, r['content'], category=cn)
                success += 1
                print(f"  [{idx+1}/{total}] ✓ {cn[:6]} | {title[:30]:30s} → {n}块 | DB={collection.count()}", flush=True)
            else:
                empty += 1
                print(f"  [{idx+1}/{total}] ⊘ {title[:30]:30s} → 空", flush=True)
            done.add(url)
        except Exception as e:
            failed += 1
            print(f"  [{idx+1}/{total}] ✗ {title[:30]:30s} → {type(e).__name__}", flush=True)

    pf.write_text(json.dumps(list(done), ensure_ascii=False))
    dt = time.time() - t0
    print(f"\n[本批] 成功:{success} 空:{empty} 失败:{failed} 耗时:{dt:.0f}s", flush=True)
    print(f"[DB] 总分块: {collection.count()}", flush=True)

if __name__ == "__main__":
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    asyncio.run(main(start, count))
