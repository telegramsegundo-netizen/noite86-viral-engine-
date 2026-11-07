# Requirement R3 Technical Survey & Architectural Specification: Specialist Multi-Agent System, Autonomous Storefront & Validation Harness

**Author**: Explorer 3 (Specialist Agents & Storefront Spec Explorer)  
**Parent Orchestrator ID**: `a5e87fb8-1970-4caf-809e-c3fe935bfa92`  
**Working Directory**: `C:\Users\victo\teamwork_projects\gta6_ecommerce_agents\.agents\teamwork\explorer_survey_3\`  
**Date**: 2026-11-07  
**Scope**: Requirement R3 (Store Architect Agent, Content Clipper & Social Campaign Agent, Orchestration Engine, High-Converting Standalone Storefront, and Automated Validation Harness)

---

## Executive Summary

To enable rapid, autonomous monetization leveraging the cultural hype around the retro-futuristic Vice City aesthetic (inspired by the upcoming GTA 6 phenomenon without infringing intellectual property), this document defines the complete architectural blueprint and engineering specification for **Requirement R3**:

1. **Specialist Multi-Agent System**:
   - **Store Architect Agent**: Ingests product catalog data (from R1), establishes category taxonomy, optimizes psychological dual-currency pricing (BRL & USD) with protected gross margins (>65%), generates high-conversion Vice City dark neon copy (headlines, banners, scarcity alerts), creates promotional bundles, and configures checkout rules (PIX discounts, shipping policies).
   - **Content Clipper & Social Campaign Agent**: Pairs localized video clips and transcripts (from R2) with catalog products, detects 3-second viral hooks, generates platform-native Portuguese (PT-BR) captions, crafts tiered hashtag strategies, builds a 7-day 21-post omnichannel posting schedule, and embeds conversion CTAs with UTM attribution.
   - **Agent Orchestration Engine**: An executable Python engine (compatible with Python 3.12 and Node.js) with modular prompt architectures, strict JSON schema validation, and dual-mode execution (deterministic offline mock mode for 100% CI reproducibility + live LLM mode via Gemini API) enabling end-to-end store and campaign launch in under 24 hours.

2. **High-Converting Standalone Web Storefront**:
   - Built on a lightweight, zero-dependency stack (**HTML5 + Tailwind CSS + Vanilla ES6+ JavaScript**), requiring no complex server backend or build pipeline.
   - Distinctive **"Vice City Dark Neon"** aesthetic: Deep obsidian background (`#09090f`), vibrant neon pink (`#ff007f`), cyber cyan (`#00f0ff`), electric violet (`#8a2be2`), glowing gradients, and retro scanline effects.
   - Interactive components: Dynamic announcement bar, responsive product grid, interactive product modal with AI mockup gallery and scarcity indicator, slide-over cart drawer with free shipping progress bar and coupon validation (`VICE10`), and a dual-currency **Checkout Simulator** featuring instant PIX QR code generation and "Copia e Cola" clipboard integration.
   - Instant deployment: Ready for one-command local preview (`python -m http.server 8000` or browser open) and static hosting on Vercel, Netlify, or GitHub Pages.

3. **Automated Validation & Testing Harness**:
   - `validate_system.py`: A 5-tier test harness validating agent execution, JSON schema conformity, storefront DOM and asset integrity, IP compliance (zero banned trademark tokens), and deterministic offline execution.

---

## 1. System Architecture & End-to-End Operational Flow

```
                                  +-----------------------------+
                                  |     ORIGINAL_REQUEST.md     |
                                  +--------------+--------------+
                                                 |
                   +-----------------------------+-----------------------------+
                   |                                                           |
                   v                                                           v
   +-------------------------------+                           +-------------------------------+
   |   Requirement R1 (Explorer 1) |                           |   Requirement R2 (Explorer 2) |
   |   - 12 Out-of-the-Box Products|                           |   - Video Localization Pipeline|
   |   - AI Visual Prompts (Flux/MJ)|                          |   - Subtitle Burner (SRT/VTT) |
   |   - IP Clearance Matrix       |                           |   - 9:16 Vertical Reformatting|
   |   ==> catalog.json            |                           |   ==> localized_clips.json    |
   +---------------+---------------+                           +---------------+---------------+
                   |                                                           |
                   +-----------------------------+-----------------------------+
                                                 |
                                                 v
                       +---------------------------------------------------+
                       |            Agent Orchestration Engine             |
                       |       (engine/orchestrator.py / CLI entry)        |
                       |     - Modular Prompt Templates                    |
                       |     - Offline Deterministic Mock Mode             |
                       |     - Live LLM Integration (Google GenAI)         |
                       +-------------------------+-------------------------+
                                                 |
                       +-------------------------+-------------------------+
                       |                                                   |
                       v                                                   v
+---------------------------------------+   +---------------------------------------+
|         Store Architect Agent         |   | Content Clipper & Social Campaign Ag. |
|  - Ingests catalog.json               |   |  - Ingests localized_clips.json       |
|  - Category Taxonomy Generator        |   |  - Viral Hook Detection (3-sec gap)   |
|  - Dual-Currency Pricing Engine       |   |  - PT-BR Native Viral Copy & Emojis   |
|  - Vice City Storytelling & Banners   |   |  - 3-Tier Hashtag Clusters            |
|  - Bundle & AOV Optimization Engine   |   |  - 7-Day Posting Schedule (21 posts)  |
|  - PIX / Gateway Checkout Config      |   |  - Product-Linked Conversion CTAs     |
|  ==> store_config.json                |   |  ==> social_campaign.json             |
+-------------------+-------------------+   +-------------------+-------------------+
                    |                                           |
                    |                                           |
                    v                                           v
+---------------------------------------+   +---------------------------------------+
|       Autonomous Web Storefront       |   |      Social Media Growth Engine       |
|  - HTML5 / Tailwind / Vanilla JS      |   |  - campaign_calendar.md               |
|  - Vice City Dark Neon Aesthetic      |   |  - TikTok, Reels, Shorts Assets       |
|  - Dynamic Product Grid & Filter Tabs |   |  - Bio Link & UTM Tracking Matrix     |
|  - Product Modal with Mockup Gallery  |   |  - Coupon VICE10 Direct Attribution   |
|  - Slide-Over Cart Drawer             |   +---------------------------------------+
|  - Checkout Simulator (PIX & USD)     |
+-------------------+-------------------+
                    |
                    v
+-----------------------------------------------------------------------------------+
|                         Automated Validation Harness                              |
|                          (validate_system.py)                                     |
|  - Tier 1: Agent Execution Integrity                                              |
|  - Tier 2: Output JSON Schema Validation (store_config.json, social_campaign.json)|
|  - Tier 3: Storefront DOM & Asset Check (index.html, JS handlers, IDs, styles)   |
|  - Tier 4: Trademark & Legal Non-Infringement Scan (zero Rockstar/GTA tokens)     |
|  - Tier 5: Deterministic Offline Pass Verification (zero network dependency)      |
+-----------------------------------------------------------------------------------+
```

