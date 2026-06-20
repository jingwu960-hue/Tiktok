#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, '/Users/wujing/QingZhen/Tiktok/TikTokShop/知识库/utils')

from persistence import KnowledgePersistence

def test_persistence_system():
    print("🚀 开始测试知识持久化系统...")
    
    kp = KnowledgePersistence()
    print("✅ 系统初始化成功")
    
    print("\n📊 当前统计信息：")
    stats = kp.get_statistics()
    print(f"   - 总条目数：{stats.get('total_entries', 0)}")
    print(f"   - 备份次数：{stats.get('backup_count', 0)}")
    print(f"   - 最后更新：{stats.get('last_updated', 'N/A')}")
    
    test_knowledge = "选品技巧：越南市场爆款商品通常具备以下特点：轻小件（<200g）、客单价$5-$15、解决痛点需求"
    
    print("\n📝 测试自动知识捕获...")
    result = kp.capture_knowledge(test_knowledge, context="测试自动捕获功能")
    print(f"   结果：{result.get('message', '未知')}")
    if result.get('success'):
        print(f"   条目ID：{result.get('entry_id')}")
        print(f"   分类：{result.get('category')}")
        print(f"   版本：{result.get('version')}")
    
    test_knowledge2 = "Q:如何提高商品曝光？A:优化标题关键词、制作高质量主图、设置合理价格、参与平台活动"
    print("\n📝 测试问答形式知识捕获...")
    result2 = kp.capture_knowledge(test_knowledge2, context="测试问答形式")
    print(f"   结果：{result2.get('message', '未知')}")
    
    print("\n🔍 测试知识搜索...")
    results = kp.search_knowledge("选品")
    print(f"   找到 {len(results)} 条相关知识")
    for i, r in enumerate(results, 1):
        print(f"   {i}. {r['category']}")
    
    print("\n📦 测试备份功能...")
    backup_result = kp.create_backup()
    print(f"   结果：{backup_result.get('message', '未知')}")
    if backup_result.get('success'):
        print(f"   备份文件：{backup_result.get('backup_file')}")
    
    print("\n📊 更新后的统计信息：")
    stats = kp.get_statistics()
    print(f"   - 总条目数：{stats.get('total_entries', 0)}")
    print(f"   - 备份次数：{stats.get('backup_count', 0)}")
    
    print("\n🎉 所有测试完成！")

if __name__ == "__main__":
    test_persistence_system()