"""
video_pipeline/dashboard_server.py
NOITE 86 — VIRAL COMMAND CENTER V3.0
Painel Web Completo de Operações Autônomas 24/7.
Integração com Radar Internacional, Fila Persistente, Renderizador 9:16 e Vault de Vídeos.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# UTF-8 encoding no console Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, jsonify, request, send_from_directory, render_template_string

from autonomous_engine.commander import AutonomousCommander
from autonomous_engine.production_queue import ProductionQueue, JobStatus
from autonomous_engine.radar_engine import ViralRadarEngine
from autonomous_engine.viral_analyst import ViralIntelligenceAnalyst
from autonomous_engine.rights_clearance import RightsClearanceOfficer
from autonomous_engine.content_strategist import BrazilianContentStrategist
from autonomous_engine.local_worker import LocalProductionWorker
from video_pipeline.ffmpeg_resolver import get_ffmpeg_exe

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024  # 500 MB

UPLOAD_DIR = PROJECT_ROOT / "uploads"
OUTPUT_DIR = PROJECT_ROOT / "output_noite86"
STORAGE_BASE = Path(r"C:\Users\victo\NOITE86_FACTORY")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Instâncias globais da Operação
queue = ProductionQueue()
worker = LocalProductionWorker(queue=queue)
radar = ViralRadarEngine()
analyst = ViralIntelligenceAnalyst()
rights_officer = RightsClearanceOfficer()
strategist = BrazilianContentStrategist()
commander = AutonomousCommander()

# Estado de operação autônoma 24/7
operational_state = {
    "autonomous_loop_active": False,
    "last_radar_scan": None,
    "last_sync": datetime.now(timezone.utc).isoformat(),
    "items_discovered_count": 0,
    "active_workers": 1,
}

# Jobs manuais do endpoint /api/process
manual_jobs: Dict[str, Dict[str, Any]] = {}


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NOITE 86 — VIRAL COMMAND CENTER V3.0</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800;900&family=Inter:wght@300;400;500;600;700&display=swap');

  :root {
    --neon-pink: #FF2D78;
    --neon-cyan: #00F5FF;
    --neon-purple: #9B30FF;
    --neon-green: #00FF88;
    --bg-dark: #070714;
    --bg-card: #0E0E22;
    --bg-card-alt: #141432;
    --text-main: #EDEDFF;
    --text-muted: #7E7EA6;
    --border: rgba(0, 245, 255, 0.15);
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: var(--bg-dark);
    font-family: 'Inter', sans-serif;
    color: var(--text-main);
    min-height: 100vh;
    padding-bottom: 60px;
  }

  /* Grid background */
  body::before {
    content: '';
    position: fixed; inset: 0;
    background-image:
      linear-gradient(rgba(0, 245, 255, 0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0, 245, 255, 0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
  }

  .container { max-width: 1200px; margin: 0 auto; padding: 24px 20px; position: relative; z-index: 1; }

  /* Top Command Header */
  .header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 24px 30px;
    border: 1px solid var(--border);
    border-radius: 20px;
    background: linear-gradient(135deg, rgba(14,14,34,0.95), rgba(20,20,50,0.95));
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
  }
  .header::before {
    content: '';
    position: absolute; top: 0; left: -100%;
    width: 300%; height: 2px;
    background: linear-gradient(90deg, transparent, var(--neon-pink), var(--neon-cyan), transparent);
    animation: scan 4s linear infinite;
  }
  @keyframes scan { to { left: 100%; } }

  .logo-block h1 {
    font-family: 'Orbitron', sans-serif;
    font-size: 2.1rem;
    font-weight: 900;
    letter-spacing: 3px;
    background: linear-gradient(135deg, var(--neon-pink), var(--neon-cyan));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .logo-block p { color: var(--text-muted); font-size: 0.82rem; letter-spacing: 1px; margin-top: 4px; }

  .header-actions { display: flex; gap: 12px; align-items: center; }
  .status-pill {
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 1px;
    display: flex; align-items: center; gap: 8px;
    background: rgba(0, 255, 136, 0.1);
    border: 1px solid var(--neon-green);
    color: var(--neon-green);
  }
  .pulse-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--neon-green); animation: blink 1.2s infinite; }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

  .btn {
    padding: 10px 18px;
    border-radius: 10px;
    font-family: 'Orbitron', sans-serif;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 1px;
    cursor: pointer;
    border: none;
    transition: all 0.3s;
    text-transform: uppercase;
  }
  .btn-primary {
    background: linear-gradient(135deg, var(--neon-pink), var(--neon-purple));
    color: white;
  }
  .btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(255,45,120,0.4);
  }
  .btn-secondary {
    background: rgba(0, 245, 255, 0.1);
    border: 1px solid var(--neon-cyan);
    color: var(--neon-cyan);
  }
  .btn-secondary:hover {
    background: var(--neon-cyan); color: black;
  }

  /* Metric Cards Grid */
  .metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
  }
  .metric-card {
    background: var(--bg-card);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 18px 20px;
    transition: transform 0.2s, border-color 0.2s;
  }
  .metric-card:hover { transform: translateY(-2px); border-color: rgba(0, 245, 255, 0.25); }
  .metric-title { font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; }
  .metric-value { font-family: 'Orbitron', sans-serif; font-size: 1.8rem; font-weight: 800; color: var(--neon-cyan); margin: 6px 0; }
  .metric-sub { font-size: 0.72rem; color: var(--text-muted); }

  /* Navigation Tabs */
  .nav-tabs {
    display: flex; gap: 10px; margin-bottom: 20px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    padding-bottom: 12px;
  }
  .nav-tab {
    padding: 10px 22px;
    border-radius: 10px;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    background: transparent;
    border: 1px solid transparent;
    color: var(--text-muted);
    transition: all 0.25s;
    font-family: 'Inter', sans-serif;
  }
  .nav-tab:hover { color: var(--text-main); background: rgba(255,255,255,0.03); }
  .nav-tab.active {
    background: rgba(0, 245, 255, 0.1);
    border-color: var(--neon-cyan);
    color: var(--neon-cyan);
  }

  /* Section Containers */
  .tab-content { display: none; }
  .tab-content.active { display: block; }

  .card {
    background: var(--bg-card);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
  }
  .card-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 18px;
  }
  .card-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 0.95rem;
    letter-spacing: 1.5px;
    color: var(--neon-cyan);
    text-transform: uppercase;
    display: flex; align-items: center; gap: 10px;
  }

  /* Table & Feed List */
  .trend-item {
    display: flex; align-items: center; justify-content: space-between;
    padding: 16px;
    background: var(--bg-card-alt);
    border: 1px solid rgba(255,255,255,0.04);
    border-radius: 12px;
    margin-bottom: 10px;
    transition: border-color 0.2s, background 0.2s;
  }
  .trend-item:hover { border-color: rgba(0, 245, 255, 0.25); background: #18183c; }
  .trend-info { flex: 1; padding-right: 16px; }
  .trend-title { font-size: 0.95rem; font-weight: 600; margin-bottom: 6px; color: var(--text-main); }
  .trend-meta { display: flex; gap: 12px; font-size: 0.75rem; color: var(--text-muted); align-items: center; }
  .badge {
    padding: 3px 8px; border-radius: 6px; font-size: 0.7rem; font-weight: 600;
  }
  .badge-high { background: rgba(255, 45, 120, 0.15); border: 1px solid var(--neon-pink); color: var(--neon-pink); }
  .badge-med { background: rgba(0, 245, 255, 0.15); border: 1px solid var(--neon-cyan); color: var(--neon-cyan); }
  .score-pill {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.3rem;
    font-weight: 800;
    color: var(--neon-cyan);
    min-width: 60px;
    text-align: center;
  }

  /* Video Vault Grid */
  .video-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 18px;
  }
  .video-card {
    background: var(--bg-card-alt);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    overflow: hidden;
    transition: transform 0.2s;
  }
  .video-card:hover { transform: translateY(-3px); border-color: var(--neon-cyan); }
  .video-thumb {
    width: 100%; height: 260px; background: #000;
    display: flex; align-items: center; justify-content: center;
    position: relative;
  }
  .video-thumb video { width: 100%; height: 100%; object-fit: cover; }
  .video-details { padding: 14px; }
  .video-title { font-size: 0.85rem; font-weight: 600; margin-bottom: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .video-actions { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; }

  /* Input styles for manual tab */
  .input-text {
    width: 100%;
    background: var(--bg-card-alt);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    color: var(--text-main);
    padding: 12px 16px;
    font-size: 0.9rem;
    outline: none;
    margin-bottom: 12px;
  }
  .input-text:focus { border-color: var(--neon-cyan); }

  .log-box {
    background: #000;
    border: 1px solid rgba(0,245,255,0.1);
    border-radius: 8px;
    padding: 14px;
    font-family: monospace;
    font-size: 0.75rem;
    color: #00FF88;
    max-height: 220px;
    overflow-y: auto;
    white-space: pre-wrap;
  }
</style>
</head>
<body>
<div class="container">

  <!-- Command Header -->
  <div class="header">
    <div class="logo-block">
      <h1>NOITE 86</h1>
      <p>VIRAL COMMAND CENTER V3.0 // OPERAÇÃO AUTÔNOMA 24/7</p>
    </div>
    <div class="header-actions">
      <div class="status-pill" id="badgeLocalRadar" style="border-color: rgba(255,255,255,0.1);">
        <div class="pulse-dot" style="background:#888;" id="dotLocalRadar"></div>
        <span id="textLocalRadar">LOCAL: VERIFICANDO...</span>
      </div>
      <div class="status-pill" id="badgeCloudRadar" style="border-color: rgba(255,255,255,0.1);">
        <span id="textCloudRadar">☁️ NUVEM: VERIFICANDO...</span>
      </div>
      <button class="btn btn-secondary" onclick="runRadarScan()">🛰️ Varredura Agora</button>
      <button class="btn btn-primary" onclick="runCommanderCycle()">⚡ Produzir Top 1</button>
    </div>
  </div>

  <!-- Operational Metrics -->
  <div class="metrics-grid">
    <div class="metric-card">
      <div class="metric-title">Tendências Descobertas</div>
      <div class="metric-value" id="mTrends">0</div>
      <div class="metric-sub">YouTube · Reddit · Trends</div>
    </div>
    <div class="metric-card">
      <div class="metric-title">Fila de Produção</div>
      <div class="metric-value" id="mQueue">0</div>
      <div class="metric-sub">Pendentes / Na esteira</div>
    </div>
    <div class="metric-card">
      <div class="metric-title">Vídeos Prontos (9:16)</div>
      <div class="metric-value" id="mVideos">0</div>
      <div class="metric-sub">1080x1920 MP4 Validados</div>
    </div>
    <div class="metric-card">
      <div class="metric-title">Custo Operacional</div>
      <div class="metric-value" style="color:var(--neon-green)">R$ 0,00</div>
      <div class="metric-sub">Whisper + Edge-TTS + FFmpeg</div>
    </div>
  </div>

  <!-- Navigation Tabs -->
  <div class="nav-tabs">
    <button class="nav-tab active" onclick="showTab('tab-radar')">🛰️ Radar de Tendências</button>
    <button class="nav-tab" onclick="showTab('tab-queue')">⚡ Fila Persistente</button>
    <button class="nav-tab" onclick="showTab('tab-vault')">🎬 Vault de Vídeos Prontos</button>
    <button class="nav-tab" onclick="showTab('tab-manual')">🔗 Produção Manual (Link)</button>
    <button class="nav-tab" onclick="showTab('tab-logs')">📋 Logs do Sistema</button>
  </div>

  <!-- TAB 1: RADAR -->
  <div class="tab-content active" id="tab-radar">
    <div class="card">
      <div class="card-header">
        <div class="card-title"><span>📡</span> Oportunidades Internacionais Detectadas</div>
        <button class="btn btn-secondary" onclick="loadTrends()">🔄 Atualizar</button>
      </div>
      <div id="trendsList">Carregando oportunidades do radar...</div>
    </div>
  </div>

  <!-- TAB 2: QUEUE -->
  <div class="tab-content" id="tab-queue">
    <div class="card">
      <div class="card-header">
        <div class="card-title"><span>⚙️</span> Esteira de Processamento Autônomo</div>
        <div>
          <button class="btn btn-secondary" onclick="reprocessFailed()">♻️ Reprocessar Falhas</button>
          <button class="btn btn-primary" onclick="processNextWorker()">▶ Processar Próximo</button>
        </div>
      </div>
      <div id="queueList">Carregando fila...</div>
    </div>
  </div>

  <!-- TAB 3: VAULT -->
  <div class="tab-content" id="tab-vault">
    <div class="card">
      <div class="card-header">
        <div class="card-title"><span>🎬</span> Galeria de Vídeos Prontos (NOITE 86)</div>
        <button class="btn btn-secondary" onclick="loadVideos()">🔄 Atualizar</button>
      </div>
      <div class="video-grid" id="videoGrid">Carregando vídeos produzidos...</div>
    </div>
  </div>

  <!-- TAB 4: MANUAL LINK -->
  <div class="tab-content" id="tab-manual">
    <div class="card">
      <div class="card-header">
        <div class="card-title"><span>🔗</span> Inserção Manual de Link Direto</div>
      </div>
      <input type="text" class="input-text" id="manualUrl" placeholder="Cole o link do YouTube, Twitter/X, TikTok..." />
      <button class="btn btn-primary" style="width:100%" onclick="submitManual()">▶ Processar Link Agora</button>
      <div id="manualMsg" style="margin-top:12px;display:none;color:var(--neon-green)"></div>
    </div>
  </div>

  <!-- TAB 5: LOGS -->
  <div class="tab-content" id="tab-logs">
    <div class="card">
      <div class="card-header">
        <div class="card-title"><span>💻</span> Terminal de Operações em Tempo Real</div>
      </div>
      <div class="log-box" id="systemLogs">Aguardando eventos do sistema...</div>
    </div>
  </div>

</div>

<script>
function showTab(tabId) {
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach(el => el.classList.remove('active'));
  document.getElementById(tabId).classList.add('active');
  event.target.classList.add('active');
  if (tabId === 'tab-radar') loadTrends();
  if (tabId === 'tab-queue') loadQueue();
  if (tabId === 'tab-vault') loadVideos();
}

async function loadTrends() {
  try {
    const res = await fetch('/api/radar/trends');
    const data = await res.json();
    document.getElementById('mTrends').textContent = data.length || 0;
    const container = document.getElementById('trendsList');
    if (!data.length) {
      container.innerHTML = '<p style="color:var(--text-muted)">Nenhuma oportunidade pendente. Clique em "Varredura Agora".</p>';
      return;
    }
    container.innerHTML = data.map(item => {
      const srcName = item.source_name || item.author || 'Fonte Internacional';
      const platform = (item.platform || 'web').toUpperCase();
      const angle = item.recommended_angle_br ? (item.recommended_angle_br.length > 70 ? item.recommended_angle_br.substring(0, 70) + '...' : item.recommended_angle_br) : 'Análise autoral para o público brasileiro';
      const hook = item.suggested_hook_pt || '';
      const priority = item.priority_level || 'PADRÃO';
      const score = Math.round(item.viral_score || 0);

      return `
        <div class="trend-item">
          <div class="trend-info">
            <div class="trend-title">${item.title || 'Sem título'}</div>
            <div class="trend-meta">
              <span class="badge ${score >= 65 ? 'badge-high' : 'badge-med'}">${priority}</span>
              <span>📍 ${srcName} (${platform})</span>
              <span>🎯 ${angle}</span>
            </div>
            ${hook ? `<div style="font-size:0.75rem;color:var(--accent);margin-top:4px;">🔥 Gancho BR: "${hook}"</div>` : ''}
          </div>
          <div style="display:flex;align-items:center;gap:16px;">
            <div class="score-pill">${score}</div>
            <button class="btn btn-primary" style="padding:6px 12px;font-size:0.75rem;" onclick="enqueueOpportunity('${item.id}')">
              + Produzir
            </button>
          </div>
        </div>
      `;
    }).join('');
  } catch(e) {}
}

async function loadQueue() {
  try {
    const res = await fetch('/api/queue');
    const data = await res.json();
    document.getElementById('mQueue').textContent = data.stats.queued || 0;
    const container = document.getElementById('queueList');
    if (!data.jobs.length) {
      container.innerHTML = '<p style="color:var(--text-muted)">A fila de produção está vazia.</p>';
      return;
    }
    container.innerHTML = data.jobs.map(j => `
      <div class="trend-item">
        <div class="trend-info">
          <div class="trend-title">${j.title}</div>
          <div class="trend-meta">
            <span class="badge ${j.status === 'completed' ? 'badge-med' : 'badge-high'}">${j.status.toUpperCase()}</span>
            <span>Prioridade: ${j.priority}</span>
            <span>Rota: ${j.route}</span>
            <span>Tentativas: ${j.retry_count}</span>
          </div>
        </div>
      </div>
    `).join('');
  } catch(e) {}
}

async function loadVideos() {
  try {
    const res = await fetch('/api/videos');
    const data = await res.json();
    document.getElementById('mVideos').textContent = data.length || 0;
    const grid = document.getElementById('videoGrid');
    if (!data.length) {
      grid.innerHTML = '<p style="color:var(--text-muted)">Nenhum vídeo renderizado ainda.</p>';
      return;
    }
    grid.innerHTML = data.map(v => {
      const s = v.sommelier;
      let badgeHtml = '';
      let critHtml = '';
      if (s) {
        const isGold = s.overall_score >= 88;
        badgeHtml = `<span class="badge ${isGold ? 'badge-high' : 'badge-med'}" style="margin-bottom:6px;display:inline-block;">${s.verdict_badge} SOMMELIER: ${s.overall_score}/100 (${s.verdict.replace('_', ' ')})</span>`;
        critHtml = `<div style="font-size:0.75rem;color:var(--accent);margin:6px 0;line-height:1.3;">🍷 <i>${s.critique_summary}</i></div>`;
      }
      return `
        <div class="video-card">
          <div class="video-thumb">
            <video src="/api/stream?path=${encodeURIComponent(v.path)}" controls preload="metadata"></video>
          </div>
          <div class="video-details">
            ${badgeHtml}
            <div class="video-title">${v.name}</div>
            <div style="font-size:0.75rem;color:var(--text-muted)">Tamanho: ${(v.size_bytes/1024/1024).toFixed(1)} MB · 9:16 Vertical</div>
            ${critHtml}
            <div class="video-actions">
              <a class="btn btn-secondary" style="font-size:0.75rem;padding:6px 12px;text-decoration:none;" href="/api/download?path=${encodeURIComponent(v.path)}" download>
                ⬇️ Baixar MP4
              </a>
            </div>
          </div>
        </div>
      `;
    }).join('');
  } catch(e) {}
}

async function runRadarScan() {
  log("Iniciando varredura no Radar Internacional...");
  await fetch('/api/radar/scan', { method: 'POST' });
  loadTrends();
}

async function runCommanderCycle() {
  log("Comandante: executando ciclo mestre autônomo...");
  await fetch('/api/commander/cycle', { method: 'POST' });
  loadTrends();
  loadQueue();
  loadVideos();
}

async function enqueueOpportunity(id) {
  await fetch('/api/queue/enqueue_trend', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({opportunity_id: id})
  });
  loadQueue();
  loadTrends();
}

async function processNextWorker() {
  log("Executando produção do próximo job da fila...");
  await fetch('/api/worker/process_next', { method: 'POST' });
  loadQueue();
  loadVideos();
}

async function reprocessFailed() {
  await fetch('/api/queue/reprocess_failed', { method: 'POST' });
  loadQueue();
}

async function submitManual() {
  const url = document.getElementById('manualUrl').value.trim();
  if (!url) return alert('Cole uma URL');
  const msg = document.getElementById('manualMsg');
  msg.style.display = 'block';
  msg.textContent = 'Enviado para produção! Acompanhe na aba Fila.';
  const formData = new FormData();
  formData.append('video_url', url);
  await fetch('/api/process', { method: 'POST', body: formData });
  document.getElementById('manualUrl').value = '';
  loadQueue();
}

async function updateTelemetry() {
  try {
    const res = await fetch('/api/system/status');
    const data = await res.json();

    const dotLocal = document.getElementById('dotLocalRadar');
    const textLocal = document.getElementById('textLocalRadar');
    if (dotLocal && textLocal) {
      if (data.radar_local === 'ONLINE') {
        dotLocal.style.background = '#00FF88';
        textLocal.textContent = `RADAR LOCAL: ONLINE (PID ${data.radar_local_pid})`;
        textLocal.style.color = '#00FF88';
      } else {
        dotLocal.style.background = '#ff4444';
        textLocal.textContent = 'RADAR LOCAL: OFFLINE';
        textLocal.style.color = '#ff6b6b';
      }
    }

    const textCloud = document.getElementById('textCloudRadar');
    if (textCloud) {
      if (data.radar_cloud === 'CONFIGURADO') {
        textCloud.textContent = `☁️ NUVEM: ATIVA (${data.last_cloud_run})`;
        textCloud.style.color = '#00FF88';
      } else {
        textCloud.textContent = '☁️ NUVEM: PENDENTE GITHUB PUSH';
        textCloud.style.color = '#ffaa00';
      }
    }
  } catch(e) {}
}

function log(msg) {
  const b = document.getElementById('systemLogs');
  b.textContent = `[${new Date().toLocaleTimeString()}] ${msg}\\n` + b.textContent;
}

// Inicialização
loadTrends();
loadQueue();
loadVideos();
updateTelemetry();
setInterval(() => {
  loadQueue();
  loadVideos();
  updateTelemetry();
}, 6000);
</script>
</body>
</html>"""


