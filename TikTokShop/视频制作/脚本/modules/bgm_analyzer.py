# modules/bgm_analyzer.py
"""BGM分析模块：鼓点检测、onset检测与卡点匹配（优化版）"""
import librosa
import numpy as np


def analyze_beats(audio_path: str) -> dict:
    """
    分析BGM的BPM、鼓点位置、onset和强拍

    Args:
        audio_path: 音频文件路径

    Returns:
        dict: {
            "bpm": float,
            "beats": list[float],          # 所有节拍时间戳
            "strong_beats": list[float],   # 强拍时间戳（downbeat）
            "onsets": list[float],         # onset时间戳（能量突变点）
            "onset_envelope": list[float], # onset强度包络
            "duration": float,
            "climax_start": float
        }
    """
    y, sr = librosa.load(audio_path, sr=22050)
    duration = librosa.get_duration(y=y, sr=sr)

    # 节拍检测
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    # onset检测：音频能量突变点（比鼓点更精确）
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)

    # onset强度包络：用于卡点闪烁效果
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)

    # 强拍检测：基于onset强度，区分强拍和弱拍
    strong_beats = _detect_strong_beats(beat_times, onset_env, sr)

    # 高潮起点：RMS能量最大处
    rms = librosa.feature.rms(y=y)[0]
    climax_frame = np.argmax(rms)
    climax_start = librosa.frames_to_time(climax_frame, sr=sr)

    return {
        "bpm": float(tempo),
        "beats": beat_times.tolist(),
        "strong_beats": strong_beats,
        "onsets": onset_times.tolist(),
        "onset_envelope": onset_env.tolist(),
        "duration": float(duration),
        "climax_start": float(climax_start)
    }


def _detect_strong_beats(beat_times: np.ndarray, onset_env: np.ndarray, sr: int) -> list:
    """
    内部函数：检测强拍（基于onset强度）

    强拍定义：节拍位置中onset强度高于中位数的拍点。
    这些位置通常对应鼓点重音（kick drum / downbeat）。

    Args:
        beat_times: 节拍时间戳数组
        onset_env: onset强度包络
        sr: 采样率

    Returns:
        list[float]: 强拍时间戳列表
    """
    if len(beat_times) == 0:
        return []

    # 将节拍时间转换为帧索引，采样onset强度
    beat_frames = librosa.time_to_frames(beat_times, sr=sr)
    beat_frames = np.clip(beat_frames, 0, len(onset_env) - 1)
    beat_strengths = onset_env[beat_frames]

    # 强度高于中位数的拍点为强拍
    if len(beat_strengths) == 0:
        return beat_times.tolist()

    threshold = np.median(beat_strengths)
    strong_mask = beat_strengths >= threshold
    strong_beats = beat_times[strong_mask]

    return strong_beats.tolist()


def get_strong_beats(audio_path: str) -> list:
    """
    获取BGM的强拍时间戳列表

    强拍对应鼓点重音（downbeat），适合用于卡点闪烁、
    图片切换等强调效果。

    Args:
        audio_path: 音频文件路径

    Returns:
        list[float]: 强拍时间戳列表（秒）
    """
    result = analyze_beats(audio_path)
    return result["strong_beats"]


def get_onset_envelope(audio_path: str) -> list:
    """
    获取BGM的onset强度包络

    onset包络反映音频能量变化速率，可用于：
    - 卡点闪烁效果的强度控制
    - 可视化音频节奏
    - 判断节奏强弱

    Args:
        audio_path: 音频文件路径

    Returns:
        list[float]: onset强度包络（每个hop_length对应一个值）
    """
    y, sr = librosa.load(audio_path, sr=22050)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    return onset_env.tolist()


def get_beat_timestamps(audio_path: str) -> list:
    """
    获取BGM的鼓点时间戳列表

    Args:
        audio_path: 音频文件路径

    Returns:
        list[float]: 鼓点时间戳列表（秒）
    """
    result = analyze_beats(audio_path)
    return result["beats"]


def match_images_to_beats(
    image_count: int,
    beats: list,
    duration: float,
    onsets: list = None,
    strong_beats: list = None,
) -> list:
    """
    将图片切换时间点对齐BGM鼓点（优化版）

    优化策略：
    1. 优先对齐强拍（downbeat），让重要图片切换落在重音上
    2. 图片切换时间对齐到最近的onset（能量突变点），比单纯鼓点更精确
    3. 保证最小切换间隔0.5秒，避免画面闪烁过快

    Args:
        image_count: 图片数量
        beats: 鼓点时间戳列表
        duration: 视频总时长
        onsets: onset时间戳列表（可选，提供则优先对齐onset）
        strong_beats: 强拍时间戳列表（可选，提供则优先对齐强拍）

    Returns:
        list[float]: 每张图片的开始时间（秒），长度=image_count
    """
    if image_count <= 0:
        return []

    # 无任何节奏信息：均匀分布
    if not beats and not onsets:
        interval = duration / image_count
        return [i * interval for i in range(image_count)]

    result = [0.0]
    if image_count == 1:
        return result

    target_interval = duration / image_count

    # 合并候选点：强拍优先，onset次之，普通鼓点兜底
    # strong_beats 权重最高，用于关键图片切换
    strong_beats = strong_beats or []
    onsets = onsets or []
    beats = beats or []

    for i in range(1, image_count):
        target_time = i * target_interval

        # 构建候选点列表，带优先级标记
        candidates = []
        # 强拍：最高优先级
        for sb in strong_beats:
            if 0 <= sb < duration:
                candidates.append((sb, 0))  # 优先级0（最高）
        # onset：次优先级
        for ot in onsets:
            if 0 <= ot < duration:
                candidates.append((ot, 1))
        # 普通鼓点：最低优先级
        for bt in beats:
            if 0 <= bt < duration:
                candidates.append((bt, 2))

        if not candidates:
            result.append(target_time)
            continue

        # 找到离目标时间最近的候选点
        # 优先选择优先级高（数值小）且距离近的候选点
        best_time = None
        best_score = float('inf')
        for t, priority in candidates:
            dist = abs(t - target_time)
            # 综合评分：距离为主，优先级为辅（优先级高的容许更大距离）
            score = dist - priority * 0.15
            if score < best_score:
                best_score = score
                best_time = t

        # 确保不超出时长且不与上一张图过近
        if best_time is not None:
            if best_time >= duration:
                best_time = duration - target_interval
            # 保证最小间隔0.5秒
            best_time = max(best_time, result[-1] + 0.5)
            best_time = min(best_time, duration - 0.5)
        else:
            best_time = target_time

        result.append(best_time)

    return result
