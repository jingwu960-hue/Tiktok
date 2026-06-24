# test_quality_check.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
from modules.quality_check import check_video, init_publish_log, add_publish_record

def test_init_publish_log(tmp_path):
    """测试初始化发布记录"""
    log_path = str(tmp_path / "publish.json")
    init_publish_log(log_path)
    with open(log_path, 'r') as f:
        data = json.load(f)
    assert "publish_records" in data
    assert isinstance(data["publish_records"], list)

def test_add_publish_record(tmp_path):
    """测试添加发布记录"""
    log_path = str(tmp_path / "publish.json")
    init_publish_log(log_path)
    
    record = {
        "video_id": "v_test_001",
        "product_id": "123",
        "product_name": "Test Product",
        "category": "手镯",
        "template": "A",
        "bgm": "test.mp3",
        "publish_time": "2026-06-25 19:00",
        "metrics": {
            "views": 0,
            "completion_rate": 0,
            "click_rate": 0,
            "add_to_cart": 0,
            "orders": 0
        },
        "score": 0,
        "status": "已发布"
    }
    add_publish_record(log_path, record)
    
    with open(log_path, 'r') as f:
        data = json.load(f)
    assert len(data["publish_records"]) == 1
    assert data["publish_records"][0]["video_id"] == "v_test_001"