# =========================================================================
# API ENDPOINTS
# =========================================================================

@app.route("/")
def index():
    return render_template_string(DASHBOARD_HTML)


@app.route("/api/radar/scan", methods=["POST"])
def api_radar_scan():
    """Dispara varredura imediata de todas as fontes internacionais."""
    findings = radar.scan_all_sources()
    scored = analyst.analyze_and_rank(findings)
    operational_state["last_radar_scan"] = datetime.now(timezone.utc).isoformat()
    operational_state["items_discovered_count"] = len(findings)
    return jsonify({
        "status": "success",
        "discovered_count": len(findings),
        "top_score": scored[0].viral_score if scored else 0
    })


@app.route("/api/radar/trends", methods=["GET"])
def api_radar_trends():
    """Retorna as oportunidades ranqueadas pelo analista viral."""
    cache_file = PROJECT_ROOT / "autonomous_engine" / "latest_trends.json"
    if cache_file.exists():
        try:
            data = json.loads(cache_file.read_text(encoding="utf-8"))
            items = [radar._scan_youtube_feed(s) for s in []] # stub
            # reconstrói items
            from autonomous_engine.radar_engine import DiscoveredItem
            disc = [DiscoveredItem(**d) for d in data]
            ranked = analyst.analyze_and_rank(disc)
            return jsonify([r.to_dict() for r in ranked[:15]])
        except Exception:
            pass
    # Se não há cache, faz varredura
    findings = radar.scan_all_sources()
    ranked = analyst.analyze_and_rank(findings)
    return jsonify([r.to_dict() for r in ranked[:15]])


