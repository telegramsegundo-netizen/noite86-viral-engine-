"""
video_pipeline package
OPERAÇÃO NOITE 86 — Fábrica Inteligente de Vídeos para TikTok, Instagram Reels e YouTube Shorts.
"""
from __future__ import annotations

from video_pipeline.ffmpeg_resolver import (
    check_ffmpeg_filters,
    create_synthetic_video,
    get_ffmpeg_exe,
    resolve_ffmpeg,
)
from video_pipeline.ingestion import (
    download_video,
    get_video_info,
    ingest_video,
    validate_input,
    validate_video_path,
)
from video_pipeline.localizer import (
    RuleBasedOfflineLocalizer,
    VideoLocalizer,
    localize_text,
)
from video_pipeline.renderer import (
    build_filtergraph,
    create_vertical_filter,
    escape_ffmpeg_path,
    render_vertical_video,
    sanitize_path_for_filter,
)
from video_pipeline.rights_reviewer import (
    LicenseType,
    RightsClearanceReport,
    RightsReviewer,
)
from video_pipeline.subtitler import (
    export_subtitles,
    generate_ass,
    generate_srt,
    generate_vtt,
    to_srt,
    to_vtt,
)
from video_pipeline.transcriber import (
    FasterWhisperTranscriber,
    MockTranscriber,
    TranscriptSegment,
    Transcriber,
    WordTimestamp,
    extract_audio,
    transcribe_video,
)
from video_pipeline.translator import AITranslator
from video_pipeline.voice_engine import VoiceEngine

__all__ = [
    # ffmpeg_resolver
    "get_ffmpeg_exe",
    "resolve_ffmpeg",
    "check_ffmpeg_filters",
    "create_synthetic_video",
    # ingestion
    "validate_video_path",
    "validate_input",
    "get_video_info",
    "download_video",
    "ingest_video",
    # transcriber
    "extract_audio",
    "WordTimestamp",
    "TranscriptSegment",
    "MockTranscriber",
    "FasterWhisperTranscriber",
    "Transcriber",
    "transcribe_video",
    # localizer & translator
    "RuleBasedOfflineLocalizer",
    "VideoLocalizer",
    "localize_text",
    "AITranslator",
    # voice
    "VoiceEngine",
    # rights
    "RightsReviewer",
    "LicenseType",
    "RightsClearanceReport",
    # subtitler
    "generate_srt",
    "to_srt",
    "generate_vtt",
    "to_vtt",
    "generate_ass",
    "export_subtitles",
    # renderer
    "escape_ffmpeg_path",
    "sanitize_path_for_filter",
    "build_filtergraph",
    "create_vertical_filter",
    "render_vertical_video",
]
