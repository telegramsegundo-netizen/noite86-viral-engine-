# E2E Test Infrastructure & Verification Specification
## GTA 6-Inspired E-Commerce & Multi-Agent Operations System

---

## 1. Opaque-Box Testing Philosophy & Integrity Principles

This end-to-end (E2E) testing suite is engineered according to strict **opaque-box, requirement-driven verification principles**. 

### 1.1 Fundamental Principles
1. **Authoritative Specification Derivation**: Every test case, expected value, boundary limit, and assertion is derived directly from the authoritative source documents:
   - `ORIGINAL_REQUEST.md` (Initial user requirements R1, R2, R3 and acceptance criteria)
   - `PROJECT.md` (System architecture, feature inventory F1–F15, interface contracts, and file layout)
2. **Zero Facade / Anti-Cheating Guarantee**:
   - No mock shortcuts designed to trivially pass assertions without executing genuine logic.
   - Assertions inspect tangible, observable system state: validated JSON schema conformity, mathematical correctness of margins and pricing formulas, pixel geometry and filter strings of generated media, DOM structural integrity, regex scanning of IP safety, and end-to-end checkout flow simulation.
3. **Progressive Testability**:
   - In a concurrent multi-agent development environment where Milestones M1, M2, and M3 may be completed at different intervals, tests are designed to dynamically detect milestone artifact presence.
   - When an interface artifact is pending completion by its assigned worker, the test provides a clean, descriptive skip message (e.g., `Milestone 2 video_pipeline not yet implemented`) rather than an unhandled syntax crash.
   - Once all milestones are implemented, the entire suite executes with 100% test coverage and 0 skips.
4. **Offline Determinism & Speed**:
   - External network calls (e.g. YouTube downloading or live LLM API queries) are decoupled from CI testing via deterministic mock/offline switches (`--mock`, `--offline`, synthetic `lavfi` video generation).
   - Entire test suite completes in under 15 seconds.

---

## 2. Feature Inventory & Traceability Matrix (F1–F15)

The following matrix maps every system feature to its testing tier, test implementation, expected output source, and acceptance criteria.

