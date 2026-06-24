# modules/bgm_analyzer.py
"""BGM分析模块：鼓点检测与卡点匹配"""
import librosa
import numpy as np


def analyze_beats(audio_path: str) -> dict:
    """
    分析BGM的BPM和鼓点位置

    Args:
        audio_path: 音频文件路径

    Returns:
        dict: {
            "bpm": float,
            "beats": list[float],
            "duration": float,
            "climax_start": float
        }
    """
    y, sr = librosa.load(audio_path, sr=22050)
    duration = librosa.get_duration(y=y, sr=sr)

    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    rms = librosa.feature.rms(y=y)[0]
    climax_frame = np.argmax(rms)
    climax_start = librosa.frames_to_time(climax_frame, sr=sr)

    return {
        "bpm": float(tempo),
        "beats": beat_times.tolist(),
        "duration": float(duration),
        "climax_start": float(climax_start)
    }


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


def match_images_to_beats(image_count: int, beats: list, duration: float) -> list:
    """
    将图片切换时间点对齐BGM鼓点

    Args:
        image_count: 图片数量
        beats: 鼓点时间戳列表
        duration: 视频总时长

    Returns:
        list[float]: 每张图片的开始时间（秒），长度=image_count
    """
    if not beats or image_count <= 0:
        interval = duration / image_count
        return [i * interval for i in range(image_count)]

    result = [0.0]

    if image_count == 1:
        return result

    target_interval = duration / image_count

    for i in range(1, image_count):
        target_time = i * target_interval
        if beats:
            closest_beat = min(beats, key=lambda b: abs(b - target_time))
            if closest_beat >= duration:
                closest_beat = duration - target_interval
            result.append(max(closest_beat, result[-1] + 0.5))
        else:
            result.append(target_time)

    return result
