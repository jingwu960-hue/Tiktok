# modules/quality_check.py
"""质检模块：检查视频质量，管理发布记录"""
import os
import json
from moviepy.editor import VideoFileClip


def check_video(video_path: str) -> dict:
    """
    检查视频质量

    Args:
        video_path: 视频文件路径

    Returns:
        dict: {
            "valid": bool,
            "resolution": tuple,
            "duration": float,
            "fps": float,
            "has_audio": bool,
            "issues": list[str]
        }
    """
    result = {
        "valid": True,
        "resolution": None,
        "duration": 0,
        "fps": 0,
        "has_audio": False,
        "issues": []
    }

    if not os.path.exists(video_path):
        result["valid"] = False
        result["issues"].append("文件不存在")
        return result

    try:
        clip = VideoFileClip(video_path)
        result["resolution"] = clip.size
        result["duration"] = clip.duration
        result["fps"] = clip.fps
        result["has_audio"] = clip.audio is not None

        if clip.size[0] != 1080 or clip.size[1] != 1920:
            result["issues"].append(f"分辨率不符: {clip.size}，应为(1080, 1920)")
            result["valid"] = False

        if clip.duration < 10 or clip.duration > 30:
            result["issues"].append(f"时长异常: {clip.duration:.1f}秒，应在15-25秒")
            result["valid"] = False

        if not result["has_audio"]:
            result["issues"].append("无音频")
            result["valid"] = False

        clip.close()

    except Exception as e:
        result["valid"] = False
        result["issues"].append(f"读取失败: {str(e)}")

    return result


def init_publish_log(log_path: str):
    """初始化发布记录文件"""
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    data = {"publish_records": []}
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_publish_record(log_path: str, record: dict):
    """添加一条发布记录"""
    with open(log_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    data["publish_records"].append(record)
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
