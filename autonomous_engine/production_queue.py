"""
autonomous_engine/production_queue.py
Fila de Produção Persistente (SQLite + Atomic JSON)

Controla o ciclo de vida de cada produção autônoma com garantia de integridade,
recuperação de tarefas interrompidas (crashes / reinicialização) e retentativas (retries).
"""
from __future__ import annotations

import json
import sqlite3
import time
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
DB_PATH = PROJECT_ROOT / "autonomous_engine" / "queue.db"
STORAGE_BASE = Path(r"C:\Users\victo\NOITE86_FACTORY")


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class QueueJob(BaseModel):
    id: str
    opportunity_id: str
    title: str
    priority: int  # 1 (baixa) a 100 (alta)
    status: JobStatus
    retry_count: int = 0
    max_retries: int = 3
    source_url: str
    route: str
    briefing_data: Dict[str, Any]
    artifacts: Dict[str, Any] = {}
    error_message: Optional[str] = None
    created_at: str
    updated_at: str
    lock_expires_at: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "opportunity_id": self.opportunity_id,
            "title": self.title,
            "priority": self.priority,
            "status": self.status.value,
            "retry_count": self.retry_count,
            "source_url": self.source_url,
            "route": self.route,
            "artifacts": self.artifacts,
            "error_message": self.error_message,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class ProductionQueue:
    """Gerenciador transacional de fila persistente."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=15)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS production_queue (
                    id TEXT PRIMARY KEY,
                    opportunity_id TEXT UNIQUE,
                    title TEXT NOT NULL,
                    priority INTEGER DEFAULT 50,
                    status TEXT DEFAULT 'queued',
                    retry_count INTEGER DEFAULT 0,
                    max_retries INTEGER DEFAULT 3,
                    source_url TEXT,
                    route TEXT,
                    briefing_json TEXT,
                    artifacts_json TEXT DEFAULT '{}',
                    error_message TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    lock_expires_at REAL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_status_priority ON production_queue(status, priority DESC)")
            conn.commit()

    def get_job_by_opportunity(self, opportunity_id: str) -> Optional[Dict[str, Any]]:
        """Busca se uma oportunidade já existe na fila (qualquer status)."""
        with self._get_conn() as conn:
            cur = conn.execute("SELECT id, status FROM production_queue WHERE opportunity_id = ?", (opportunity_id,))
            row = cur.fetchone()
            if row:
                return {"id": row["id"], "status": row["status"]}
            return None

    def enqueue(
        self,
        opportunity_id: str,
        title: str,
        priority: int,
        source_url: str,
        route: str,
        briefing_dict: Dict[str, Any],
    ) -> Optional[str]:
        """Insere um novo trabalho na fila se já não existir."""
        job_id = f"job_{opportunity_id}"
        now = datetime.now(timezone.utc).isoformat()

        with self._get_conn() as conn:
            cur = conn.execute("SELECT id FROM production_queue WHERE opportunity_id = ?", (opportunity_id,))
            if cur.fetchone():
                return None  # Já existe na fila

            conn.execute("""
                INSERT INTO production_queue (
                    id, opportunity_id, title, priority, status,
                    source_url, route, briefing_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_id, opportunity_id, title, priority, JobStatus.QUEUED.value,
                source_url, route, json.dumps(briefing_dict, ensure_ascii=False), now, now
            ))
            conn.commit()
        return job_id

    def claim_next_job(self, lock_seconds: int = 600) -> Optional[QueueJob]:
        """Reivindica atomicamente o próximo trabalho de maior prioridade."""
        now_ts = time.time()
        lock_expiry = now_ts + lock_seconds

        with self._get_conn() as conn:
            # Primeiro recupera jobs abandonados cujo lock expirou
            conn.execute("""
                UPDATE production_queue 
                SET status = 'queued', lock_expires_at = NULL 
                WHERE status = 'processing' AND lock_expires_at < ?
            """, (now_ts,))

            # Seleciona o job com maior prioridade
            row = conn.execute("""
                SELECT * FROM production_queue
                WHERE status = 'queued'
                ORDER BY priority DESC, created_at ASC
                LIMIT 1
            """).fetchone()

            if not row:
                return None

            job_id = row["id"]
            now_iso = datetime.now(timezone.utc).isoformat()

            conn.execute("""
                UPDATE production_queue
                SET status = 'processing', lock_expires_at = ?, updated_at = ?
                WHERE id = ?
            """, (lock_expiry, now_iso, job_id))
            conn.commit()

            claimed_job = self._row_to_job(row)
            claimed_job.status = JobStatus.PROCESSING
            return claimed_job

    def complete_job(self, job_id: str, artifacts: Dict[str, Any]):
        """Marca o trabalho como concluído com seus artefatos finais."""
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._get_conn() as conn:
            conn.execute("""
                UPDATE production_queue
                SET status = 'completed', artifacts_json = ?, lock_expires_at = NULL, updated_at = ?
                WHERE id = ?
            """, (json.dumps(artifacts, ensure_ascii=False), now_iso, job_id))
            conn.commit()

    def fail_job(self, job_id: str, error: str):
        """Registra falha e incrementa contador de tentativas ou move para FAILED."""
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._get_conn() as conn:
            row = conn.execute("SELECT retry_count, max_retries FROM production_queue WHERE id = ?", (job_id,)).fetchone()
            if not row:
                return
            retries = row["retry_count"] + 1
            max_retries = row["max_retries"]
            new_status = JobStatus.FAILED.value if retries >= max_retries else JobStatus.QUEUED.value

            conn.execute("""
                UPDATE production_queue
                SET status = ?, retry_count = ?, error_message = ?, lock_expires_at = NULL, updated_at = ?
                WHERE id = ?
            """, (new_status, retries, str(error), now_iso, job_id))
            conn.commit()

    def list_jobs(self, limit: int = 50, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retorna lista de jobs para exibição no painel e monitoramento."""
        with self._get_conn() as conn:
            if status_filter:
                rows = conn.execute(
                    "SELECT * FROM production_queue WHERE status = ? ORDER BY priority DESC, updated_at DESC LIMIT ?",
                    (status_filter, limit)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM production_queue ORDER BY updated_at DESC LIMIT ?",
                    (limit,)
                ).fetchall()

            jobs = []
            for r in rows:
                j = self._row_to_job(r)
                jobs.append(j.to_dict())
            return jobs

    def get_stats(self) -> Dict[str, int]:
        """Métricas de produtividade e saúde da fila."""
        with self._get_conn() as conn:
            rows = conn.execute("SELECT status, COUNT(*) as count FROM production_queue GROUP BY status").fetchall()
            stats = {s.value: 0 for s in JobStatus}
            for r in rows:
                stats[r["status"]] = r["count"]
            stats["total"] = sum(stats.values())
            return stats

    def _row_to_job(self, row: sqlite3.Row) -> QueueJob:
        return QueueJob(
            id=row["id"],
            opportunity_id=row["opportunity_id"],
            title=row["title"],
            priority=row["priority"],
            status=JobStatus(row["status"]),
            retry_count=row["retry_count"],
            max_retries=row["max_retries"],
            source_url=row["source_url"] or "",
            route=row["route"] or "transformative",
            briefing_data=json.loads(row["briefing_json"] or "{}"),
            artifacts=json.loads(row["artifacts_json"] or "{}"),
            error_message=row["error_message"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            lock_expires_at=row["lock_expires_at"],
        )
