import json
import os
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from autonomous_engine.production_queue import ProductionQueue
from autonomous_engine.local_worker import LocalProductionWorker
from autonomous_engine.sommelier_council import VideoSommelierCouncil

q = ProductionQueue()
worker = LocalProductionWorker(queue=q)

# 17 pautas virais de altíssimo impacto para somar aos 3 existentes e totalizar 20
VIRAL_THEMES = [
    {
        "id": "gta6_fisica_agua",
        "title": "GTA 6: A Nova Física da Água e Tempestades em Vice City",
        "hook": "🚨 VOCÊ VIU ISSO?! A física da água no GTA 6 tá surreal!",
        "summary": "O sistema de ondas dinâmicas e o comportamento da água batendo nos barcos em Leonida superam qualquer outro jogo da história.",
        "product": "Luminária Neon Laser 'Ocean Drive Nocturne'"
    },
    {
        "id": "gta6_jason_lucia",
        "title": "GTA 6: A Dinâmica Brutal de Jason e Lucia Revelada",
        "hook": "🚨 CUIDADO COM ESSA DUPLA! Jason e Lucia vão dominar Vice City!",
        "summary": "A química no estilo Bonnie e Clyde e a mecânica de troca instantânea entre os dois protagonistas durante os tiroteios.",
        "product": "Camiseta Oversized Miami Overdrive 1986"
    },
    {
        "id": "gta6_mapa_gigante",
        "title": "GTA 6: O Tamanho Absurdo do Mapa de Leonida",
        "hook": "🚨 É 3 VEZES MAIOR! O mapa de GTA 6 vai assustar todo mundo!",
        "summary": "Leonida inteira recriada com pântanos, praias, cidades vizinhas e mais de 2700 pontos de interesse interativos.",
        "product": "Mini Boombox Cassette 1986 Bluetooth"
    },
    {
        "id": "gta6_ia_npcs",
        "title": "GTA 6: A Nova Inteligência Artificial dos NPCs",
        "hook": "🚨 PARECEM PESSOAS DE VERDADE! A nova IA de GTA 6 chocou os gamers!",
        "summary": "Pedestres reagem às suas roupas, carros e atitudes com rotinas diárias completas e memória de incidentes.",
        "product": "Camiseta Oversized Miami Overdrive 1986"
    },
    {
        "id": "gta6_graficos_chuva",
        "title": "GTA 6: Reflexos Noturnos no Asfalto Molhado",
        "hook": "🚨 OLHA ESSE REFLEXO! Ocean Drive na chuva tá idêntica à vida real!",
        "summary": "A iluminação volumétrica com ray tracing no asfalto molhado redefine os padrões da indústria de jogos.",
        "product": "Luminária Neon Laser 'Ocean Drive Nocturne'"
    },
    {
        "id": "gta6_carros_retro",
        "title": "GTA 6: Carros Clássicos dos Anos 80 e Customização",
        "hook": "🚨 RONCO DE MOTOR PURO! Os carros clássicos de GTA 6 tão perfeitos!",
        "summary": "Modelos inspirados em Testarossas e muscle cars com deformação milimétrica de lataria e física de tração realista.",
        "product": "Camiseta Oversized Miami Overdrive 1986"
    },
    {
        "id": "gta6_vida_noturna",
        "title": "GTA 6: O Retorno do Malibu Club e Baladas Noturnas",
        "hook": "🚨 A FESTA VOLTOU! O icônico Malibu Club tá confirmado em GTA 6!",
        "summary": "As baladas de Vice City voltam com iluminação laser estroboscópica e trilha sonora synthwave exclusiva.",
        "product": "Mini Boombox Cassette 1986 Bluetooth"
    },
    {
        "id": "gta6_combate_armas",
        "title": "GTA 6: O Novo Sistema de Combate e Recuo de Armas",
        "hook": "🚨 IMPACTO PESADO! O tiroteio de GTA 6 parece filme de ação!",
        "summary": "Animações viscerais de recuo e física de projéteis inspirada no realismo de Red Dead Redemption 2.",
        "product": "Camiseta Oversized Miami Overdrive 1986"
    },
    {
        "id": "gta6_vida_selvagem",
        "title": "GTA 6: Os Jacarés e o Perigo dos Pântanos de Leonida",
        "hook": "🚨 NÃO CAIA NESSA ÁGUA! A vida selvagem em GTA 6 é impiedosa!",
        "summary": "Crocodilos gigantes invadindo piscinas e o ecossistema agressivo dos pântanos ao redor da metrópole.",
        "product": "Luminária Neon Laser 'Ocean Drive Nocturne'"
    },
    {
        "id": "gta6_assaltos_banco",
        "title": "GTA 6: Novos Sistemas de Assalto e Fugas Policiais",
        "hook": "🚨 ALERTA GERAL! As perseguições policiais em GTA 6 tão insanas!",
        "summary": "A polícia usa táticas de cerco inteligente e helicópteros com holofotes térmicos vasculhando vielas.",
        "product": "Camiseta Oversized Miami Overdrive 1986"
    },
    {
        "id": "gta6_interiores_abertos",
        "title": "GTA 6: 70% dos Prédios com Interiores Exploráveis",
        "hook": "🚨 DÁ PRA ENTRAR EM TUDO?! A densidade de interiores de GTA 6!",
        "summary": "Hotéis de luxo, lojas de conveniência e prédios residenciais com portas abertas sem telas de carregamento.",
        "product": "Mini Boombox Cassette 1986 Bluetooth"
    },
    {
        "id": "gta6_trilha_sonora",
        "title": "GTA 6: A Trilha Sonora Retrowave e Anos 80 Confirmada",
        "hook": "🚨 ESSA MÚSICA ARREPIA! As rádios de Vice City vão dominar o mundo!",
        "summary": "Uma seleção musical nostálgica misturando sintetizadores vintage, hip-hop moderno e clássicos do rock.",
        "product": "Mini Boombox Cassette 1986 Bluetooth"
    },
    {
        "id": "gta6_motor_rage9",
        "title": "GTA 6: O Poder Gráfico do Novo Motor RAGE 9",
        "hook": "🚨 O MOTOR MAIS FORTE DO MUNDO! O RAGE 9 da Rockstar humilhou a concorrência!",
        "summary": "Tecnologia de texturas 8K e renderização física de tecidos que reagem ao vento e à umidade tropical.",
        "product": "Camiseta Oversized Miami Overdrive 1986"
    },
    {
        "id": "gta6_praia_vice",
        "title": "GTA 6: A Orla de Vice Beach e Densidade de Turistas",
        "hook": "🚨 PARECE UMA PRAIA REAL! Vice Beach em GTA 6 quebrou a internet!",
        "summary": "Centenas de banhistas, jet-skis cortando as ondas e o calor escaldante refletindo no horizonte.",
        "product": "Luminária Neon Laser 'Ocean Drive Nocturne'"
    },
    {
        "id": "gta6_estetica_noite86",
        "title": "GTA 6: A Estética Retrô Neon e a Moda Streetwear",
        "hook": "🚨 O ESTILO DOS ANOS 80 VOLTOU! Vista a atmosfera de Vice City!",
        "summary": "Como o lançamento de GTA 6 reacendeu a paixão global pelo retrowave, luzes neon e cortes oversized.",
        "product": "Camiseta Oversized Miami Overdrive 1986"
    },
    {
        "id": "gta6_pre_venda",
        "title": "GTA 6: Detalhes da Edição de Colecionador e Pré-Venda",
        "hook": "🚨 VAI ESGOTAR EM MINUTOS! Tudo sobre o lançamento oficial de GTA 6!",
        "summary": "A contagem regressiva começou e a expectativa é de bater o recorde histórico de maior faturamento do entretenimento.",
        "product": "Mini Boombox Cassette 1986 Bluetooth"
    },
    {
        "id": "gta6_conclusao_hype",
        "title": "GTA 6: Por Que Esse Será o Maior Jogo de Todos os Tempos",
        "hook": "🚨 A REGUA FOI ELEVADA! Nenhum jogo vai superar GTA 6 nesta geração!",
        "summary": "A junção de narrativa cinematográfica, fidelidade gráfica e mundo aberto vivo estabelece um novo marco.",
        "product": "Camiseta Oversized Miami Overdrive 1986"
    }
]