---

## 2. Specialist Multi-Agent System Architecture

### 2.1 Store Architect Agent

#### 2.1.1 Persona & System Instructions
The Store Architect Agent acts as a world-class e-commerce growth director, merchandiser, and copywriter specializing in retro-futuristic streetwear and gaming pop culture.

```markdown
Role: Autonomous Store Architect & E-Commerce Director
Aesthetic Identity: Vice City Dark Neon (1980s Miami retro-futurism, Ocean Drive noir, synthwave luxury)
Target Demographics: Urban streetwear enthusiasts, gamers, tech lifestyle adopters, retro-aesthetic collectors in Brazil and International markets.

Core Responsibilities:
1. Taxonomy Structuring: Categorize products into intuitive, high-converting collections.
2. Pricing & Margin Defense: Maintain minimum 65% gross margins across both BRL and USD pricing tiers. Apply psychological pricing (.90 / .99) and configure installment logic (e.g., até 12x no cartão).
3. Brand Voice & Storytelling: Craft hypnotic hero copy, scarcity alerts, drop announcements, and policy microcopy in Brazilian Portuguese (primary) and English (secondary).
4. Promotional Engineering: Create high-perceived-value bundles and cart cross-sells to boost Average Order Value (AOV).
5. Checkout Policy Configuration: Set up simulated PIX instant payment (with 5-10% discount incentive) and international card workflows, free shipping thresholds, and delivery lead times.
```

#### 2.1.2 Algorithmic Capabilities & Formulas

1. **Category Taxonomy Algorithm**:
   Groups products into 4 curated collections + 1 VIP bundle category:
   - `apparel` ("Vestuário Noturno"): Tees, bowling shirts, bomber jackets.
   - `headwear_accessories` ("Acessórios & Headwear"): Snapbacks, sunglasses, tumblers.
   - `tech_decor` ("Setup & Tech Decor"): Acrylic neon lamps, gaming deskmats, cassette speakers.
   - `collectibles` ("Itens de Colecionador & EDC"): Secret stash cans, motel keytags, air fresheners.
   - `bundles` ("Combos Exclusivos & Drops"): Curated multi-item packs with bundled discounts.

2. **Dual-Currency Pricing & Margin Formula**:
   - Given supplier production cost $C_{BRL}$ and $C_{USD}$ (from R1):
   - $P_{BRL} = \text{RoundTo90}(C_{BRL} / (1 - M_{target}))$, where $M_{target} \ge 0.65$.
   - $P_{USD} = \text{RoundTo99}(C_{USD} / (1 - M_{target}))$.
   - Installment calculator for Brazil: $\text{Parcela}_{12x} = \text{RoundTo2Decimals}(P_{BRL} / 12)$.
   - Real-world example:
     - Bomber Jacket: $C_{BRL} = \text{R\$} 115,00 \rightarrow P_{BRL} = \text{R\$} 349,90$ (Margin: 67.1%, 12x de R$ 29,15).
     - Oversized Tee: $C_{BRL} = \text{R\$} 38,00 \rightarrow P_{BRL} = \text{R\$} 139,90$ (Margin: 72.8%, 12x de R$ 11,65).
     - Motel Keytag: $C_{BRL} = \text{R\$} 5,50 \rightarrow P_{BRL} = \text{R\$} 39,90$ (Margin: 86.2%).

