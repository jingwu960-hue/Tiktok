# test_image_processor.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PIL import Image
from modules.image_processor import resize_image, apply_filter, add_text_overlay

def test_resize_image(tmp_path):
    """测试图片裁剪为竖屏"""
    img = Image.new("RGB", (800, 800), color="red")
    img_path = str(tmp_path / "test.jpg")
    img.save(img_path)
    
    result = resize_image(img_path, (1080, 1920))
    assert result.size == (1080, 1920)

def test_apply_filter():
    """测试滤镜应用"""
    img = Image.new("RGB", (1080, 1920), color=(100, 100, 100))
    result = apply_filter(img, "bright_warm")
    assert result.size == (1080, 1920)

def test_add_text_overlay():
    """测试文字叠加"""
    img = Image.new("RGB", (1080, 1920), color="white")
    result = add_text_overlay(img, "Test Text", "center", 60, (255, 0, 0))
    assert result.size == (1080, 1920)
