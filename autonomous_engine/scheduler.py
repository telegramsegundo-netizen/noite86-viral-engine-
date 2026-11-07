"""
autonomous_engine/scheduler.py
AGENTE 13 — Cloud Infrastructure Engineer
AGENTE 14 — Operations Analyst

Agendador autônomo industrial para operação 24/7 no Windows.
Recursos:
- Lockfile com detecção de PID ativo (proteção contra instâncias concorrentes).
- Intervalos configuráveis via ENV ou argumentos.
- Tratamento de HTTP 429 e backoff exponencial com jitter.
- Sincronização automática de tendências geradas pela nuvem (Cloud -> Local).
- Gravação persistente de logs em NOITE86_FACTORY/09_LOGS/scheduler.log.
"""
from __future__ import annotations

import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# UTF-8 encoding no console Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from autonomous_engine.commander import AutonomousCommander
from autonomous_engine.production_queue import ProductionQueue

FACTORY_DIR = Path(r"C:\Users\victo\NOITE86_FACTORY")
LOGS_DIR = FACTORY_DIR / "09_LOGS"
LOCK_FILE = FACTORY_DIR / "09_LOGS" / "scheduler.lock"


def format_duration(seconds: int) -> str:
    """Formata segundos em representação legível (ex: '45s', '30 min', '2h')."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins} min" if secs == 0 else f"{mins}m {secs}s"
    else:
        hours = seconds // 3600
        mins = (seconds % 3600) // 60
        return f"{hours}h {mins}m"


def setup_logger() -> logging.Logger:
    """Configura logger duplo: console e arquivo persistente."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOGS_DIR / "scheduler.log"

    logger = logging.getLogger("Noite86Scheduler")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    # Formatter estruturado
    fmt = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    # Handler de arquivo com rotação simples
    fh = logging.FileHandler(str(log_path), encoding="utf-8", mode="a")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    # Handler de console
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    return logger


class ProcessLock:
    """Garante que apenas uma instância do agendador execute ao mesmo tempo."""

    def __init__(self, lock_path: Path, logger: logging.Logger):
        self.lock_path = lock_path
        self.logger = logger
        self.acquired = False

    def acquire(self) -> bool:
        if self.lock_path.exists():
            try:
                pid = int(self.lock_path.read_text(encoding="utf-8").strip())
                # Verifica se o PID ainda está vivo no Windows
                if self._is_pid_running(pid):
                    self.logger.warning(f"Instância concorrente ativa detectada (PID {pid}). Abortando inicialização duplicada.")
                    return False
                else:
                    self.logger.info(f"Lock órfão encontrado (PID {pid} inativo). Assumindo controle.")
            except Exception:
                pass

        try:
            self.lock_path.write_text(str(os.getpid()), encoding="utf-8")
            self.acquired = True
            return True
        except Exception as e:
            self.logger.error(f"Falha ao criar arquivo de lock: {e}")
            return False

    def release(self):
        if self.acquired and self.lock_path.exists():
            try:
                self.lock_path.unlink()
            except Exception:
                pass
            self.acquired = False

    @staticmethod
    def _is_pid_running(pid: int) -> bool:
        """Verifica existência de processo no Windows de forma segura."""
        import ctypes
        kernel32 = ctypes.windll.kernel32
        SYNCHRONIZE = 0x00100000
        process = kernel32.OpenProcess(SYNCHRONIZE, False, pid)
        if process != 0:
            kernel32.CloseHandle(process)
            return True
        return False


def sync_cloud_trends_if_available(queue: ProductionQueue, logger: logging.Logger):
    """Sincroniza oportunidades capturadas pelo GitHub Actions com a fila local."""
    cloud_file = PROJECT_ROOT / "autonomous_engine" / "cloud_latest_trends.json"
    if not cloud_file.exists():
        return

    try:
        data = json.loads(cloud_file.read_text(encoding="utf-8"))
        if not data:
            return

        imported = 0
        for item in data:
            opp_id = item.get("id")
            if not opp_id:
                continue

            # Se já foi enfileirado anteriormente, pula
            existing = queue.get_job_by_opportunity(opp_id)
            if existing:
                continue

            score = float(item.get("viral_score", 50.0))
            if score >= 65.0:  # Limiar de qualificação para fila automática
                lic = item.get("license_category", "unauthorized")
                route = "fair_use_commentary" if lic == "public_trailer" else "original_transformative"
                res = queue.enqueue(
                    opportunity_id=opp_id,
                    title=item.get("title", "Sem título"),
                    priority=int(score),
                    source_url=item.get("url", ""),
                    route=route,
                    briefing_dict=item
                )
                if res:
                    imported += 1

        if imported > 0:
            logger.info(f"⚡ [Nuvem -> Local] Sincronizadas {imported} novas oportunidades descobertas pelo GitHub Actions!")
    except Exception as e:
        logger.error(f"Erro ao sincronizar tendências da nuvem: {e}")