3. **Promotional Bundle Engine**:
   - Identifies complementary high-margin items to boost AOV:
     * **"Vice Night Runner Pack"**: Oversized Tee (`VC-APP-003`) + Corduroy Cap (`VC-APP-004`) + Car Air Freshener (`VC-AUT-001`). Original: R$ 319,70. Bundle Price: R$ 269,90 (Save 15%).
     * **"Underground Syndicate Kit"**: Holographic Bomber (`VC-APP-002`) + Secret Stash Can (`VC-NOQ-001`) + Motel Keytag (`VC-EDC-001`). Original: R$ 509,70. Bundle Price: R$ 429,90 (Save 16%).
     * **"Ocean Drive Setup Pack"**: XXL Deskmat (`VC-DSK-001`) + Acrylic Neon Lamp (`VC-LGT-001`) + Cassette Speaker (`VC-AUD-001`). Original: R$ 459,70. Bundle Price: R$ 389,90 (Save 15%).

4. **Checkout Configuration Generator**:
   - `free_shipping_threshold_brl`: R$ 199,00
   - `free_shipping_threshold_usd`: $50.00
   - `pix_instant_discount_percentage`: 5%
   - `national_delivery_days`: "5 a 10 dias úteis (Produção sob demanda + Rastreio Correios Sedex/Jadlog)"
   - `international_delivery_days`: "7 to 14 business days (Global Express Delivery)"
   - `simulated_pix_key`: `pagamentos@vicedistrict.store`

#### 2.1.3 Store Architect Input & Output Schema

**Output: `store_config.json`**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "StoreConfiguration",
  "type": "object",
  "required": ["store_info", "categories", "hero_banner", "announcements", "bundles", "checkout_config", "products"],
  "properties": {
    "store_info": {
      "type": "object",
      "required": ["brand_name", "tagline", "tagline_en", "currency_default", "supported_currencies"],
      "properties": {
        "brand_name": { "type": "string" },
        "tagline": { "type": "string" },
        "tagline_en": { "type": "string" },
        "currency_default": { "type": "string" },
        "supported_currencies": { "type": "array", "items": { "type": "string" } }
      }
    },
    "hero_banner": {
      "type": "object",
      "required": ["headline", "subheadline", "cta_text", "urgency_badge", "countdown_end_hours"],
      "properties": {
        "headline": { "type": "string" },
        "subheadline": { "type": "string" },
        "cta_text": { "type": "string" },
        "urgency_badge": { "type": "string" },
        "countdown_end_hours": { "type": "integer" }
      }
    },
    "announcements": {
      "type": "array",
      "items": { "type": "string" }
    },
    "categories": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "label_pt", "label_en", "icon"],
        "properties": {
          "id": { "type": "string" },
          "label_pt": { "type": "string" },
          "label_en": { "type": "string" },
          "icon": { "type": "string" }
        }
      }
    },
    "bundles": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "name", "items_sku", "original_price_brl", "bundle_price_brl", "discount_percentage"],
        "properties": {
          "id": { "type": "string" },
          "name": { "type": "string" },
          "items_sku": { "type": "array", "items": { "type": "string" } },
          "original_price_brl": { "type": "number" },
          "bundle_price_brl": { "type": "number" },
          "discount_percentage": { "type": "number" }
        }
      }
    },
    "checkout_config": {
      "type": "object",
      "required": ["free_shipping_threshold_brl", "free_shipping_threshold_usd", "pix_discount_percent", "pix_receiver_name", "pix_key"],
      "properties": {
        "free_shipping_threshold_brl": { "type": "number" },
        "free_shipping_threshold_usd": { "type": "number" },
        "pix_discount_percent": { "type": "number" },
        "pix_receiver_name": { "type": "string" },
        "pix_key": { "type": "string" }
      }
    },
    "products": {
      "type": "array",
      "items": { "type": "object" }
    }
  }
}
```

---

### 2.2 Content Clipper & Social Campaign Agent

#### 2.2.1 Persona & System Instructions
The Content Clipper & Social Campaign Agent functions as a high-velocity viral media strategist, TikTok/Reels clip editor, and direct-response copywriter.

```markdown
Role: Autonomous Content Clipper & Social Media Campaign Strategist
Core Mission: Transform localized international video clips into high-converting vertical content funnels for TikTok, Instagram Reels, and YouTube Shorts.
Audience: Brazilian gaming audience, streetwear fans, Gen Z and Millennials obsessed with Vice City culture.

Key Capabilities:
1. Viral Hook Architecture: Identify the critical 0-3 second visual and verbal hook to stop the scroll.
2. Narrative Pacing: 
   - 0-3s: Hook (Curiosity gap, pattern interrupt, shocking claim)
   - 3-15s: Lore / Breakdown (Trailer analysis, hidden Easter eggs, Miami culture)
   - 15-25s: Aesthetic Bridge (Connect the video hype with physical streetwear pieces)
   - 25-30s: Conversion CTA (Bio link, limited drop coupon, urgency)
