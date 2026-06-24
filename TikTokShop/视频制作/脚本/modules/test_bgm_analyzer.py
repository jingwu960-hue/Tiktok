# test_bgm_analyzer.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from modules.bgm_analyzer import match_images_to_beats

def test_match_images_to_beats():
    """测试图片卡点匹配"""
    beats = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
    result = match_images_to_beats(image_count=6, beats=beats, duration=15.0)
    assert len(result) == 6
    assert result[0] == 0.0
    assert result[-1] < 15.0

def test_match_images_to_beats_empty():
    """测试空鼓点列表"""
    result = match_images_to_beats(image_count=4, beats=[], duration=12.0)
    assert len(result) == 4
    assert result[0] == 0.0
