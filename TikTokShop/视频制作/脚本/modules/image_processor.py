# modules/image_processor.py
"""图片处理模块：裁剪、滤镜、文字叠加、动画效果"""
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import numpy as np


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

    font = None
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/PingFang.ttc",
    ]
    for fp in font_paths:
        try:
            font = ImageFont.truetype(fp, font_size)
            break
        except (IOError, OSError):
            continue
    if font is None:
        font = ImageFont.load_default()

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
