# modules/image_processor.py
"""图片处理模块：裁剪、滤镜、文字叠加、动画效果（优化版）"""
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import numpy as np


# 支持越南语的字体路径（按优先级排序）
# Arial Unicode MS 提供最完整的越南语字符支持
_VIETNAMESE_FONT_PATHS = [
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",  # 完整越南语支持
    "/System/Library/Fonts/Helvetica.ttc",                  # 基本越南语支持
    "/System/Library/Fonts/Supplemental/Arial.ttf",          # Arial 常规
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",    # Arial 粗体
]

# 粗体字体路径
_BOLD_FONT_PATHS = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]


def _load_font(font_size: int, bold: bool = False):
    """
    加载支持越南语的字体

    Args:
        font_size: 字体大小
        bold: 是否使用粗体

    Returns:
        PIL.ImageFont: 字体对象
    """
    paths = _BOLD_FONT_PATHS if bold else _VIETNAMESE_FONT_PATHS
    for fp in paths:
        try:
            return ImageFont.truetype(fp, font_size)
        except (IOError, OSError, KeyError):
            continue
    return ImageFont.load_default()


def resize_image(img_path: str, target_size: tuple = (1080, 1920)) -> Image.Image:
    """
    将图片裁剪并缩放到目标尺寸（居中裁剪）

    Args:
        img_path: 图片路径
        target_size: 目标尺寸 (width, height)

    Returns:
        PIL.Image: 处理后的图片
    """
    img = Image.open(img_path).convert("RGB")
    target_w, target_h = target_size
    src_w, src_h = img.size

    target_ratio = target_w / target_h
    src_ratio = src_w / src_h

    if src_ratio > target_ratio:
        new_w = int(src_h * target_ratio)
        left = (src_w - new_w) // 2
        img = img.crop((left, 0, left + new_w, src_h))
    else:
        new_h = int(src_w / target_ratio)
        top = (src_h - new_h) // 2
        img = img.crop((0, top, src_w, top + new_h))

    img = img.resize(target_size, Image.LANCZOS)
    return img


def apply_filter(img: Image.Image, filter_name: str) -> Image.Image:
    """
    应用滤镜效果

    Args:
        img: PIL图片对象
        filter_name: 滤镜名称（bright_warm/elegant_warm/none）

    Returns:
        PIL.Image: 处理后的图片
    """
    if filter_name == "bright_warm":
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.15)
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.2)
        arr = np.array(img).astype(np.float32)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.05, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.95, 0, 255)
        img = Image.fromarray(arr.astype(np.uint8))
    elif filter_name == "elegant_warm":
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(0.85)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.05)
        arr = np.array(img).astype(np.float32)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.03, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.97, 0, 255)
        img = Image.fromarray(arr.astype(np.uint8))

    return img


def add_text_overlay(
    img: Image.Image,
    text: str,
    position: str = "center",
    font_size: int = 60,
    color: tuple = (255, 255, 255),
    stroke_color: tuple = (0, 0, 0),
) -> Image.Image:
    """
    在图片上添加文字（带描边）

    Args:
        img: PIL图片对象
        text: 文字内容
        position: 位置（center/top/bottom）
        font_size: 字体大小
        color: 文字颜色 (R, G, B)
        stroke_color: 描边颜色

    Returns:
        PIL.Image: 添加文字后的图片
    """
    draw = ImageDraw.Draw(img)

    font = _load_font(font_size)

    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    img_w, img_h = img.size

    if position == "center":
        x = (img_w - text_w) // 2
        y = (img_h - text_h) // 2
    elif position == "top":
        x = (img_w - text_w) // 2
        y = int(img_h * 0.1)
    else:  # bottom
        x = (img_w - text_w) // 2
        y = int(img_h * 0.85) - text_h

    stroke_offsets = [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1), (-1, 1), (1, -1)]
    for dx, dy in stroke_offsets:
        draw.text((x + dx, y + dy), text, font=font, fill=stroke_color)

    draw.text((x, y), text, font=font, fill=color)

    return img


def add_text_with_background(
    img: Image.Image,
    text: str,
    position: str = "center",
    font_size: int = 55,
    text_color: tuple = (255, 255, 255),
    text_type: str = "scene",
) -> Image.Image:
    """
    在图片上添加带半透明背景框的文字（优化版）

    文字下方添加半透明黑色圆角矩形背景，文字白色+黑色描边，
    提升在复杂背景上的可读性。

    Args:
        img: PIL图片对象
        text: 文字内容（支持越南语）
        position: 位置（center/top/bottom）
        font_size: 字体大小
        text_color: 文字颜色 (R, G, B)
        text_type: 文字类型，决定默认样式
            - "hook": 钩子文字，字号80，黄色，粗体
            - "scene": 卖点文字，字号55，白色
            - "cta": CTA文字，字号60，黄色，粗体

    Returns:
        PIL.Image: 添加文字后的图片
    """
    # 根据文字类型设置默认样式
    if text_type == "hook":
        font_size = font_size if font_size != 55 else 80
        text_color = (255, 230, 0) if text_color == (255, 255, 255) else text_color
        bold = True
    elif text_type == "cta":
        font_size = font_size if font_size != 55 else 60
        text_color = (255, 230, 0) if text_color == (255, 255, 255) else text_color
        bold = True
    else:  # scene
        bold = False

    font = _load_font(font_size, bold=bold)
    draw = ImageDraw.Draw(img, "RGBA")

    img_w, img_h = img.size

    # 计算文字尺寸
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    # 计算文字位置
    if position == "center":
        x = (img_w - text_w) // 2
        y = (img_h - text_h) // 2
    elif position == "top":
        x = (img_w - text_w) // 2
        y = int(img_h * 0.12)
    else:  # bottom
        x = (img_w - text_w) // 2
        y = int(img_h * 0.82)

    # 背景框内边距
    pad_x = 30
    pad_y = 20
    bg_x1 = x - pad_x
    bg_y1 = y - pad_y
    bg_x2 = x + text_w + pad_x
    bg_y2 = y + text_h + pad_y

    # 绘制半透明黑色圆角矩形背景
    bg_radius = 15
    draw.rounded_rectangle(
        [bg_x1, bg_y1, bg_x2, bg_y2],
        radius=bg_radius,
        fill=(0, 0, 0, 160)  # 半透明黑色
    )

    # 绘制黑色描边（8方向）
    stroke_offsets = [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1), (-1, 1), (1, -1)]
    for dx, dy in stroke_offsets:
        draw.text((x + dx, y + dy), text, font=font, fill=(0, 0, 0, 255))

    # 绘制主文字
    draw.text((x, y), text, font=font, fill=text_color + (255,))

    return img