3. Social Copywriting: Write punchy PT-BR captions with line breaks, emojis, and comment bait questions.
4. Tiered Hashtags: Combine high-volume broad tags with niche aesthetic and e-commerce conversion tags.
5. Omnichannel Scheduling: Produce a comprehensive 7-day calendar with 3 timed daily drops.
```

#### 2.2.2 Viral Hook Taxonomy & Selection Criteria

| Hook Category | Trigger Mechanism | Example Hook Script (0–3s) | Linked Catalog Item |
|---|---|---|---|
| **Curiosity Gap** | Unrevealed secret or trailer breakdown | *"Você percebeu esse detalhe sinistro no trailer de Leonida?"* | `VC-APP-003` (Heavyweight Tee) |
| **FOMO / Scarcity Drop** | Limited edition time-sensitive drop | *"Só quem viveu os anos 80 sabe o que significa essa jaqueta..."* | `VC-APP-002` (Holographic Bomber) |
| **Tactical / Intrigue** | Unexpected hidden mechanism | *"Parece uma lata de refri comum, mas olha o que tem embaixo..."* | `VC-NOQ-001` (Secret Stash Can) |
| **Aesthetic Flex** | Atmospheric chillout & setup vibes | *"POV: Você acabou de chegar em Vice City em 1986..."* | `VC-DSK-001` (XXL Deskmat) |
| **Streetwear Lifestyle** | Direct style inspiration | *"Como se vestir como o rei do submundo de Miami sem parecer fantasia"* | `VC-APP-001` (Bowling Shirt) |

#### 2.2.3 Hashtag Strategy Matrix (3 Tiers)

```
[Tier 1: Mega Reach & Algorithmic Hype] (Broad discovery)
#GTA6 #GTA6Brasil #ViceCity #GTA6Trailer #GamingBrasil #GamerLife

[Tier 2: Aesthetic & Niche Culture] (Targeted interest)
#SynthwaveBrasil #Anos80 #MiamiViceAesthetic #StreetwearBrasil #Outrun #RetroWave #VaporwaveVibes

[Tier 3: E-Commerce & Direct Conversion] (Purchase intent)
#ModaMasculina #DropshippingBrasil #DropLimitado #AchadosShopee #StreetwearOutfit #ModaGamer
```

#### 2.2.4 7-Day Posting Schedule Architecture (21 Posts Total)

- **Daily Cadence**: 3 posts per day optimized for Brazil peak engagement windows:
  1. **Slot 1 (12:30 BRT)**: Lunch break — Fast curiosity hooks & easter eggs (Shorts / TikTok).
  2. **Slot 2 (18:15 BRT)**: Commute / Transit — High energy lore, vehicle breakdowns, music vibes (Reels / TikTok).
  3. **Slot 3 (21:30 BRT)**: Prime relaxation — Aesthetic showcases, unboxings, direct store drop CTAs (TikTok / Reels).

- **Weekly Content Mix**:
  - 40% (8 posts): Viral Video Clips & Lore Localization (from R2).
  - 30% (7 posts): Aesthetic & Outfit Showcase (AI mockups, styling tips, setup inspiration).
  - 30% (6 posts): Direct Offer & Unboxing (Stash can demos, bundle promotions, coupon `VICE10`).

#### 2.2.5 Social Campaign Data Contract

**Output: `social_campaign.json`**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "SocialCampaignPlan",
  "type": "object",
  "required": ["campaign_name", "coupon_code", "discount_percentage", "total_posts", "schedule"],
  "properties": {
    "campaign_name": { "type": "string" },
    "coupon_code": { "type": "string" },
    "discount_percentage": { "type": "number" },
    "total_posts": { "type": "integer" },
    "schedule": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "post_id", "day", "time_slot", "platform", "content_type",
          "hook_text", "caption_pt", "hashtags", "linked_product_sku",
          "cta_text", "utm_link"
        ],
        "properties": {
          "post_id": { "type": "string" },
          "day": { "type": "string" },
          "time_slot": { "type": "string" },
          "platform": { "type": "string", "enum": ["TikTok", "Instagram Reels", "YouTube Shorts"] },
          "content_type": { "type": "string", "enum": ["Viral Clip Breakdown", "Aesthetic Showcase", "Product Unboxing", "Drop Announcement"] },
          "hook_text": { "type": "string" },
          "audio_suggestion": { "type": "string" },
          "caption_pt": { "type": "string" },
          "hashtags": { "type": "array", "items": { "type": "string" } },
          "linked_product_sku": { "type": "string" },
          "cta_text": { "type": "string" },
          "utm_link": { "type": "string" }
        }
      }
    }
  }
}
```

---

### 2.3 Agent Orchestration Engine

#### 2.3.1 Engine Architecture & Runtime Strategy
The Orchestration Engine connects the modular sub-systems into a coherent executable pipeline.
- **Runtime Choice**: Pure Python 3.12 (standard library + `uv` optional support) with fallback to Node.js.
  - Zero external dependency requirement: standard library modules (`json`, `re`, `argparse`, `pathlib`, `urllib.request`, `http.server`) are used for core orchestration, mock generation, and verification.
  - Optional LLM integration: When `GEMINI_API_KEY` is present in the environment, the engine optionally invokes the modern Google GenAI SDK (`google-genai` / `gemini-2.5-flash`) for real-time creative expansion.
  - **Deterministic Offline Mock Mode (`--mock`)**: When no API key is provided or when running in CI/CD pipelines, the engine executes high-fidelity deterministic algorithms that generate schema-perfect JSON and Markdown files instantly (<2 seconds), ensuring 100% test reproducibility.

#### 2.3.2 File Layout for Orchestration Module

