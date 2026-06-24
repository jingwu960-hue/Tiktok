# templates/template_a_fast.py
"""模板A：快节奏卡点风视频生成（优化版）

时间轴结构：
  0-3秒：钩子开场（第1张图，Ken Burns缓慢放大+闪白转场）
  3-12秒：卡点展示（第2-5张图，跟BGM鼓点切换，滑动转场）
  12-15秒：价格+CTA（第6张图，淡入+缩放，价格标签）
"""
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeVideoClip, ColorClip, VideoClip
)
import numpy as np
from PIL import Image

from modules.image_processor import (
    resize_image, apply_filter, add_text_with_background, add_price_tag
)
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

# 时间轴结构（秒）
HOOK_DURATION = 3.0       # 0-3s: 钩子开场
SCENES_DURATION = 9.0     # 3-12s: 卡点展示
CTA_DURATION = 3.0       # 12-15s: 价格+CTA
TRANSITION_DUR = 0.2     # 滑动转场时长
CTA_FADE_DUR = 0.3       # CTA淡入时长


def _apply_ken_burns(clip, duration, max_scale=1.05):
    """
    对clip应用Ken Burns缓慢放大效果

    通过逐帧缩放+中心裁剪实现，保持画面中心不变。

    Args:
        clip: MoviePy视频片段
        duration: 效果持续时长（秒）
        max_scale: 最终缩放比例（1.05=放大5%）

    Returns:
        应用了Ken Burns效果的clip
    """
    def ken_burns_fl(get_frame, t):
        frame = get_frame(t)
        h, w = frame.shape[:2]
        progress = min(t / duration, 1.0)
        scale = 1.0 + (max_scale - 1.0) * progress
        new_w = int(w * scale)
        new_h = int(h * scale)
        img = Image.fromarray(frame)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        # 从中心裁剪回原始尺寸
        left = (new_w - w) // 2
        top = (new_h - h) // 2
        img = img.crop((left, top, left + w, top + h))
        return np.array(img)

    # apply_to=[] 避免对mask应用缩放变换
    return clip.fl(ken_burns_fl, apply_to=[])


def _make_flash_clip(resolution, start_time, duration, max_opacity=0.3):
    """
    创建白色闪烁效果clip（用于卡点闪烁）

    在指定时间点创建一个白色覆盖层，从max_opacity渐变到0，
    模拟鼓点卡点的闪烁效果。

    Args:
        resolution: 画面尺寸 (width, height)
        start_time: 闪烁开始时间（秒，全局时间）
        duration: 闪烁持续时长（秒）
        max_opacity: 最大不透明度（0.0-1.0）

    Returns:
        MoviePy ColorClip: 闪烁效果片段
    """
    w, h = resolution
    flash = ColorClip(resolution, color=(255, 255, 255), duration=duration)
    flash = flash.set_start(start_time)
    # 创建渐变mask：从max_opacity渐变到0
    # 注意：mask的make_frame接收的是本地时间（相对于clip起始）
    mask = VideoClip(
        lambda t: np.full(
            (h, w),
            max_opacity * max(0, 1 - t / duration),
            dtype=np.float32
        ),
        ismask=True,
        duration=duration
    )
    flash = flash.set_mask(mask)
    return flash