@app.route("/api/queue", methods=["GET"])
def api_get_queue():
    """Retorna o estado da fila de produção."""
    jobs = queue.list_jobs(limit=30)
    stats = queue.get_stats()
    return jsonify({"jobs": jobs, "stats": stats})


@app.route("/api/queue/enqueue_trend", methods=["POST"])
def api_enqueue_trend():
    """Aprova uma oportunidade e a coloca na fila de produção."""
    data = request.json or {}
    opp_id = data.get("opportunity_id")
    if not opp_id:
        return jsonify({"error": "ID ausente"}), 400

    # Busca a oportunidade no cache
    cache_file = PROJECT_ROOT / "autonomous_engine" / "latest_trends.json"
    if not cache_file.exists():
        return jsonify({"error": "Cache vazio"}), 404

    trends = json.loads(cache_file.read_text(encoding="utf-8"))
    from autonomous_engine.radar_engine import DiscoveredItem
    match = next((DiscoveredItem(**t) for t in trends if t["id"] == opp_id), None)
    if not match:
        return jsonify({"error": "Item não encontrado"}), 404

    opp = analyst._score_item(match)
    verdict = rights_officer.evaluate_opportunity(opp)
    briefing = strategist.create_briefing(opp, verdict)

    job_id = queue.enqueue(
        opportunity_id=opp.item.id,
        title=opp.item.title,
        priority=int(round(opp.viral_score)),
        source_url=opp.item.url,
        route=verdict.route.value,
        briefing_dict=briefing.to_dict()
    )
    return jsonify({"status": "enqueued", "job_id": job_id})


