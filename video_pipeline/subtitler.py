"""
video_pipeline/subtitler.py
Subtitle formatter and generator producing standards-compliant .srt, .vtt,
and styled .ass (Advanced SubStation Alpha) subtitle files with accurate timestamps.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Union

from video_pipeline.transcriber import TranscriptSegment


def format_timestamp_srt(seconds: float) -> str:
    """Format seconds into SubRip timecode (HH:MM:SS,mmm)."""
    if seconds < 0:
        seconds = 0.0
    total_ms = int(round(seconds * 1000))
    ms = total_ms % 1000
    total_sec = total_ms // 1000
    s = total_sec % 60
    total_min = total_sec // 60
    m = total_min % 60
    h = total_min // 60
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def format_timestamp_vtt(seconds: float) -> str:
    """Format seconds into WebVTT timecode (HH:MM:SS.mmm)."""
    if seconds < 0:
        seconds = 0.0
    total_ms = int(round(seconds * 1000))
    ms = total_ms % 1000
    total_sec = total_ms // 1000
    s = total_sec % 60
    total_min = total_sec // 60
    m = total_min % 60
    h = total_min // 60
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def format_timestamp_ass(seconds: float) -> str:
    """Format seconds into ASS timecode (H:MM:SS.cc where cc is centiseconds)."""
    if seconds < 0:
        seconds = 0.0
    total_cs = int(round(seconds * 100))
    cs = total_cs % 100
    total_sec = total_cs // 100
    s = total_sec % 60
    total_min = total_sec // 60
    m = total_min % 60
    h = total_min // 60
    return f"{h:01d}:{m:02d}:{s:02d}.{cs:02d}"


def _extract_segment_fields(seg: Any, fallback_id: int = 1) -> tuple[int, float, float, str]:
    """Extract (id, start, end, text) from dict or TranscriptSegment."""
    if isinstance(seg, dict):
        seg_id = seg.get("id", fallback_id)
        start = float(seg.get("start", 0.0))
        end = float(seg.get("end", start + 2.0))
        text = str(seg.get("text", "")).strip()
    else:
        seg_id = getattr(seg, "id", fallback_id)
        start = float(getattr(seg, "start", 0.0))
        end = float(getattr(seg, "end", start + 2.0))
        text = str(getattr(seg, "text", "")).strip()
    return seg_id, start, end, text


def generate_srt(segments: Sequence[Union[Dict[str, Any], TranscriptSegment]]) -> str:
    """
    Generate SubRip (.srt) subtitle string.
    Format:
    1
    00:00:01,000 --> 00:00:03,500
    TEXT CONTENT
    """
    lines: List[str] = []
    for idx, seg in enumerate(segments, start=1):
        _, start, end, text = _extract_segment_fields(seg, idx)
        lines.append(str(idx))
        lines.append(f"{format_timestamp_srt(start)} --> {format_timestamp_srt(end)}")
        lines.append(text)
        lines.append("")  # Blank line separator
    return "\n".join(lines).strip() + "\n"


# Alias
to_srt = generate_srt


def generate_vtt(segments: Sequence[Union[Dict[str, Any], TranscriptSegment]]) -> str:
    """
    Generate WebVTT (.vtt) subtitle string.
    Format:
    WEBVTT

    1
    00:00:01.000 --> 00:00:03.500
    TEXT CONTENT
    """
    lines: List[str] = ["WEBVTT", ""]
    for idx, seg in enumerate(segments, start=1):
        _, start, end, text = _extract_segment_fields(seg, idx)
        lines.append(str(idx))
        lines.append(f"{format_timestamp_vtt(start)} --> {format_timestamp_vtt(end)}")
        lines.append(text)
        lines.append("")
    return "\n".join(lines).strip() + "\n"


# Alias
to_vtt = generate_vtt


def generate_ass(
    segments: Sequence[Union[Dict[str, Any], TranscriptSegment]],
    title: str = "Vice City Neon Subtitles",
    video_width: int = 1080,
    video_height: int = 1920,
) -> str:
    """
    Generate Advanced SubStation Alpha (.ass) subtitle string styled with
    Vice City retro neon colors and high mobile legibility safe-zone positioning.
    """
    header = f"""[Script Info]
Title: {title}
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: {video_width}
PlayResY: {video_height}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: ViceCityNeon,Arial,58,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5.0,2.0,2,40,40,280,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events: List[str] = []
    for idx, seg in enumerate(segments, start=1):
        _, start, end, text = _extract_segment_fields(seg, idx)
        t_start = format_timestamp_ass(start)
        t_end = format_timestamp_ass(end)
        events.append(f"Dialogue: 0,{t_start},{t_end},ViceCityNeon,,0,0,0,,{text}")

    return header + "\n".join(events) + "\n"


def export_subtitles(
    segments: Sequence[Union[Dict[str, Any], TranscriptSegment]],
    output_prefix: Union[str, Path],
    formats: Iterable[str] = ("srt", "vtt", "ass"),
) -> Dict[str, Path]:
    """
    Export subtitles to files on disk.
    Returns mapping of format extension -> Path.
    """
    prefix = Path(output_prefix).resolve()
    prefix.parent.mkdir(parents=True, exist_ok=True)
    created: Dict[str, Path] = {}

    if "srt" in formats:
        srt_file = prefix.with_suffix(".srt")
        srt_file.write_text(generate_srt(segments), encoding="utf-8")
        created["srt"] = srt_file

    if "vtt" in formats:
        vtt_file = prefix.with_suffix(".vtt")
        vtt_file.write_text(generate_vtt(segments), encoding="utf-8")
        created["vtt"] = vtt_file

    if "ass" in formats:
        ass_file = prefix.with_suffix(".ass")
        ass_file.write_text(generate_ass(segments), encoding="utf-8")
        created["ass"] = ass_file

    return created
