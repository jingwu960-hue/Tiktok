#!/bin/bash
# run_batch.sh - 在用户终端运行的后台批量导入脚本
# 用途：脱离 Trae 沙箱限制，连续跑完全部 644 篇
# 用法：bash run_batch.sh

cd /Users/wujing/QingZhen/Tiktok/TikTokShop/mcp-rag

# 创建带 KeepAlive 的 launchd 任务（自动重启被中断的进程）
PLIST=~/Library/LaunchAgents/com.user.tiktok.batch.plist
mkdir -p ~/Library/LaunchAgents

cat > "$PLIST" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.tiktok.batch</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/wujing/QingZhen/Tiktok/TikTokShop/mcp-rag/.venv/bin/python</string>
        <string>-u</string>
        <string>/Users/wujing/QingZhen/Tiktok/TikTokShop/mcp-rag/auto_runner.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/wujing/QingZhen/Tiktok/TikTokShop/mcp-rag</string>
    <key>StandardOutPath</key>
    <string>/tmp/launchd_auto.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/launchd_auto.log</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>ThrottleInterval</key>
    <integer>10</integer>
</dict>
</plist>
EOF

# 重新加载 launchd 任务
launchctl unload "$PLIST" 2>/dev/null
launchctl load "$PLIST"

echo ""
echo "=========================================="
echo "批量导入已启动！"
echo "=========================================="
echo ""
echo "查看实时进度："
echo "  tail -f /tmp/launchd_auto.log"
echo ""
echo "查看知识库大小："
echo "  cd /Users/wujing/QingZhen/Tiktok/TikTokShop/mcp-rag && .venv/bin/python -c \"import sys; sys.path.insert(0,'.'); from server import collection; print('已入库分块:', collection.count())\""
echo ""
echo "停止任务："
echo "  launchctl unload ~/Library/LaunchAgents/com.user.tiktok.batch.plist"
echo ""
echo "预计耗时: 60-90 分钟（644 篇 × ~10 秒）"
echo "=========================================="
