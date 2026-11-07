# Project: GTA 6-Inspired E-Commerce & Multi-Agent Content Automation System

## Architecture
The system enables rapid, autonomous monetization leveraging the cultural momentum and aesthetic of 1980s/1990s Vice City and retro Miami neon culture without infringing Rockstar Games / Take-Two Interactive trademarks.

```
+-----------------------------------------------------------------------------------+
|                                 USER / OPERATOR                                   |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|                           Multi-Agent Operations Hub                              |
|  - run_agents.py (CLI: --mock / --live)                                           |
|  - Store Architect Agent  ──> generates store_config.json & merchandising bundles |
|  - Content Clipper Agent  ──> generates social_campaign.json (Hooks, Copy, Sched) |
+-----------------------------------------------------------------------------------+
         │                                                        │
         ▼                                                        ▼
+-----------------------------------+    +------------------------------------------+
|  Autonomous Web Storefront        |    |  Video Localization & Clipping Pipeline  |
|  - index.html (Vice City Neon)    |    |  - video_pipeline.py                     |
|  - products.json (12 items)       |    |  - ImageIO FFmpeg 9.0.2 auto-resolver    |
|  - Cart Drawer & Free Shipping Bar|    |  - Faster-Whisper / Mock Transcriber     |
|  - PIX Checkout Simulator (SVG QR)|    |  - PT-BR Gamer Slang Localizer           |
|  - Dual BRL / USD Pricing Engine  |    |  - Subtitles (.srt, .vtt, .ass)          |
+-----------------------------------+    |  - 9:16 Vertical Blur Pad + CTA Banner   |
                                         +------------------------------------------+
                                                  │
                                                  ▼
                                         +------------------------------------------+
                                         |  Viral TikTok / Reels / Shorts Assets    |
                                         |  (Ready for 24h immediate publication)   |
                                         +------------------------------------------+
```

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Out-of-the-Box Catalog | 12 high-margin products (>67%-86%) across streetwear, stash novelties, audio, desk decor | M1 | Survey (Explorer 1) |
| 2 | Generative AI Prompt Matrix | Midjourney v6.1 & Flux.1 Pro prompt specifications with optics, volumetric lighting, print vectors | M1 | Survey (Explorer 1) |
| 3 | IP Clearance Matrix & Scanner | Automated filter and legal guidelines prohibiting Rockstar Games / Take-Two trademarks | M1 | Survey (Explorer 1) |
| 4 | Catalog Data Schemas | TypeScript types, JSON Schema Draft-07, and master `products.json` | M1 | Survey (Explorer 1) |
| 5 | Video Ingestion Module | Local video ingestion (.mp4) and downloadable URL parsing fallback | M2 | Survey (Explorer 2) |
| 6 | Audio Extraction & STT | 16kHz audio extraction and timestamped transcription (Faster-Whisper CPU & MockTranscriber) | M2 | Survey (Explorer 2) |
| 7 | PT-BR Video Localization | High-energy Portuguese localization with viral gamer slang and cultural adaptation | M2 | Survey (Explorer 2) |
| 8 | Subtitle Generation | Precise subtitle generator in `.srt`, `.vtt`, and `.ass` formats | M2 | Survey (Explorer 2) |
| 9 | Vertical 9:16 Video Rendering | FFmpeg complex filter converting 16:9 to 9:16 vertical with boxblur padding and store CTA | M2 | Survey (Explorer 2) |
| 10 | Video Test Harness & Synthesizer | Synthetic test video generator (`lavfi`) running deterministic tests in <3s offline | M2 | Survey (Explorer 2) |
| 11 | Store Architect Agent | Merchandising, pricing strategy, taxonomy, bundles, and `store_config.json` generator | M3 | Survey (Explorer 3) |
| 12 | Content Clipper & Campaign Agent | Viral hooks (0-3s), PT-BR copy formulas, 3-tier hashtags, and 7-day social schedule | M3 | Survey (Explorer 3) |
| 13 | Multi-Agent Orchestrator CLI | Unified Python orchestration runner (`run_agents.py`) with mock and live modes | M3 | Survey (Explorer 3) |
| 14 | Responsive Vice City Web Store | Zero-dependency HTML5/Tailwind/JS storefront with modal gallery, cart drawer, and PIX simulator | M3 | Survey (Explorer 3) |
| 15 | System Validation Suite | 5-tier automated validation test suite (`validate_system.py`) | M3 | Survey (Explorer 3) |
| 16 | E2E Testing Infrastructure | Opaque-box requirement-driven test suite (Tiers 1-4) and `TEST_READY.md` publication | E2E Track | Project Pattern |
| 17 | E2E Verification & Hardening | 100% pass across all E2E test tiers + Tier 5 adversarial coverage hardening | Final (M4) | Project Pattern |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Catalog, AI Prompts & Legal Engine | F1, F2, F3, F4 | none | PLANNED |
| M2 | Video Localization & Vertical Pipeline | F5, F6, F7, F8, F9, F10 | none | PLANNED |
| M3 | Specialist Agents & Storefront Scaffold | F11, F12, F13, F14, F15 | M1 | PLANNED |
| M4 | Final Integration & Adversarial Hardening | F16, F17 | M1, M2, M3, E2E Track | PLANNED |
| E2E | E2E Testing Track | Test infra, runner, Tiers 1-4 tests, TEST_READY.md | none (runs parallel) | PLANNED |

