# utils/translator.py
"""越南语翻译与文案生成模块"""
import os

# 5套文案模板（越南语）
SUBTITLE_TEMPLATES = {
    "痛点型": {
        "hook": "Đừng đeo trang sức rẻ tiền nữa!",
        "scenes": [
            "Chất liệu cao cấp",
            "Bền đẹp vượt thời gian",
            "An toàn cho da",
        ],
        "cta": "Cam kết chất lượng - Mua ngay!",
        "category_match": ["手镯", "项链"]
    },
    "颜值型": {
        "hook": "Xinh hơn chỉ với 1 món phụ kiện",
        "scenes": [
            "Thiết kế thời thượng",
            "Tôn lên vẻ đẹp",
            "Phối đồ dễ dàng",
        ],
        "cta": "Thay đổi phong cách - Đặt hàng ngay!",
        "category_match": ["眼镜", "耳环"]
    },
    "情感型": {
        "hook": "Quà tặng ý nghĩa cho người yêu",
        "scenes": [
            "Thiết kế đôi tình nhân",
            "Bao bì quà tặng cao cấp",
            "Ý nghĩa vĩnh cửu",
        ],
        "cta": "Đặt hàng ngay cho người thương!",
        "category_match": ["情侣戒"]
    },
    "性价比型": {
        "hook": "Đẹp mà rẻ, ai cũng muốn có",
        "scenes": [
            "Giá tốt nhất thị trường",
            "Chất liệu cao cấp",
            "Bền đẹp lâu dài",
        ],
        "cta": "Số lượng có hạn - Đặt hàng ngay!",
        "category_match": ["*"]
    },
    "潮流型": {
        "hook": "Xu hướng 2026 hot nhất",
        "scenes": [
            "Mẫu mới nhất 2026",
            "Phong cách INS Hàn Nhật",
            "Đang bán chạy nhất",
        ],
        "cta": "Săn ngay kẻo hết!",
        "category_match": ["*"]
    }
}


def translate_to_vietnamese(text: str, api_key: str = None) -> str:
    """将中文翻译为越南语（使用OpenAI API）"""
    api_key = api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return text

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a Vietnamese translator. Translate the following Chinese text to natural Vietnamese suitable for e-commerce marketing."},
                {"role": "user", "content": text}
            ],
            max_tokens=200,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return text


def generate_subtitle(product_info: dict, template_name: str, api_key: str = None) -> dict:
    """
    根据商品信息和模板名生成越南语文案

    Args:
        product_info: 包含product_name, category, price_vnd, features的商品信息
        template_name: 模板名称（痛点型/颜值型/情感型/性价比型/潮流型）
        api_key: OpenAI API Key（可选）

    Returns:
        dict: {"hook": str, "scenes": list[str], "cta": str}
    """
    template = SUBTITLE_TEMPLATES.get(template_name, SUBTITLE_TEMPLATES["性价比型"])

    features = product_info.get("features", [])

    if features:
        scenes = features[:3]
        while len(scenes) < 3:
            scenes.append(template["scenes"][len(scenes) % len(template["scenes"])])
    else:
        scenes = template["scenes"]

    return {
        "hook": template["hook"],
        "scenes": scenes,
        "cta": template["cta"]
    }
