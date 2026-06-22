#!/usr/bin/env python3
"""
auto_runner - 自动循环运行 smart_ingest 直至全部 644 篇完成
每次运行 50 篇（约 8 分钟），如果被 kill 就重新启动接着跑
"""
import sys
import os
import time
import json
import subprocess
from pathlib import Path

BASE = Path('/Users/wujing/QingZhen/Tiktok/TikTokShop/mcp-rag')
LOG = '/tmp/auto_runner.log'


def log(msg):
    ts = time.strftime('%H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG, 'a') as f:
        f.write(line + '\n')


def main():
    log("=== Auto Runner 启动 ===")
    # 加载进度
    pf = BASE / 'ingest_progress.json'
    while True:
        if pf.exists():
            try:
                done = len(json.loads(pf.read_text()))
            except:
                done = 0
        else:
            done = 0

        log(f"已完成: {done}/644")

        if done >= 644:
            log("全部完成！")
            break

        # 运行一批 50 篇
        log(f"启动一批 50 篇...")
        result = subprocess.run(
            [str(BASE / '.venv/bin/python'), '-u', str(BASE / 'smart_ingest.py'), '50'],
            cwd=str(BASE)
        )
        log(f"本批退出码: {result.returncode}")
        time.sleep(2)


if __name__ == "__main__":
    main()
