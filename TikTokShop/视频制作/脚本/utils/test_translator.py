# test_translator.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.translator import SUBTITLE_TEMPLATES, generate_subtitle, translate_to_vietnamese

def test_subtitle_templates_exist():
    """测试文案模板存在"""
    assert "痛点型" in SUBTITLE_TEMPLATES
    assert "颜值型" in SUBTITLE_TEMPLATES
    assert "情感型" in SUBTITLE_TEMPLATES
    assert "性价比型" in SUBTITLE_TEMPLATES
    assert "潮流型" in SUBTITLE_TEMPLATES

def test_template_structure():
    """测试模板结构完整"""
    for name, template in SUBTITLE_TEMPLATES.items():
        assert "hook" in template
        assert "scenes" in template
        assert "cta" in template
        assert isinstance(template["scenes"], list)

def test_generate_subtitle_without_api():
    """测试不调用API时的默认文案生成"""
    product_info = {
        "product_name": "Vòng tay thép titan",
        "category": "手镯",
        "price_vnd": "194,204₫",
        "features": ["thép titan", "không phai màu", "chống dị ứng"]
    }
    result = generate_subtitle(product_info, "痛点型")
    assert "hook" in result
    assert "scenes" in result
    assert "cta" in result
    assert len(result["hook"]) > 0