def run_scheduler_daemon(
    radar_interval_seconds: Optional[int] = None,
    worker_check_seconds: Optional[int] = None,
):
    """Loop industrial de produção contínua 24/7 com proteção de rate limit e backoff."""
    logger = setup_logger()

    # Leitura de variáveis de ambiente com defaults robustos
    if radar_interval_seconds is None:
        radar_interval_seconds = int(os.environ.get("NOITE86_RADAR_INTERVAL_SEC", "1800")) # 30 min
    if worker_check_seconds is None:
        worker_check_seconds = int(os.environ.get("NOITE86_WORKER_INTERVAL_SEC", "60"))     # 1 min

    lock = ProcessLock(LOCK_FILE, logger)
    if not lock.acquire():
        print("Operação cancelada: Agendador já está rodando em segundo plano.")
        return

    commander = AutonomousCommander()

    logger.info("=" * 65)
    logger.info("🚀 NOITE 86 — AGENDADOR AUTÔNOMO 24/7 INDUSTRIAL INICIADO")
    logger.info(f"   PID do Processo: {os.getpid()}")
    logger.info(f"   Intervalo de Radar: a cada {format_duration(radar_interval_seconds)}")
    logger.info(f"   Checagem de Fila: a cada {format_duration(worker_check_seconds)}")
    logger.info(f"   Logs Persistentes: {LOGS_DIR / 'scheduler.log'}")
    logger.info("=" * 65)

    last_radar_scan = 0.0
    consecutive_errors = 0
    max_backoff_seconds = 600 # 10 min máximo de backoff

    try:
        while True:
            try:
                now_ts = time.time()

                # 1. Sincronização automática com a nuvem (Cloud -> Local)
                sync_cloud_trends_if_available(commander.queue, logger)

                # 2. Varredura periódica de radar
                if now_ts - last_radar_scan >= radar_interval_seconds:
                    logger.info("🛰️ Disparando ciclo de inteligência de tendências...")
                    cycle_res = commander.run_cycle(max_queue_items=2, process_jobs=False)
                    logger.info(
                        f"Radar finalizado: {cycle_res.get('discovered_count', 0)} encontrados, "
                        f"{cycle_res.get('enqueued_count', 0)} novos trabalhos enfileirados."
                    )
                    last_radar_scan = time.time()
                    consecutive_errors = 0

                # 3. Consumo de trabalho na esteira local
                job = commander.worker.process_next_job()
                if job:
                    logger.info(f"✅ Vídeo finalizado com sucesso: Job {job.get('id')} ({job.get('title')})")

                # Reseta backoff se ciclo completou com sucesso
                current_sleep = worker_check_seconds

            except Exception as e:
                consecutive_errors += 1
                current_sleep = min(worker_check_seconds * (2 ** consecutive_errors), max_backoff_seconds)
                err_str = str(e)

                if "429" in err_str:
                    logger.warning(f"⚠️ [HTTP 429 - Rate Limit Detectado] Aplicando resfriamento forçado de {current_sleep}s...")
                else:
                    logger.error(f"⚠️ Falha no ciclo operacional (#{consecutive_errors}): {e}. Aplicando backoff de {current_sleep}s...")

            time.sleep(current_sleep)

    except KeyboardInterrupt:
        logger.info("🛑 Agendador pausado pelo operador (SIGINT).")
    finally:
        lock.release()
        logger.info("🔒 Trava de processo liberada. Operação finalizada.")


if __name__ == "__main__":
    run_scheduler_daemon()