```
C:\Users\victo\teamwork_projects\gta6_ecommerce_agents\
├── engine/
│   ├── __init__.py
│   ├── orchestrator.py           # Main CLI orchestrator & pipeline controller
│   ├── config.py                 # Paths, constants, aesthetic tokens, default settings
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py         # Abstract agent interface & common LLM/mock handler
│   │   ├── store_architect.py    # Store Architect Agent implementation
│   │   └── content_clipper.py    # Content Clipper & Campaign Agent implementation
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── store_architect.txt   # System prompt and few-shot formatting for Store Architect
│   │   └── content_clipper.txt   # System prompt and formatting for Content Clipper
│   └── schemas/
│       ├── __init__.py
│       ├── store_config.schema.json
│       └── social_campaign.schema.json
├── data/
│   ├── catalog.json              # Ingested from R1 (12 products)
│   ├── localized_clips.json      # Ingested from R2 (video clips & transcripts)
│   ├── store_config.json         # Generated output for Storefront
│   └── social_campaign.json      # Generated output for Social Media
├── campaigns/
│   └── campaign_calendar.md      # Human-readable 7-day social calendar
```

#### 2.3.3 Execution CLI Options

```bash
# Standard autonomous run in deterministic offline mock mode (zero external keys needed):
uv run python -m engine.orchestrator --mock

# Standard run with custom catalog and clips inputs:
uv run python -m engine.orchestrator --catalog data/catalog.json --clips data/localized_clips.json --output storefront/data/

# Live AI generation mode with Gemini:
set GEMINI_API_KEY=your_key_here
uv run python -m engine.orchestrator --live
```

---

## 3. High-Converting Web Storefront Architecture

### 3.1 Tech Stack Justification

| Requirement | Solution | Rationale |
|---|---|---|
| **Zero-Config Serving** | HTML5 + Vanilla ES6+ JS | Runs instantly with `python -m http.server 8000` or direct file open in any modern browser without npm build errors or version mismatches. |
| **High-Performance Styling** | Tailwind CSS (CDN + Custom Config) | Instant responsive utility classes, zero stylesheet compile step, beautiful dark mode and custom hex values. |
| **Mobile-First UX** | Viewport optimized for 375px–430px | 85%+ of social media traffic from TikTok and Instagram Reels lands on mobile devices; mobile layout prioritizes large tap targets, bottom-anchored drawers, and one-tap checkout. |
| **Dynamic Interactivity** | Reactive DOM State Store | Cart state, modal rendering, currency toggling (BRL/USD), coupon calculation, and PIX QR generation handled cleanly in browser memory and `localStorage`. |
| **Asset Portability** | SVG Icons & Inline Vector Placeholders | Self-contained assets guarantee that UI previews never display broken images, even in offline environments. |

---

### 3.2 Visual Design System: "Vice City Dark Neon"

```css
/* Color Palette & CSS Variables */
:root {
  --bg-deep-void: #09090f;        /* Deep obsidian space */
  --bg-surface-dark: #12121f;     /* Card and modal backgrounds */
  --bg-surface-elevated: #1a1a2e; /* Hover states, dropdowns */
  
  --neon-pink: #ff007f;           /* Neon Flamingo: Primary accent, CTA borders */
  --neon-pink-glow: rgba(255, 0, 127, 0.4);
  
  --neon-cyan: #00f0ff;           /* Biscayne Electric Cyan: Secondary accents, badges */
  --neon-cyan-glow: rgba(0, 240, 255, 0.4);
  
  --neon-purple: #8a2be2;         /* Sunset Violet: Gradients, overlays */
  --sunset-amber: #ffa800;        /* Golden hour accent: Ratings, urgency */
  --neon-green: #00ff9d;          /* Success green: PIX paid confirmation */
  
  --text-primary: #ffffff;
  --text-secondary: #a0a0c0;
  --text-muted: #606080;
}
```

#### Visual Effects & Design Tokens:
- **Scanlines Overlay**: Subtle retro CRT scanline effect on hero banner for authentic 1980s atmosphere.
- **Glassmorphism**: `backdrop-blur-md bg-opacity-80 border border-purple-900/30` on modals and cart drawer.
- **Neon Pulse Badges**: `@keyframes pulse-glow` applied to scarcity chips and announcement pills.
- **Typography**:
  - Headlines: Display uppercase bold retro-futuristic styling (`Chakra Petch`, `Orbitron`, or sans-serif uppercase with letter-spacing tracking).
  - Body: High-legibility clean modern sans-serif (`Inter`, `System-UI`).

---

### 3.3 Interactive Storefront Modules & Specifications

#### 1. Dynamic Announcement Bar
- Position: Top-most fixed banner.
- Visual: Gradient background `#ff007f` $\rightarrow$ `#8a2be2` with pulsing neon badge.
- Rotational message:
  - *"⚡ DROP 01 // FRETE GRÁTIS PARA TODO O BRASIL ACIMA DE R$ 199 // USE CUPOM: VICE10"*
  - *"🌴 EDIÇÃO LIMITADA DE LANÇAMENTO // APENAS 50 PEÇAS POR MODELO // SEM REPOSIÇÃO"*
- Currency Selector: Interactive toggle `[ R$ BRL | $ USD ]` on the right side that updates all product prices and checkout modes instantly across the page.