| Feature ID | Feature Name | Milestone | Test File | Primary Test Method | Authoritative Source | Verification Criteria |
|---|---|---|---|---|---|---|
| **F1** | Out-of-the-Box Catalog | M1 | `test_e2e_tier1_features.py` | `test_f01_catalog_products_count_and_margins` | R1, PROJECT.md | $\ge 10$ products (target 12); unit gross margins $\ge 65\%$; dual currency BRL/USD positive values. |
| **F2** | Generative AI Prompt Matrix | M1 | `test_e2e_tier1_features.py` | `test_f02_prompt_generator_flux_and_midjourney` | R1, PROJECT.md | Generates Flux and Midjourney prompts containing camera optics, neon lighting tokens, and negative tokens. |
| **F3** | IP Clearance Matrix & Scanner | M1 | `test_e2e_tier1_features.py` | `test_f03_ip_clearance_scanner` | R1, PROJECT.md | Zero false negatives: correctly blocks "Rockstar", "GTA", "Lucia", "Jason", "Vercetti", "Ammu-Nation"; catalog contains 0 banned terms. |
| **F4** | Catalog Data Schemas | M1 | `test_e2e_tier1_features.py` | `test_f04_catalog_schema_validation` | R1, PROJECT.md | `products.json` validates 100% against `catalog.schema.json` (Draft-07). |
| **F5** | Video Ingestion Module | M2 | `test_e2e_tier1_features.py` | `test_f05_video_ingestion_local_and_validation` | R2, PROJECT.md | Accepts valid local `.mp4` file; raises expected error on non-existent or invalid video path. |
| **F6** | Audio Extraction & STT | M2 | `test_e2e_tier1_features.py` | `test_f06_audio_extraction_and_transcription` | R2, PROJECT.md | Extracts 16kHz audio or executes MockTranscriber producing timestamped segments (`start`, `end`, `text`). |
| **F7** | PT-BR Video Localization | M2 | `test_e2e_tier1_features.py` | `test_f07_video_localization_ptbr_gamer_slang` | R2, PROJECT.md | Translates and adapts English gaming terms to authentic pt-BR gamer slang ("tá maluco", "surreal", "drop", "link na bio"). |
| **F8** | Subtitle Generation | M2 | `test_e2e_tier1_features.py` | `test_f08_subtitle_generation_srt_and_vtt` | R2, PROJECT.md | Produces standards-compliant `.srt` and `.vtt` subtitle files with sequential indices and valid timecodes. |
| **F9** | Vertical 9:16 Video Rendering | M2 | `test_e2e_tier1_features.py` | `test_f09_vertical_video_rendering_9_16` | R2, PROJECT.md | Renders 1080x1920 MP4 vertical output with boxblur background padding and CTA overlay. |
| **F10** | Video Test Harness & Synthesizer | M2 | `test_e2e_tier1_features.py` | `test_f10_synthetic_video_generator` | R2, PROJECT.md | Generates valid test MP4 clip via FFmpeg `lavfi` in <3 seconds without network dependencies. |
| **F11** | Store Architect Agent | M3 | `test_e2e_tier1_features.py` | `test_f11_store_architect_agent_config` | R3, PROJECT.md | Produes valid `store_config.json` with brand info, category taxonomy, bundle discounts, and checkout rules. |
| **F12** | Content Clipper & Campaign Agent | M3 | `test_e2e_tier1_features.py` | `test_f12_content_clipper_social_campaign` | R3, PROJECT.md | Produces valid `social_campaign.json` with $\ge 21$ posts across 7 days, 3 daily slots, viral hooks, and linked SKUs. |
| **F13** | Multi-Agent Orchestrator CLI | M3 | `test_e2e_tier1_features.py` | `test_f13_multi_agent_orchestrator_cli` | R3, PROJECT.md | CLI `run_agents.py --mock` exits 0 and writes all required output artifacts in $<5$ seconds. |
| **F14** | Responsive Vice City Web Store | M3 | `test_e2e_tier1_features.py` | `test_f14_storefront_dom_and_checkout_simulator` | R3, PROJECT.md | HTML DOM contains all mandatory IDs (`#product-grid`, `#cart-drawer`, `#checkout-modal`, `#pix-qr-code`, `#currency-toggle`); PIX simulator generates SVG QR and payload. |
| **F15** | System Validation Suite | M3 | `test_e2e_tier1_features.py` | `test_f15_system_validation_suite_execution` | R3, PROJECT.md | Standalone `validate_system.py` executes all tiers and reports 0 fatal errors. |

---

## 3. Four-Tier Test Architecture

The test suite is structured into four ascending tiers of verification rigour:

```
+-----------------------------------------------------------------------------------+
|                        TIER 4: REAL-WORLD E2E SCENARIOS                           |
|  - Complete 24h store launch flow (Catalog -> Video -> Agents -> Store -> PIX)    |
|  - Customer purchase journey, cart drawer, discount stacking, order receipt       |
+-----------------------------------------------------------------------------------+
                                         ▲
+-----------------------------------------------------------------------------------+
|                        TIER 3: COMBINATIONS & INTEGRATIONS                        |
|  - Cross-module contract verification (Catalog ↔ Storefront, Video ↔ Clipper)    |
|  - Store Architect output ↔ Storefront UI binding                                 |
|  - Pricing math: Bundle Discount + Coupon (10%) + PIX Instant Discount (5%)      |
+-----------------------------------------------------------------------------------+
                                         ▲
+-----------------------------------------------------------------------------------+
|                     TIER 2: BOUNDARIES, NEGATIVE & SECURITY                       |
|  - Corrupt / malformed files & empty inputs                                       |
|  - Margin boundaries (< 65% rejected, zero/negative prices)                      |
|  - Adversarial trademark evasion (obfuscated 'G-T-A', 'rOcKsTaR', 'v.e.r.c.e.t.t.i')|
|  - Windows path escaping in FFmpeg filtergraphs (drive letters 'C:\')             |
|  - Missing API key graceful fallback to deterministic mock mode                   |
+-----------------------------------------------------------------------------------+
                                         ▲
+-----------------------------------------------------------------------------------+
|                        TIER 1: ISOLATED FEATURE COVERAGE                          |
|  - Independent verification of each feature F1 through F15 in isolation           |
|  - Strict interface and schema validation                                         |
+-----------------------------------------------------------------------------------+
```