## Interface Contracts
### M1 Catalog ↔ M3 Storefront & Agents
- `data/products.json`: Array of products conforming to `schemas/catalog.schema.json`.
- Required fields per product:
  - `id`: string (e.g. `VC-APP-001`)
  - `title`: string (e.g. `"Camisa Resort Vice Sunset '86"`)
  - `category`: string enum (`"Apparel"`, `"Novelty"`, `"Accessories"`, `"Decor"`)
  - `price_brl`: number (BRL sale price, e.g. 189.90)
  - `price_usd`: number (USD sale price, e.g. 42.00)
  - `production_cost_brl`: number (COGS, e.g. 52.00)
  - `margin_percent`: number (e.g. 72.6)
  - `ai_art_prompt`: object with `flux_prompt`, `midjourney_prompt`, `negative_prompt`
  - `tags`: array of strings (e.g. `["bestseller", "streetwear", "retro"]`)
  - `image_placeholder`: string (SVG data URI or relative path)

### M2 Video Pipeline ↔ M3 Content Clipper Agent
- Pipeline CLI input: `python -m video_pipeline.cli process --input <path_or_url> --output-dir <dir> [--mock]`
- Output artifacts generated in output directory:
  - `<basename>_transcript.json`: Raw English speech transcript with word-level timestamps.
  - `<basename>_localized.json`: Portuguese translated and adapted script with hook tags.
  - `<basename>_subtitles.srt`: SubRip subtitle file.
  - `<basename>_subtitles.vtt`: WebVTT subtitle file.
  - `<basename>_vertical.mp4`: 1080x1920 vertical video with blurred background, subtitles, and CTA overlay.
- Clipper Agent imports `video_pipeline` or reads the generated metadata to select viral hooks and craft post captions.

### M3 Storefront ↔ User / Local Host
- Entry point: `storefront/index.html`
- Servable with any static server: `python -m http.server 8000 --directory storefront`
- Responsive viewport (desktop and mobile 375px+).
- Interactivity:
  - Cart state persists in `localStorage`.
  - Checkout simulator validates customer fields and renders dynamic PIX QR code + copyable PIX payload.

## Code Layout
```
gta6_ecommerce_agents/
├── ORIGINAL_REQUEST.md                 # Authoritative user requirements
├── PROJECT.md                          # Master project specification and index
├── TEST_READY.md                       # Published by E2E track when test suite is ready
├── README.md                           # Quickstart, setup, and usage documentation
├── pyproject.toml                      # Python dependencies and project metadata
├── catalog/                            # M1: Catalog & Prompt Engineering
│   ├── __init__.py
│   ├── products.json                   # Master 12-product dataset
│   ├── schemas/
│   │   └── catalog.schema.json         # JSON Schema draft-07
│   ├── ip_filter.py                    # Trademark scanner and IP defense matrix
│   └── prompt_generator.py             # Generative AI prompt builder (Midjourney & Flux)
├── video_pipeline/                     # M2: Automated Video Localization Pipeline
│   ├── __init__.py
│   ├── ffmpeg_resolver.py              # Auto-detection of FFmpeg via imageio-ffmpeg / PATH
│   ├── ingestion.py                    # Video downloader and local file validator
│   ├── transcriber.py                  # Faster-whisper audio extractor and STT (+ Mock)
│   ├── localizer.py                    # PT-BR cultural translation and slang adaptation
│   ├── subtitler.py                    # .srt and .vtt file generator
│   ├── renderer.py                     # 9:16 vertical transform, blur pad, and CTA burning
│   └── cli.py                          # Unified CLI entrypoint for video processing
├── agents/                             # M3: Autonomous Specialist Agents
│   ├── __init__.py
│   ├── store_architect.py              # Store Architect Agent implementation
│   ├── content_clipper.py              # Content Clipper & Campaign Agent implementation
│   ├── run_agents.py                   # Master orchestration engine CLI
│   └── templates/                      # Agent prompt templates and system instructions
├── storefront/                         # M3: High-Converting Web Storefront
│   ├── index.html                      # Single-page modern Vice City storefront
│   ├── css/
│   │   └── styles.css                  # Custom neon animations and scanline effects
│   ├── js/
│   │   ├── app.js                      # Product rendering, cart drawer, modal gallery
│   │   └── checkout.js                 # PIX simulator, validation, and QR generator
│   └── assets/                         # SVG icons, logo, and placeholder artwork
├── tests/                              # Dual Track: E2E and Unit Test Suites
│   ├── __init__.py
│   ├── test_e2e_tier1_features.py      # Tier 1: Feature coverage (all 12 products, pipeline, agents)
│   ├── test_e2e_tier2_boundaries.py    # Tier 2: Boundary, error handling & edge cases
│   ├── test_e2e_tier3_combinations.py  # Tier 3: Cross-module integrations
│   ├── test_e2e_tier4_scenarios.py     # Tier 4: Real-world operational scenarios
│   └── run_all_tests.py                # Standalone test runner with exit code 0 on pass
└── validate_system.py                  # Automated 5-tier system validation script
```