def generate_video_a(
    images: list,
    subtitle: dict,
    bgm_path: str = None,
    output_path: str = "output.mp4",
    price_vnd: str = None,
) -> str:
    """
    生成模板A视频（快节奏卡点风）- 优化版

    Args:
        images: 图片路径列表（至少6张）
        subtitle: 文案字典 {"hook": str, "scenes": list, "cta": str}
        bgm_path: BGM音频文件路径，None时无音频
        output_path: 输出视频路径
        price_vnd: 价格字符串（如 "194.204₫"），用于显示价格标签

    Returns:
        str: 输出视频文件路径
    """
    config = TEMPLATE_A_CONFIG
    duration = config["duration"]
    resolution = config["resolution"]
    fps = config["fps"]

    use_bgm = bool(bgm_path)

    # 确保图片数量足够
    if len(images) < config["image_count"]:
        images = images * (config["image_count"] // len(images) + 1)
    images = images[:config["image_count"]]

    # 安全获取文案
    hook_text = subtitle.get("hook", "") if subtitle else ""
    scenes = subtitle.get("scenes", []) if subtitle else []
    cta_text = subtitle.get("cta", "") if subtitle else ""

    # 分析BGM
    beat_info = None
    strong_beats = []
    if use_bgm:
        beat_info = analyze_beats(bgm_path)
        strong_beats = beat_info.get("strong_beats", [])

    clips = []

    # ============================================================
    # 第1张图：钩子开场（0-3秒）
    # Ken Burns缓慢放大 + 闪白转场
    # ============================================================
    img1 = resize_image(images[0], resolution)
    img1 = apply_filter(img1, config["filter"])
    if hook_text:
        img1 = add_text_with_background(img1, hook_text, "center", text_type="hook")
    img1_array = np.array(img1)

    # 钩子clip持续时间延长以与第2张图重叠（用于滑动转场）
    hook_clip_dur = HOOK_DURATION + TRANSITION_DUR
    clip1 = ImageClip(img1_array, duration=hook_clip_dur)
    clip1 = _apply_ken_burns(clip1, HOOK_DURATION, max_scale=1.05)
    clip1 = clip1.set_start(0)
    clips.append(clip1)

    # 闪白转场（开场0-0.4秒，强闪烁）
    flash_open = _make_flash_clip(resolution, 0, 0.4, max_opacity=0.8)
    clips.append(flash_open)

    # ============================================================
    # 第2-5张图：卡点展示（3-12秒）
    # 跟BGM鼓点切换 + 快速滑动转场
    # ============================================================
    scene_images = images[1:5]
    scene_count = len(scene_images)

    # 计算场景图片的起始时间（跟BGM鼓点对齐）
    if use_bgm and beat_info:
        scene_start_times = match_images_to_beats(
            image_count=scene_count,
            beats=beat_info["beats"],
            duration=SCENES_DURATION,
            onsets=beat_info.get("onsets", []),
            strong_beats=beat_info.get("strong_beats", []),
        )
        # 偏移到场景段起始时间（3秒后）
        scene_start_times = [t + HOOK_DURATION for t in scene_start_times]
    else:
        # 无BGM：均匀分布
        step = SCENES_DURATION / scene_count
        scene_start_times = [HOOK_DURATION + i * step for i in range(scene_count)]

    # 在BGM高潮部分加速图片切换
    if use_bgm and beat_info and len(scene_start_times) > 2:
        climax = beat_info.get("climax_start", 0)
        if HOOK_DURATION < climax < HOOK_DURATION + SCENES_DURATION:
            # 找到最接近高潮的场景图索引
            climax_idx = min(
                range(len(scene_start_times)),
                key=lambda i: abs(scene_start_times[i] - climax)
            )
            # 压缩高潮附近的图片间隔（加速切换）
            for i in range(1, len(scene_start_times)):
                dist_to_climax = abs(i - climax_idx)
                if dist_to_climax <= 1:
                    new_time = scene_start_times[i] - 0.2
                    scene_start_times[i] = max(
                        scene_start_times[i - 1] + 0.5,
                        new_time
                    )

    for i, img_path in enumerate(scene_images):
        # 处理图片
        img = resize_image(img_path, resolution)
        img = apply_filter(img, config["filter"])

        # 添加卖点文字
        scene_idx = min(i, len(scenes) - 1)
        scene_text = scenes[scene_idx] if scenes and scene_idx < len(scenes) else ""
        if scene_text:
            img = add_text_with_background(img, scene_text, "top", text_type="scene")

        start_t = scene_start_times[i]
        # 延长持续时间以与下一张图重叠（用于滑动转场）
        if i < scene_count - 1:
            end_t = scene_start_times[i + 1] + TRANSITION_DUR
        else:
            # 最后一张场景图与CTA图重叠（用于CTA淡入）
            end_t = HOOK_DURATION + SCENES_DURATION + CTA_FADE_DUR
        clip_dur = max(end_t - start_t, 0.5)

        img_array = np.array(img)
        clip = ImageClip(img_array, duration=clip_dur)
        clip = clip.set_start(start_t)

        # 快速滑动转场：从右侧滑入
        # 注意：set_position的lambda接收全局时间，需减去clip起始时间
        clip = clip.set_position(
            lambda t, cs=start_t, sd=TRANSITION_DUR, rw=resolution[0]: (
                int(rw * max(0, 1 - (t - cs) / sd)),
                0
            )
        )
        clips.append(clip)

    # ============================================================
    # 第6张图：价格+CTA（12-15秒）
    # 淡入+缩放 + 价格标签
    # ============================================================
    img_last = resize_image(images[-1], resolution)
    img_last = apply_filter(img_last, config["filter"])
    if cta_text:
        img_last = add_text_with_background(img_last, cta_text, "bottom", text_type="cta")
    if price_vnd:
        img_last = add_price_tag(img_last, price_vnd)
    img_last_array = np.array(img_last)

    cta_start = HOOK_DURATION + SCENES_DURATION  # 12秒
    clip_last = ImageClip(img_last_array, duration=CTA_DURATION)
    # 淡入 + 缓慢缩放
    clip_last = clip_last.crossfadein(CTA_FADE_DUR)
    clip_last = _apply_ken_burns(clip_last, CTA_DURATION, max_scale=1.03)
    clip_last = clip_last.set_start(cta_start)
    clips.append(clip_last)

    # ============================================================
    # 强拍闪烁效果（在强拍位置添加微妙的白色闪烁）
    # ============================================================
    for sb in strong_beats:
        # 避免在开场闪白和CTA淡入处重复闪烁
        if 0.5 < sb < duration - 0.5:
            flash = _make_flash_clip(resolution, sb, 0.15, max_opacity=0.25)
            clips.append(flash)

    # ============================================================
    # 合成视频
    # ============================================================
    video = CompositeVideoClip(clips, size=resolution)
    video = video.set_duration(duration)

    # 添加BGM（无BGM模式跳过，发布时在TikTok内选择）
    if use_bgm:
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