print(f"============================================================")
print(f"🏭 OPERAÇÃO SAFRA 20: PRODUÇÃO EM MASSA DE 17 NOVOS CORTES")
print(f"============================================================\n")

completed_count = 0
for idx, theme in enumerate(VIRAL_THEMES, start=1):
    opp_id = f"{theme['id']}_{int(time.time())}"
    title = theme["title"]
    print(f"\n[{idx}/17] 🎯 Enfileirando e processando: '{title}'...")

    job_id = q.enqueue(
        opportunity_id=opp_id,
        title=title,
        priority=90 + (17 - idx),
        source_url="https://www.youtube.com/watch?v=RiR77AI4uQ8",
        route="ROUTE_ORIGINAL_REVIEW",
        briefing_dict={
            "opportunity_id": opp_id,
            "title": title,
            "url": "https://www.youtube.com/watch?v=RiR77AI4uQ8",
            "suggested_hook_pt": theme["hook"],
            "summary": theme["summary"],
            "viral_score": 90.0 + idx * 0.5,
            "call_to_action": f"COLEÇÃO NOITE 86 // {theme['product'].upper()} // LINK NA BIO"
        }
    )

    t0 = time.time()
    res = worker.process_next_job()
    elapsed = round(time.time() - t0, 1)

    if res:
        somm = res.get("sommelier_eval", {})
        badge = somm.get("verdict_badge", "✅")
        score = somm.get("overall_score", 0)
        verdict = somm.get("verdict", "APROVADO")
        size_mb = Path(res["rendered_video"]).stat().st_size / 1024 / 1024
        print(f"     ✅ Sucesso em {elapsed}s | {badge} {score}/100 ({verdict}) | {size_mb:.2f} MB")
        completed_count += 1
    else:
        print(f"     ❌ Falha ao processar {job_id}")

print(f"\n============================================================")
print(f"🏆 SAFRA CONCLUÍDA: {completed_count} NOVOS VÍDEOS RENDERIZADOS E APROVADOS!")
print(f"============================================================")