def add_price_tag(
    img: Image.Image,
    price_text: str,
    font_size: int = 50,
) -> Image.Image:
    """
    在画面右下角添加价格标签

    黄色圆角矩形背景 + 黑色文字显示价格。

    Args:
        img: PIL图片对象
        price_text: 价格文本（如 "194.204₫"）
        font_size: 字体大小

    Returns:
        PIL.Image: 添加价格标签后的图片
    """
    draw = ImageDraw.Draw(img, "RGBA")
    font = _load_font(font_size, bold=True)

    img_w, img_h = img.size

    # 计算文字尺寸
    bbox = draw.textbbox((0, 0), price_text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    # 价格标签位置：右下角
    margin = 40
    pad_x = 25
    pad_y = 15

    bg_x2 = img_w - margin
    bg_y2 = img_h - margin
    bg_x1 = bg_x2 - text_w - pad_x * 2
    bg_y1 = bg_y2 - text_h - pad_y * 2

    # 绘制黄色圆角矩形背景
    draw.rounded_rectangle(
        [bg_x1, bg_y1, bg_x2, bg_y2],
        radius=12,
        fill=(255, 215, 0, 255)  # 鲜艳黄色
    )

    # 绘制黑色价格文字
    text_x = bg_x1 + pad_x
    text_y = bg_y1 + pad_y
    draw.text((text_x, text_y), price_text, font=font, fill=(0, 0, 0, 255))

    return img


def add_flash_effect(
    img: Image.Image,
    intensity: float = 0.5,
) -> Image.Image:
    """
    在图片上添加白色闪烁效果（用于卡点）

    在图片上叠加一层半透明白色，模拟卡点闪烁效果。
    intensity越大越亮。

    Args:
        img: PIL图片对象
        intensity: 闪烁强度（0.0-1.0），0.5为中等强度

    Returns:
        PIL.Image: 添加闪烁效果后的图片
    """
    intensity = max(0.0, min(1.0, intensity))

    # 创建白色叠加层
    overlay = Image.new("RGBA", img.size, (255, 255, 255, int(255 * intensity)))

    # 合成到原图
    result = img.convert("RGBA")
    result = Image.alpha_composite(result, overlay)

    return result.convert("RGB")


def create_slide_animation(img: Image.Image, duration: float, direction: str = "left") -> list:
    """
    生成滑动动画帧

    Args:
        img: PIL图片对象
        duration: 动画时长（秒）
        direction: 滑动方向（left/right/up/down）

    Returns:
        list: PIL.Image帧列表
    """
    fps = 30
    frame_count = int(duration * fps)
    frames = []
    img_w, img_h = img.size

    for i in range(frame_count):
        progress = i / frame_count
        offset = int(progress * img_w * 0.1)

        frame = img.copy()
        if direction == "left":
            frame = frame.transform(
                (img_w, img_h),
                Image.AFFINE,
                (1, 0, -offset, 0, 1, 0),
                fillcolor=(0, 0, 0)
            )
        elif direction == "right":
            frame = frame.transform(
                (img_w, img_h),
                Image.AFFINE,
                (1, 0, offset, 0, 1, 0),
                fillcolor=(0, 0, 0)
            )

        frames.append(frame)

    return frames


def create_zoom_animation(img: Image.Image, duration: float, scale: float = 1.1) -> list:
    """
    生成缓慢缩放动画帧（Ken Burns效果）

    Args:
        img: PIL图片对象
        duration: 动画时长（秒）
        scale: 最终缩放比例

    Returns:
        list: PIL.Image帧列表
    """
    fps = 30
    frame_count = int(duration * fps)
    frames = []
    img_w, img_h = img.size

    for i in range(frame_count):
        progress = i / frame_count
        current_scale = 1.0 + (scale - 1.0) * progress

        new_w = int(img_w * current_scale)
        new_h = int(img_h * current_scale)
        resized = img.resize((new_w, new_h), Image.LANCZOS)

        left = (new_w - img_w) // 2
        top = (new_h - img_h) // 2
        frame = resized.crop((left, top, left + img_w, top + img_h))

        frames.append(frame)

    return frames
