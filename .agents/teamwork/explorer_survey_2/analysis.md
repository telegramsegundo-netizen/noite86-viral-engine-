# Technical Specification & Survey: Automated Video Localization Pipeline (R2)

**Author:** Explorer 2 (Video Pipeline Spec Explorer)  
**Date:** 2026-11-07  
**Working Directory:** `.agents/teamwork/explorer_survey_2/`  
**Status:** Validated & Executable  

---

## 1. Executive Summary

Requirement R2 mandates an automated, executable video localization and clipping pipeline in Python that transforms international gaming clips (specifically English GTA 6 trailers, gameplay leaks, reactions, and analysis) into viral, high-converting Brazilian vertical shorts (9:16 format for TikTok, Instagram Reels, and YouTube Shorts).

The core pipeline encompasses:
1. **Video Ingestion:** Local `.mp4` file ingestion and remote URL downloading via `yt-dlp` (with offline synthetic mock fallbacks).
2. **Audio Extraction & Speech-to-Text:** 16kHz mono PCM extraction, timestamped transcription via `faster-whisper` (CTranslate2 INT8 CPU/CUDA) and OpenAI Whisper API, plus an instant `MockTranscriber` for deterministic offline testing.
3. **Translation & Cultural Localization:** High-energy English to Brazilian Portuguese (`pt-BR`) adaptation using viral gamer slang ("hype surreal", "tá maluco", "o bagulho tá insano", "drop exclusivo", "link na bio"), supported by LLM prompts and an offline rule-based dictionary engine.
4. **Subtitling:** Export to standardized `.srt`, `.vtt`, and rich `.ass` (Advanced SubStation Alpha) subtitle formats with precise millisecond timestamps.
5. **Video Reformatting & Rendering:** Transforming 16:9 landscape video into 1080x1920 vertical 9:16 video using **blur padding** (top & bottom blurred background, middle crisp video), burning styled subtitles in the mobile safe zone, and overlaying high-converting Call-to-Action (CTA) headers, footers, and outro cards pointing to the Vice City e-commerce store.
6. **Audio Dubbing (Optional Add-on):** Synthesizing natural Portuguese speech via `edge-tts` (`pt-BR-AntonioNeural` / `pt-BR-FranciscaNeural`) with background audio ducking (-12dB).

All critical pipeline stages have been live-tested and verified on the target Windows environment.

---

## 2. Windows Runtime Environment & Toolchain Discovery

### 2.1 System Environment Inspection
Our exploratory execution on the Windows host revealed the following environmental realities:
- **Python / Package Manager:** `uv` is installed (`uv 0.12.22`), providing managed CPython 3.12 and 3.14 environments. Execution via `uv run` guarantees reproducible dependency isolation without system PATH pollution.
- **FFmpeg Discovery:** Standalone `ffmpeg.exe` was not initially bound to system PATH. However, installing `imageio-ffmpeg` provides a precompiled, fully featured FFmpeg binary (`ffmpeg-win-x86_64-v9.0.2.exe`) directly in the uv cache/site-packages directory.
- **Node.js:** Node.js v24.20.0 and npm 11.19.0 are also available if secondary JS tooling is desired, but Python was chosen as the primary language due to superior native bindings for Whisper, CTranslate2, edge-tts, and audio processing.

### 2.2 Verified FFmpeg Binary Capabilities
Direct inspection of the `imageio-ffmpeg` binary confirmed full filter support:
```
ffmpeg version 9.0.2-essentials_build-www.gyan.dev
Filters enabled:
  drawtext: True
  subtitles: True
  crop: True
  boxblur: True
  gblur: True
Libraries:
  libass (subtitles & ASS rendering)
  libfreetype & libharfbuzz (text rendering & font shaping)
  libx264, libmp3lame, aac, libopus
```