#### 2. Header & Brand Navigation
- Brand Logo: **"VICE DISTRICT"** with glowing palm tree SVG icon and neon pink subtitle **"LEONIDA // 1986"**.
- Navigation Links: "Coleção Noturna", "Acessórios", "Combos", "Sobre o Drop".
- Search Input: Real-time search filter filtering the product grid by keyword.
- Cart Drawer Trigger: Glowing cart icon with real-time numeric counter badge (e.g. `[ 2 ]`) that pulses when items are added.

#### 3. Hero Section (Cinematic Billboard)
- Visual: Deep dark background with animated retro wireframe grid perspective and neon sunset gradient orb.
- Headline: **"VICE CITY SUBMUNDO // DROP 01"**
- Subheadline: *"Coleção conceitual autônoma inspirada nas noites elétricas de Leonida e na cultura retro-futurista de Miami anos 80. Peças exclusivas de alta qualidade com produção sob demanda."*
- Urgency Countdown Timer: Live ticking JavaScript countdown:
  `[ 14h : 23m : 45s ] - LOTE INICIAL ENCERRA EM BREVE`
- Action Buttons:
  - Primary CTA: *"EXPLORAR DROP"* (smooth scroll to catalog grid).
  - Secondary CTA: *"VER COMBOS VIP"* (filters to bundle packages).

#### 4. Category Filter Bar
- Interactive tab pills:
  - `Todos os Itens (12)`
  - `Vestuário Noturno (4)`
  - `Acessórios & Headwear (3)`
  - `Setup & Tech Decor (3)`
  - `Colecionáveis & EDC (2)`
  - `Combos Promocionais (3)`
- Active tab state: Electric cyan border with glowing underline.

#### 5. Responsive Product Grid
- Layout: 1 column on mobile (375px), 2 columns on tablet (768px), 3–4 columns on desktop (1280px).
- Product Card Elements:
  - Floating Badges: Top-left `NOVO DROP`, Top-right `LOTE LIMITADO (Apenas 7 restando)`.
  - Image Container: Aspect ratio 1:1 with smooth zoom-on-hover effect.
  - Category tag in cyan uppercase.
  - Product Title with bold white lettering.
  - Price Block:
    - BRL mode: `R$ 139,90` or `12x de R$ 13,99` (with green tag `5% OFF no PIX: R$ 132,90`).
    - USD mode: `$27.90` (with tag `Free US Shipping over $50`).
  - Action Buttons:
    - Quick Add: Button with plus icon to instantly add to cart drawer.
    - View Details: Full-width button *"Ver Detalhes"* opening the dynamic product modal.

#### 6. Dynamic Product Modal (Lightbox Gallery & Customizer)
- Triggered by clicking any product card.
- Component Breakdown:
  - **AI Mockup Gallery**:
    - Large primary image viewport.
    - 3 interactive thumbnail selectors (Front View, Back Art, Close-up Detail / Lifestyle). Clicking a thumbnail smoothly updates the main viewport.
  - **Scarcity & Social Proof Indicator**:
    - Live animated counter: *"🔥 14 pessoas estão vendo este item agora. Apenas 6 unidades restantes neste lote!"*
  - **Size Selector**:
    - Buttons for `P`, `M`, `G`, `GG`, `XG` (Apparel) with interactive active state and "Guia de Medidas" popup tooltip.
  - **Quantity Selector**:
    - Interactive stepper `[-]` `[ 1 ]` `[+]`.
  - **Detailed Spec Accordion Tabs**:
    - *Aesthetic Concept*: Detailed narrative behind the piece.
    - *Tecido & Material*: 260 GSM combed cotton / 18/8 stainless steel / acrylic optical grade.
    - *Envio & Garantia*: 5 a 10 dias úteis, rastreamento Correios, 7 dias para troca incondicional.
  - **Conversion Action Buttons**:
    - Primary: *"COMPRAR AGORA (PIX / CARTÃO)"* (adds item and immediately opens checkout).
    - Secondary: *"ADICIONAR AO CARRINHO"*.

#### 7. Slide-Over Cart Drawer
- Smooth CSS transition `translate-x-full` $\rightarrow$ `translate-x-0` with backdrop blur overlay.
- Cart Drawer Header: *"SEU CARRINHO (X ITENS)"* with close button `✕`.
- **Free Shipping Progress Bar**:
  - Dynamic progress bar: If total < R$ 199, shows *"Faltam apenas R$ 49,10 para FRETE GRÁTIS!"*.
  - When total $\ge$ R$ 199, illuminates in neon green: *"🎉 PARABÉNS! VOCÊ GANHOU FRETE GRÁTIS!"*.
- Items List:
  - Product thumbnail, title, selected size, unit price, quantity increment/decrement, and trash remove button.
- **Coupon Code Input**:
  - Input field + *"APLICAR"* button.
  - Validates code `VICE10` $\rightarrow$ applies 10% discount across subtotal with glowing green success badge.
- Summary Breakdown:
  - Subtotal: `R$ 279,80`
  - Desconto Cupom (10%): `- R$ 27,98`
  - Frete: `GRÁTIS`
  - **Total**: `R$ 251,82` (ou 12x de R$ 25,18)
- Checkout Button: *"FINALIZAR PEDIDO (CHECKOUT SEGURO)"*.

#### 8. High-Converting Checkout Simulator Modal

