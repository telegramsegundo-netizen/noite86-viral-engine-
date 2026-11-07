import re
from pathlib import Path

index_path = Path(r"C:\Users\victo\teamwork_projects\gta6_ecommerce_agents\storefront\index.html")
content = index_path.read_text(encoding="utf-8")

# Replacement for Hero Section
old_hero_pattern = re.compile(
    r'<!-- Hero Section with CRT Scanlines & Perspective Grid -->.*?<!-- Category Filter Pills Bar -->',
    re.DOTALL
)

new_hero = '''<!-- Hero Section with Motion Background & Multi-Layer Gradients -->
  <section class="relative border-b border-gray-800 min-h-[600px] sm:min-h-[680px] flex items-center overflow-hidden">
    <!-- Cinematic Motion Background Image with Parallax Ken Burns Effect -->
    <div class="absolute inset-0 z-0 overflow-hidden pointer-events-none">
      <img src="assets/banners/hero_sunset_drive.jpg" alt="Vice District Sunset Drive" class="w-full h-full object-cover object-center hero-motion-bg filter brightness-95">
    </div>

    <!-- Multi-Layer Cinematic Gradients -->
    <!-- 1. Horizontal Vignette (Dark on left for text legibility, transparent on right for supercar & Ocean Drive) -->
    <div class="absolute inset-0 z-1 bg-gradient-to-r from-vice-void via-vice-void/85 to-vice-void/30 md:via-vice-void/70 md:to-transparent pointer-events-none"></div>
    <!-- 2. Vertical Blend Gradients (Seamless connection to header and category bar) -->
    <div class="absolute inset-0 z-1 bg-gradient-to-t from-vice-void via-transparent to-vice-void/80 pointer-events-none"></div>
    
    <!-- 3. Ambient Neon Color Pulses -->
    <div class="absolute -top-20 -left-20 w-96 h-96 bg-neon-pink/20 rounded-full blur-3xl pointer-events-none neon-aura-pulse"></div>
    <div class="absolute top-1/2 right-10 w-96 h-96 bg-neon-cyan/20 rounded-full blur-3xl pointer-events-none neon-aura-pulse"></div>

    <!-- 4. Dynamic Light Sweep Ray -->
    <div class="absolute inset-0 z-1 overflow-hidden pointer-events-none">
      <div class="w-1/2 h-[200%] -top-1/2 bg-gradient-to-r from-transparent via-white/10 to-transparent hero-light-sweep"></div>
    </div>

    <!-- 5. CRT Scanlines Overlay -->
    <div class="absolute inset-0 z-2 scanlines-overlay opacity-30 pointer-events-none"></div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 py-16 sm:py-24 w-full">
      <div class="max-w-2xl text-left">
        <!-- Scarcity Badge -->
        <div class="inline-flex items-center gap-2 rounded-full border border-neon-pink/50 bg-black/60 backdrop-blur-md px-4 py-1.5 text-xs font-bold text-neon-pink mb-6 pulse-badge shadow-[0_0_15px_rgba(255,0,127,0.3)]">
          <span class="animate-pulse">🔥</span>
          <span>LOTE 01 DISPONÍVEL // APENAS 50 PEÇAS POR MODELO</span>
        </div>

        <!-- Main Headline -->
        <h1 class="text-4xl sm:text-6xl md:text-7xl font-black tracking-tight text-white uppercase mb-4 leading-tight drop-shadow-[0_4px_25px_rgba(0,0,0,0.9)]">
          VICE CITY <span class="text-neon-cyan drop-shadow-[0_0_25px_rgba(0,240,255,0.6)]">SUBMUNDO</span>
        </h1>

        <!-- Subheadline -->
        <p class="text-base sm:text-lg text-gray-200 font-medium leading-relaxed mb-8 drop-shadow-[0_2px_10px_rgba(0,0,0,0.8)]">
          Coleção conceitual autônoma inspirada nas noites elétricas de Leonida e na cultura retro-futurista de Miami anos 80. Peças exclusivas com estampagem HD sob demanda e entrega expressa.
        </p>

        <!-- Live Countdown Timer -->
        <div class="mb-10 inline-block rounded-2xl border border-gray-700/80 bg-black/75 p-4 shadow-2xl backdrop-blur-xl">
          <span class="text-[11px] font-extrabold text-gray-400 block mb-1 uppercase tracking-wider">
            O Lote 01 Encerra Em:
          </span>
          <div id="countdown-timer" class="text-2xl sm:text-3xl font-black text-sunset-amber tracking-widest font-mono drop-shadow-[0_0_15px_rgba(255,168,0,0.5)]">
            14h : 23m : 45s
          </div>
        </div>

        <!-- Hero CTAs -->
        <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-4">
          <a href="#catalogo" class="px-8 py-4 rounded-xl btn-neon-pink font-extrabold text-sm uppercase tracking-wider text-center shadow-[0_0_25px_rgba(255,0,127,0.5)] hover:shadow-[0_0_35px_rgba(255,0,127,0.8)] transition-all">
            EXPLORAR DROP 01
          </a>
          <a href="#combos" class="px-8 py-4 rounded-xl border border-neon-cyan/80 bg-black/60 backdrop-blur-md text-neon-cyan hover:bg-neon-cyan hover:text-gray-900 font-extrabold text-sm uppercase tracking-wider text-center transition-all shadow-[0_0_15px_rgba(0,240,255,0.3)]">
            VER COMBOS PROMOCIONAIS (-16%)
          </a>
        </div>
      </div>
    </div>
  </section>

  <!-- Category Filter Pills Bar -->'''

content, count = old_hero_pattern.subn(new_hero, content)
print(f"Hero section replaced: {count} matches")

# Upgrade Combos section background with hero_panoramic_model.jpg
old_combos = '<section id="combos" class="py-16 bg-vice-dark border-t border-b border-gray-800">'
new_combos = '''<!-- Promotional Bundles VIP Section with Panoramic Skyline Background -->
  <section id="combos" class="relative py-20 border-t border-b border-gray-800 overflow-hidden">
    <!-- Panoramic Background -->
    <div class="absolute inset-0 z-0">
      <img src="assets/banners/hero_panoramic_model.jpg" alt="Vice District Skyline Banner" class="w-full h-full object-cover object-center filter brightness-50">
      <div class="absolute inset-0 bg-gradient-to-b from-vice-void via-vice-dark/85 to-vice-void"></div>
    </div>
    <div class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">'''

if old_combos in content:
    content = content.replace(old_combos, new_combos)
    # Also adjust closing div of combos if needed
    print("Combos section updated with panoramic banner")

index_path.write_text(content, encoding="utf-8")
print("index.html written successfully!")
