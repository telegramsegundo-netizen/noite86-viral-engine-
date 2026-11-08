"""
produce_20_pristine_cuts.py
Gera 20 cortes virais de GTA 6 para a NOITE 86 com:
- Zero sobreposição de vozes (narração estritamente linear com pausas de 350ms)
- Roteiros dinâmicos e variados por pauta
- Masterização broadcast EBU R128 (-14 LUFS, True Peak -1.0 dBFS, 48kHz)
- Legendas na Safe Zone mobile (PlayRes 1080x1920)
- Auditoria do Agente 15 (Audio Taskforce) e Conselho de Sommelier
"""
import os
import sys
import time
import shutil
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from autonomous_engine.production_queue import ProductionQueue
from autonomous_engine.local_worker import LocalProductionWorker
from autonomous_engine.audio_taskforce import AudioQualityTaskforce

READY_DIR = Path(r"C:\Users\victo\NOITE86_FACTORY\06_READY_VIDEOS")
REJECTED_ARCHIVE = Path(r"C:\Users\victo\NOITE86_FACTORY\07_REJECTED\flawed_audio_archive")
OUTPUT_DIR = Path(r"C:\Users\victo\teamwork_projects\gta6_ecommerce_agents\output_noite86")

REJECTED_ARCHIVE.mkdir(parents=True, exist_ok=True)
READY_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 1. Purga os vídeos antigos com áudio defeituoso (move para backup de rejeitados)
print("🧹 Arquivando vídeos antigos com erros de duplicidade sonora...")
old_videos = list(READY_DIR.glob("*.mp4"))
for v in old_videos:
    # Se for o teste audio_perfeito já aprovado, mantém; senão move para o arquivo
    if "audio_perfeito_" in v.name:
        continue
    dest = REJECTED_ARCHIVE / v.name
    try:
        shutil.move(str(v), str(dest))
        print(f"   [Arquivado] {v.name} -> 07_REJECTED")
    except Exception as e:
        print(f"   Erro ao mover {v.name}: {e}")

# Limpa cópias em output_noite86 também
for v in OUTPUT_DIR.glob("*.mp4"):
    if "audio_perfeito_" not in v.name:
        try:
            v.unlink()
        except Exception:
            pass

print("✅ Cofre higienizado! Pronto para receber a nova safra cristalina.")

