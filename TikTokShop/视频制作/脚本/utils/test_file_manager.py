# test_file_manager.py
import json
import os
import tempfile
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.file_manager import load_products, filter_by_category, load_images, ensure_dir, get_product_category

def test_load_products():
    """测试读取商品数据"""
    products = load_products("../../products.json")
    assert len(products) > 0
    assert "product_name" in products[0]

def test_filter_by_category():
    """测试按品类筛选"""
    products = [
        {"product_name": "Vòng tay thép titan", "product_id": "1"},
        {"product_name": "Nhẫn nam xoay", "product_id": "2"},
        {"product_name": "Kính râm nữ", "product_id": "3"},
    ]
    result = filter_by_category(products, ["手镯"])
    assert len(result) == 1
    assert result[0]["product_name"] == "Vòng tay thép titan"

def test_get_product_category():
    """测试品类识别"""
    assert get_product_category("Vòng tay thép titan") == "手镯"
    assert get_product_category("Nhẫn nam xoay titan") == "戒指"
    assert get_product_category("Kính râm nữ") == "眼镜"
    assert get_product_category("Đồng hồ nữ") == "手表"
    assert get_product_category("Dây chuyền") == "项链"
    assert get_product_category("Khuyên tai") == "耳环"

def test_ensure_dir(tmp_path):
    """测试目录创建"""
    test_dir = str(tmp_path / "test_subdir")
    ensure_dir(test_dir)
    assert os.path.isdir(test_dir)

def test_load_images(tmp_path):
    """测试图片加载"""
    for i in range(3):
        (tmp_path / f"img{i}.jpg").write_bytes(b"fake_jpg")
    images = load_images(str(tmp_path))
    assert len(images) == 3
