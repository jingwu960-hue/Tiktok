# download_bgm.py
"""BGM批量下载脚本：从YouTube下载越南TikTok热门歌曲"""
import os
import sys
import json
import subprocess
from pathlib import Path

# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def load_songs(json_path: str) -> list:
    """读取歌曲清单"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def download_audio(search_query: str, output_path: str) -> bool:
    """
    用yt-dlp从YouTube下载音频

    Args:
        search_query: 搜索关键词
        output_path: 输出文件路径（不含扩展名）

    Returns:
        bool: 是否下载成功
    """
    try:
        cmd = [
            "yt-dlp",
            "-x",  # 只提取音频
            "--audio-format", "mp3",
            "-o", f"{output_path}.%(ext)s",
            f"ytsearch1:{search_query}",  # 搜索并下载第一个结果
            "--no-playlist",
            "--extractor-args", "youtube:player_client=android",  # 绕过YouTube 403限制
            "--format", "bestaudio/best",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            error_lines = [l for l in result.stderr.split('\n') if 'ERROR' in l]
            if error_lines:
                print(f"  yt-dlp错误: {error_lines[0][:200]}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"  下载超时（300秒），跳过")
        return False
    except Exception as e:
        print(f"  下载失败: {e}")
        return False


def trim_audio(input_path: str, output_path: str, start: float = 0, duration: float = 18) -> bool:
    """
    用ffmpeg截取音频高潮段落并标准化音量

    Args:
        input_path: 输入音频路径
        output_path: 输出音频路径
        start: 开始时间（秒）
        duration: 截取时长（秒）

    Returns:
        bool: 是否截取成功
    """
    try:
        cmd = [
            "ffmpeg",
            "-y",  # 覆盖输出
            "-i", input_path,
            "-ss", str(start),
            "-t", str(duration),
            "-af", "loudnorm=I=-3:TP=-1:LRA=7",  # 音量标准化
            "-codec:a", "libmp3lame",
            "-b:a", "192k",
            output_path,
            "-loglevel", "error",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result.returncode == 0
    except Exception as e:
        print(f"  截取失败: {e}")
        return False


def get_audio_duration(audio_path: str) -> float:
    """获取音频时长（秒）"""
    try:
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            audio_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return float(result.stdout.strip())
    except Exception:
        return 0.0


def batch_download():
    """批量下载BGM"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    songs_path = os.path.join(script_dir, "bgm_songs.json")
    bgm_dir = os.path.join(script_dir, "..", "音乐库")

    # 确保音乐库目录存在
    os.makedirs(bgm_dir, exist_ok=True)

    # 读取歌曲清单
    songs = load_songs(songs_path)
    print(f"共 {len(songs)} 首歌曲待下载\n")

    # 检查yt-dlp是否安装
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, timeout=5)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("错误: yt-dlp 未安装，请运行: pip3 install yt-dlp")
        return

    success_count = 0
    fail_count = 0

    for i, song in enumerate(songs):
        song_id = song["id"]
        song_name = song["name"]
        artist = song["artist"]
        search_query = song["search_query"]

        # 输出文件路径
        final_path = os.path.join(bgm_dir, f"{song_id}.mp3")
        temp_path = os.path.join(bgm_dir, f"{song_id}_full.mp3")

        # 如果已存在则跳过
        if os.path.exists(final_path):
            print(f"[{i+1}/{len(songs)}] {song_name} - 已存在，跳过")
            success_count += 1
            continue

        print(f"[{i+1}/{len(songs)}] 下载: {song_name} - {artist}")
        print(f"  搜索: {search_query}")

        # Step 1: 下载完整音频
        temp_base = os.path.join(bgm_dir, song_id)
        if not download_audio(search_query, temp_base):
            print(f"  下载失败，跳过")
            fail_count += 1
            continue

        # 查找下载的文件（yt-dlp会自动加扩展名）
        downloaded_file = None
        for ext in ['.mp3', '.m4a', '.webm', '.opus']:
            candidate = temp_base + ext
            if os.path.exists(candidate):
                downloaded_file = candidate
                break

        if not downloaded_file:
            print(f"  未找到下载文件，跳过")
            fail_count += 1
            continue

        # Step 2: 获取音频时长
        duration = get_audio_duration(downloaded_file)
        if duration < 18:
            print(f"  音频太短（{duration:.1f}秒），直接使用")
            # 如果音频短于18秒，直接重命名
            os.rename(downloaded_file, final_path)
            success_count += 1
            continue

        # Step 3: 截取高潮段落（从40%位置开始，截取18秒）
        start_time = duration * 0.4
        print(f"  截取: {start_time:.1f}s - {start_time + 18:.1f}s / {duration:.1f}s")

        if trim_audio(downloaded_file, final_path, start=start_time, duration=18):
            # 删除临时文件
            os.remove(downloaded_file)
            print(f"  成功: {final_path}")
            success_count += 1
        else:
            print(f"  截取失败，使用完整音频")
            os.rename(downloaded_file, final_path)
            success_count += 1

    print(f"\n=== BGM下载完成 ===")
    print(f"成功: {success_count} 首")
    print(f"失败: {fail_count} 首")
    print(f"输出目录: {os.path.abspath(bgm_dir)}")

    # 生成音乐信息文件
    generate_bgm_info(songs, bgm_dir)


def generate_bgm_info(songs: list, bgm_dir: str):
    """生成音乐信息库JSON"""
    info = {"bgm_library": []}
    for song in songs:
        file_path = os.path.join(bgm_dir, f"{song['id']}.mp3")
        info["bgm_library"].append({
            "id": song["id"],
            "name": song["name"],
            "artist": song["artist"],
            "file": f"{song['id']}.mp3",
            "exists": os.path.exists(file_path),
            "bpm_type": song["bpm_type"],
            "style": "快节奏" if song["bpm_type"] == "fast" else "中慢节奏",
            "suitable_templates": [song["template"]],
            "duration": 18,
        })

    info_path = os.path.join(bgm_dir, "音乐信息.json")
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    print(f"音乐信息库已生成: {info_path}")


if __name__ == "__main__":
    batch_download()