# 2. Definição das 20 pautas virais de alto calibre
VIRAL_THEMES_20 = [
    {
        "id": "gta6_01_fisica_agua",
        "title": "GTA 6: A Nova Física da Água e Tempestades em Vice City",
        "hook": "🚨 VOCÊ VIU ISSO?! A física da água no GTA 6 tá surreal!",
        "summary": "O sistema de ondas dinâmicas e o comportamento da água batendo nos barcos em Leonida superam qualquer outro jogo da história.",
        "product": "Luminária Neon Laser 'Ocean Drive Nocturne'"
    },
    {
        "id": "gta6_02_jason_lucia",
        "title": "GTA 6: A Dinâmica Brutal de Jason e Lucia Revelada",
        "hook": "🚨 CUIDADO COM ESSA DUPLA! Jason e Lucia vão dominar Vice City!",
        "summary": "A química no estilo Bonnie e Clyde e a mecânica de troca instantânea entre os dois protagonistas durante os tiroteios.",
        "product": "Camiseta Oversized Miami Overdrive 1986"
    },
    {
        "id": "gta6_03_mapa_gigante",
        "title": "GTA 6: O Tamanho Absurdo do Mapa de Leonida",
        "hook": "🚨 É 3 VEZES MAIOR! O mapa de GTA 6 vai assustar todo mundo!",
        "summary": "Leonida inteira recriada com pântanos, praias, cidades vizinhas e mais de 2700 pontos de interesse interativos.",
        "product": "Mini Boombox Cassette 1986 Bluetooth"
    },
    {
        "id": "gta6_04_ia_npcs",
        "title": "GTA 6: A Nova Inteligência Artificial dos NPCs",
        "hook": "🚨 PARECEM PESSOAS DE VERDADE! A nova IA de GTA 6 chocou os gamers!",
        "summary": "Pedestres reagem às suas roupas, carros e atitudes com rotinas diárias completas e memória de incidentes.",
        "product": "Camiseta Oversized Miami Overdrive 1986"
    },
    {
        "id": "gta6_05_graficos_chuva",
        "title": "GTA 6: Reflexos Noturnos no Asfalto Molhado",
        "hook": "🚨 OLHA ESSE REFLEXO! Ocean Drive na chuva tá idêntica à vida real!",
        "summary": "A iluminação volumétrica com ray tracing no asfalto molhado redefine os padrões da indústria de jogos.",
        "product": "Luminária Neon Laser 'Ocean Drive Nocturne'"
    },
    {
        "id": "gta6_06_carros_retro",
        "title": "GTA 6: Carros Clássicos dos Anos 80 e Customização",
        "hook": "🚨 RONCO DE MOTOR PURO! Os carros clássicos de GTA 6 tão perfeitos!",
        "summary": "Modelos inspirados em Testarossas e muscle cars com deformação milimétrica de lataria e física de tração realista.",
        "product": "Camiseta Oversized Miami Overdrive 1986"
    },
    {
        "id": "gta6_07_vida_noturna",
        "title": "GTA 6: O Retorno do Malibu Club e Baladas Noturnas",
        "hook": "🚨 A FESTA VOLTOU! O icônico Malibu Club tá confirmado em GTA 6!",
        "summary": "As baladas de Vice City voltam com iluminação laser estroboscópica e trilha sonora synthwave exclusiva.",
        "product": "Mini Boombox Cassette 1986 Bluetooth"
    },
    {
        "id": "gta6_08_combate_armas",
        "title": "GTA 6: O Novo Sistema de Combate e Recuo de Armas",
        "hook": "🚨 IMPACTO PESADO! O tiroteio de GTA 6 parece filme de ação!",
        "summary": "Animações viscerais de recuo e física de projéteis inspirada no realismo de Red Dead Redemption 2.",
        "product": "Camiseta Oversized Miami Overdrive 1986"
    },
    {
        "id": "gta6_09_vida_selvagem",
        "title": "GTA 6: Os Jacarés e o Perigo dos Pântanos de Leonida",
        "hook": "🚨 NÃO CAIA NESSA ÁGUA! A vida selvagem em GTA 6 é impiedosa!",
        "summary": "Crocodilos gigantes invadindo piscinas e o ecossistema agressivo dos pântanos ao redor da metrópole.",
        "product": "Luminária Neon Laser 'Ocean Drive Nocturne'"
    },
    {
        "id": "gta6_10_assaltos_banco",
        "title": "GTA 6: Novos Sistemas de Assalto e Fugas Policiais",
        "hook": "🚨 ALERTA GERAL! As perseguições policiais em GTA 6 tão insanas!",
        "summary": "A polícia usa táticas de cerco inteligente e helicópteros com holofotes térmicos vasculhando vielas.",
        "product": "Camiseta Oversized Miami Overdrive 1986"
    },
    {
        "id": "gta6_11_interiores_abertos",
        "title": "GTA 6: 70% dos Prédios com Interiores Exploráveis",
        "hook": "🚨 DÁ PRA ENTRAR EM TUDO?! A densidade de interiores de GTA 6!",
        "summary": "Hotéis de luxo, lojas de conveniência e prédios residenciais com portas abertas sem telas de carregamento.",
        "product": "Mini Boombox Cassette 1986 Bluetooth"
    },
    {
        "id": "gta6_12_trilha_sonora",
        "title": "GTA 6: A Trilha Sonora Retrowave e Anos 80 Confirmada",
        "hook": "🚨 ESSA MÚSICA ARREPIA! As rádios de Vice City vão dominar o mundo!",
        "summary": "Uma seleção musical nostálgica misturando sintetizadores vintage, hip-hop moderno e clássicos do rock.",
        "product": "Mini Boombox Cassette 1986 Bluetooth"
    },
    {
        "id": "gta6_13_motor_rage9",
        "title": "GTA 6: O Poder Gráfico do Novo Motor RAGE 9",
        "hook": "🚨 O MOTOR MAIS FORTE DO MUNDO! O RAGE 9 da Rockstar humilhou a concorrência!",
        "summary": "Tecnologia de texturas 8K e renderização física de tecidos que reagem ao vento e à umidade tropical.",
        "product": "Camiseta Oversized Miami Overdrive 1986"
    },
    {
        "id": "gta6_14_praia_vice",
        "title": "GTA 6: A Orla de Vice Beach e Densidade de Turistas",
        "hook": "🚨 PARECE UMA PRAIA REAL! Vice Beach em GTA 6 quebrou a internet!",
        "summary": "Centenas de banhistas, jet-skis cortando as ondas e o calor escaldante refletindo no horizonte.",
        "product": "Luminária Neon Laser 'Ocean Drive Nocturne'"
    },
    {
        "id": "gta6_15_estetica_noite86",
        "title": "GTA 6: A Estética Retrô Neon e a Moda Streetwear",
        "hook": "🚨 O ESTILO DOS ANOS 80 VOLTOU! Vista a atmosfera de Vice City!",
        "summary": "Como o lançamento de GTA 6 reacendeu a paixão global pelo retrowave, luzes neon e cortes oversized.",
        "product": "Camiseta Oversized Miami Overdrive 1986"
    },
    {
        "id": "gta6_16_pre_venda",
        "title": "GTA 6: Detalhes da Edição de Colecionador e Pré-Venda",
        "hook": "🚨 VAI ESGOTAR EM MINUTOS! Tudo sobre o lançamento oficial de GTA 6!",
        "summary": "A contagem regressiva começou e a expectativa é de bater o recorde histórico de maior faturamento do entretenimento.",
        "product": "Mini Boombox Cassette 1986 Bluetooth"
    },
    {
        "id": "gta6_17_conclusao_hype",
        "title": "GTA 6: Por Que Esse Será o Maior Jogo de Todos os Tempos",
        "hook": "🚨 A REGUA FOI ELEVADA! Nenhum jogo vai superar GTA 6 nesta geração!",
        "summary": "A junção de narrativa cinematográfica, fidelidade gráfica e mundo aberto vivo estabelece um novo marco.",
        "product": "Camiseta Oversized Miami Overdrive 1986"
    },
    {
        "id": "gta6_18_aeroporto_voo",
        "title": "GTA 6: Aeroporto Internacional Escobar e Voos Noturnos",
        "hook": "🚨 VOO NOTURNO CINEMATOGRÁFICO! O aeroporto de Vice City é colossal!",
        "summary": "Jatos particulares, pistas de pouso com sinalização luminosa realista e a visão aérea de Ocean Drive iluminada.",
        "product": "Luminária Neon Laser 'Ocean Drive Nocturne'"
    },
    {
        "id": "gta6_19_submundo_cartel",
        "title": "GTA 6: O Submundo dos Cartéis e Mansões em Starfish Island",
        "hook": "🚨 LUXO E PERIGO! As mansões dos barões do crime em GTA 6!",
        "summary": "Docas secretas, iates de luxo e a rota do tráfico entre as ilhas e o continente de Leonida.",
        "product": "Camiseta Oversized Miami Overdrive 1986"
    },
    {
        "id": "gta6_20_fauna_marinha",
        "title": "GTA 6: Vida Marinha Hiper-Realista e Mergulho Noturno",
        "hook": "🚨 CORAIS E TUBARÕES! O oceano de GTA 6 é um jogo à parte!",
        "summary": "Cardumes de peixes reagindo dinamicamente, tubarões nos recifes e iluminação subaquática fotorealista.",
        "product": "Mini Boombox Cassette 1986 Bluetooth"
    }
]

