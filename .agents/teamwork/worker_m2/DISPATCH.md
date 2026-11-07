## 2026-11-07T00:57:43Z

You are Worker M2 (Video Localization & Vertical Clipping Pipeline Worker).
Your identity: teamwork_worker
Your working directory: C:\Users\victo\teamwork_projects\gta6_ecommerce_agents\.agents\teamwork\worker_m2\
Parent Orchestrator Conversation ID: a5e87fb8-1970-4caf-809e-c3fe935bfa92

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Mandatory instructions:
1. First, read the authoritative user request at:
   C:\Users\victo\teamwork_projects\gta6_ecommerce_agents\ORIGINAL_REQUEST.md
2. Read the master project architecture at:
   C:\Users\victo\teamwork_projects\gta6_ecommerce_agents\PROJECT.md
3. Read Explorer 2's survey analysis and specifications at:
   C:\Users\victo\teamwork_projects\gta6_ecommerce_agents\.agents\teamwork\explorer_survey_2\analysis.md
   and C:\Users\victo\teamwork_projects\gta6_ecommerce_agents\.agents\teamwork\explorer_survey_2\handoff.md
4. Read the E2E test suite and test runner declarations at:
   C:\Users\victo\teamwork_projects\gta6_ecommerce_agents\TEST_INFRA.md
   C:\Users\victo\teamwork_projects\gta6_ecommerce_agents\TEST_READY.md
   C:\Users\victo\teamwork_projects\gta6_ecommerce_agents\tests\test_e2e_tier1_features.py

Your Scope and Write Ownership:
You exclusively own and must implement the following files in C:\Users\victo\teamwork_projects\gta6_ecommerce_agents\:

Task 0 (Immediate Bugfix):
- `catalog/ip_filter.py`: Fix the defect at `_term_to_regex` (line ~217) where `re.escape(term)` escapes hyphens (`\-`) in Python 3.7+ causing `ammu\\[\s\-_]+nation` to miss literal hyphens. Ensure terms with hyphens (e.g. "Ammu-Nation", "e-Cola") are properly detected.

Task 1 (Video Pipeline Implementation):
- `video_pipeline/__init__.py`: Package initialization and exports.
- `video_pipeline/ffmpeg_resolver.py`: Auto-resolve FFmpeg binary via `imageio_ffmpeg.get_ffmpeg_exe()` with fallback to system PATH, verifying `libass`, `drawtext`, and `boxblur` filters.
- `video_pipeline/ingestion.py`: Video file ingestion and validation (inspecting duration, resolution, fps), plus optional URL download via yt-dlp with graceful error handling.
- `video_pipeline/transcriber.py`: Audio extraction to 16kHz mono WAV, timestamped speech-to-text transcription with faster-whisper CPU INT8, plus deterministic `MockTranscriber` for fast offline tests.
- `video_pipeline/localizer.py`: Portuguese translation & cultural localization (pt-BR) tailored for Brazilian gaming culture, viral 3s hook insertion, slang adaptation, plus `RuleBasedOfflineLocalizer` for offline deterministic runs and LLM prompt integration for live runs.
- `video_pipeline/subtitler.py`: Formatter producing `.srt`, `.vtt`, and `.ass` subtitle files with accurate timestamps and safe-zone styling.
- `video_pipeline/renderer.py`: FFmpeg filtergraph rendering 1080x1920 9:16 vertical video with blurred background padding (`boxblur=20:5`), centered crisp foreground video, safe-zone burned subtitles, and store Call-to-Action (CTA) overlay banners (e.g. pointing to catalog products / store link). Ensure Windows file path escaping in FFmpeg filtergraphs is handled cleanly.
- `video_pipeline/cli.py`: Unified CLI entrypoint (`python -m video_pipeline.cli process --input <path> --output-dir <dir> [--mock] [--cta <text>]`).
- `tests/test_video_pipeline.py`: Comprehensive test suite verifying all pipeline modules with synthetic test media (`lavfi`), running deterministically in <5s offline.

Verification:
- Run `uv run pytest tests/test_video_pipeline.py`
- Run `uv run pytest tests/test_e2e_tier1_features.py -k "f05 or f06 or f07 or f08 or f09 or f10"`
- Run `uv run pytest tests/test_e2e_tier2_boundaries.py` to confirm that all boundary and negative tests (including B05 hyphen evasion) pass cleanly.
- Run `uv run python tests/run_all_tests.py`

Deliverables:
- Write your completion report in C:\Users\victo\teamwork_projects\gta6_ecommerce_agents\.agents\teamwork\worker_m2\handoff.md
- Update your progress.md and send a message back to the orchestrator (conversation ID a5e87fb8-1970-4caf-809e-c3fe935bfa92) using send_message.
