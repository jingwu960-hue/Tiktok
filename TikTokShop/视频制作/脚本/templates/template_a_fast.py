# templates/template_a_fast.py
"""模板A：快节奏卡点风视频生成"""
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip
import numpy as np
from PIL import Image

from modules.image_processor import resize_image, apply_filter, add_text_overlay
from modules.bgm_analyzer import analyze_beats, match_images_to_beats

# 模板A配置
TEMPLATE_A_CONFIG = {
    "duration": 15,
    "image_count": 6,
    "image_duration": 1.5,
    "bpm_range": [120, 140],
    "transition": "slide_left",
    "filter": "bright_warm",
    "resolution": (1080, 1920),
    "fps": 30,
}


def generate_video_a(
    images: list,
    subtitle: dict,
    bgm_path: str,
    output_path: str,
) -> str:
    """
    生成模板A视频（快节奏卡点风）

    Args:
        images: 图片路径列表（至少6张）
        subtitle: 文案字典 {"hook": str, "scenes": list, "cta": str}
        bgm_path: BGM音频文件路径
        output_path: 输出视频路径

    Returns:
        str: 输出视频文件路径
    """
    config = TEMPLATE_A_CONFIG
    duration = config["duration"]
    resolution = config["resolution"]
    fps = config["fps"]

    # 确保图片数量足够
    if len(images) < config["image_count"]:
        images = images * (config["image_count"] // len(images) + 1)
    images = images[:config["image_count"]]

    # 分析BGM鼓点
    beat_info = analyze_beats(bgm_path)
    beats = beat_info["beats"]

    # 将图片切换对齐鼓点
    image_start_times = match_images_to_beats(
        image_count=len(images),
        beats=beats,
        duration=duration
    )

    # 处理每张图片并创建ImageClip
    clips = []
    for i, img_path in enumerate(images):
        # 处理图片
        img = resize_image(img_path, resolution)
        img = apply_filter(img, config["filter"])

        # 添加文字
        if i == 0:
            img = add_text_overlay(img, subtitle["hook"], "center", font_size=70, color=(255, 255, 0))
        elif i == len(images) - 1:
            img = add_text_overlay(img, subtitle["cta"], "bottom", font_size=55, color=(255, 255, 0))
        else:
            scene_idx = min(i - 1, len(subtitle["scenes"]) - 1)
            img = add_text_overlay(img, subtitle["scenes"][scene_idx], "top", font_size=50, color=(255, 255, 255))

        # 计算这张图的持续时间
        if i < len(images) - 1:
            clip_duration = image_start_times[i + 1] - image_start_times[i]
        else:
            clip_duration = duration - image_start_times[i]

        clip_duration = max(clip_duration, 0.5)

        # 转换PIL.Image为numpy数组
        img_array = np.array(img)

        # 创建ImageClip并添加淡入效果
        clip = ImageClip(img_array, duration=clip_duration)
        clip = clip.set_start(image_start_times[i])
        clip = clip.crossfadein(0.2)

        clips.append(clip)

    # 合成视频
    video = CompositeVideoClip(clips, size=resolution)
    video = video.set_duration(duration)

    # 添加BGM
    audio = AudioFileClip(bgm_path).subclip(0, duration)
    video = video.set_audio(audio)

    # 导出视频
    video.write_videofile(
        output_path,
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        verbose=False,
        logger=None
    )

    return output_path