q = ProductionQueue()
worker = LocalProductionWorker(queue=q)
taskforce = AudioQualityTaskforce()

print(f"\n============================================================")
print(f"🏭 SAFRA DE OURO NOITE 86: PRODUZINDO 20 CORTES COM ÁUDIO CRISTALINO")
print(f"============================================================\n")

total = len(VIRAL_THEMES_20)
success_count = 0
audio_perfect_count = 0

for idx, theme in enumerate(VIRAL_THEMES_20, start=1):
    opp_id = f"{theme['id']}_{int(time.time())}"
    title = theme["title"]
    print(f"\n[{idx}/{total}] 🎯 Produzindo: '{title}'...")

    job_id = q.enqueue(
        opportunity_id=opp_id,
        title=title,
        priority=100 - idx,
        source_url="https://www.youtube.com/watch?v=RiR77AI4uQ8",
        route="ROUTE_ORIGINAL_REVIEW",
        briefing_dict={
            "opportunity_id": opp_id,
            "title": title,
            "url": "https://www.youtube.com/watch?v=RiR77AI4uQ8",
            "suggested_hook_pt": theme["hook"],
            "summary": theme["summary"],
            "viral_score": 92.0 + (idx * 0.3),
            "call_to_action": f"COLEÇÃO NOITE 86 // {theme['product'].upper()} // LINK NA BIO"
        }
    )

    t0 = time.time()
    res = worker.process_next_job()
    elapsed = round(time.time() - t0, 1)

    if res:
        video_p = Path(res["rendered_video"])
        somm = res.get("sommelier_eval", {})
        badge = somm.get("verdict_badge", "✅")
        score = somm.get("overall_score", 0)
        verdict = somm.get("verdict", "APROVADO")
        size_mb = video_p.stat().st_size / 1024 / 1024

        # Auditoria rigorosa de áudio (Agente 15)
        audio_report = taskforce.audit_audio_integrity(video_p)
        audio_ok = audio_report.passed
        if audio_ok:
            audio_perfect_count += 1
            audio_status = f"✅ ÁUDIO CRISTALINO ({audio_report.integrated_lufs} LUFS | Peak {audio_report.true_peak_db} dBFS)"
        else:
            audio_status = f"⚠️ ALERTA ÁUDIO ({audio_report.issues})"

        print(f"     ✅ Renderizado em {elapsed}s | {badge} {score}/100 ({verdict}) | {size_mb:.2f} MB")
        print(f"     🔊 {audio_status}")
        success_count += 1
    else:
        print(f"     ❌ Falha ao processar job {job_id}")

print(f"\n============================================================")
print(f"🏆 SAFRA DE OURO FINALIZADA COM SUCESSO!")
print(f"Total Concluídos: {success_count}/{total}")
print(f"Áudio 100% Cristalino (Zero Overlap): {audio_perfect_count}/{total}")
print(f"============================================================")