### Tier 1: Feature Coverage in Isolation (`tests/test_e2e_tier1_features.py`)
Validates that each feature functions according to its contract independently.

### Tier 2: Boundaries, Edge Cases & Negative Paths (`tests/test_e2e_tier2_boundaries.py`)
Adversarially attacks the system inputs and configurations:
- Empty strings, whitespace, and null fields.
- Corrupt JSON files and malformed video files.
- Products breaching the 65% minimum gross margin requirement.
- Windows drive letter path escaping (`C:\path` vs `C\\:/path`) to prevent FFmpeg crashes.
- Obfuscated trademark variations (case manipulation, punctuation separation, substring camouflage).
- Missing environment variables (`GEMINI_API_KEY`, `OPENAI_API_KEY`) verifying zero crashes.
- Invalid coupon codes in cart and checkout simulator.

### Tier 3: Combinations & Cross-Feature Integration (`tests/test_e2e_tier3_combinations.py`)
Validates that independently developed modules interact with full data fidelity:
- **Catalog ↔ Storefront**: Products defined in `products.json` render in storefront templates with matching prices and category tabs.
- **Video Pipeline ↔ Content Clipper Agent**: Metadata from video processing feeds directly into the hook detection engine.
- **Store Architect ↔ Storefront Config**: Bundles, hero headlines, and checkout policies generated by the agent populate the storefront without data loss.
- **Multi-Discount Compound Math**: Validates that stacked discounts (Bundle Base + Coupon `VICE10` + 5% PIX Instant Discount) match exact financial formulas.

### Tier 4: Real-World Scenarios (`tests/test_e2e_tier4_scenarios.py`)
Simulates the complete operational user story:
1. Operator triggers 24h store launch sequence.
2. Catalog is verified and loaded.
3. Video pipeline localizes gaming clip and burns vertical subtitles.
4. Autonomous agents execute and generate store configuration and 7-day social marketing plan.
5. Storefront is staged and served.
6. A customer adds items to cart, applies discount code, selects PIX payment, receives verifiable dynamic SVG QR code, and completes payment confirmation.

---

## 4. Test Execution & Runner Syntax

### 4.1 Master Standalone Test Runner
Execute all tiers with summary reporting:
```bash
# Direct python execution:
python tests/run_all_tests.py

# Via uv environment:
uv run python tests/run_all_tests.py

# Running a specific tier:
uv run python tests/run_all_tests.py --tier 1
uv run python tests/run_all_tests.py --tier 2
uv run python tests/run_all_tests.py --tier 3
uv run python tests/run_all_tests.py --tier 4

# Verbose output:
uv run python tests/run_all_tests.py --verbose
```

### 4.2 Standard Pytest Execution
```bash
# Run all tests:
uv run pytest

# Run a specific tier file:
uv run pytest tests/test_e2e_tier1_features.py
uv run pytest tests/test_e2e_tier2_boundaries.py
uv run pytest tests/test_e2e_tier3_combinations.py
uv run pytest tests/test_e2e_tier4_scenarios.py
```

---

## 5. Coverage & Verification Thresholds

| Metric | Required Threshold | Verification Method |
|---|---|---|
| **Feature Coverage** | 100% of Features F1–F15 | Tier 1 tests |
| **Gross Margin Floor** | Minimum 65.0% on all catalog products | Catalog Schema & Tier 1/2 tests |
| **Trademark Infringement** | 0 banned tokens detected in any project asset | IP Scanner & Tier 2 regex tests |
| **Deterministic Offline Execution** | 100% of tests executable with `--mock` / `--offline` | Tier 1–4 tests without network |
| **Master Runner Exit Code** | `0` (Success) | Standalone runner exit code check |