@app.route("/api/queue/reprocess_failed", methods=["POST"])
def api_reprocess_failed():
    """Reseta todos os jobs que falharam para que sejam reexecutados."""
    with queue._get_conn() as conn:
        conn.execute("UPDATE production_queue SET status = 'queued', retry_count = 0 WHERE status = 'failed'")
        conn.commit()
    return jsonify({"status": "reset_completed"})


@app.route("/api/worker/process_next", methods=["POST"])
def api_worker_process():
    """Dispara a produção imediata do próximo job da fila."""
    art = worker.process_next_job()
    return jsonify({"status": "success" if art else "no_jobs", "artifacts": art})


@app.route("/api/commander/cycle", methods=["POST"])
def api_commander_cycle():
    """Executa um ciclo mestre completo (Radar + Fila + Produção)."""
    summary = commander.run_cycle(max_queue_items=1, process_jobs=True)
    return jsonify(summary)


@app.route("/api/system/status", methods=["GET"])
def api_system_status():
    """Retorna o status em tempo real de cada componente para o painel de operações."""
    import subprocess
    factory_dir = Path(r"C:\Users\victo\NOITE86_FACTORY")
    lock_file = factory_dir / "09_LOGS" / "scheduler.lock"

    # 1. Radar Local
    local_scheduler_online = False
    local_pid = None
    if lock_file.exists():
        try:
            pid = int(lock_file.read_text(encoding="utf-8").strip())
            from autonomous_engine.scheduler import ProcessLock
            if ProcessLock._is_pid_running(pid):
                local_scheduler_online = True
                local_pid = pid
        except Exception:
            pass

    # 2. Radar Nuvem (Verifica se há git remote configurado)
    try:
        git_res = subprocess.run(["git", "remote"], capture_output=True, text=True, cwd=str(PROJECT_ROOT))
        cloud_radar_configured = bool(git_res.stdout.strip())
    except Exception:
        cloud_radar_configured = False

    cloud_file = PROJECT_ROOT / "autonomous_engine" / "cloud_latest_trends.json"
    last_cloud_run = datetime.fromtimestamp(cloud_file.stat().st_mtime).strftime("%d/%m %H:%M") if cloud_file.exists() else "Aguardando 1º push"

    # 3. Métricas de produção
    ready_dir = factory_dir / "06_READY_VIDEOS"
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
    videos_today = len([f for f in ready_dir.glob("*.mp4") if f.stat().st_mtime >= today_start]) if ready_dir.exists() else 0

    rejected_dir = factory_dir / "07_REJECTED"
    rejected_count = len(list(rejected_dir.glob("*"))) if rejected_dir.exists() else 0

    queue_stats = queue.get_stats()

    return jsonify({
        "radar_local": "ONLINE" if local_scheduler_online else "OFFLINE",
        "radar_local_pid": local_pid,
        "radar_cloud": "CONFIGURADO" if cloud_radar_configured else "PENDENTE REPOSITÓRIO",
        "worker_video": "PRONTO",
        "last_scan": datetime.now().strftime("%H:%M:%S"),
        "last_cloud_run": last_cloud_run,
        "videos_today": videos_today,
        "videos_rejected": rejected_count,
        "queue_failures": queue_stats.get("failed", 0),
        "next_run": "A cada 30 min (se ativo)"
    })


