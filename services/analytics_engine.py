#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
EduHub AI — Privacy-Preserving Lightweight Visitor Analytics Engine
===============================================================================
1. GDPR & CCPA compliant: IP addresses are salted and hashed (never stored raw).
2. Zero-cookie, lightweight telemetry: tracks visits, referrers, devices, UTM.
3. Thread-safe in-memory aggregation with persistent JSON storage.
4. Auto-differentiates Search Crawlers (Google/Bing/Yandex) from Human Visitors.
===============================================================================
"""

import os
import sys
import json
import time
import hashlib
from datetime import datetime, timezone
from threading import Lock
from typing import Dict, Any, Optional
from urllib.parse import urlparse

# Base data paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
ANALYTICS_FILE = os.path.join(DATA_DIR, "visitor_analytics.json")

BOT_KEYWORDS = [
    "bot", "crawler", "spider", "slurp", "bingbot", "googlebot",
    "yandex", "duckduckbot", "baiduspider", "lighthouse", "ahrefs",
    "semrush", "pingdom", "uptime", "render"
]

class VisitorAnalyticsEngine:
    """Движок внутренней веб-аналитики и телеметрии посещаемости."""

    def __init__(self, filepath: str = ANALYTICS_FILE):
        self.filepath = filepath
        self.lock = Lock()
        self._cache: Dict[str, Any] = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        """Загружает существующие данные или инициализирует пустую схему."""
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[ANALYTICS] Warning: Failed to read {self.filepath}: {e}")

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "all_time": {
                "total_pageviews": 0,
                "human_pageviews": 0,
                "bot_pageviews": 0,
                "unique_visitors": []
            },
            "daily": {
                today: {
                    "total_pageviews": 0,
                    "human_pageviews": 0,
                    "bot_pageviews": 0,
                    "unique_visitors": [],
                    "pages": {},
                    "referrers": {},
                    "devices": {"desktop": 0, "mobile": 0, "bot": 0},
                    "utm_sources": {}
                }
            },
            "recent_events": []
        }

    def _save_data(self):
        """Сохраняет кэш данных в файл."""
        try:
            temp_file = self.filepath + ".tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, indent=2, ensure_ascii=False)
            if os.path.exists(self.filepath):
                os.replace(temp_file, self.filepath)
            else:
                os.rename(temp_file, self.filepath)
        except Exception as e:
            print(f"[ANALYTICS] Error saving analytics data: {e}")

    def _hash_visitor(self, ip: str, ua: str, date_str: str) -> str:
        """Создает анонимный однодневный идентификатор посетителя."""
        salt = f"eduhub_salt_{date_str}"
        raw = f"{ip}_{ua}_{salt}".encode("utf-8")
        return hashlib.sha256(raw).hexdigest()[:12]

    def _detect_device(self, user_agent: str) -> str:
        """Определяет тип устройства: desktop, mobile или bot."""
        ua_lower = user_agent.lower()
        if any(b in ua_lower for b in BOT_KEYWORDS):
            return "bot"
        if any(m in ua_lower for m in ["android", "iphone", "ipad", "mobile", "phone"]):
            return "mobile"
        return "desktop"

    def _clean_referrer(self, raw_ref: Optional[str]) -> str:
        """Извлекает чистый домен реферера."""
        if not raw_ref or raw_ref in ["Direct", "None", ""]:
            return "Direct"
        try:
            parsed = urlparse(raw_ref)
            domain = parsed.netloc.lower()
            if not domain:
                return "Direct"
            if "youtube" in domain or "youtu.be" in domain:
                return "YouTube"
            if "google" in domain:
                return "Google Search"
            if "t.me" in domain or "telegram" in domain:
                return "Telegram"
            if "instagram" in domain:
                return "Instagram"
            if "linkedin" in domain:
                return "LinkedIn"
            if "reddit" in domain:
                return "Reddit"
            if "render" in domain:
                return "Render System"
            if "eduhub-ai" in domain or "localhost" in domain:
                return "Internal Navigation"
            return domain
        except Exception:
            return "Other"

    def record_hit(
        self,
        path: str,
        ip: str = "127.0.0.1",
        user_agent: str = "",
        referrer: Optional[str] = None,
        utm_source: Optional[str] = None,
        utm_medium: Optional[str] = None,
        country: Optional[str] = None
    ):
        """Регистрирует просмотр страницы."""
        ignored_extensions = (".css", ".js", ".png", ".jpg", ".jpeg", ".ico", ".svg", ".json", ".map", ".woff", ".woff2")
        if any(path.endswith(ext) for ext in ignored_extensions):
            return
        if path.startswith(("/static/", "/health", "/favicon.ico")):
            return

        now = datetime.now(timezone.utc)
        today = now.strftime("%Y-%m-%d")
        device = self._detect_device(user_agent)
        is_bot = (device == "bot")
        visitor_id = self._hash_visitor(ip, user_agent, today)
        clean_ref = self._clean_referrer(referrer)

        with self.lock:
            self._cache["all_time"]["total_pageviews"] += 1
            if is_bot:
                self._cache["all_time"]["bot_pageviews"] += 1
            else:
                self._cache["all_time"]["human_pageviews"] += 1

            if visitor_id not in self._cache["all_time"]["unique_visitors"]:
                self._cache["all_time"]["unique_visitors"].append(visitor_id)
                if len(self._cache["all_time"]["unique_visitors"]) > 10000:
                    self._cache["all_time"]["unique_visitors"] = self._cache["all_time"]["unique_visitors"][-10000:]

            if today not in self._cache["daily"]:
                self._cache["daily"][today] = {
                    "total_pageviews": 0,
                    "human_pageviews": 0,
                    "bot_pageviews": 0,
                    "unique_visitors": [],
                    "pages": {},
                    "referrers": {},
                    "devices": {"desktop": 0, "mobile": 0, "bot": 0},
                    "utm_sources": {}
                }

            d_data = self._cache["daily"][today]
            d_data["total_pageviews"] += 1
            if is_bot:
                d_data["bot_pageviews"] += 1
            else:
                d_data["human_pageviews"] += 1

            if visitor_id not in d_data["unique_visitors"]:
                d_data["unique_visitors"].append(visitor_id)

            clean_path = path.split("?")[0]
            d_data["pages"][clean_path] = d_data["pages"].get(clean_path, 0) + 1
            d_data["referrers"][clean_ref] = d_data["referrers"].get(clean_ref, 0) + 1
            d_data["devices"][device] = d_data["devices"].get(device, 0) + 1

            if utm_source:
                d_data["utm_sources"][utm_source] = d_data["utm_sources"].get(utm_source, 0) + 1

            event_entry = {
                "time": now.strftime("%H:%M:%S UTC"),
                "date": today,
                "path": clean_path,
                "visitor_id": visitor_id,
                "is_bot": is_bot,
                "device": device,
                "referrer": clean_ref,
                "country": country or "Unknown"
            }
            self._cache["recent_events"].insert(0, event_entry)
            if len(self._cache["recent_events"]) > 50:
                self._cache["recent_events"] = self._cache["recent_events"][:50]

            self._save_data()

    def get_summary(self) -> Dict[str, Any]:
        """Возвращает агрегированный аналитический отчет."""
        with self.lock:
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            daily_today = self._cache["daily"].get(today, {
                "total_pageviews": 0,
                "human_pageviews": 0,
                "bot_pageviews": 0,
                "unique_visitors": [],
                "pages": {},
                "referrers": {},
                "devices": {"desktop": 0, "mobile": 0, "bot": 0},
                "utm_sources": {}
            })

            sorted_pages = sorted(daily_today.get("pages", {}).items(), key=lambda x: x[1], reverse=True)[:10]
            sorted_referrers = sorted(daily_today.get("referrers", {}).items(), key=lambda x: x[1], reverse=True)[:10]

            return {
                "status": "success",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "today": {
                    "date": today,
                    "total_views": daily_today["total_pageviews"],
                    "human_views": daily_today["human_pageviews"],
                    "bot_views": daily_today["bot_pageviews"],
                    "unique_visitors": len(daily_today["unique_visitors"]),
                    "devices": daily_today["devices"],
                    "top_pages": dict(sorted_pages),
                    "top_referrers": dict(sorted_referrers),
                    "utm_campaigns": daily_today.get("utm_sources", {})
                },
                "all_time": {
                    "total_views": self._cache["all_time"]["total_pageviews"],
                    "human_views": self._cache["all_time"]["human_pageviews"],
                    "bot_views": self._cache["all_time"]["bot_pageviews"],
                    "unique_visitors_count": len(self._cache["all_time"]["unique_visitors"])
                },
                "recent_live_events": self._cache.get("recent_events", [])[:15]
            }

analytics_engine = VisitorAnalyticsEngine()