```
+-------------------------------------------------------------------------+
|  [✕] CHECKOUT SEGURO // VICE DISTRICT ENCRIPTADO 256-BIT                |
+-------------------------------------------------------------------------+
|                                                                         |
|  [PASSO 1: DADOS PESSOAIS]                  [PASSO 2: PAGAMENTO]        |
|  Nome Completo: [ Victor Rossi            ] (o) PIX Instantâneo (5% OFF)|
|  E-mail:        [ victor@email.com        ] ( ) Cartão de Crédito (12x) |
|  WhatsApp:      [ (11) 99876-5432         ]                             |
|  CEP / Zip:     [ 01310-100       ] [Buscar]                            |
|  Endereço:      Av. Paulista, 1000 - Apto 42                            |
|                                                                         |
+-------------------------------------------------------------------------+
|  [ÁREA PIX INTERATIVA]                                                  |
|                                                                         |
|     +------------------+   Valor Final: R$ 239,22                       |
|     |  [PIX QR CODE]   |   Economia Total: R$ 40,58 (Cupom + PIX)       |
|     |  (SVG Dinâmico)  |                                                |
|     +------------------+   Tempo restante: [ 14:52 ]                    |
|                                                                         |
|  Código Copia e Cola:                                                   |
|  [ 00020126580014br.gov.bcb.pix0136pagamentos@vicedistrict... ] [COPIAR]|
|                                                                         |
|  [ ✓ SIMULAR PAGAMENTO CONFIRMADO ]                                     |
+-------------------------------------------------------------------------+
|  [CONFIRMAÇÃO DO PEDIDO - TELA DE SUCESSO]                              |
|  🎉 PEDIDO CONFIRMADO #VD-84920!                                        |
|  Um comprovante foi enviado para seu e-mail e WhatsApp.                 |
|  Previsão de entrega: 6 dias úteis via Sedex Express.                   |
|  [ ENTRAR NO GRUPO VIP DO WHATSAPP // RASTREIO E DROPS EXCLUSIVOS ]     |
+-------------------------------------------------------------------------+
```

---

### 3.4 Deployment & Hosting Blueprint

#### 1. Zero-Config Local Preview
```bash
# Option A: Standard Python (available in any environment)
python -m http.server 8000 --directory storefront
# Open browser at: http://localhost:8000

# Option B: Node.js (v24 already installed)
npx serve storefront -p 8000

# Option C: Direct browser execution
# Double-click storefront/index.html (fully works with local data fallback)
```

#### 2. Vercel Deployment Configuration (`vercel.json`)
```json
{
  "version": 2,
  "name": "vice-city-ecommerce",
  "builds": [
    { "src": "storefront/**", "use": "@vercel/static" }
  ],
  "routes": [
    { "src": "/(.*)", "dest": "/storefront/$1" }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-XSS-Protection", "value": "1; mode=block" }
      ]
    }
  ]
}
```

#### 3. Netlify Deployment Configuration (`netlify.toml`)
```toml
[build]
  publish = "storefront"

[[headers]]
  for = "/*"
  [headers.values]
    Cache-Control = "public, max-age=3600"
    X-Frame-Options = "DENY"
```

---

## 4. End-to-End Autonomous Operation Pipeline (<24h Launch)

### 4.1 Orchestration Workflow

```
[Hour 00:00] Ingest inputs:
             - data/catalog.json (12 products from R1)
             - data/localized_clips.json (video metadata from R2)

[Hour 00:02] Store Architect Agent Execution:
             - Validates margins, formats prices, generates bundles
             - Writes storefront/data/store_config.json

[Hour 00:04] Content Clipper & Campaign Agent Execution:
             - Detects hooks, writes PT-BR captions & hashtags
             - Produces 7-day schedule (21 posts)
             - Writes campaigns/social_campaign.json & campaign_calendar.md

[Hour 00:06] Storefront Synthesis:
             - Generates storefront/index.html with current store_config.json
             - Prepares static assets, SVG icons, and fallback mockups

[Hour 00:08] Automated Validation Script:
             - Executes validate_system.py (Tiers 1-5)
             - Generates validation_report.json

[Hour 00:10] Store Live & Content Scheduled:
             - Store ready for immediate customer traffic & checkout
             - Operator / scheduler can broadcast post 1 at 12:30 BRT
```

---

## 5. Automated Validation & Testing Harness Specification

### 5.1 Test Architecture (`validate_system.py`)

The test harness provides comprehensive, automated verification across 5 distinct tiers.