@app.route("/api/videos", methods=["GET"])
def api_list_videos():
    """Lista todos os vídeos MP4 prontos com os respectivos laudos do Conselho de Sommeliers."""
    ready_dir = STORAGE_BASE / "06_READY_VIDEOS"
    reports_dir = STORAGE_BASE / "08_REPORTS"
    videos = []
    if ready_dir.exists():
        for f in ready_dir.glob("*.mp4"):
            somm_file = reports_dir / f"sommelier_{f.stem}.json"
            somm_data = None
            if somm_file.exists():
                try:
                    somm_data = json.loads(somm_file.read_text(encoding="utf-8"))
                except Exception:
                    pass
            videos.append({
                "name": f.name,
                "path": str(f),
                "size_bytes": f.stat().st_size,
                "modified_at": f.stat().st_mtime,
                "sommelier": somm_data
            })
    # Ordena pelos mais recentes
    videos.sort(key=lambda x: x["modified_at"], reverse=True)
    return jsonify(videos)


@app.route("/api/download")
def api_download_file():
    p = Path(request.args.get("path", ""))
    if not p.exists():
        return "Arquivo não encontrado", 404
    return send_from_directory(str(p.parent), p.name, as_attachment=True)


@app.route("/api/stream")
def api_stream_video():
    p = Path(request.args.get("path", ""))
    if not p.exists():
        return "Arquivo não encontrado", 404
    return send_from_directory(str(p.parent), p.name, mimetype="video/mp4")


