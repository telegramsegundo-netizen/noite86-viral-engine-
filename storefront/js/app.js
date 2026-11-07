/**
 * storefront/js/app.js - Modern Vice City Web Storefront Main Application
 * Manages product rendering, filtering, dual currency toggle (BRL/USD),
 * interactive product modal with AI art prompt reveal, slide-over cart drawer with free shipping progress bar,
 * coupon code validation, and localStorage state persistence.
 */

// Fallback embedded products dataset (guarantees offline/direct-file execution without server)
const FALLBACK_PRODUCTS = [
  {
    id: "VC-APP-001",
    sku: "VC-APP-001",
    title: "\"Vice Sunset\" Silk-Touch Camp Collar Bowling Shirt",
    category: "Apparel",
    price_brl: 189.90,
    price_usd: 38.00,
    production_cost_brl: 58.00,
    margin_percent: 69.46,
    tags: ["bestseller", "streetwear", "resort", "synthwave"],
    headline: "Camisa resort de caimento boxy com estampa Art Deco e neon crepúsculo.",
    description: "Confeccionada em viscose toque de seda com respirabilidade superior. Estampa geométrica Art Deco fluida inspirada nas noites de Ocean Drive.",
    features: ["Tecido acetinado respirável anti-suor", "Gola cubana clássica resort", "Botões em resina tartaruga", "Corte boxy oversized"],
    image_placeholder: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 600 600'><rect width='600' height='600' fill='%23080E24'/><path d='M150,120 L450,120 L520,240 L450,270 L450,540 L150,540 L150,270 L80,240 Z' fill='%23121B38' stroke='%2300F0FF' stroke-width='4'/><polygon points='230,120 300,280 370,120' fill='%23FF1381' opacity='0.85'/><circle cx='300' cy='360' r='90' fill='%23FFA800' opacity='0.7'/><text x='300' y='575' text-anchor='middle' fill='%2300F0FF' font-family='sans-serif' font-weight='bold' font-size='20'>VICE SUNSET SHIRT</text></svg>",
    ai_art_prompt: {
      flux_prompt: "Seamless textile print pattern, 1980s Miami aesthetic, art deco geometric lines, stylized tropical palm tree silhouettes, subtle neon pink and cyan flamingo wireframes, gradient background of twilight purple and warm sunset orange, clean vector repeat, 300 DPI",
      midjourney_prompt: "Commercial editorial lookbook photograph of a men's relaxed-fit Cuban collar silk bowling shirt, vibrant 1980s Miami Vice color palette, pastel turquoise and hot magenta gradient base with repeating subtle art deco palm leaf silhouettes --ar 3:4 --v 6.1"
    }
  },
  {
    id: "VC-APP-002",
    sku: "VC-APP-002",
    title: "\"Neon Mirage\" Reversible Holographic Bomber Jacket",
    category: "Apparel",
    price_brl: 349.90,
    price_usd: 69.90,
    production_cost_brl: 115.00,
    margin_percent: 67.13,
    tags: ["luxury", "outerwear", "holographic", "statement"],
    headline: "Jaqueta bomber reversível em cetim dicróico com 40.000 pontos de bordado.",
    description: "Lado A em cetim dicróico holográfico furta-cor magenta/ciano com bordado gigante de flamingos neon. Lado B em navy tático com bolso contrabandista interno.",
    features: ["Construção reversível dupla-face", "Bordado de alta densidade nas costas", "Zíper robusto reversível em prata envelhecida", "Bolso secreto interno"],
    image_placeholder: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 600 600'><rect width='600' height='600' fill='%23080E24'/><path d='M180,150 L420,150 L530,280 L460,330 L450,510 L150,510 L140,330 L70,280 Z' fill='%23181C26' stroke='%23FF1381' stroke-width='4'/><circle cx='300' cy='310' r='70' fill='none' stroke='%2300F0FF' stroke-width='3'/><text x='300' y='570' text-anchor='middle' fill='%23FF1381' font-family='sans-serif' font-weight='bold' font-size='20'>NEON MIRAGE BOMBER</text></svg>",
    ai_art_prompt: {
      flux_prompt: "Studio product photograph of a luxury reversible bomber jacket displayed on a matte black minimalist mannequin, illuminated by neon tubes in pink and blue, cinematic vaporwave editorial, ultra-detailed fabric micro-texture",
      midjourney_prompt: "High-fashion streetwear product shot of an iridescent satin bomber jacket floating in mid-air, dual-tone dichroic fabric shifting between neon cyan and electric magenta, intricate embroidered back patch --ar 1:1 --v 6.1"
    }
  },
  {
    id: "VC-APP-003",
    sku: "VC-APP-003",
    title: "\"Miami Overdrive '84\" Heavyweight Oversized Graphic Tee",
    category: "Apparel",
    price_brl: 139.90,
    price_usd: 27.90,
    production_cost_brl: 38.00,
    margin_percent: 72.84,
    tags: ["bestseller", "streetwear", "heavyweight", "graphic-tee"],
    headline: "Camiseta oversized 260 GSM algodão penteado estonado com esportivo clássico 1984.",
    description: "Algodão premium 260 GSM com lavagem estonada vintage mineral. Estampa distressed de alta definição com as lanternas horizontais de um esportivo clássico acelerando sob palmeiras neon.",
    features: ["100% Algodão penteado 260 GSM ultra-pesado", "Lavagem mineral acid wash vintage", "Estampa silk DTG HD toque zero", "Gola canelada grossa de 3cm"],
    image_placeholder: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 600 600'><rect width='600' height='600' fill='%23080E24'/><path d='M160,140 L440,140 L540,250 L470,290 L450,540 L150,540 L130,290 L60,250 Z' fill='%23181C26'/><rect x='210' y='220' width='180' height='160' rx='10' fill='%230A0D17' stroke='%23FF1381' stroke-width='3'/><text x='300' y='575' text-anchor='middle' fill='%2300F0FF' font-family='sans-serif' font-weight='bold' font-size='20'>MIAMI OVERDRIVE '84 TEE</text></svg>",
    ai_art_prompt: {
      flux_prompt: "T-shirt graphic design illustration, 1984 retro wedge sports car speeding down an Ocean Drive boulevard at night, neon signboards, towering coconut palms, giant synthwave wireframe sun on the horizon, 300 DPI",
      midjourney_prompt: "Flat lay commercial apparel photography of an oversized heavyweight washed black vintage t-shirt, dropped shoulders, thick ribbed collar, featuring a large chest graphic print of a 1984 red wedge sports car --ar 4:5 --v 6.1"
    }
  },
  {
    id: "VC-APP-004",
    sku: "VC-APP-004",
    title: "\"South Beach Syndicate\" Embroidered Corduroy Snapback",
    category: "Accessories",
    price_brl: 129.90,
    price_usd: 25.90,
    production_cost_brl: 32.00,
    margin_percent: 75.37,
    tags: ["headwear", "accessories", "corduroy", "embroidery"],
    headline: "Boné 6-panel desestruturado em veludo cotelê turquesa com bordado 3D puff.",
    description: "Veludo cotelê 12-wale vintage cor turquesa marinho com bordado 3D em alto relevo rosa neon. Fecho traseiro em latão envelhecido e aba inferior em verde clássico retrô.",
    features: ["100% Veludo cotelê premium 12-wale", "Bordado 3D puff de alta densidade", "Aba inferior verde vintage Kelly Green", "Fecho ajustável em latão maciço"],
    image_placeholder: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 600 600'><rect width='600' height='600' fill='%23080E24'/><path d='M150,380 C150,220 450,220 450,380 Z' fill='%232DE2A6' stroke='%2300F0FF' stroke-width='4'/><path d='M110,380 C110,350 490,350 490,380 C490,440 110,440 110,380 Z' fill='%231AB582'/><text x='300' y='570' text-anchor='middle' fill='%232DE2A6' font-family='sans-serif' font-weight='bold' font-size='20'>CORDUROY SNAPBACK</text></svg>",
    ai_art_prompt: {
      flux_prompt: "Ultra realistic product photo of a turquoise vintage corduroy cap, pink 3D puff embroidery, studio lighting with neon side accents, close up fabric texture, brass buckle",
      midjourney_prompt: "Product hero shot of an unstructured vintage 6-panel corduroy snapback hat in seafoam turquoise color, 3D puff embroidery, macro lens, detailed wale rib texture --ar 1:1 --v 6.1"
    }
  },
  {
    id: "VC-LGT-001",
    sku: "VC-LGT-001",
    title: "\"Ocean Drive Nocturne\" Laser-Etched Acrylic Neon Lamp",
    category: "Decor",
    price_brl: 149.90,
    price_usd: 29.90,
    production_cost_brl: 38.00,
    margin_percent: 74.65,
    tags: ["desk-setup", "ambient-light", "decor", "acrylic-lamp"],
    headline: "Luminária de mesa em acrílico óptico 5mm gravado a laser com base em alumínio.",
    description: "Placa em acrílico fundido de 5mm com gravação vetorial precisa da orla Art Deco de Ocean Drive. Base cilíndrica pesada em alumínio escovado com LEDs RGB duais (ciano e magenta) e controle touch.",
    features: ["Acrílico óptico 5mm de alta transmissão", "LEDs bicolores ciano (#00F0FF) e magenta (#FF1381)", "Base em alumínio escovado maciço", "Alimentação via USB-C com dimmer touch"],
    image_placeholder: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 600 600'><rect width='600' height='600' fill='%23080E24'/><rect x='150' y='100' width='300' height='360' rx='15' fill='%230E1A38' stroke='%2300F0FF' stroke-width='3'/><rect x='120' y='460' width='360' height='50' rx='8' fill='%231F2937' stroke='%23374151' stroke-width='2'/><text x='300' y='570' text-anchor='middle' fill='%2300F0FF' font-family='sans-serif' font-weight='bold' font-size='20'>OCEAN DRIVE NEON LAMP</text></svg>",
    ai_art_prompt: {
      flux_prompt: "Studio product photograph of a glowing acrylic edge-lit desk lamp with retro 80s Miami boulevard scene, laser etched lines illuminated in neon pink and cyan light, brushed black metallic base",
      midjourney_prompt: "High-end commercial product photograph of a modern edge-lit acrylic desk lamp, precision laser-etched clear acrylic plate showing retro sports car driving past art deco beachfront hotels --ar 16:9 --v 6.1"
    }
  },
  {
    id: "VC-AUD-001",
    sku: "VC-AUD-001",
    title: "\"Synthwave Cassette\" Retro Boombox Bluetooth Speaker Case",
    category: "Decor",
    price_brl: 179.90,
    price_usd: 35.90,
    production_cost_brl: 45.00,
    margin_percent: 74.99,
    tags: ["audio", "speaker", "bluetooth", "boombox", "cassette"],
    headline: "Miniatura boombox 1986 com driver de neodímio 5W e bateria de 10 horas.",
    description: "Carcaça de silicone fosco anti-impacto moldada com botões táteis e visor analógico de fita cassete. Som potente e cristalino com radiador passivo de graves.",
    features: ["Driver neodímio 5W com graves encorpados", "Bluetooth 5.3 com 10m de alcance", "Bateria recarregável de 1200mAh (10h de som)", "Microfone embutido para chamadas viva-voz"],
    image_placeholder: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 600 600'><rect width='600' height='600' fill='%23080E24'/><rect x='80' y='180' width='440' height='260' rx='25' fill='%231E293B' stroke='%23FF1381' stroke-width='4'/><circle cx='180' cy='310' r='60' fill='%230F172A' stroke='%2300F0FF' stroke-width='4'/><circle cx='420' cy='310' r='60' fill='%230F172A' stroke='%2300F0FF' stroke-width='4'/><text x='300' y='570' text-anchor='middle' fill='%23FFA800' font-family='sans-serif' font-weight='bold' font-size='20'>SYNTHWAVE BOOMBOX SPEAKER</text></svg>",
    ai_art_prompt: {
      flux_prompt: "Studio product photograph of a miniature retro 80s boombox portable speaker, matte turquoise and neon pink casing, realistic speaker grill, cassette tape door with amber LED backlight",
      midjourney_prompt: "Macro product shot of a retro 1980s portable boombox cassette player miniaturized into a compact silicone Bluetooth speaker, tactile rubberized buttons --ar 1:1 --v 6.1"
    }
  },
  {
    id: "VC-NOQ-001",
    sku: "VC-NOQ-001",
    title: "\"Vice Rush '86\" Secret Compartment Stash Can",
    category: "Novelty",
    price_brl: 119.90,
    price_usd: 23.90,
    production_cost_brl: 26.00,
    margin_percent: 78.32,
    tags: ["collectible", "stash-can", "tactical", "decoy", "novelty"],
    headline: "Lata de refrigerante com fundo rosqueável indetectável e cápsula antifurto.",
    description: "Lata de alumínio com peso idêntico ao de uma bebida cheia de 355ml. O fundo falso com rosca CNC de precisão revela um compartimento estanque anti-odor para chaves, cédulas ou joias.",
    features: ["Centro de gravidade idêntico a lata cheia", "Rosca invisível sem emendas perceptíveis", "Cápsula interna com vedação em silicone anti-odor", "Verniz brilhante automotivo anti-risco"],
    image_placeholder: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 600 600'><rect width='600' height='600' fill='%23080E24'/><path d='M220,160 C220,140 380,140 380,160 L380,440 C380,460 220,460 220,440 Z' fill='%23FF1381' stroke='%2300F0FF' stroke-width='4'/><text x='300' y='570' text-anchor='middle' fill='%23FF1381' font-family='sans-serif' font-weight='bold' font-size='20'>SECRET STASH CAN</text></svg>",
    ai_art_prompt: {
      flux_prompt: "Product photo of a retro aluminum energy drink can called Vice Rush, unscrewed metal base showing secret compartment, realistic water droplets, studio softbox lighting",
      midjourney_prompt: "Commercial product photograph of an aluminum soda can with condensation droplets, vintage 1986 Florida energy drink branding, bottom portion unscrewed showing secret compartment --ar 1:1 --v 6.1"
    }
  },
  {
    id: "VC-DRK-001",
    sku: "VC-DRK-001",
    title: "\"Golden Hour Biscayne\" Gradient Thermal Tumbler (900ml)",
    category: "Accessories",
    price_brl: 159.90,
    price_usd: 31.90,
    production_cost_brl: 42.00,
    margin_percent: 73.73,
    tags: ["drinkware", "tumbler", "thermal", "laser-engraved"],
    headline: "Copo térmico inox 18/8 com pintura eletrostática degradê magenta e âmbar.",
    description: "Parede dupla com isolamento a vácuo em aço inoxidável 18/8. Mantém líquidos gelados por até 24h e quentes por 8h. Gravação permanente a laser de palmeiras retro-futuristas.",
    features: ["900ml em aço cirúrgico 18/8 livre de BPA", "Isolamento a vácuo com retenção de 24h gelado", "Pintura a pó antiderrapante com gravação a laser", "Tampa de vedação em Eastman Tritan transparente"],
    image_placeholder: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 600 600'><rect width='600' height='600' fill='%23080E24'/><path d='M210,140 L390,140 L360,480 L240,480 Z' fill='%23FFA800' stroke='%2300F0FF' stroke-width='3'/><text x='300' y='570' text-anchor='middle' fill='%23FFA800' font-family='sans-serif' font-weight='bold' font-size='20'>GRADIENT THERMAL TUMBLER</text></svg>",
    ai_art_prompt: {
      flux_prompt: "Studio commercial shot of an ombre pink and orange stainless steel insulated tumbler cup with straw, palm tree laser engraving, crisp droplets of ice water",
      midjourney_prompt: "Hero shot of a 30oz stainless steel thermal tumbler, powder coated smooth ombre gradient transitioning from intense neon flamingo pink to warm golden mango --ar 3:4 --v 6.1"
    }
  },
  {
    id: "VC-AUT-001",
    sku: "VC-AUT-001",
    title: "\"Sunburst Palm\" Coconut & Sea-Breeze Car Freshener (3-Pack)",
    category: "Novelty",
    price_brl: 49.90,
    price_usd: 9.90,
    production_cost_brl: 7.50,
    margin_percent: 84.97,
    tags: ["automotive", "air-freshener", "accessories", "impulse-buy"],
    headline: "Trio de aromatizantes automotivos com essência de coco tostado e brisa tropical.",
    description: "Cartão de algodão absorvente espesso com 3 designs colecionáveis (Chaveiro Motel, Flamingos e Cupê 80s). Óleos essenciais orgânicos de liberação lenta com durabilidade de até 45 dias.",
    features: ["Pack com 3 formatos die-cut exclusivos", "Papelão celulose pesado de 2mm", "Fragrância duradoura de coco e baunilha", "Cordão elástico de nylon reforçado"],
    image_placeholder: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 600 600'><rect width='600' height='600' fill='%23080E24'/><polygon points='160,220 230,120 300,220 230,320' fill='%232DE2A6' stroke='%2300F0FF' stroke-width='3'/><path d='M340,300 C340,200 480,200 480,300 Z' fill='%23FF1381'/><text x='300' y='570' text-anchor='middle' fill='%232DE2A6' font-family='sans-serif' font-weight='bold' font-size='20'>CAR AIR FRESHENER 3-PACK</text></svg>",
    ai_art_prompt: {
      flux_prompt: "Product photograph of 3 die cut hanging car scent fresheners, synthwave shapes, resting on stitched leather sports car seat, sunset light flare",
      midjourney_prompt: "Commercial product packaging shot of three hanging car air fresheners: retro turquoise motel room key, 80s sports car silhouette in magenta, and palm tree --ar 1:1 --v 6.1"
    }
  },
  {
    id: "VC-EDC-001",
    sku: "VC-EDC-001",
    title: "\"Pelican Bay Motel\" Hot-Foil Stamped Acrylic Keytag",
    category: "Novelty",
    price_brl: 39.90,
    price_usd: 7.90,
    production_cost_brl: 5.50,
    margin_percent: 86.22,
    tags: ["keychain", "edc", "collectible", "motel-key", "gold-foil"],
    headline: "Chaveiro losango de motel anos 80 em acrílico seafoam com estampagem em folha de ouro.",
    description: "Formato icônico de chaveiro de motel dos anos 70/80 em acrílico translúcido seafoam. Tipografia estampada a quente em folha de ouro metálica brilhante e argola em latão maciço.",
    features: ["Silhueta clássica em losango vintage", "Estampagem profunda hot-foil dourada", "Argola reforçada em latão envelhecido", "Item perfeito para order bump"],
    image_placeholder: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 600 600'><rect width='600' height='600' fill='%23080E24'/><polygon points='300,100 480,300 300,500 120,300' fill='%232DE2A6' stroke='%2300F0FF' stroke-width='4'/><text x='300' y='360' text-anchor='middle' fill='%23FFA800' font-family='sans-serif' font-weight='bold' font-size='32'>305</text><text x='300' y='570' text-anchor='middle' fill='%232DE2A6' font-family='sans-serif' font-weight='bold' font-size='20'>PELICAN BAY KEYTAG</text></svg>",
    ai_art_prompt: {
      flux_prompt: "Studio product photograph of a retro turquoise motel keychain with gold embossed letters 'PELICAN BAY RESORT - ROOM 305', brass key attached",
      midjourney_prompt: "Macro close-up photograph of a vintage 1980s diamond rhombus motel keychain, made of translucent turquoise acrylic with deep metallic gold hot-foil stamped text --ar 1:1 --v 6.1"
    }
  },
  {
    id: "VC-DSK-001",
    sku: "VC-DSK-001",
    title: "\"Midnight Tropic\" XXL Stitched Gaming Deskmat (900x400)",
    category: "Decor",
    price_brl: 129.90,
    price_usd: 25.90,
    production_cost_brl: 34.00,
    margin_percent: 73.83,
    tags: ["deskmat", "mousepad", "gaming", "battlestation", "synthwave-map"],
    headline: "Deskmat estendido 900x400x4mm com mapa costeiro synthwave e borda costurada.",
    description: "Tecido micro-trançado de baixo atrito hidrofóbico (repelente a líquidos). Base de borracha natural chevron antiderrapante e bordas costuradas em magenta neon anti-desfiamento.",
    features: ["Área generosa 900x400x4mm cobrindo teclado e mouse", "Superfície speed-control para sensores ópticos", "Borda com costura dupla reforçada 360°", "Revestimento impermeável fácil de limpar"],
    image_placeholder: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 600 600'><rect width='600' height='600' fill='%23080E24'/><rect x='60' y='180' width='480' height='240' rx='12' fill='%230F172A' stroke='%23FF1381' stroke-width='6'/><text x='300' y='570' text-anchor='middle' fill='%2300F0FF' font-family='sans-serif' font-weight='bold' font-size='20'>MIDNIGHT TROPIC DESKMAT</text></svg>",
    ai_art_prompt: {
      flux_prompt: "Overhead top-down setup view of an extra large gaming desk mat with glowing retro Miami coastline map design, neon roads and cyan water channels, magenta stitched borders",
      midjourney_prompt: "Elevated 45-degree angle desk setup photograph highlighting a 900x400mm extended gaming mousepad, vivid high-contrast synthwave artwork --ar 16:9 --v 6.1"
    }
  },
  {
    id: "VC-EYE-001",
    sku: "VC-EYE-001",
    title: "\"Palm Mirage\" Polarized Rose-Gold Aviator Sunglasses",
    category: "Accessories",
    price_brl: 169.90,
    price_usd: 33.90,
    production_cost_brl: 36.00,
    margin_percent: 78.81,
    tags: ["eyewear", "accessories", "aviator", "polarized", "retro-luxury"],
    headline: "Óculos aviador 1980 em aço inox dourado com lentes degradê polarizadas TAC UV400.",
    description: "Armação clássica em aço inoxidável com banho dourado acetinado e ponteiras em acetato ciano. Lentes TAC polarizadas com proteção total UV400 e filtro degradê âmbar rosé.",
    features: ["Lentes polarizadas TAC UV400 Categoria 3", "Armação inoxidável ultrafina e resistente", "Dobradiças reforçadas com 5 barris e mola", "Acompanha case rígido e flanela synthwave"],
    image_placeholder: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 600 600'><rect width='600' height='600' fill='%23080E24'/><circle cx='210' cy='300' r='75' fill='%231E293B' stroke='%23FFA800' stroke-width='5'/><circle cx='390' cy='300' r='75' fill='%231E293B' stroke='%23FFA800' stroke-width='5'/><line x1='285' y1='275' x2='315' y2='275' stroke='%23FFA800' stroke-width='4'/><text x='300' y='570' text-anchor='middle' fill='%23FFA800' font-family='sans-serif' font-weight='bold' font-size='20'>PALM MIRAGE AVIATORS</text></svg>",
    ai_art_prompt: {
      flux_prompt: "Product photograph of vintage gold aviator sunglasses with gradient amber lenses, resting on a neon-lit sports car hood, warm sunset golden hour reflections",
      midjourney_prompt: "Luxury commercial product shoot of gold teardrop aviator sunglasses with amber-to-rose polarized lenses, resting on an 80s marble bar counter with tropical lighting --ar 1:1 --v 6.1"
    }
  }
];

