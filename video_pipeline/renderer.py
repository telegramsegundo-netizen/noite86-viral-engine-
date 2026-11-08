"""
video_pipeline/renderer.py
Video rendering and reformatting engine.
Converts 16:9 landscape clips to 1080x1920 9:16 vertical videos (TikTok, Reels, Shorts)
with boxblur background padding, centered crisp video, safe-zone burned subtitles,
and high-converting e-commerce Call-to-Action (CTA) overlay banners.
Safely escapes Windows file paths for FFmpeg filtergraphs.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Optional, Union

from video_pipeline.ffmpeg_resolver import get_ffmpeg_exe
from video_pipeline.ingestion import get_video_info


def escape_ffmpeg_path(path_input: Union[str, Path]) -> str:
    """
    Sanitize and escape a filesystem path for FFmpeg filtergraph syntax on Windows.
    Colons in Windows drive letters (e.g. C:) must be escaped as C\\: or C\\:/
    and backslashes replaced with forward slashes to prevent syntax errors.
    """
    raw_str = str(path_input).strip()
    # Normalize backslashes to forward slashes
    forward_slash = raw_str.replace("\\", "/")
    # Escape drive letter colon (e.g. C: -> C\:)
    if len(forward_slash) >= 2 and forward_slash[1] == ":":
        escaped = forward_slash[0] + r"\:" + forward_slash[2:]
    else:
        escaped = forward_slash.replace(":", r"\:")
    return escaped


# Alias for backward/test compatibility
sanitize_path_for_filter = escape_ffmpeg_path


def build_filtergraph(
    cta_text: str = "COLEÇÃO NOITE 86 // LINK NA BIO",
    subtitle_path: Optional[Union[str, Path]] = None,
    mode: str = "blur_padding",
    target_width: int = 1080,
    target_height: int = 1920,
    duration: float = 0.0,
    header_text: Optional[str] = "🚨 NOITE 86 // GTA 6 BRASIL 🚨",
) -> str:
    """
    Build FFmpeg filter_complex string converting 16:9 to 9:16 vertical
    with boxblur padding, burned subtitles, and CTA banners.
    """
    w = target_width
    h = target_height

    # 1. Base transformation: blur_padding (default) or crop_center
    if mode == "crop_center":
        filter_chain = [
            f"[0:v]scale=-1:{h},crop={w}:{h}[base]"
        ]
        current_node = "base"
    else:
        # Default: blur_padding (stretched blurred background + centered crisp video)
        filter_chain = [
            f"[0:v]split=2[bg_raw][fg_raw]",
            f"[bg_raw]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},boxblur=20:5[bg]",
            f"[fg_raw]scale={w}:-1[fg]",
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2[base]",
        ]
        current_node = "base"

    # 2. Burned Subtitles in Mobile Safe Zone
    if subtitle_path:
        sub_p = Path(subtitle_path)
        if sub_p.exists():
            safe_sub = escape_ffmpeg_path(sub_p)
            next_node = "subbed"
            # Style places text in mobile safe zone (lower third, right above bottom CTA)
            # Explicit PlayRes coordinates ensure pixel-accurate scaling on 1080x1920
            style = f"PlayResY={h},PlayResX={w},Fontsize=42,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=3,Alignment=2,MarginV=300,MarginL=80,MarginR=80"
            filter_chain.append(
                f"[{current_node}]subtitles='{safe_sub}':force_style='{style}'[{next_node}]"
            )
            current_node = next_node

    # 3. Call-To-Action (CTA) Text Overlays
    cta_clean = cta_text.replace("'", "").replace(":", "-").replace("%", "").strip() if cta_text else ""
    header_clean = header_text.replace("'", "").replace(":", "-").replace("%", "").strip() if header_text else ""

    overlay_count = 0

    # Top Header Banner
    if header_clean:
        next_node = f"v_top_{overlay_count}"
        top_filter = (
            f"[{current_node}]drawtext=text='{header_clean}':expansion=none:fontsize=36:fontcolor=yellow:"
            f"box=1:boxcolor=black@0.7:boxborderw=12:x=(w-text_w)/2:y=160[{next_node}]"
        )
        filter_chain.append(top_filter)
        current_node = next_node
        overlay_count += 1

    # Bottom Sticky CTA Footer
    if cta_clean:
        next_node = f"v_bot_{overlay_count}"
        bot_filter = (
            f"[{current_node}]drawtext=text='{cta_clean}':expansion=none:fontsize=32:fontcolor=white:"
            f"box=1:boxcolor=0xFF007FAA:boxborderw=10:x=(w-text_w)/2:y=h-240[{next_node}]"
        )
        filter_chain.append(bot_filter)
        current_node = next_node
        overlay_count += 1

    # Outro End-Card (if duration > 4s)
    if duration >= 4.0:
        next_node = "v_outro"
        outro_time = max(0.0, duration - 3.0)
        outro_filter = (
            f"[{current_node}]drawtext=text='GARANTA O SEU ANTES QUE ACABE!\nLINK NA BIO':"
            f"fontsize=42:fontcolor=white:box=1:boxcolor=black@0.85:boxborderw=20:"
            f"x=(w-text_w)/2:y=(h-text_h)/2:enable='gte(t,{outro_time:.2f})'[{next_node}]"
        )
        filter_chain.append(outro_filter)
        current_node = next_node

    # If the last step has a named node, alias it to [vout] or leave it as current_node
    if current_node != "vout":
        filter_chain.append(f"[{current_node}]copy[vout]")

    return ";".join(filter_chain)


# Alias
create_vertical_filter = build_filtergraph


def render_vertical_video(
    input_video: Union[str, Path],
    output_video: Union[str, Path],
    subtitle_path: Optional[Union[str, Path]] = None,
    cta_text: Optional[str] = "COLEÇÃO NOITE 86 // LINK NA BIO",
    header_text: Optional[str] = "🚨 NOITE 86 // GTA 6 BRASIL 🚨",
    narration_audio: Optional[Union[str, Path]] = None,
    mode: str = "blur_padding",
    target_width: int = 1080,
    target_height: int = 1920,
) -> Path:
    """
    Render 1080x1920 9:16 vertical video using FFmpeg filtergraph.
    Supports burning subtitles, adding NOITE 86 CTA banners, and mixing
    narration audio (ducking original video audio if present).
    """
    in_path = Path(input_video).resolve()
    if not in_path.exists():
        raise FileNotFoundError(f"Input video not found: {in_path}")

    out_path = Path(output_video).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    info = get_video_info(in_path)
    duration = info.get("duration", 0.0)
    has_audio = info.get("has_audio", False)

    filter_complex = build_filtergraph(
        cta_text=cta_text or "",
        subtitle_path=subtitle_path,
        mode=mode,
        target_width=target_width,
        target_height=target_height,
        duration=duration,
        header_text=header_text,
    )

    exe = get_ffmpeg_exe()
    cmd = [
        exe,
        "-y",
        "-i", str(in_path),
    ]

    has_narration = False
    if narration_audio:
        nar_path = Path(narration_audio).resolve()
        if nar_path.exists() and nar_path.stat().st_size > 0:
            has_narration = True
            cmd.extend(["-i", str(nar_path)])

    # Video filters
    cmd.extend([
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
    ])

    # Audio mapping & mixing logic com AGENTE 14 (Audio Mastering Engineer)
    from autonomous_engine.audio_taskforce import AudioQualityTaskforce
    audio_engine = AudioQualityTaskforce()

    if has_narration or has_audio:
        mastered_audio_filter = audio_engine.build_broadcast_audio_filter(
            has_narration=has_narration,
            has_video_audio=has_audio,
            bg_volume=0.12,
            narration_volume=1.0,
            target_lufs=-14.0
        )
        if mastered_audio_filter:
            combined_filter = f"{filter_complex};{mastered_audio_filter}"
            fc_idx = cmd.index("-filter_complex")
            cmd[fc_idx + 1] = combined_filter
            cmd.extend(["-map", "[aout]", "-c:a", "aac", "-b:a", "192k", "-ar", "48000"])
        elif has_narration:
            cmd.extend(["-map", "1:a", "-c:a", "aac", "-b:a", "192k", "-ar", "48000"])
        elif has_audio:
            cmd.extend(["-map", "0:a?", "-c:a", "aac", "-b:a", "128k", "-ar", "48000"])

    # Ensure output is clipped to the shortest or padded properly
    cmd.extend(["-shortest", str(out_path)])

    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg vertical video render failed: {proc.stderr}")

    if not out_path.exists() or out_path.stat().st_size == 0:
        raise RuntimeError(f"Rendered video missing or 0 bytes: {out_path}")

    return out_path