# Compatibilidade com formulário avulso do painel
@app.route("/api/process", methods=["POST"])
def api_manual_process():
    video_url = request.form.get("video_url", "").strip()
    if not video_url:
        return jsonify({"error": "URL ausente"}), 400

    opp_id = f"manual_{uuid.uuid4().hex[:8]}"
    job_id = queue.enqueue(
        opportunity_id=opp_id,
        title=f"Manual Input: {video_url[:40]}",
        priority=99,
        source_url=video_url,
        route="direct_adaptation",
        briefing_dict={
            "briefing_id": f"brief_{opp_id}",
            "opportunity_id": opp_id,
            "title_br": "Vídeo Manual NOITE 86",
            "viral_score": 90.0,
            "route": "direct_adaptation",
            "script_segments": [
                {"id": 1, "start_sec": 0.0, "end_sec": 5.0, "narration_pt": "🚨 SE LIGA NESSE DETALHE INSANO DE GTA 6!", "visual_cue": "", "on_screen_text": "🚨 ALERTA GERAL"},
                {"id": 2, "start_sec": 5.1, "end_sec": 18.0, "narration_pt": "Os novos detalhes e gráficos de Vice City tão surreais.", "visual_cue": "", "on_screen_text": "VICE CITY 1986"},
                {"id": 3, "start_sec": 18.1, "end_sec": 30.0, "narration_pt": "Garanta suas peças de streetwear na coleção NOITE 86 no link da bio!", "visual_cue": "", "on_screen_text": "COLEÇÃO NOITE 86"}
            ],
            "call_to_action": "COLEÇÃO NOITE 86 // LINK NA BIO"
        }
    )
    # Processa em background
    threading.Thread(target=worker.process_next_job, daemon=True).start()
    return jsonify({"status": "queued", "job_id": job_id})


if __name__ == "__main__":
    port = 8086
    print("=" * 60)
    print("🚀 NOITE 86 — VIRAL COMMAND CENTER V3.0 NO AR!")
    print(f"   Acesse no navegador: http://localhost:{port}")
    print("=" * 60)
    app.run(host="0.0.0.0", port=port, debug=False)
