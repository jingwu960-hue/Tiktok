# main.py
"""主入口：批量生成TikTok带货视频"""
import os
import sys
import json
import yaml
from datetime import datetime
from pathlib import Path

# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.file_manager import load_products, filter_by_category, load_images, ensure_dir, get_product_category
from utils.translator import SUBTITLE_TEMPLATES, generate_subtitle
from templates.template_a_fast import generate_video_a, TEMPLATE_A_CONFIG


def load_config() -> dict:
    """读取config.yaml配置"""
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def select_template(product: dict, index: int) -> str:
    """选择模板（A/B轮换）"""
    return "template_a"


def select_bgm(bgm_dir: str, template_name: str) -> str:
    """选择BGM（轮换使用）"""
    bgm_files = sorted([
        f for f in os.listdir(bgm_dir)
        if f.endswith(('.mp3', '.wav', '.m4a'))
    ])
    if not bgm_files:
        return None
    import time
    idx = int(time.time()) % len(bgm_files)
    return os.path.join(bgm_dir, bgm_files[idx])


def select_subtitle_template(category: str) -> str:
    """根据品类选择文案模板"""
    for name, template in SUBTITLE_TEMPLATES.items():
        match_list = template.get("category_match", [])
        if category in match_list or "*" in match_list:
            return name
    return "性价比型"


def batch_generate(use_bgm: bool = True):
    """批量生成视频

    Args:
        use_bgm: 是否使用BGM。False时生成无音频视频（发布时在TikTok内选BGM）
    """
    config = load_config()
    paths = config["paths"]

    # 读取商品数据
    products_json_path = os.path.join(os.path.dirname(__file__), paths["products_json"])
    products = load_products(products_json_path)
    print(f"共读取 {len(products)} 个商品")

    # 筛选优先品类（手镯+项链）
    priority_products = filter_by_category(products, ["手镯", "项链"])
    print(f"优先品类商品数: {len(priority_products)}")

    if not priority_products:
        print("未找到优先品类商品，使用全部商品")
        priority_products = products

    # 创建输出目录
    today = datetime.now().strftime("%Y-%m-%d")
    output_dir = os.path.join(os.path.dirname(__file__), paths["output_dir"], today)
    ensure_dir(output_dir)

    # 检查BGM库
    bgm_dir = os.path.join(os.path.dirname(__file__), paths["bgm_dir"])
    if use_bgm:
        if not os.path.isdir(bgm_dir):
            print(f"警告: BGM目录不存在 {bgm_dir}")
            print("自动切换到无BGM模式（发布时在TikTok App内添加BGM）")
            use_bgm = False
        else:
            # 检查BGM目录是否有可用音频文件
            bgm_files = [f for f in os.listdir(bgm_dir) if f.endswith(('.mp3', '.wav', '.m4a'))]
            if not bgm_files:
                print(f"警告: BGM目录为空，无可用音频文件 {bgm_dir}")
                print("自动切换到无BGM模式（发布时在TikTok App内添加BGM）")
                use_bgm = False

    if not use_bgm:
        print("提示: 视频将在TikTok App内添加BGM（享受平台热门BGM流量加持）")

    # 为每个商品生成视频
    success_count = 0
    fail_count = 0

    for i, product in enumerate(priority_products):
        product_name = product.get("product_name", f"product_{i}")
        product_id = product.get("product_id", str(i))
        category = get_product_category(product_name)

        print(f"\n[{i+1}/{len(priority_products)}] 处理: {product_name[:40]}...")

        try:
            # 查找商品图片
            product_img_dir = os.path.join(
                os.path.dirname(__file__),
                paths["assets_dir"],
                category,
                product_id
            )
            images = load_images(product_img_dir)

            if len(images) < 3:
                print(f"  跳过: 图片不足（{len(images)}张），需要至少3张")
                fail_count += 1
                continue

            # 选择模板
            template_name = select_template(product, i)

            # 选择BGM（无BGM模式跳过）
            bgm_path = None
            if use_bgm:
                bgm_path = select_bgm(bgm_dir, template_name)
                if not bgm_path:
                    print("  跳过: 无可用BGM")
                    fail_count += 1
                    continue

            # 生成文案
            subtitle_template = select_subtitle_template(category)
            features = [product_name]
            product_info = {
                "product_name": product_name,
                "category": category,
                "price_vnd": "",
                "features": features
            }
            subtitle = generate_subtitle(product_info, subtitle_template)

            # 生成视频（无BGM模式时bgm_path=None）
            output_path = os.path.join(output_dir, f"{product_id}.mp4")
            generate_video_a(images, subtitle, bgm_path=bgm_path, output_path=output_path)

            print(f"  成功: {output_path}")
            success_count += 1

        except Exception as e:
            print(f"  失败: {e}")
            fail_count += 1
            continue

    print(f"\n=== 批量生成完成 ===")
    print(f"成功: {success_count} 个")
    print(f"失败: {fail_count} 个")
    print(f"输出目录: {output_dir}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="批量生成TikTok带货视频")
    parser.add_argument("--no-bgm", action="store_true", help="不添加BGM（发布时在TikTok内选择）")
    args = parser.parse_args()
    batch_generate(use_bgm=not args.no_bgm)