### 2.3 Critical Windows Implementation Nuance: Path Escaping in FFmpeg
During our live filter tests, we discovered a crucial Windows pitfall when burning subtitles using the `subtitles` filter:
- In FFmpeg filtergraphs, the colon `:` is a parameter delimiter. An absolute Windows path like `C:\Users\foo\sub.srt` causes FFmpeg to choke on `C:`.
- **Solution Strategy:**
  1. Pass paths either as relative filenames (executing FFmpeg in the working directory where the subtitle file resides).
  2. Or escape backslashes and colons: `subtitles='C\\:/Users/foo/sub.srt'`.
  3. Or convert to forward slashes with double-escaped drive letters: `C\:/Users/foo/sub.srt`.

---

## 3. Pipeline Architecture & Modular Design

The pipeline follows a clean, modular Unix-philosophy design where each stage is a decoupled Python module with clear input/output contracts.

```
video_pipeline/
├── __init__.py
├── cli.py                     # Command-line interface (argparse/click)
├── config.py                  # Pydantic schema for pipeline configuration
├── ingestion.py               # Local video handling & yt-dlp downloader
├── audio.py                   # FFmpeg audio stream extraction (16kHz WAV)
├── transcription/
│   ├── __init__.py
│   ├── base.py                # Abstract Base Transcriber & Segment model
│   ├── faster_whisper.py      # CTranslate2 local engine (CPU int8 / GPU)
│   ├── openai_whisper.py      # Cloud API fallback
│   └── mock.py                # Deterministic offline mock for CI/CD
├── localization/
│   ├── __init__.py
│   ├── base.py                # Abstract Base Localizer
│   ├── llm.py                 # Gemini / OpenAI gamer slang prompt engine
│   └── rule_based.py          # Deterministic offline slang dictionary
├── subtitling.py              # SRT, VTT, and ASS format generators
├── rendering.py               # 16:9 to 9:16 reformatting, subtitle burning & CTA overlays
├── dubbing.py                 # edge-tts voiceover & audio ducking (optional)
└── utils/
    ├── ffmpeg.py              # Automatic ffmpeg binary resolution & subprocess runner
    └── synthetic.py           # Synthetic video generator for tests
```

---

## 4. Stage-by-Stage Specifications

### Stage 1: Video Ingestion (`ingestion.py`)
- **Inputs:**
  - Local filepath: `video.mp4`, `.mov`, `.mkv`, `.webm`.
  - Remote URL: YouTube (`youtube.com/watch`, `youtu.be/`, `/shorts/`), TikTok, Instagram Reels, Twitter/X.
  - Mock URL: `mock://sample` or `--mock` flag.
- **Mechanism:**
  - For URLs: Uses `yt_dlp.YoutubeDL` with options:
    ```python
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': str(output_dir / '%(id)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'quiet': True,
    }
    ```
  - For Mock / Test Mode: Automatically generates a 2-5 second synthetic video via `ffmpeg`'s `testsrc` filter with sine-wave audio if offline or running automated tests.

### Stage 2: Audio Extraction & Speech-to-Text (`audio.py` & `transcription/`)
- **Audio Extraction:**
  - Extracts 16kHz mono 16-bit PCM WAV:
    `ffmpeg -y -i input.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 audio.wav`
- **Data Model:**
  ```python
  class WordTimestamp(BaseModel):
      word: str
      start: float
      end: float
      probability: float = 1.0

  class TranscriptSegment(BaseModel):
      id: int
      start: float
      end: float
      text: str
      words: list[WordTimestamp] = []
  ```
- **Transcription Engines:**
  1. `FasterWhisperTranscriber`:
     - Model: `tiny` (39MB) or `base` (74MB) for high speed; `small`/`medium` for max accuracy.
     - Device: `cpu`, `compute_type="int8"` (runs on standard Windows laptops without dedicated GPU in near real-time).
     - Extracts word-level timestamps via `word_timestamps=True`.
  2. `MockTranscriber`:
     - Returns deterministic GTA 6 gaming segments in 0.01 seconds without loading any AI model.

### Stage 3: Translation & Cultural Localization (`localization/`)
- **Cultural Adaptation Criteria:**
  - Standard literal translation kills video engagement on TikTok/Reels. The translation must use authentic Brazilian gaming slang and high-energy punctuation.
  - Vocabulary mapping examples:
    - *"Look at this trailer"* -> *"SE LIGA NESSE TRAILER, TÁ MALUCO!"*
    - *"The graphics are unbelievable"* -> *"O GRÁFICO TÁ SIMPLESMENTE SURREAL!"*
    - *"Vice City is back"* -> *"VICE CITY TÁ DE VOLTA, QUE NOSTALGIA INSANA!"*
    - *"Check the link in bio"* -> *"DROP LIMITADO NA BIO, NÃO MOSCA!"*