// App State
const StoreApp = {
  products: FALLBACK_PRODUCTS,
  bundles: [],
  cart: [],
  currency: 'BRL', // 'BRL' or 'USD'
  currentCategory: 'all',
  searchQuery: '',
  coupon: null,
  selectedProduct: null,
  selectedSize: 'M',
  selectedQuantity: 1,

  init() {
    this.loadCartFromStorage();
    this.loadCatalogData();
    this.initCountdownTimer();
    this.setupEventListeners();
    this.render();
  },

  loadCartFromStorage() {
    try {
      const saved = localStorage.getItem('vice_cart');
      if (saved) {
        this.cart = JSON.parse(saved);
      }
    } catch (e) {
      this.cart = [];
    }
  },

  saveCartToStorage() {
    try {
      localStorage.setItem('vice_cart', JSON.stringify(this.cart));
    } catch (e) {}
    this.updateCartBadge();
    this.renderCartDrawer();
  },

  getCart() {
    return this.cart;
  },

  clearCart() {
    this.cart = [];
    this.saveCartToStorage();
  },

  loadCatalogData() {
    // Attempt dynamic fetch from data/store_config.json
    fetch('data/store_config.json')
      .then(res => res.json())
      .then(config => {
        if (config.products && config.products.length >= 10) {
          this.products = config.products;
        }
        if (config.bundles) {
          this.bundles = config.bundles;
        }
        this.render();
      })
      .catch(() => {
        // Fallback already pre-loaded
        this.render();
      });
  },

  setCurrency(curr) {
    this.currency = curr;
    const btnBrl = document.getElementById('currency-btn-brl');
    const btnUsd = document.getElementById('currency-btn-usd');
    if (btnBrl && btnUsd) {
      if (curr === 'BRL') {
        btnBrl.className = 'px-3 py-1 text-xs font-bold rounded bg-neon-pink text-white';
        btnUsd.className = 'px-3 py-1 text-xs font-bold rounded text-gray-400 hover:text-white';
      } else {
        btnBrl.className = 'px-3 py-1 text-xs font-bold rounded text-gray-400 hover:text-white';
        btnUsd.className = 'px-3 py-1 text-xs font-bold rounded bg-neon-cyan text-gray-900';
      }
    }
    this.render();
    this.renderCartDrawer();
  },

  toggleCurrency() {
    this.setCurrency(this.currency === 'BRL' ? 'USD' : 'BRL');
  },

  formatPrice(priceBrl, priceUsd) {
    if (this.currency === 'BRL') {
      return `R$ ${Number(priceBrl).toFixed(2)}`;
    }
    return `$ ${Number(priceUsd).toFixed(2)}`;
  },

  getFilteredProducts() {
    return this.products.filter(p => {
      // Category match
      let matchCategory = true;
      if (this.currentCategory !== 'all') {
        const cat = (p.display_category || p.category || '').toLowerCase();
        matchCategory = cat.includes(this.currentCategory.toLowerCase());
      }
      // Search match
      let matchSearch = true;
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        matchSearch = (p.title && p.title.toLowerCase().includes(query)) ||
                      (p.description && p.description.toLowerCase().includes(query)) ||
                      (p.headline && p.headline.toLowerCase().includes(query)) ||
                      (p.tags && p.tags.some(t => t.toLowerCase().includes(query)));
      }
      return matchCategory && matchSearch;
    });
  },

  render() {
    this.renderProductGrid();
    this.updateCartBadge();
  },

  renderProductGrid() {
    const grid = document.getElementById('product-grid');
    if (!grid) return;

    const items = this.getFilteredProducts();

    if (items.length === 0) {
      grid.innerHTML = `
        <div class="col-span-full py-16 text-center text-gray-400">
          <p class="text-xl">Nenhum produto encontrado nesta categoria.</p>
          <button onclick="StoreApp.setCategory('all')" class="mt-4 px-6 py-2 btn-neon-cyan rounded-lg">Ver Todos os Produtos</button>
        </div>
      `;
      return;
    }

    grid.innerHTML = items.map(p => {
      const priceFormatted = this.formatPrice(p.price_brl, p.price_usd);
      const installmentText = this.currency === 'BRL'
        ? `12x de R$ ${(p.price_brl / 12).toFixed(2)}`
        : 'Frete Internacional Expresso';
      const pixIncentive = this.currency === 'BRL'
        ? `<span class="text-xs text-neon-green font-semibold">5% OFF no PIX: R$ ${(p.price_brl * 0.95).toFixed(2)}</span>`
        : `<span class="text-xs text-neon-cyan font-semibold">Free US Shipping over $50</span>`;

      const badgeText = p.margin_percent >= 80 ? 'HIGH DEMAND' : (p.tags && p.tags.includes('bestseller') ? 'BESTSELLER' : 'DROP 01');

      return `
        <div class="group relative rounded-xl border border-gray-800 bg-[#12121f] p-4 transition-all duration-300 hover:border-neon-pink hover:shadow-[0_0_25px_rgba(255,0,127,0.3)] flex flex-col justify-between">
          <div>
            <!-- Top Badges -->
            <div class="mb-3 flex items-center justify-between">
              <span class="rounded bg-neon-pink/20 px-2 py-0.5 text-[11px] font-bold text-neon-pink border border-neon-pink/40 pulse-badge">
                ${badgeText}
              </span>
              <span class="text-[11px] font-semibold text-neon-cyan uppercase tracking-wider">
                ${p.display_category || p.category}
              </span>
            </div>

            <!-- Image Viewport -->
            <div class="relative mb-4 aspect-square w-full overflow-hidden rounded-lg bg-[#09090f] flex items-center justify-center cursor-pointer" onclick="StoreApp.openProductModal('${p.sku || p.id}')">
              <img src="${p.image_placeholder}" alt="${p.title}" class="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105" loading="lazy">
              <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-3">
                <span class="text-xs font-bold text-white flex items-center gap-1">
                  🔍 Ver Detalhes & Prompts
                </span>
              </div>
            </div>

            <!-- Title & Headline -->
            <h3 class="mb-1 text-base font-bold text-white group-hover:text-neon-pink transition-colors line-clamp-1 cursor-pointer" onclick="StoreApp.openProductModal('${p.sku || p.id}')">
              ${p.title}
            </h3>
            <p class="mb-3 text-xs text-gray-400 line-clamp-2">
              ${p.headline || p.description}
            </p>
          </div>

          <!-- Price & CTAs -->
          <div class="pt-3 border-t border-gray-800/80">
            <div class="flex items-baseline justify-between mb-1">
              <span class="text-xl font-extrabold text-white">${priceFormatted}</span>
              <span class="text-[11px] text-gray-400">${installmentText}</span>
            </div>
            <div class="mb-3">${pixIncentive}</div>
            
            <div class="grid grid-cols-2 gap-2">
              <button onclick="StoreApp.openProductModal('${p.sku || p.id}')" class="w-full py-2 px-3 text-xs font-bold rounded-lg border border-gray-700 hover:border-neon-cyan text-gray-200 hover:text-neon-cyan transition-colors">
                Detalhes
              </button>
              <button onclick="StoreApp.quickAddToCart('${p.sku || p.id}')" class="w-full py-2 px-3 text-xs font-bold rounded-lg btn-neon-pink flex items-center justify-center gap-1">
                + Carrinho
              </button>
            </div>
          </div>
        </div>
      `;
    }).join('');
  },

  setCategory(cat) {
    this.currentCategory = cat;
    // Update pills styling
    document.querySelectorAll('.cat-pill').forEach(btn => {
      const pillCat = btn.getAttribute('data-category');
      if (pillCat === cat) {
        btn.className = 'cat-pill px-4 py-2 rounded-full text-xs font-bold border border-neon-cyan bg-neon-cyan/10 text-neon-cyan shadow-[0_0_15px_rgba(0,240,255,0.3)] transition-all';
      } else {
        btn.className = 'cat-pill px-4 py-2 rounded-full text-xs font-bold border border-gray-800 bg-[#12121f] text-gray-400 hover:text-white hover:border-gray-700 transition-all';
      }
    });
    this.renderProductGrid();
  },

  openProductModal(sku) {
    const product = this.products.find(p => (p.sku || p.id) === sku);
    if (!product) return;

    this.selectedProduct = product;
    this.selectedSize = 'M';
    this.selectedQuantity = 1;

    const modal = document.getElementById('product-modal');
    if (!modal) return;

    // Populate Modal Content
    document.getElementById('modal-product-img').src = product.image_placeholder;
    document.getElementById('modal-product-title').textContent = product.title;
    document.getElementById('modal-product-category').textContent = product.display_category || product.category;
    document.getElementById('modal-product-price').textContent = this.formatPrice(product.price_brl, product.price_usd);
    document.getElementById('modal-product-description').textContent = product.description;
    document.getElementById('modal-qty-input').value = '1';

    // AI Prompts accordion
    const fluxEl = document.getElementById('modal-prompt-flux');
    const mjEl = document.getElementById('modal-prompt-mj');
    if (fluxEl) {
      fluxEl.textContent = (product.ai_art_prompt && product.ai_art_prompt.flux_prompt) || (product.ai_prompts && product.ai_prompts.flux_pro_prompt) || 'N/A';
    }
    if (mjEl) {
      mjEl.textContent = (product.ai_art_prompt && product.ai_art_prompt.midjourney_prompt) || (product.ai_prompts && product.ai_prompts.midjourney_v6_prompt) || 'N/A';
    }

    // Features list
    const featuresList = document.getElementById('modal-product-features');
    if (featuresList && product.features) {
      featuresList.innerHTML = product.features.map(f => `<li class="flex items-center gap-2">✓ ${f}</li>`).join('');
    }

    modal.classList.remove('hidden');
    modal.classList.add('flex');
    document.body.classList.add('overflow-hidden');
  },

  closeProductModal() {
    const modal = document.getElementById('product-modal');
    if (!modal) return;
    modal.classList.add('hidden');
    modal.classList.remove('flex');
    document.body.classList.remove('overflow-hidden');
  },

  selectModalSize(size) {
    this.selectedSize = size;
    document.querySelectorAll('.size-btn').forEach(btn => {
      if (btn.getAttribute('data-size') === size) {
        btn.className = 'size-btn h-9 w-9 rounded border border-neon-cyan bg-neon-cyan/20 text-neon-cyan font-bold text-xs flex items-center justify-center';
      } else {
        btn.className = 'size-btn h-9 w-9 rounded border border-gray-700 bg-transparent text-gray-300 font-bold text-xs hover:border-gray-500 flex items-center justify-center';
      }
    });
  },

  adjustModalQuantity(delta) {
    const input = document.getElementById('modal-qty-input');
    if (!input) return;
    let qty = parseInt(input.value) || 1;
    qty = Math.max(1, Math.min(10, qty + delta));
    input.value = qty;
    this.selectedQuantity = qty;
  },

  addProductFromModal() {
    if (!this.selectedProduct) return;
    this.addToCart(this.selectedProduct, this.selectedQuantity, this.selectedSize);
    this.closeProductModal();
    this.openCartDrawer();
  },

  buyNowFromModal() {
    if (!this.selectedProduct) return;
    this.addToCart(this.selectedProduct, this.selectedQuantity, this.selectedSize);
    this.closeProductModal();
    if (window.CheckoutSimulator && typeof window.CheckoutSimulator.open === 'function') {
      window.CheckoutSimulator.open();
    }
  },

  quickAddToCart(sku) {
    const product = this.products.find(p => (p.sku || p.id) === sku);
    if (!product) return;
    this.addToCart(product, 1, 'M');
    this.openCartDrawer();
  },

  addToCart(product, quantity = 1, size = 'M') {
    const sku = product.sku || product.id;
    const existingIndex = this.cart.findIndex(i => i.sku === sku && i.size === size);

    if (existingIndex > -1) {
      this.cart[existingIndex].quantity += quantity;
    } else {
      this.cart.push({
        sku: sku,
        title: product.title,
        price_brl: product.price_brl,
        price_usd: product.price_usd,
        image: product.image_placeholder,
        size: size,
        quantity: quantity
      });
    }

    this.saveCartToStorage();
  },

  updateCartItemQty(index, delta) {
    if (!this.cart[index]) return;
    this.cart[index].quantity += delta;
    if (this.cart[index].quantity <= 0) {
      this.cart.splice(index, 1);
    }
    this.saveCartToStorage();
  },

  removeCartItem(index) {
    if (!this.cart[index]) return;
    this.cart.splice(index, 1);
    this.saveCartToStorage();
  },

  updateCartBadge() {
    const badge = document.getElementById('cart-badge');
    const totalCount = this.cart.reduce((sum, item) => sum + item.quantity, 0);
    if (badge) {
      badge.textContent = totalCount;
      if (totalCount > 0) {
        badge.classList.remove('hidden');
      } else {
        badge.classList.add('hidden');
      }
    }
  },

  openCartDrawer() {
    const drawer = document.getElementById('cart-drawer');
    const overlay = document.getElementById('cart-overlay');
    if (!drawer) return;
    drawer.classList.remove('translate-x-full');
    drawer.classList.add('translate-x-0');
    if (overlay) overlay.classList.remove('hidden');
    document.body.classList.add('overflow-hidden');
    this.renderCartDrawer();
  },

  closeCartDrawer() {
    const drawer = document.getElementById('cart-drawer');
    const overlay = document.getElementById('cart-overlay');
    if (!drawer) return;
    drawer.classList.remove('translate-x-0');
    drawer.classList.add('translate-x-full');
    if (overlay) overlay.classList.add('hidden');
    document.body.classList.remove('overflow-hidden');
  },

  applyCoupon() {
    const input = document.getElementById('coupon-input');
    const feedback = document.getElementById('coupon-feedback');
    if (!input) return;

    const code = input.value.trim().toUpperCase();
    if (code === 'VICE10') {
      this.coupon = { code: 'VICE10', discountPercent: 10 };
      if (feedback) {
        feedback.textContent = '✓ Cupom VICE10 aplicado: 10% de desconto!';
        feedback.className = 'text-xs text-neon-green mt-1 font-semibold';
        feedback.classList.remove('hidden');
      }
    } else {
      this.coupon = null;
      if (feedback) {
        feedback.textContent = '✕ Cupom inválido ou expirado.';
        feedback.className = 'text-xs text-red-400 mt-1 font-semibold';
        feedback.classList.remove('hidden');
      }
    }
    this.renderCartDrawer();
  },

  renderCartDrawer() {
    const container = document.getElementById('cart-items-container');
    const subtotalEl = document.getElementById('cart-subtotal');
    const shippingEl = document.getElementById('cart-shipping');
    const discountEl = document.getElementById('cart-discount');
    const totalEl = document.getElementById('cart-total');
    const freeShippingBar = document.getElementById('free-shipping-progress');
    const freeShippingText = document.getElementById('free-shipping-text');

    if (!container) return;

    if (this.cart.length === 0) {
      container.innerHTML = `
        <div class="py-20 text-center text-gray-400">
          <p class="text-base font-semibold">Seu carrinho está vazio.</p>
          <p class="text-xs text-gray-500 mt-1">Explore os itens do Drop 01 e turbine seu estilo.</p>
          <button onclick="StoreApp.closeCartDrawer()" class="mt-6 px-6 py-2 btn-neon-cyan rounded-lg text-xs font-bold">
            Ver Produtos
          </button>
        </div>
      `;
      if (subtotalEl) subtotalEl.textContent = this.formatPrice(0, 0);
      if (shippingEl) shippingEl.textContent = this.formatPrice(0, 0);
      if (totalEl) totalEl.textContent = this.formatPrice(0, 0);
      return;
    }

    // Render items list
    container.innerHTML = this.cart.map((item, idx) => {
      const priceFormatted = this.formatPrice(item.price_brl, item.price_usd);
      return `
        <div class="flex items-center gap-3 py-3 border-b border-gray-800/60">
          <img src="${item.image}" alt="${item.title}" class="h-14 w-14 rounded-lg bg-gray-900 object-cover border border-gray-800">
          <div class="flex-1 min-w-0">
            <h4 class="text-xs font-bold text-white truncate">${item.title}</h4>
            <div class="flex items-center gap-2 mt-0.5">
              <span class="text-[11px] text-gray-400">Tam: <strong class="text-white">${item.size}</strong></span>
              <span class="text-xs font-extrabold text-neon-pink">${priceFormatted}</span>
            </div>
            <div class="flex items-center gap-2 mt-2">
              <button onclick="StoreApp.updateCartItemQty(${idx}, -1)" class="h-6 w-6 rounded bg-gray-800 text-white flex items-center justify-center text-xs hover:bg-gray-700">-</button>
              <span class="text-xs font-bold text-white px-1">${item.quantity}</span>
              <button onclick="StoreApp.updateCartItemQty(${idx}, 1)" class="h-6 w-6 rounded bg-gray-800 text-white flex items-center justify-center text-xs hover:bg-gray-700">+</button>
            </div>
          </div>
          <button onclick="StoreApp.removeCartItem(${idx})" class="p-1.5 text-gray-500 hover:text-red-400 transition-colors" title="Remover item">
            ✕
          </button>
        </div>
      `;
    }).join('');

    // Totals calculations
    const totals = window.CheckoutSimulator
      ? window.CheckoutSimulator.calculateTotals(this.cart, this.currency, this.coupon)
      : { subtotal: 0, couponDiscount: 0, netSubtotal: 0, shippingFee: 0, isFreeShipping: false, totalBeforePix: 0 };

    const symbol = this.currency === 'BRL' ? 'R$ ' : '$ ';
    const threshold = this.currency === 'BRL' ? 199.00 : 50.00;

    // Free shipping bar update
    if (freeShippingBar && freeShippingText) {
      const remaining = Math.max(0, threshold - totals.netSubtotal);
      const percent = Math.min(100, Math.round((totals.netSubtotal / threshold) * 100));
      freeShippingBar.style.width = `${percent}%`;

      if (totals.isFreeShipping) {
        freeShippingText.innerHTML = '🎉 <strong class="text-neon-green">PARABÉNS! VOCÊ GANHOU FRETE GRÁTIS!</strong>';
        freeShippingBar.className = 'h-2 rounded-full bg-neon-green transition-all duration-500';
      } else {
        freeShippingText.innerHTML = `Faltam apenas <strong class="text-white">${symbol}${remaining.toFixed(2)}</strong> para <strong>FRETE GRÁTIS</strong>!`;
        freeShippingBar.className = 'h-2 rounded-full bg-gradient-to-r from-neon-pink to-neon-cyan transition-all duration-500';
      }
    }

    if (subtotalEl) subtotalEl.textContent = `${symbol}${totals.subtotal.toFixed(2)}`;
    if (shippingEl) {
      shippingEl.textContent = totals.isFreeShipping ? 'GRÁTIS' : `${symbol}${totals.shippingFee.toFixed(2)}`;
      shippingEl.className = totals.isFreeShipping ? 'font-bold text-neon-green' : 'text-white';
    }
    if (discountEl) {
      if (totals.couponDiscount > 0) {
        discountEl.textContent = `- ${symbol}${totals.couponDiscount.toFixed(2)}`;
        discountEl.parentElement.classList.remove('hidden');
      } else {
        discountEl.parentElement.classList.add('hidden');
      }
    }
    if (totalEl) totalEl.textContent = `${symbol}${totals.totalBeforePix.toFixed(2)}`;
  },

  initCountdownTimer() {
    const timerEl = document.getElementById('countdown-timer');
    if (!timerEl) return;

    // Ticking 24h countdown
    let secondsLeft = 14 * 3600 + 23 * 60 + 45;
    setInterval(() => {
      const h = Math.floor(secondsLeft / 3600);
      const m = Math.floor((secondsLeft % 3600) / 60);
      const s = secondsLeft % 60;
      timerEl.textContent = `${String(h).padStart(2, '0')}h : ${String(m).padStart(2, '0')}m : ${String(s).padStart(2, '0')}s`;
      if (secondsLeft > 0) secondsLeft--;
    }, 1000);
  },

  setupEventListeners() {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        this.searchQuery = e.target.value.trim();
        this.renderProductGrid();
      });
    }
  }
};

// Global export for HTML callbacks
window.StoreApp = StoreApp;

// Auto-boot on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  StoreApp.init();
});
