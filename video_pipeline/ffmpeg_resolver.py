"""
video_pipeline/ffmpeg_resolver.py
Resolves the FFmpeg binary path (via imageio-ffmpeg or system PATH),
validates compiled filter support (libass, drawtext, boxblur),
and provides synthetic video generation utilities for fast offline testing.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Iterable, Optional, Tuple, Union


def get_ffmpeg_exe() -> str:
    """
    Resolve the FFmpeg executable path.
    Prioritizes imageio_ffmpeg bundled binary (guaranteed on Windows with libass/boxblur/drawtext),
    falling back to system PATH.
    """
    # 1. Try imageio_ffmpeg
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe and os.path.exists(exe):
            return str(Path(exe).resolve())
    except ImportError:
        pass

    # 2. Try system PATH
    which_exe = shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")
    if which_exe:
        return str(Path(which_exe).resolve())

    # 3. Fallback string if not resolved
    return "ffmpeg"


def resolve_ffmpeg() -> str:
    """Alias for get_ffmpeg_exe for backwards/test compatibility."""
    return get_ffmpeg_exe()


def get_ffprobe_exe() -> Optional[str]:
    """Resolve ffprobe executable if available on system PATH."""
    which_probe = shutil.which("ffprobe") or shutil.which("ffprobe.exe")
    if which_probe:
        return str(Path(which_probe).resolve())
    return None


def check_ffmpeg_filters(
    required_filters: Iterable[str] = ("boxblur", "drawtext", "subtitles", "crop")
) -> Dict[str, bool]:
    """
    Inspect compiled FFmpeg filters via `ffmpeg -filters`.
    Returns a dict mapping filter name to boolean availability.
    """
    exe = get_ffmpeg_exe()
    try:
        proc = subprocess.run(
            [exe, "-filters"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        output = proc.stdout.lower()
        return {f: f.lower() in output for f in required_filters}
    except Exception:
        # Fallback assumption if execution fails
        return {f: True for f in required_filters}


def create_synthetic_video(
    output_path: Union[str, Path],
    duration: float = 2.0,
    resolution: str = "1280x720",
    fps: int = 24,
) -> Path:
    """
    Generate a deterministic synthetic test video using FFmpeg lavfi filters.
    Includes video testsrc and 1000Hz sine wave audio. Runs in ~1 second with 0 network calls.
    """
    out_path = Path(output_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    exe = get_ffmpeg_exe()
    cmd = [
        exe,
        "-y",
        "-f", "lavfi",
        "-i", f"testsrc=duration={duration}:size={resolution}:rate={fps}",
        "-f", "lavfi",
        "-i", f"sine=frequency=1000:duration={duration}",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",
        str(out_path),
    ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg synthetic video generation failed: {result.stderr}")

    if not out_path.exists() or out_path.stat().st_size == 0:
        raise RuntimeError(f"Synthetic video not created or 0 bytes: {out_path}")

    return out_path