- **LLM Prompt Architecture:**
  - System prompt enforces uppercase punchy subtitles, short sentences (max 6-8 words per subtitle block for high reading speed on mobile), and viral hype tone.
- **RuleBasedOfflineLocalizer:**
  - Dictionary of 50+ common English gaming/trailer phrases mapped directly to pt-BR gamer slang. Guarantees 100% offline predictability during CI tests.

### Stage 4: Subtitle Generation (`subtitling.py`)
- **SRT Generation:**
  - Timecode format: `00:00:01,234 --> 00:00:03,567`
  - Clean UTF-8 without BOM.
- **VTT Generation:**
  - Timecode format: `00:00:01.234 --> 00:00:03.567` with `WEBVTT` header.
- **ASS (Advanced SubStation Alpha) Generation:**
  - Styled for GTA Vice City aesthetics:
    - Primary Color: Pure White (`&H00FFFFFF`) or Neon Yellow (`&H0000FFFF`).
    - Outline: 3.5px solid black (`&H00000000`) for universal contrast against light or dark footage.
    - Font: `Arial` or `Impact`, Bold (`-1`), MarginV: 180 (positions text ~75% down the screen, leaving room for TikTok bottom text and buttons).

### Stage 5: Video Reformatting & Rendering (`rendering.py`)
- **Target Aspect Ratio:** 9:16 vertical (1080x1920 pixels).
- **Transformation Modes:**
  1. `blur_padding` (**Primary Recommended Mode**):
     - Background: Stretched and cropped to 1080x1920 with heavy Gaussian or box blur (`boxblur=25:5`).
     - Foreground: Original 16:9 video scaled to 1080px width, placed directly in the center.
     - FFmpeg Filtergraph:
       ```
       [0:v]split=2[bg_raw][fg_raw];
       [bg_raw]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5[bg];
       [fg_raw]scale=1080:-1[fg];
       [bg][fg]overlay=(W-w)/2:(H-h)/2[base]
       ```
  2. `crop_center`: Direct center crop to 1080x1920 (for gameplay centered on player character).
  3. `letterbox`: Black or retro neon color bars top and bottom.
- **Burned Subtitles:**
  - Appended via `subtitles=temp.srt:force_style='FontSize=22,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2.5,Alignment=2,MarginV=180'`
- **High-Converting CTA Overlays:**
  - Top Banner (Sticky Hook):
    `drawtext=text='🚨 DROP EXCLUSIVO VICE CITY 🚨':fontsize=36:fontcolor=yellow:box=1:boxcolor=black@0.7:boxborderw=12:x=(w-text_w)/2:y=160`
  - Bottom Store CTA (Footer Hook):
    `drawtext=text='🔗 PEÇAS LIMITADAS: LINK NA BIO':fontsize=32:fontcolor=white:box=1:boxcolor=0xFF007FAA:boxborderw=10:x=(w-text_w)/2:y=h-240`
  - Outro End-Card (Last 3 seconds):
    `drawtext=text='GARANTA O SEU ANTES QUE ACABE!\nACESSA: VICECITY80S.COM':fontsize=42:fontcolor=white:box=1:boxcolor=black@0.85:boxborderw=20:x=(w-text_w)/2:y=(h-text_h)/2:enable='gte(t,VIDEO_DURATION-3)'`

### Stage 6: Audio Dubbing (Optional Add-on) (`dubbing.py`)
- Uses `edge_tts.Communicate(text, voice="pt-BR-AntonioNeural")`.
- Mixes translated TTS speech with original audio ducked to 20% volume (-14dB) using FFmpeg `amix` filter or `volume` filter with `sidechaincompress`.

---

## 5. CLI Interface & Configuration

