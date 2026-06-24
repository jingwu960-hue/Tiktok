# test_template_a.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from templates.template_a_fast import TEMPLATE_A_CONFIG

def test_template_a_config():
    """测试模板A配置"""
    assert TEMPLATE_A_CONFIG["duration"] == 15
    assert TEMPLATE_A_CONFIG["image_count"] == 6
    assert TEMPLATE_A_CONFIG["bpm_range"] == [120, 140]
    assert TEMPLATE_A_CONFIG["transition"] == "slide_left"
    assert TEMPLATE_A_CONFIG["filter"] == "bright_warm"
