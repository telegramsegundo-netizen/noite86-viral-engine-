"""
agents/content_clipper.py - Autonomous Content Clipper & Social Campaign Agent
Ingests localized video clips and catalog metadata, generates 0-3s viral hooks,
high-energy PT-BR copy formulas, 3-tier hashtag matrix, 7-day 21-post omnichannel schedule,
and conversion CTAs tied to catalog products. Outputs valid social_campaign.json and campaign_calendar.md.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CATALOG_PATH = PROJECT_ROOT / "catalog" / "products.json"
CAMPAIGNS_DIR = PROJECT_ROOT / "campaigns"
OUTPUT_CAMPAIGN_JSON = CAMPAIGNS_DIR / "social_campaign.json"
OUTPUT_CALENDAR_MD = CAMPAIGNS_DIR / "campaign_calendar.md"


class ContentClipperAgent:
    """
    Content Clipper & Campaign Agent for Vice District.
    Produces high-converting viral social funnels across TikTok, Instagram Reels, and YouTube Shorts.
    """

    def __init__(self, mock_mode: bool = True, api_key: Optional[str] = None):
        self.mock_mode = mock_mode
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.prompt_template_path = PROJECT_ROOT / "agents" / "templates" / "content_clipper_prompt.txt"

    def _load_catalog_skus(self, catalog_path: Optional[Path | str] = None) -> List[Dict[str, Any]]:
        path = Path(catalog_path) if catalog_path else DEFAULT_CATALOG_PATH
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("products", [])
            except Exception:
                pass
        return []

    def generate_campaign(
        self,
        clips_input: Optional[List[Dict[str, Any]]] = None,
        catalog_path: Optional[Path | str] = None,
    ) -> Dict[str, Any]:
        """
        Generate full 7-day 21-post omnichannel campaign schedule.
        """
        products = self._load_catalog_skus(catalog_path)
        valid_skus = [p.get("sku") or p.get("id") for p in products] if products else [
            "VC-APP-001", "VC-APP-002", "VC-APP-003", "VC-APP-004",
            "VC-LGT-001", "VC-AUD-001", "VC-NOQ-001", "VC-DRK-001",
            "VC-AUT-001", "VC-EDC-001", "VC-DSK-001", "VC-EYE-001",
        ]

        sku_titles = {
            (p.get("sku") or p.get("id")): p.get("title", "") for p in products
        }

        # 21 post definitions across 7 days, 3 slots per day:
        # Slot 1: 12:30 (Lunch break - Curiosity/Breakdown)
        # Slot 2: 18:15 (Commute - High Energy Lore & Aesthetic)
        # Slot 3: 21:30 (Prime Evening - Unboxing & Direct Offer)

        post_templates = [
            # Dia 1
            {
                "day": "Dia 1",
                "time_slot": "12:30",
                "platform": "TikTok",
                "content_type": "Viral Clip Breakdown",
                "hook_text": "Você percebeu esse detalhe sinistro no mapa de Leonida?",
                "audio_suggestion": "Synthwave Synth Bassline Slowed & Reverb",
                "caption_pt": (
                    "Se liga nos mínimos detalhes desse trailer em Vice Coast! A atmosfera retrô dos anos 80 tá surreal demais. "
                    "Qual detalhe mais te hypou? Comenta aqui embaixo! 👇\n\n"
                    "Drop 01 da coleção física disponível no link da bio. Use o cupom VICE10 para 10% OFF!"
                ),
                "hashtags": ["#ViceCity", "#Leonida", "#ViceCoast", "#SynthwaveBrasil", "#GamingBrasil", "#ModaGamer"],
                "sku_index": 2,  # VC-APP-003
                "cta_text": "Garanta a Camiseta Oversized 'Miami Overdrive' no link da bio!",
            },
            {
                "day": "Dia 1",
                "time_slot": "18:15",
                "platform": "Instagram Reels",
                "content_type": "Aesthetic Showcase",
                "hook_text": "POV: Você acabou de chegar em Vice City em 1986...",
                "audio_suggestion": "Kavinsky - Nightcall (Vice Ambient Remix)",
                "caption_pt": (
                    "A estética Miami anos 80 é simplesmente insubstituível. Cores neon, palmeiras e noites elétricas. "
                    "Montamos esse setup definitivo com o Deskmat XXL e iluminação cyberpunk. O que achou dessa vibe?\n\n"
                    "Peças exclusivas com frete grátis acima de R$ 199. Link na bio!"
                ),
                "hashtags": ["#MiamiViceAesthetic", "#SetupGamer", "#BattlestationBrasil", "#RetroWave", "#Outrun"],
                "sku_index": 10,  # VC-DSK-001
                "cta_text": "Confira o Deskmat XXL Midnight Tropic na loja!",
            },
            {
                "day": "Dia 1",
                "time_slot": "21:30",
                "platform": "TikTok",
                "content_type": "Product Unboxing",
                "hook_text": "Parece uma lata de refri comum dos anos 80, mas olha embaixo...",
                "audio_suggestion": "Trap Beat Lo-Fi Vice",
                "caption_pt": (
                    "Essa lata secreta com compartimento antifurto é a coisa mais insana que você vai ver hoje! "
                    "Peso real de 355ml e fundo rosqueável indetectável. Perfeito para guardar suas chaves e segredos. 🤫🔥\n\n"
                    "Apenas 50 unidades no primeiro lote. Cupom VICE10 ativo!"
                ),
                "hashtags": ["#AchadosShopee", "#ViralTikTok", "#SecretStash", "#ViceDistrict", "#Colecionavel"],
                "sku_index": 6,  # VC-NOQ-001
                "cta_text": "Pegue a sua Lata Stash Can com 5% OFF no PIX no link da bio!",
            },
            # Dia 2
            {
                "day": "Dia 2",
                "time_slot": "12:30",
                "platform": "YouTube Shorts",
                "content_type": "Viral Clip Breakdown",
                "hook_text": "Os easter eggs que quase ninguém viu nas praias de Leonida!",
                "audio_suggestion": "Retro Synth Darksynth Wave",
                "caption_pt": (
                    "Analisamos quadro a quadro a cena da orla de Ocean Drive. As referências culturais dos anos 80 estão em todo lugar! "
                    "Qual seu local favorito de Vice City? Fala nos comentários! 🌴\n\n"
                    "Conheça a coleção oficial de streetwear retrô inspirada em Vice District."
                ),
                "hashtags": ["#ViceCity", "#GamerLife", "#Leonida", "#ShortsBrasil", "#ModaStreetwear"],
                "sku_index": 0,  # VC-APP-001
                "cta_text": "Vista a Camisa Resort Vice Sunset - toque de seda!",
            },
            {
                "day": "Dia 2",
                "time_slot": "18:15",
                "platform": "TikTok",
                "content_type": "Aesthetic Showcase",
                "hook_text": "Só quem viveu os anos 80 sabe o que significa essa jaqueta...",
                "audio_suggestion": "Synthpop 80s Electric Drums",
                "caption_pt": (
                    "Jaqueta Bomber Reversível Holográfica: de um lado brilho dicróico ciano e magenta, do outro navy profundo tático. "
                    "Bordado de alta precisão com 40 mil pontos. É arte de vestir!\n\n"
                    "Edição limitada com frete grátis e desconto no PIX."
                ),
                "hashtags": ["#StreetwearBrasil", "#BomberJacket", "#Holographic", "#ModaMasculina", "#DropLimitado"],
                "sku_index": 1,  # VC-APP-002
                "cta_text": "Garanta a Jaqueta Neon Mirage no link da bio!",
            },
            {
                "day": "Dia 2",
                "time_slot": "21:30",
                "platform": "Instagram Reels",
                "content_type": "Drop Announcement",
                "hook_text": "Alerta de Drop: O Underground Syndicate Kit liberou agora!",
                "audio_suggestion": "Cyberpunk 2080 Synth Bass",
                "caption_pt": (
                    "O combo mais cobiçado de Leonida acabou de pousar no site: Jaqueta Bomber + Lata Secreta + Chaveiro Pelican Bay. "
                    "Economize mais de 15% levando o combo completo. E ainda rola 5% extra no PIX! 🔥⚡\n\n"
                    "Estoque extremamente limitado. Não perca!"
                ),
                "hashtags": ["#DropExclusivo", "#StreetwearOutfit", "#ViceCity", "#ModaGamer", "#Promoção"],
                "sku_index": 1,  # VC-APP-002
                "cta_text": "Acesse a loja e garanta seu Syndicate Kit antes que zere!",
            },
            # Dia 3
            {
                "day": "Dia 3",
                "time_slot": "12:30",
                "platform": "TikTok",
                "content_type": "Viral Clip Breakdown",
                "hook_text": "Essa cena de perseguição noturna mudou tudo que sabemos!",
                "audio_suggestion": "80s Chase Synthwave Beat",
                "caption_pt": (
                    "A física dos carros e os reflexos neon no asfalto molhado de Leonida estão inacreditáveis. "
                    "Se você é fã de carros clássicos esportivos dos anos 80, esse visual é um prato cheio. Curtiram? 🏎️💨\n\n"
                    "Estampa exclusiva do esportivo clássico na bio!"
                ),
                "hashtags": ["#CarrosAntigos", "#ViceCoast", "#NeonVibes", "#GamerBrasil", "#GamerLife"],
                "sku_index": 2,  # VC-APP-003
                "cta_text": "Confira a camiseta 260 GSM Miami Overdrive no site!",
            },
            {
                "day": "Dia 3",
                "time_slot": "18:15",
                "platform": "YouTube Shorts",
                "content_type": "Product Unboxing",
                "hook_text": "Essa luminária neon vai transformar seu setup para sempre!",
                "audio_suggestion": "Chill Lofi Synth Sunset",
                "caption_pt": (
                    "Acrílico óptico cortado a laser com gravação de Ocean Drive e base de alumínio anodizado. "
                    "Cores ciano e magenta com controle touch e controle remoto sem fio. Deixa qualquer quarto com clima de hotel retrô.\n\n"
                    "Use o cupom VICE10 para 10% de desconto!"
                ),
                "hashtags": ["#SetupGamer", "#DecoracaoQuarto", "#LuminariaNeon", "#ShortsBrasil", "#Synthwave"],
                "sku_index": 4,  # VC-LGT-001
                "cta_text": "Compre a Luminária Ocean Drive Nocturne na bio!",
            },
            {
                "day": "Dia 3",
                "time_slot": "21:30",
                "platform": "Instagram Reels",
                "content_type": "Aesthetic Showcase",
                "hook_text": "Como se vestir como o rei do submundo de Miami sem parecer fantasia",
                "audio_suggestion": "Nu-Disco Midnight Vibes",
                "caption_pt": (
                    "O segredo do estilo Vice City está no equilíbrio: camisa resort fluida com corte boxy, boné de veludo cotelê "
                    "e óculos aviador degradê rosé. Sofisticado, nostálgico e marcante. 🔥\n\n"
                    "Monte seu visual noturno completo no link da bio com frete grátis!"
                ),
                "hashtags": ["#ModaMasculina", "#OOTDBrasil", "#EstiloRetro", "#MiamiVice", "#Streetwear"],
                "sku_index": 11,  # VC-EYE-001
                "cta_text": "Veja os Óculos Polarizados Palm Mirage na bio!",
            },
            # Dia 4
            {
                "day": "Dia 4",
                "time_slot": "12:30",
                "platform": "TikTok",
                "content_type": "Viral Clip Breakdown",
                "hook_text": "O que ninguém te contou sobre a trilha sonora de Vice Coast!",
                "audio_suggestion": "Synthwave Saxophone Solo",
                "caption_pt": (
                    "Dos clássicos do synthpop até as batidas eletrônicas noturnas, o som dessa cidade molda toda a cultura. "
                    "Para ouvir suas playlists com estilo autêntico, criamos esse speaker retrô em formato de boombox de fita cassete! 📻🎶\n\n"
                    "Som de alta fidelidade com bateria de 10 horas."
                ),
                "hashtags": ["#Musica80s", "#RetroTech", "#Boombox", "#ViceCity", "#GamerBrasil"],
                "sku_index": 5,  # VC-AUD-001
                "cta_text": "Garanta a Caixa de Som Synthwave Boombox na bio!",
            },
            {
                "day": "Dia 4",
                "time_slot": "18:15",
                "platform": "Instagram Reels",
                "content_type": "Product Unboxing",
                "hook_text": "O chaveiro vintage do motel mais secreto de Ocean Drive...",
                "audio_suggestion": "Vintage Hotel Elevator Synth Lofi",
                "caption_pt": (
                    "Chaveiro losango Pelican Bay Motel '86 em acrílico translúcido seafoam com hot-foil dourado metálico. "
                    "Item colecionável exclusivo que dá um charme único ao seu molho de chaves ou mochila. ✨🗝️\n\n"
                    "Custa menos de R$ 40 e tem 5% de desconto no PIX!"
                ),
                "hashtags": ["#EDCBrasil", "#KeytagVintage", "#AchadosDoDia", "#AcessoriosMasculinos", "#RetroAesthetic"],
                "sku_index": 9,  # VC-EDC-001
                "cta_text": "Adicione o Chaveiro Pelican Bay ao seu carrinho na bio!",
            },
            {
                "day": "Dia 4",
                "time_slot": "21:30",
                "platform": "TikTok",
                "content_type": "Aesthetic Showcase",
                "hook_text": "Seu carro merece ter o cheiro do verão de Miami em 1986!",
                "audio_suggestion": "Vaporwave Ocean Breeze Loop",
                "caption_pt": (
                    "Trio de aromatizantes Sunburst Palm: essência pura de coco tostado, baunilha e brisa oceânica. "
                    "Formatos icônicos de chaveiro de motel, flamingos e cupê retrô. Dura até 45 dias perfumando seu cockpit! 🥥🌴\n\n"
                    "Kit com 3 unidades por apenas R$ 49,90. Link na bio!"
                ),
                "hashtags": ["#CarroRebaixado", "#EsteticaAutomotiva", "#Aromatizante", "#MiamiVibes", "#CarroEDC"],
                "sku_index": 8,  # VC-AUT-001
                "cta_text": "Peça o Trio de Aromatizantes Sunburst Palm na bio!",
            },
            # Dia 5
            {
                "day": "Dia 5",
                "time_slot": "12:30",
                "platform": "YouTube Shorts",
                "content_type": "Viral Clip Breakdown",
                "hook_text": "A evolução gráfica absurda da noite de Vice City!",
                "audio_suggestion": "Dark Synthwave Tension",
                "caption_pt": (
                    "Comparando a névoa, a iluminação volumétrica dos postes e as poças d'água no asfalto com a versão clássica. "
                    "A sensação de nostalgia com gráficos da nova geração é indescritível. Concorda? Deixe sua opinião! 🏙️⚡\n\n"
                    "Coleção comemorativa com cupom VICE10 no link da bio."
                ),
                "hashtags": ["#GraficosSurreais", "#ViceCity", "#ShortsBrasil", "#GamingCommunity", "#GamerLife"],
                "sku_index": 0,  # VC-APP-001
                "cta_text": "Explore a coleção completa no link da bio!",
            },
            {
                "day": "Dia 5",
                "time_slot": "18:15",
                "platform": "TikTok",
                "content_type": "Drop Announcement",
                "hook_text": "Atenção: Metade das peças do Drop 01 já esgotou!",
                "audio_suggestion": "High Tempo Electronic Trap",
                "caption_pt": (
                    "A procura pelo Drop 01 de Vice District superou todas as expectativas. Restam poucas unidades de jaquetas e camisetas "
                    "nos tamanhos M e G. Produção sob demanda exclusiva sem reposição garantida! Corra antes que acabe. ⚠️⏳\n\n"
                    "Frete grátis para todo o Brasil acima de R$ 199."
                ),
                "hashtags": ["#UltimasPecas", "#DropLimitado", "#StreetwearBrasil", "#ModaGamer", "#ViceDistrict"],
                "sku_index": 1,  # VC-APP-002
                "cta_text": "Acesse agora a loja e garanta suas peças!",
            },
            {
                "day": "Dia 5",
                "time_slot": "21:30",
                "platform": "Instagram Reels",
                "content_type": "Product Unboxing",
                "hook_text": "Mantém sua bebida trincando por 24 horas no calor de Leonida!",
                "audio_suggestion": "Summer Chill Out Beach Beat",
                "caption_pt": (
                    "Copo Térmico Golden Hour Biscayne (900ml) em inox 18/8 com isolamento a vácuo e pintura eletrostática degradê magenta e âmbar. "
                    "Gravação a laser permanente de palmeiras retro-futuristas. Ideal para sua mesa de trabalho ou academia. 🧊🍹\n\n"
                    "Use o cupom VICE10 para 10% OFF!"
                ),
                "hashtags": ["#CopoTermico", "#SetupGamer", "#LifestyleGamer", "#Academia", "#BiscayneBay"],
                "sku_index": 7,  # VC-DRK-001
                "cta_text": "Garanta o Copo Térmico Biscayne na bio!",
            },
            # Dia 6
            {
                "day": "Dia 6",
                "time_slot": "12:30",
                "platform": "TikTok",
                "content_type": "Viral Clip Breakdown",
                "hook_text": "Os veículos secretos que você provavelmente perdeu no trailer!",
                "audio_suggestion": "Synth Wave Eurobeat Mashup",
                "caption_pt": (
                    "Motos esportivas clássicas, lanchas offshore com listras neon e helicópteros sobrevoando a marina de Leonida. "
                    "Qual veículo você vai pilotar primeiro assim que chegar em Vice Coast? Comenta aí! 🚤🚁\n\n"
                    "Camisas e acessórios da coleção com desconto especial no PIX."
                ),
                "hashtags": ["#VeiculosClassicos", "#ViceCity", "#GamerLife", "#Leonida", "#GamerBrasil"],
                "sku_index": 3,  # VC-APP-004
                "cta_text": "Confira o Boné South Beach Syndicate na bio!",
            },
            {
                "day": "Dia 6",
                "time_slot": "18:15",
                "platform": "Instagram Reels",
                "content_type": "Aesthetic Showcase",
                "hook_text": "Transformei meu setup comum numa cobertura de luxo em Miami!",
                "audio_suggestion": "Synthwave Ambient Ocean Sunset",
                "caption_pt": (
                    "Combinação do Deskmat XXL Midnight Tropic com a Luminária Laser Ocean Drive e o Mini Boombox. "
                    "O clima noturno perfeito para maratonar gameplays e trabalhar com estilo. O que achou dessa transformação?\n\n"
                    "Kit Setup VIP com mais de R$ 70 de desconto no site!"
                ),
                "hashtags": ["#SetupDosSonhos", "#Battlestation", "#Deskmats", "#DecoracaoGamer", "#Synthwave"],
                "sku_index": 10,  # VC-DSK-001
                "cta_text": "Veja o Ocean Drive Setup Pack na bio!",
            },
            {
                "day": "Dia 6",
                "time_slot": "21:30",
                "platform": "YouTube Shorts",
                "content_type": "Product Unboxing",
                "hook_text": "O boné de veludo cotelê mais autêntico que você vai encontrar!",
                "audio_suggestion": "Lo-Fi Hip Hop Chill Beats",
                "caption_pt": (
                    "Boné South Beach Syndicate em veludo cotelê turquesa com bordado 3D puff rosa pastel e fecho de latão envelhecido. "
                    "Conforto premium e toque retrô que combina com qualquer outfit de rua. 🧢🔥\n\n"
                    "Enviamos para todo o Brasil com código de rastreio!"
                ),
                "hashtags": ["#BoneCotelê", "#StreetwearBrasil", "#ShortsBrasil", "#ModaMasculina", "#Acessorios"],
                "sku_index": 3,  # VC-APP-004
                "cta_text": "Peça o Boné South Beach Syndicate na bio!",
            },
            # Dia 7
            {
                "day": "Dia 7",
                "time_slot": "12:30",
                "platform": "TikTok",
                "content_type": "Viral Clip Breakdown",
                "hook_text": "Leonida é o mapa mais imersivo já criado na história dos games?",
                "audio_suggestion": "Synth Epic Cinematic Score",
                "caption_pt": (
                    "Pantanais selvagens com jacarés, arranha-céus reluzentes à beira-mar e bairros clandestinos cheios de neon. "
                    "A diversidade desse cenário vai redefinir o padrão dos jogos de mundo aberto. Tá preparado? 🐊🌴\n\n"
                    "Celebre o retorno a Vice City com peças exclusivas na bio."
                ),
                "hashtags": ["#MundoAberto", "#ViceCity", "#GamerBrasil", "#Leonida", "#Streetwear"],
                "sku_index": 0,  # VC-APP-001
                "cta_text": "Visite a loja oficial Vice District no link da bio!",
            },
            {
                "day": "Dia 7",
                "time_slot": "18:15",
                "platform": "YouTube Shorts",
                "content_type": "Aesthetic Showcase",
                "hook_text": "O look completo para a noite mais quente de Vice District!",
                "audio_suggestion": "Miami 1986 Synth Funk",
                "caption_pt": (
                    "Camisa Resort silk-touch + Óculos Aviador TAC Polarizado + Boné Cotelê. "
                    "Look impecável para curtir o fim de semana com a verdadeira atitude retrô anos 80. 🔥🕶️\n\n"
                    "Últimas horas para usar o cupom VICE10 com 10% de desconto."
                ),
                "hashtags": ["#LookDoDia", "#ModaMasculina", "#EstiloVintage", "#ShortsBrasil", "#Streetwear"],
                "sku_index": 11,  # VC-EYE-001
                "cta_text": "Monte seu outfit completo na bio!",
            },
            {
                "day": "Dia 7",
                "time_slot": "21:30",
                "platform": "TikTok",
                "content_type": "Drop Announcement",
                "hook_text": "ÚLTIMA CHAMADA: Encerramento oficial do Lote de Lançamento!",
                "audio_suggestion": "Countdown Dramatic Electronic Beat",
                "caption_pt": (
                    "O cronômetro do Lote 01 está zerando! Essa é sua chance final de garantir as peças exclusivas da coleção Vice District "
                    "com os preços promocionais e frete grátis antes da virada de lote. Não deixe para depois! ⏰🚨\n\n"
                    "Use o cupom VICE10 e finalize no PIX com mais 5% de desconto imediato."
                ),
                "hashtags": ["#UltimaChance", "#DropFinal", "#ViceDistrict", "#StreetwearBrasil", "#Promocao"],
                "sku_index": 1,  # VC-APP-002
                "cta_text": "Garanta suas peças antes do encerramento oficial na bio!",
            },
        ]

        # Assemble full schedule objects
        schedule = []
        for i, item in enumerate(post_templates):
            sku_idx = item["sku_index"] % len(valid_skus)
            linked_sku = valid_skus[sku_idx]
            platform_clean = item["platform"].replace(" ", "").lower()
            utm = f"https://vicedistrict.store/drop01?utm_source={platform_clean}&utm_medium=social&utm_campaign=vice_launch&sku={linked_sku}&coupon=VICE10"

            # If user provided clips, integrate the clip title or hook into first item
            hook = item["hook_text"]
            if clips_input and i < len(clips_input):
                custom_clip = clips_input[i]
                custom_hook = custom_clip.get("hook_pt") or custom_clip.get("hook")
                if custom_hook and len(custom_hook) > 10:
                    hook = custom_hook
                if custom_clip.get("recommended_sku") and custom_clip.get("recommended_sku") in valid_skus:
                    linked_sku = custom_clip["recommended_sku"]

            post_obj = {
                "post_id": f"post_{i+1:02d}",
                "day": item["day"],
                "time_slot": item["time_slot"],
                "platform": item["platform"],
                "content_type": item["content_type"],
                "hook_text": hook,
                "audio_suggestion": item["audio_suggestion"],
                "caption_pt": item["caption_pt"],
                "hashtags": item["hashtags"],
                "linked_product_sku": linked_sku,
                "linked_product_title": sku_titles.get(linked_sku, linked_sku),
                "cta_text": item["cta_text"],
                "utm_link": utm,
            }
            schedule.append(post_obj)

        campaign: Dict[str, Any] = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "campaign_name": "Vice District Drop 01 Launch Blitz",
            "coupon_code": "VICE10",
            "discount_percentage": 10.0,
            "total_posts": len(schedule),
            "target_region": "Brasil (Peak BRT Hours)",
            "cadence": "3 posts por dia (12:30, 18:15, 21:30)",
            "schedule": schedule,
        }

        # Write output files
        CAMPAIGNS_DIR.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_CAMPAIGN_JSON, "w", encoding="utf-8") as f:
            json.dump(campaign, f, indent=2, ensure_ascii=False)

        # Also save in root and agents if needed
        with open(PROJECT_ROOT / "social_campaign.json", "w", encoding="utf-8") as f:
            json.dump(campaign, f, indent=2, ensure_ascii=False)

        # Generate readable Markdown calendar
        self._write_markdown_calendar(campaign, OUTPUT_CALENDAR_MD)

        return campaign

    def _write_markdown_calendar(self, campaign: Dict[str, Any], output_path: Path):
        lines = [
            f"# {campaign.get('campaign_name', 'Social Campaign')} — 7-Day Omnichannel Calendar",
            "",
            f"**Cupom Oficial**: `{campaign.get('coupon_code', 'VICE10')}` ({campaign.get('discount_percentage', 10)}% OFF)",
            f"**Total de Publicações**: {campaign.get('total_posts', 21)} posts verticais",
            f"**Horários Nobres BRT**: 12:30 (Almoço), 18:15 (Trânsito), 21:30 (Relax Prime)",
            "",
            "---",
            "",
        ]

        current_day = None
        for post in campaign.get("schedule", []):
            if post["day"] != current_day:
                current_day = post["day"]
                lines.append(f"## {current_day}")
                lines.append("")

            lines.append(f"### [{post['time_slot']}] {post['platform']} — {post['content_type']} (`{post['post_id']}`)")
            lines.append(f"- **Hook (0-3s)**: *\"{post['hook_text']}\"*")
            lines.append(f"- **Áudio Recomendado**: `{post['audio_suggestion']}`")
            lines.append(f"- **Produto Vinculado**: `{post['linked_product_sku']}` ({post.get('linked_product_title', '')})")
            lines.append(f"- **Legenda**: {post['caption_pt']}")
            lines.append(f"- **Hashtags**: {' '.join(post['hashtags'])}")
            lines.append(f"- **Link / UTM**: [{post['cta_text']}]({post['utm_link']})")
            lines.append("")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def run(
        self,
        clips_input: Optional[List[Dict[str, Any]]] = None,
        catalog_path: Optional[Path | str] = None,
    ) -> Dict[str, Any]:
        """Orchestration execution entry point."""
        return self.generate_campaign(clips_input, catalog_path)


# Backward compatibility and alias
ContentClipper = ContentClipperAgent