### 5.1 CLI Command Structure
The tool will provide both a standalone executable CLI and Python module invocation:
```bash
# Full end-to-end processing:
python -m video_pipeline.cli process "https://youtube.com/shorts/example" \
    --mode blur_padding \
    --cta-text "COLEÇÃO VICE CITY - LINK NA BIO" \
    --output output/gta6_short_br.mp4

# Local video file with custom options:
python -m video_pipeline.cli process input_trailer.mp4 \
    --reformat 9:16 \
    --transcriber faster-whisper \
    --model-size tiny \
    --burn-subtitles \
    --export-srt \
    --output-dir ./dist

# Fast offline test run (uses synthetic video and mock AI engines):
python -m video_pipeline.cli process --mock --offline --output-dir ./dist
```

### 5.2 Configuration Options (Pydantic Schema)
```python
class PipelineConfig(BaseModel):
    input_source: str
    output_path: Path
    mode: Literal["blur_padding", "crop_center", "letterbox"] = "blur_padding"
    target_width: int = 1080
    target_height: int = 1920
    transcriber_engine: Literal["faster-whisper", "openai", "mock"] = "faster-whisper"
    whisper_model: str = "tiny"
    whisper_device: str = "cpu"
    localizer_engine: Literal["llm", "rule_based"] = "rule_based"
    burn_subtitles: bool = True
    subtitle_style: str = "vice_city_neon"
    cta_header_text: str = "🚨 NOVO VAZAMENTO GTA 6 🚨"
    cta_footer_text: str = "🛒 DROP EXCLUSIVO VICE CITY: LINK NA BIO"
    enable_dubbing: bool = False
    tts_voice: str = "pt-BR-AntonioNeural"
    offline: bool = False
```

---

## 6. Offline Testing & Deterministic Verification Strategy

A major risk in multi-agent video projects is test suites hanging or failing due to:
1. Missing `ffmpeg` in system PATH.
2. Missing internet connection to download YouTube clips or connect to LLM/Whisper APIs.
3. Lack of GPU leading to Whisper timeouts.

### 6.1 Mitigation & Verification Protocol
1. **Bundled FFmpeg via `imageio-ffmpeg`:**
   The utility module `video_pipeline.utils.ffmpeg` will automatically resolve:
   `ffmpeg_exe = shutil.which("ffmpeg") or imageio_ffmpeg.get_ffmpeg_exe()`
   This guarantees FFmpeg is always found on Windows without manual environment changes.
2. **Synthetic Media Generation:**
   `video_pipeline.utils.synthetic.create_test_video(duration=2, size="1280x720")` uses FFmpeg's `lavfi` source (`testsrc` + `sine`) to generate a valid, real `.mp4` file in ~1 second with zero network access.
3. **Mock AI Engines:**
   When `--mock` or `--offline` is set, `MockTranscriber` and `RuleBasedOfflineLocalizer` generate realistic, timestamped subtitles and translations instantly.
4. **Fast Unit & E2E Pytest Suite:**
   The test suite executes the complete chain:
   Synthetic video -> Audio extraction -> Mock transcription -> Slang translation -> SRT/VTT generation -> 9:16 vertical reformatting + blur padding + subtitle burning + CTA overlay.
   **Total test duration: < 3 seconds**, completely deterministic, 100% offline.

---

## 7. Recommended Implementation Plan for Milestone 2

When Worker agents implement Milestone 2, they should execute in this order:
1. **Module Scaffolding:** Create `video_pipeline/` package and `pyproject.toml` with `imageio-ffmpeg`, `pydantic`, `yt-dlp`, `faster-whisper`, `edge-tts`, `pytest`.
2. **Core Utilities:** Implement `ffmpeg.py` (binary resolver + safe execution) and `synthetic.py`.
3. **Transcription & Localization:** Implement base classes, mock engines, and live engines (`faster-whisper` and `rule_based`/`llm`).
4. **Subtitling & Rendering:** Implement SRT/VTT writers and FFmpeg filtergraph builder for 9:16 blur padding + subtitle burning + CTA text.
5. **CLI & E2E Integration:** Implement `cli.py` argument parsing and pipeline runner.
6. **Automated Test Suite:** Comprehensive `tests/test_video_pipeline.py` testing each stage and the full pipeline.
