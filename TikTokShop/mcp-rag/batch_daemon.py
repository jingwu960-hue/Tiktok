#!/usr/bin/env python3
"""
真正脱离父进程的后台导入脚本 - 使用 os.fork() + setsid
完全脱离 trae-sandbox 进程组
"""
import os
import sys
import json
import asyncio
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent

# 第一次 fork
pid = os.fork()
if pid > 0:
    # 父进程立即退出
    print(f"[Fork] Daemon PID: {pid}")
    sys.exit(0)

# 子进程：脱离会话
os.setsid()

# 第二次 fork（避免获得终端）
pid = os.fork()
if pid > 0:
    sys.exit(0)

# 现在我们是一个完全独立的守护进程
# 重定向标准 IO
sys.stdout.flush()
sys.stderr.flush()
with open('/dev/null', 'rb') as f:
    os.dup2(f.fileno(), 0)
log_file = open('/tmp/batch_daemon.log', 'a')
os.dup2(log_file.fileno(), 1)
os.dup2(log_file.fileno(), 2)

# 写入 PID 文件
with open('/tmp/batch_daemon.pid', 'w') as f:
    f.write(str(os.getpid()))

print(f"\n[Daemon] Started PID={os.getpid()}, PPID={os.getppid()}")
print(f"[Daemon] Args: {sys.argv}")

# 主逻辑
sys.path.insert(0, str(BASE))
from server import scrape_page, store_document, collection, load_catalog


def main():
    catalog = load_catalog().get("catalog", {})
    flat = []
    for cat_name, articles in catalog.items():
        for a in articles:
            flat.append((cat_name, a))
    total = len(flat)
    print(f"[Daemon] Total articles: {total}")

    progress_file = BASE / "ingest_progress.json"
    done_urls = set()
    if progress_file.exists():
        try:
            done_urls = set(json.loads(progress_file.read_text()))
            print(f"[Daemon] Resume from {len(done_urls)} done")
        except Exception:
            pass

    success = failed = empty = 0
    t0 = time.time()

    for idx, (cat_name, article) in enumerate(flat):
        url = article.get("url", "")
        title = article.get("title", "")

        if not url or url in done_urls:
            continue

        try:
            r = asyncio.run(scrape_page(url))
            if r.get("content"):
                n = store_document(url, title, r["content"], category=cat_name)
                success += 1
                elapsed = time.time() - t0
                rate = (success + empty + failed) / elapsed if elapsed > 0 else 0
                remaining = (total - idx - 1) / rate if rate > 0 else 0
                print(f"  [{idx+1}/{total}] ✓ {cat_name[:6]} | {title[:30]:30s} → {n}块 | "
                      f"剩{remaining/60:.1f}分 | DB={collection.count()}", flush=True)
            else:
                empty += 1
                print(f"  [{idx+1}/{total}] ⊘ {title[:30]:30s} → 空", flush=True)
            done_urls.add(url)

            # 每 5 篇保存一次进度
            if (success + empty + failed) % 5 == 0:
                progress_file.write_text(json.dumps(list(done_urls), ensure_ascii=False))

        except Exception as e:
            failed += 1
            print(f"  [{idx+1}/{total}] ✗ {title[:30]:30s} → {type(e).__name__}: {str(e)[:50]}")

    progress_file.write_text(json.dumps(list(done_urls), ensure_ascii=False))

    elapsed = time.time() - t0
    print(f"\n[完成] 成功:{success} 失败:{failed} 空:{empty} 耗时:{elapsed/60:.1f}分")
    print(f"[知识库] 总分块数: {collection.count()}")


if __name__ == "__main__":
    main()
