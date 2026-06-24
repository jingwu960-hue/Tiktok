# test_e2e.py
"""端到端集成测试：验证完整视频生成流程"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.file_manager import load_images, get_product_category
from utils.translator import generate_subtitle
from templates.template_a_fast import generate_video_a
from modules.quality_check import check_video


def test_e2e_video_generation():
    """端到端测试：从图片到视频"""
    # 1. 加载测试图片
    assets_dir = os.path.join(os.path.dirname(__file__), "..", "素材库", "手镯", "test_product")
    images = load_images(assets_dir)
    assert len(images) >= 6, f"需要至少6张图片，实际{len(images)}张"

    # 2. 生成文案
    product_info = {
        "product_name": "Vòng tay test",
        "category": "手镯",
        "price_vnd": "100,000₫",
        "features": ["Thép titan", "Không phai màu", "Chống dị ứng"]
    }
    subtitle = generate_subtitle(product_info, "痛点型")
    assert "hook" in subtitle
    assert len(subtitle["scenes"]) >= 3

    # 3. 生成视频
    bgm_path = os.path.join(os.path.dirname(__file__), "..", "音乐库", "test_bgm.mp3")
    output_path = os.path.join(os.path.dirname(__file__), "..", "生成视频", "test_e2e.mp4")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    result_path = generate_video_a(images, subtitle, bgm_path, output_path)
    assert os.path.exists(result_path)

    # 4. 质检
    qc = check_video(result_path)
    assert qc["valid"], f"质检失败: {qc['issues']}"
    assert qc["duration"] > 10
    assert qc["has_audio"]

    print(f"\n端到端测试通过！")
    print(f"视频路径: {result_path}")
    print(f"分辨率: {qc['resolution']}")
    print(f"时长: {qc['duration']:.1f}秒")
    print(f"FPS: {qc['fps']}")
