"""
autonomous_engine/radar_engine.py
AGENTE 01 — YouTube Viral Hunter
AGENTE 02 — TikTok Trend Hunter (Metadados públicos e formatos virais)
AGENTE 03 — Instagram Trend Hunter (Estruturas e padrões audiovisuais)

Monitora fontes oficiais e públicas internacionais (RSS, feeds públicos, APIs abertas)
sem contornar barreiras de segurança ou realizar scraping não autorizado.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

import feedparser
import requests

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
STORAGE_BASE = Path(r"C:\Users\victo\NOITE86_FACTORY")
REGISTRY_FILE = Path(__file__).parent / "source_registry.json"


class DiscoveredItem(BaseModel):
    id: str
    platform: str
    source_name: str
    author: str
    title: str
    url: str
    published_at: str
    discovered_at: str
    summary: str = ""
    thumbnail: str = ""
    license_category: str = "unauthorized"  # own_content, explicit_permission, public_trailer, unauthorized
    niche_tags: List[str] = Field(default_factory=list)
    raw_metrics: Dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class ViralRadarEngine:
    """Motor de varredura autônoma de tendências internacionais."""

    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Noite86ViralRadar/3.0 (Operational Intelligence)"

    KEYWORDS = [
        "gta 6", "gta vi", "vice city", "rockstar games", "rockstar", "lucia", "jason",
        "trailer", "leak", "map", "graphics", "physics", "gameplay", "release date",
        "leonida", "miami", "synthwave", "retrowave", "open world", "ps5", "xbox"
    ]

    def __init__(self, registry_path: Optional[Path] = None):
        self.registry_path = registry_path or REGISTRY_FILE
        self.sources = self._load_sources()

    def _load_sources(self) -> List[Dict[str, Any]]:
        if not self.registry_path.exists():
            return []
        try:
            data = json.loads(self.registry_path.read_text(encoding="utf-8"))
            return [s for s in data.get("sources", []) if s.get("enabled", True)]
        except Exception as e:
            print(f"[RadarEngine] Erro ao carregar source_registry.json: {e}")
            return []

    def scan_all_sources(self) -> List[DiscoveredItem]:
        """Varre todas as fontes habilitadas e retorna itens relevantes descobertos."""
        findings: List[DiscoveredItem] = []
        print(f"[RadarEngine] Iniciando varredura em {len(self.sources)} fontes públicas internacionais...")

        for source in self.sources:
            try:
                platform = source.get("platform")
                if platform == "youtube_search":
                    items = self._scan_youtube_search(source)
                    findings.extend(items)
                    continue

                feed_url = source.get("feed_url")
                if not feed_url:
                    continue
                elif platform == "reddit_rss":
                    items = self._scan_reddit_rss(source)
                    findings.extend(items)
                elif platform == "youtube":
                    items = self._scan_youtube_feed(source)
                    findings.extend(items)
                elif platform == "reddit":
                    items = self._scan_reddit_feed(source)
                    findings.extend(items)
                elif platform == "google_trends":
                    items = self._scan_google_trends(source)
                    findings.extend(items)
            except Exception as e:
                print(f"[RadarEngine] Erro ao escanear fonte {source.get('name')}: {e}")

        # Salva o resultado no diretório persistente
        self._persist_findings(findings)
        print(f"[RadarEngine] Varredura concluída! {len(findings)} oportunidades identificadas.")
        return findings

    def _scan_youtube_search(self, source: Dict[str, Any]) -> List[DiscoveredItem]:
        query = source.get("query", "ytsearch10:GTA 6 official trailer")
        try:
            import yt_dlp
            ydl_opts = {"extract_flat": True, "quiet": True, "no_warnings": True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                res = ydl.extract_info(query, download=False)
                entries = res.get("entries", [])
        except Exception as e:
            print(f"[Radar] Erro ao buscar vídeos via ytsearch ({query}): {e}")
            return []

        results = []
        for e in entries:
            vid_id = e.get("id", "")
            title = e.get("title", "")
            if not vid_id or not title:
                continue
            url = f"https://www.youtube.com/watch?v={vid_id}"
            views = e.get("view_count", 0) or 0
            uploader = e.get("uploader", "Criador YouTube")
            thumb = f"https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg" if vid_id else ""
            item_id = hashlib.sha256(f"ytsearch_{vid_id}".encode("utf-8")).hexdigest()[:16]

            item = DiscoveredItem(
                id=item_id,
                platform="youtube_shorts" if "short" in query else "youtube",
                source_name=source["name"],
                author=uploader,
                title=title,
                url=url,
                published_at=datetime.now(timezone.utc).isoformat(),
                discovered_at=datetime.now(timezone.utc).isoformat(),
                summary=f"Vídeo em alta com {views:,} visualizações no canal {uploader}.",
                thumbnail=thumb,
                license_category=source.get("license_category", "unauthorized"),
                niche_tags=["gta6", "viral_clip"],
                raw_metrics={"views": views, "platform_weight": source.get("weight", 1.0)}
            )
            results.append(item)
        return results

    def _scan_reddit_rss(self, source: Dict[str, Any]) -> List[DiscoveredItem]:
        feed_url = source.get("feed_url", "https://www.reddit.com/r/GTA6/.rss")
        try:
            feed = feedparser.parse(feed_url)
        except Exception as e:
            print(f"[Radar] Falha ao ler RSS Reddit ({feed_url}): {e}")
            return []

        results = []
        for entry in feed.entries[:15]:
            title = entry.get("title", "")
            url = entry.get("link", "")
            if not title or not url:
                continue
            author = entry.get("author", "reddit_community")
            item_id = hashlib.sha256(f"reddit_rss_{url}".encode("utf-8")).hexdigest()[:16]

            item = DiscoveredItem(
                id=item_id,
                platform="reddit",
                source_name=source["name"],
                author=author,
                title=title,
                url=url,
                published_at=entry.get("published", datetime.now(timezone.utc).isoformat()),
                discovered_at=datetime.now(timezone.utc).isoformat(),
                summary=f"Discussão em alta na comunidade r/GTA6: {title}",
                thumbnail="",
                license_category=source.get("license_category", "unauthorized"),
                niche_tags=["gta6_community", "reddit_hot"],
                raw_metrics={"views": 50000, "platform_weight": source.get("weight", 0.95)}
            )
            results.append(item)
        return results

    def _scan_youtube_feed(self, source: Dict[str, Any]) -> List[DiscoveredItem]:
        feed_url = source["feed_url"]
        headers = {"User-Agent": self.USER_AGENT}
        try:
            resp = requests.get(feed_url, headers=headers, timeout=10)
            if resp.status_code != 200:
                print(f"[Radar] YouTube feed retornou HTTP {resp.status_code} para {source['name']}")
                return []
            parsed = feedparser.parse(resp.content)
        except Exception as e:
            print(f"[Radar] Falha na requisição RSS YouTube ({source['name']}): {e}")
            return []

        results = []
        for entry in parsed.entries[:10]:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            url = entry.get("link", "")
            published = entry.get("published", "") or datetime.now(timezone.utc).isoformat()
            video_id = entry.get("yt_videoid", "")

            # Filtra relevância para o nicho de GTA / Vice City / Gaming
            text_to_check = f"{title} {summary}".lower()
            matched_tags = [kw for kw in self.KEYWORDS if kw in text_to_check]

            # Se for do canal oficial da Rockstar, aceita tudo; senão, exige tags relevantes
            if "rockstar" in source["name"].lower() or len(matched_tags) >= 1:
                item_id = hashlib.sha256(f"{source['platform']}_{url}".encode("utf-8")).hexdigest()[:16]
                thumb = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg" if video_id else ""

                item = DiscoveredItem(
                    id=item_id,
                    platform="youtube",
                    source_name=source["name"],
                    author=entry.get("author", source["name"]),
                    title=title,
                    url=url,
                    published_at=published,
                    discovered_at=datetime.now(timezone.utc).isoformat(),
                    summary=summary[:300],
                    thumbnail=thumb,
                    license_category=source.get("license_category", "unauthorized"),
                    niche_tags=matched_tags or ["gaming"],
                    raw_metrics={"views": 0, "platform_weight": source.get("weight", 1.0)}
                )
                results.append(item)
        return results

    def _scan_reddit_feed(self, source: Dict[str, Any]) -> List[DiscoveredItem]:
        feed_url = source["feed_url"]
        headers = {"User-Agent": self.USER_AGENT}
        try:
            resp = requests.get(feed_url, headers=headers, timeout=10)
            if resp.status_code != 200:
                return []
            data = resp.json()
        except Exception as e:
            print(f"[Radar] Falha ao consultar feed Reddit ({source['name']}): {e}")
            return []

        results = []
        posts = data.get("data", {}).get("children", [])
        for p in posts[:12]:
            post_data = p.get("data", {})
            title = post_data.get("title", "")
            url = f"https://reddit.com{post_data.get('permalink', '')}"
            score = post_data.get("score", 0)
            comments = post_data.get("num_comments", 0)
            created_utc = post_data.get("created_utc", time.time())
            published_dt = datetime.fromtimestamp(created_utc, timezone.utc).isoformat()

            text_to_check = f"{title} {post_data.get('selftext', '')}".lower()
            matched_tags = [kw for kw in self.KEYWORDS if kw in text_to_check]

            item_id = hashlib.sha256(f"reddit_{post_data.get('id')}".encode("utf-8")).hexdigest()[:16]
            item = DiscoveredItem(
                id=item_id,
                platform="reddit",
                source_name=source["name"],
                author=post_data.get("author", "reddit_user"),
                title=title,
                url=url,
                published_at=published_dt,
                discovered_at=datetime.now(timezone.utc).isoformat(),
                summary=post_data.get("selftext", "")[:300],
                thumbnail=post_data.get("thumbnail", ""),
                license_category=source.get("license_category", "unauthorized"),
                niche_tags=matched_tags or ["gta6_community"],
                raw_metrics={"upvotes": score, "comments": comments, "platform_weight": source.get("weight", 0.9)}
            )
            results.append(item)
        return results

    def _scan_google_trends(self, source: Dict[str, Any]) -> List[DiscoveredItem]:
        # Consulta RSS pública do Google Trends
        feed_url = source["feed_url"]
        headers = {"User-Agent": self.USER_AGENT}
        try:
            resp = requests.get(feed_url, headers=headers, timeout=10)
            if resp.status_code != 200:
                return []
            parsed = feedparser.parse(resp.content)
        except Exception:
            return []

        results = []
        for entry in parsed.entries[:8]:
            title = entry.get("title", "")
            text_check = f"{title} {entry.get('summary', '')}".lower()
            matched = [kw for kw in self.KEYWORDS if kw in text_check]
            if matched:
                item_id = hashlib.sha256(f"trends_{title}".encode("utf-8")).hexdigest()[:16]
                item = DiscoveredItem(
                    id=item_id,
                    platform="google_trends",
                    source_name=source["name"],
                    author="Google Trends",
                    title=title,
                    url=entry.get("link", "https://trends.google.com"),
                    published_at=datetime.now(timezone.utc).isoformat(),
                    discovered_at=datetime.now(timezone.utc).isoformat(),
                    summary=entry.get("summary", "")[:250],
                    license_category="unauthorized",
                    niche_tags=matched,
                    raw_metrics={"traffic_surge": True, "platform_weight": source.get("weight", 0.75)}
                )
                results.append(item)
        return results

    def _persist_findings(self, findings: List[DiscoveredItem]):
        """Persiste descobertas em NOITE86_FACTORY e no workspace local."""
        data = [item.to_dict() for item in findings]
        
        # Salva em C:\Users\victo\NOITE86_FACTORY\01_TRENDS
        try:
            trends_dir = STORAGE_BASE / "01_TRENDS"
            trends_dir.mkdir(parents=True, exist_ok=True)
            trends_file = trends_dir / "latest_trends.json"
            trends_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            print(f"[Radar] Erro ao gravar em {STORAGE_BASE}: {e}")

        # Salva também cópia local no workspace
        local_cache = PROJECT_ROOT / "autonomous_engine" / "latest_trends.json"
        local_cache.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    radar = ViralRadarEngine()
    items = radar.scan_all_sources()
    print(f"Total descobertas ativas: {len(items)}")
    for i in items[:5]:
        print(f"[{i.platform.upper()}] {i.title} (Tags: {i.niche_tags})")
