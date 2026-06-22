#!/usr/bin/env python3
"""完全后台化：通过双 fork 脱离所有父进程关联"""
import os
import sys

# 第一次 fork
pid = os.fork()
if pid > 0:
    print(f"First fork PID: {pid}")
    sys.exit(0)

# 第一次子进程：创建新会话
os.setsid()

# 第二次 fork
pid = os.fork()
if pid > 0:
    sys.exit(0)

# 现在是孤儿进程 + 新会话
# 写入 PID
pid = os.getpid()
with open('/tmp/smart_ingest.pid', 'w') as f:
    f.write(str(pid))

# 重定向 IO
sys.stdin = open('/dev/null', 'r')
log = open('/tmp/smart_ingest.log', 'a')
sys.stdout = log
sys.stderr = log

# 切换工作目录
os.chdir('/Users/wujing/QingZhen/Tiktok/TikTokShop/mcp-rag')

# 执行实际任务
import asyncio
sys.path.insert(0, '/Users/wujing/QingZhen/Tiktok/TikTokShop/mcp-rag')
from server import scrape_page, store_document, collection, load_catalog


async def main():
    import json
    from pathlib import Path
    cat = load_catalog().get('catalog', {})
    flat = []
    for cn, arts in cat.items():
        for a in arts:
            flat.append((cn, a))
    total = len(flat)
    print(f"\n[Daemon] PID={os.getpid()} PPID={os.getppid()}")
    print(f"[Daemon] Total: {total}", flush=True)

    pf = Path('/Users/wujing/QingZhen/Tiktok/TikTokShop/mcp-rag/ingest_progress.json')
    done = set()
    if pf.exists():
        try: done = set(json.loads(pf.read_text()))
        except: pass
    print(f"[Daemon] Resume: {len(done)} done", flush=True)

    success = empty = failed = 0
    import time
    t0 = time.time()
    target = 100

    for idx, (cn, a) in enumerate(flat):
        if success + empty + failed >= target:
            break
        url = a.get('url', '')
        title = a.get('title', '')
        if not url or url in done:
            continue
        try:
            r = await asyncio.wait_for(scrape_page(url), timeout=15)
            if r.get('content'):
                n = store_document(url, title, r['content'], category=cn)
                success += 1
                print(f"  [{idx+1}/{total}] ✓ {cn[:6]} | {title[:30]:30s} → {n}块 DB={collection.count()}", flush=True)
            elif r.get('error'):
                failed += 1
                print(f"  [{idx+1}/{total}] ✗ {title[:30]:30s} → {r['error']}", flush=True)
            else:
                empty += 1
                print(f"  [{idx+1}/{total}] ⊘ {title[:30]:30s} → 空", flush=True)
            done.add(url)
            if (success + empty + failed) % 3 == 0:
                pf.write_text(json.dumps(list(done), ensure_ascii=False))
        except asyncio.TimeoutError:
            failed += 1
            print(f"  [{idx+1}/{total}] ✗ {title[:30]:30s} → asyncio timeout", flush=True)
        except Exception as e:
            failed += 1
            print(f"  [{idx+1}/{total}] ✗ {title[:30]:30s} → {type(e).__name__}", flush=True)

    pf.write_text(json.dumps(list(done), ensure_ascii=False))
    dt = time.time() - t0
    print(f"\n[Daemon] 完成 成功:{success} 空:{empty} 失败:{failed} 耗时:{dt:.0f}s", flush=True)
    print(f"[Daemon] DB总分块: {collection.count()}", flush=True)


asyncio.run(main())