```python
"""
validate_system.py - End-to-End Verification Suite for GTA 6 E-Commerce System
"""
import sys
import os
import json
import re
from pathlib import Path

class ValidationHarness:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.errors = []
        self.passed_checks = []

    def run_all(self):
        print("=== INITIATING GTA 6 E-COMMERCE VALIDATION SUITE ===")
        self.tier1_agent_execution_check()
        self.tier2_schema_validation()
        self.tier3_storefront_dom_integrity()
        self.tier4_trademark_compliance_scan()
        self.tier5_offline_mock_verification()
        self.print_summary()
        return len(self.errors) == 0

    # Tier 1: Agent Execution Integrity
    def tier1_agent_execution_check(self):
        print("[TIER 1] Validating Agent Execution & CLI...")
        # Checks that engine modules compile and run without syntax/runtime errors
        ...

    # Tier 2: Output JSON Schema Validation
    def tier2_schema_validation(self):
        print("[TIER 2] Validating Generated Schemas...")
        # Validates store_config.json and social_campaign.json
        # Verifies:
        # - >= 10 products present
        # - all gross margins >= 65%
        # - positive BRL and USD pricing
        # - >= 21 social posts in 7-day schedule
        # - all required bundle fields present
        ...

    # Tier 3: Storefront DOM & Asset Check
    def tier3_storefront_dom_integrity(self):
        print("[TIER 3] Validating Storefront DOM & Asset Integrity...")
        # Parses index.html and verifies:
        # - Required element IDs: #product-grid, #cart-drawer, #checkout-modal,
        #   #pix-qr-code, #currency-toggle, #product-modal, #announcement-bar
        # - Valid Tailwind CDN script tag
        # - Responsive viewport meta tag
        # - Zero broken local asset links
        ...

    # Tier 4: Trademark & Legal Non-Infringement Scan
    def tier4_trademark_compliance_scan(self):
        print("[TIER 4] Scanning for Trademark & IP Infringements...")
        # Scans all generated JSON, Markdown, and HTML files
        # Banned regex: r"\b(GTA|Grand Theft Auto|Rockstar Games|Lucia|Jason|Tommy Vercetti)\b"
        ...

    # Tier 5: Offline Mock Verification
    def tier5_offline_mock_verification(self):
        print("[TIER 5] Validating Offline / Air-Gapped Execution...")
        # Verifies complete pipeline completes without network access in mock mode
        ...
```

### 5.2 Acceptance Criteria Matrix for Downstream Workers

| Acceptance Criterion | Verification Command | Expected Result |
|---|---|---|
| **AC 1: Agent Execution** | `uv run python -m engine.orchestrator --mock` | Exit code `0`, outputs generated in `< 5s`. |
| **AC 2: Schema Integrity** | `uv run python validate_system.py --tier 2` | 100% pass, `store_config.json` and `social_campaign.json` match schemas. |
| **AC 3: Product Count & Margins** | `uv run python validate_system.py --tier 2` | 12 items verified, all margins $\ge 65\%$. |
| **AC 4: Social Campaign Schedule** | `uv run python validate_system.py --tier 2` | 21 posts verified across 7 days, 3 daily slots. |
| **AC 5: Storefront DOM & Functions** | `uv run python validate_system.py --tier 3` | All required DOM IDs and click handlers verified in `index.html`. |
| **AC 6: IP Compliance** | `uv run python validate_system.py --tier 4` | Zero matches for banned trademarks in all project outputs. |
| **AC 7: Standalone Preview** | `python -m http.server 8000 --directory storefront` | Page loads, products render, cart updates, PIX modal opens and copies key. |

---

## 6. Implementation Blueprint & Recommended Directory Layout

```
gta6_ecommerce_agents/
├── ORIGINAL_REQUEST.md
├── PROJECT.md
├── package.json                   # Optional Node.js runner scripts
├── pyproject.toml                 # uv/pip dependencies (python >= 3.12)
├── validate_system.py             # Master automated validation script
├── vercel.json                    # Static deployment configuration
├── netlify.toml                   # Static deployment configuration
├── engine/                        # Agent Orchestration Engine
│   ├── __init__.py
│   ├── orchestrator.py            # CLI entry point
│   ├── config.py                  # Aesthetics, paths, fallback constants
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   ├── store_architect.py
│   │   └── content_clipper.py
│   ├── prompts/
│   │   ├── store_architect.txt
│   │   └── content_clipper.txt
│   └── schemas/
│       ├── store_config.schema.json
│       └── social_campaign.schema.json
├── data/                          # Shared data bus between milestones
│   ├── catalog.json               # (Milestone 1 output)
│   ├── localized_clips.json       # (Milestone 2 output)
│   ├── store_config.json          # (Milestone 3 agent output)
│   └── social_campaign.json       # (Milestone 3 agent output)
├── campaigns/                     # Campaign assets
│   ├── campaign_calendar.md       # Markdown 7-day schedule
│   └── posts/                     # Individual post scripts & captions
└── storefront/                    # Autonomous Standalone Storefront
    ├── index.html                 # Complete single-page store
    ├── css/
    │   └── custom.css             # Neon glow, scanlines, animations
    ├── js/
    │   ├── app.js                 # Core state, rendering, event listeners
    │   ├── cart.js                # Cart drawer, calculations, coupon
    │   ├── checkout.js            # PIX simulator, card simulation, order success
    │   └── store_data.js          # Inlined fallback catalog data
    └── assets/                    # SVG icons, badges, UI elements
```

---

## Conclusion & Architectural Sign-Off

Requirement R3 provides the critical operational engine that turns product concepts (R1) and viral video clips (R2) into a live, monetizable e-commerce machine:
- The **Store Architect Agent** ensures business viability through mathematical margin defense and high-converting Vice City copywriting.
- The **Content Clipper & Social Campaign Agent** creates an automated organic customer acquisition funnel tailored specifically to Brazilian consumer behavior.
- The **Standalone Storefront** delivers an immersive, ultra-fast, mobile-first shopping experience with zero backend complexity and instant PIX checkout simulation.
- The **Validation Harness** guarantees that downstream worker agents produce verifiable, robust, and IP-compliant code.
