"""
video_pipeline/ingestion.py
Video ingestion and validation module.
Accepts local video files (.mp4, .mov, .mkv, .webm), validates structural integrity
and non-zero size, inspects video metadata (resolution, duration, fps),
and handles remote video downloads via yt-dlp with mock fallbacks.
"""
from __future__ import annotations

import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional, Union

from video_pipeline.ffmpeg_resolver import create_synthetic_video, get_ffmpeg_exe

VALID_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".flv"}


def validate_video_path(path_input: Union[str, Path]) -> Path:
    """
    Validate that the video path exists, is a file, is non-empty, and has a video format.
    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is 0 bytes or not a valid video file.
    """
    path = Path(path_input).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Video file not found at: {path}")

    if not path.is_file():
        raise ValueError(f"Target path is not a file: {path}")

    file_size = path.stat().st_size
    if file_size == 0:
        raise ValueError(f"Video file is empty (0 bytes): {path}")

    # Extension or basic format check
    ext = path.suffix.lower()
    if ext not in VALID_EXTENSIONS:
        # Check if FFmpeg can read video stream
        info = get_video_info(path)
        if not info.get("has_video"):
            raise ValueError(f"Unsupported or invalid video format: {path.name}")

    return path


# Alias for backward/test compatibility
validate_input = validate_video_path


def get_video_info(video_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Inspect video metadata using FFmpeg binary.
    Returns dict with keys: duration (sec), width, height, fps, has_video, has_audio.
    """
    path = Path(video_path).resolve()
    if not path.exists() or path.stat().st_size == 0:
        return {
            "duration": 0.0,
            "width": 0,
            "height": 0,
            "fps": 0.0,
            "has_video": False,
            "has_audio": False,
        }

    exe = get_ffmpeg_exe()
    proc = subprocess.run(
        [exe, "-i", str(path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    output = proc.stderr

    duration = 0.0
    dur_match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", output)
    if dur_match:
        hours, mins, secs = (
            float(dur_match.group(1)),
            float(dur_match.group(2)),
            float(dur_match.group(3)),
        )
        duration = hours * 3600 + mins * 60 + secs

    width, height = 0, 0
    res_match = re.search(r"Stream.*Video:.*?(\d{2,5})x(\d{2,5})", output)
    if res_match:
        width, height = int(res_match.group(1)), int(res_match.group(2))

    fps = 0.0
    fps_match = re.search(r"(\d+(?:\.\d+)?)\s*fps", output)
    if fps_match:
        fps = float(fps_match.group(1))

    has_video = "Video:" in output
    has_audio = "Audio:" in output

    return {
        "duration": duration,
        "width": width,
        "height": height,
        "fps": fps,
        "has_video": has_video,
        "has_audio": has_audio,
    }


def download_video(url: str, output_dir: Union[str, Path]) -> Path:
    """
    Download a video from a URL (YouTube, TikTok, etc.) via yt-dlp.
    Falls back to generating a synthetic mock video if the URL is a mock scheme.
    """
    out_dir = Path(output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if url.startswith("mock://") or url == "mock":
        target = out_dir / "mock_ingested_video.mp4"
        return create_synthetic_video(target, duration=3.0)

    try:
        import yt_dlp
    except ImportError:
        raise RuntimeError("yt-dlp is required to download online videos. Install with 'uv add yt-dlp'.")

    from video_pipeline.ffmpeg_resolver import get_ffmpeg_exe
    ffmpeg_exe = Path(get_ffmpeg_exe())
    ffmpeg_dir = ffmpeg_exe.parent

    out_template = str(out_dir / "%(id)s.%(ext)s")
    ydl_opts = {
        "format": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best",
        "outtmpl": out_template,
        "merge_output_format": "mp4",
        "ffmpeg_location": str(ffmpeg_dir),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "retries": 2,
        "socket_timeout": 10,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        downloaded_path = Path(filename).with_suffix(".mp4")
        if not downloaded_path.exists():
            downloaded_path = Path(filename)
        return validate_video_path(downloaded_path)


def ingest_video(
    source: Union[str, Path],
    output_dir: Optional[Union[str, Path]] = None,
    mock: bool = False,
) -> Path:
    """
    Main entrypoint for video ingestion.
    Resolves local paths, downloads remote URLs, or creates synthetic media in mock mode.
    """
    if mock or str(source).startswith("mock://") or source == "mock":
        target_dir = Path(output_dir or tempfile.gettempdir())
        target = target_dir / "mock_ingested_video.mp4"
        return create_synthetic_video(target, duration=3.0)

    source_str = str(source).strip()
    if source_str.startswith("http://") or source_str.startswith("https://"):
        target_dir = Path(output_dir or tempfile.gettempdir())
        return download_video(source_str, target_dir)

    return validate_video_path(source)
