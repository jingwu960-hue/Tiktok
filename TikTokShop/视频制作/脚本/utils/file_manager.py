# utils/file_manager.py
"""文件管理模块：读取商品数据、管理素材文件"""
import os
import json
from pathlib import Path


def load_products(json_path: str) -> list:
    """读取products.json商品数据"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def filter_by_category(products: list, categories: list) -> list:
    """按品类筛选商品"""
    result = []
    for product in products:
        product_category = get_product_category(product.get("product_name", ""))
        if product_category in categories:
            result.append(product)
    return result


def get_product_category(product_name: str) -> str:
    """根据商品名（越南语）推断品类"""
    name = product_name.lower()
    if "vòng tay" in name or "lắc" in name:
        return "手镯"
    elif "nhẫn" in name:
        return "戒指"
    elif "kính" in name:
        return "眼镜"
    elif "đồng hồ" in name:
        return "手表"
    elif "dây chuyền" in name or "vòng cổ" in name:
        return "项链"
    elif "hoa tai" in name or "khuyên tai" in name:
        return "耳环"
    return "其他"


def load_images(product_dir: str) -> list:
    """加载指定目录下的所有图片文件"""
    image_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    images = []
    if not os.path.isdir(product_dir):
        return images
    for filename in sorted(os.listdir(product_dir)):
        ext = os.path.splitext(filename)[1].lower()
        if ext in image_extensions:
            images.append(os.path.join(product_dir, filename))
    return images


def ensure_dir(path: str):
    """确保目录存在，不存在则创建"""
    os.makedirs(path, exist_ok=True)
