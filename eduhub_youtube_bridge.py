#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
EduHub AI & YouTube Media — Inter-Agent Bridge (Cross-Project Integration Matrix)
===============================================================================
Миссия: Сквозная интеграция продаж ИИ-продуктов EduHub SaaS с конвейером
        производства YouTube Shorts без ручного вмешательства.
===============================================================================
"""

import os
import sys
import json
import time
import argparse
import urllib.parse
from datetime import datetime
from typing import Dict, Any, Optional, Union

# Обеспечение корректной UTF-8 кодировки консоли
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


# =============================================================================
# 1. ШЛЮЗ МЕЖПРОЕКТНОЙ ИНТЕГРАЦИИ (INTER-AGENT BRIDGE)
# =============================================================================

class InterAgentBridge:
    """Изолированный файл обмена и матрица синхронизации между SaaS и YouTube."""

    def __init__(self, bridge_file: str = "api_inter_bridge.json"):
        self.bridge_file = bridge_file
        self.role = "Cross-Project Integration Matrix"
        self.last_payload: Optional[Dict[str, Any]] = None

    def sync_projects(
        self, 
        product_name: str, 
        hook_pain: str, 
        target_channel: str, 
        custom_url: Optional[str] = None
    ) -> str:
        """SaaS-Директор передает данные о продукте в Медиа-Директор."""
        # Генерация чистого production HTTPS URL с UTM-метками
        if custom_url:
            base_url = custom_url
        else:
            slug_map = {
                "ai e-com factory": "tools/marketplace-lab",
                "marketplace lab": "tools/marketplace-lab",
                "ielts": "tools/essay-grader",
                "cambridge ielts": "tools/essay-grader",
                "ats resume": "tools/ats-resume",
                "resume": "tools/ats-resume",
                "teacher lab": "tools/teacher-lab",
                "blueprints": "blueprints"
            }
            clean_key = product_name.lower().strip()
            route = "blueprints"
            for k, v in slug_map.items():
                if k in clean_key:
                    route = v
                    break
            base_url = f"https://eduhub-ai.onrender.com/{route}"

        # Добавление строгих UTM-меток
        channel_slug = target_channel.lower().replace(" ", "_")
        prod_slug = product_name.lower().replace(" ", "_").replace("/", "_")
        utm_params = urllib.parse.urlencode({
            "utm_source": "youtube_shorts",
            "utm_medium": "organic_video",
            "utm_campaign": channel_slug,
            "utm_content": prod_slug
        })
        destination_url = f"{base_url}?{utm_params}" if "?" not in base_url else f"{base_url}&{utm_params}"

        payload = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "trigger_event": "PRODUCT_MARKETING_PUSH",
            "data": {
                "promote_product": product_name,
                "user_pain_point": hook_pain,
                "target_youtube_slot": target_channel,
                "destination_url": destination_url
            },
            "status": "PENDING_MEDIA_CONSUMPTION"
        }

        self.last_payload = payload
        with open(self.bridge_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4, ensure_ascii=False)

        return f"[INTEGRATION] Успешно! Продукт '{product_name}' отправлен в медиа-конвейер для канала {target_channel}."

    def fetch_marketing_triggers(self) -> Union[Dict[str, Any], str]:
        """YouTube-Директор считывает файл и забирает ТЗ для автоматического Shorts."""
        if not os.path.exists(self.bridge_file):
            return "STATUS: Новых маркетинговых триггеров от EduHub не поступало."

        with open(self.bridge_file, "r", encoding="utf-8") as f:
            try:
                bridge_data = json.load(f)
            except Exception as e:
                return f"ERROR: Ошибка чтения моста: {e}"

        if bridge_data.get("status") == "PENDING_MEDIA_CONSUMPTION":
            # Меняем статус, чтобы не дублировать Shorts
            bridge_data["status"] = "PROCESSED_BY_YOUTUBE"
            bridge_data["consumed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.bridge_file, "w", encoding="utf-8") as f:
                json.dump(bridge_data, f, indent=4, ensure_ascii=False)

            return {
                "execute": True,
                "task": bridge_data["data"]
            }

        return "STATUS: Все триггеры уже обработаны. Конвейер Shorts заполнен."

    def record_production_result(self, script_data: Dict[str, Any]) -> None:
        """Записывает готовый виральный сценарий обратно в мост для архивации."""
        if not os.path.exists(self.bridge_file):
            return
        with open(self.bridge_file, "r", encoding="utf-8") as f:
            bridge_data = json.load(f)
        
        bridge_data["status"] = "COMPLETED_MEDIA_PRODUCED"
        bridge_data["youtube_production"] = script_data
        
        with open(self.bridge_file, "w", encoding="utf-8") as f:
            json.dump(bridge_data, f, indent=4, ensure_ascii=False)


# =============================================================================
# 2. АГЕНТ-АНАЛИТИК EDUHUB SAAS (SAAS CEO LOGIC)
# =============================================================================

class EduHubSaaSAgent:
    """
    SaaS CEO & Агент-Аналитик (CRO).
    Отслеживает воронку, анализирует просадки и генерирует целевые пуши в мост.
    """

    CATALOG_PRODUCTS = [
        {
            "product_name": "AI E-com Factory",
            "hook_pain": "Селлеры тратят по 3 дня на SEO-описания и карточки Uzum/Wildberries, теряя продажи в сезон.",
            "target_channel": "Channel_5_Marketplace_AI",
            "custom_url": "https://eduhub-ai.onrender.com/tools/marketplace-lab"
        },
        {
            "product_name": "Cambridge IELTS Band 8.5+ AI Examiner",
            "hook_pain": "Студенты платят $50/час репетиторам, но срезаются на Task 2 из-за грамматических клише.",
            "target_channel": "Channel_1_Edu_Exam",
            "custom_url": "https://eduhub-ai.onrender.com/tools/essay-grader"
        },
        {
            "product_name": "ATS Resume Tailor & Humanizer",
            "hook_pain": "92% резюме отсеиваются роботами ATS до того, как их увидит живой HR-рекрутер.",
            "target_channel": "Channel_3_Career_Tech",
            "custom_url": "https://eduhub-ai.onrender.com/tools/ats-resume"
        },
        {
            "product_name": "AI Teacher Lab & Lesson Wizard",
            "hook_pain": "Преподаватели тратят по 4 часа каждый вечер на ручную проверку тестов и планов уроков.",
            "target_channel": "Channel_2_Teacher_Tools",
            "custom_url": "https://eduhub-ai.onrender.com/tools/teacher-lab"
        }
    ]

    def __init__(self, bridge: InterAgentBridge):
        self.bridge = bridge

    def detect_and_dispatch_push(self, product_index: int = 0) -> str:
        prod = self.CATALOG_PRODUCTS[product_index % len(self.CATALOG_PRODUCTS)]
        print(f"[*] [EduHub SaaS CEO]: Анализ конверсии зафиксировал триггер для '{prod['product_name']}'...")
        msg = self.bridge.sync_projects(
            product_name=prod["product_name"],
            hook_pain=prod["hook_pain"],
            target_channel=prod["target_channel"],
            custom_url=prod["custom_url"]
        )
        print(f"[+] [EduHub SaaS CEO]: {msg}")
        return msg


# =============================================================================
# 3. АГЕНТ-ТРЕНДОЛОГ И СЦЕНАРИСТ YOUTUBE (YOUTUBE MEDIA CEO LOGIC)
# =============================================================================

class YouTubeMediaAgent:
    """
    YouTube Media CEO, Агент-Трендолог и Агент-Сценарист.
    Каждые 4 часа опрашивает мост и генерирует виральные Shorts.
    """

    def __init__(self, bridge: InterAgentBridge):
        self.bridge = bridge

    def generate_viral_shorts_script(self, task: Dict[str, Any]) -> Dict[str, Any]:
        product = task.get("promote_product", "EduHub AI")
        pain = task.get("user_pain_point", "")
        channel = task.get("target_youtube_slot", "Main_Channel")
        url = task.get("destination_url", "https://eduhub-ai.onrender.com/")

        return {
            "title": f"Секрет ИИ: Как решить проблему '{product}' за 60 секунд | Лайфхак",
            "target_channel": channel,
            "duration_seconds": 58,
            "format": "Interactive Shorts / Fast-Paced Lifehack",
            "pacing": "160-170 words per minute, high energy, no fluff",
            "storyboard": [
                {
                    "timing": "00:00 - 00:03",
                    "speaker": "Voiceover (ElevenLabs Adam / Dynamic Energy)",
                    "visual_cue": "[Быстрый зум на экран, красный акцент, звук 'Whoosh']",
                    "script_text": f"Ты до сих пор делаешь это вручную?! {pain.split(',')[0]}?!"
                },
                {
                    "timing": "00:03 - 00:15",
                    "speaker": "Voiceover",
                    "visual_cue": "[Таймлапс уставшего человека за полночь, счетчик упущенного времени и денег]",
                    "script_text": "Перестань сливать время впустую. 90% специалистов даже не догадываются, что этот процесс уже полностью автоматизирован нейросетями."
                },
                {
                    "timing": "00:15 - 00:42",
                    "speaker": "Voiceover + Screen Capture",
                    "visual_cue": f"[Запись экрана: сайт EduHub AI, запуск {product}, 1 клик, генерация решения]",
                    "script_text": f"Смотри: открываем {product}. Вставляем исходный запрос, жмем 'Сгенерировать' — и ИИ за 5 секунд выдает безупречный результат академического уровня с готовым оформлением."
                },
                {
                    "timing": "00:42 - 00:58",
                    "speaker": "Voiceover",
                    "visual_cue": "[Указательная стрелка вниз, интерфейс матового стекла, кликабельный бейдж]",
                    "script_text": "Хочешь протестировать бесплатно прямо сейчас? Прямая ссылка закреплена в первом комментарии под этим видео. Сохрани, чтобы не потерять!"
                }
            ],
            "pinned_comment": f"🚀 Протестируй '{product}' онлайн: 👉 {url}\n\nПопробуй в интерактивной песочнице прямо сейчас без сложных настроек!",
            "hashtags": ["#Shorts", "#ИИ", "#Лайфхак", "#EduHub", "#Нейросети", "#Продуктивность"]
        }

    def process_bridge_queue(self) -> Dict[str, Any]:
        print("[*] [YouTube Media CEO]: Проверка входящих маркетинговых триггеров от EduHub...")
        result = self.bridge.fetch_marketing_triggers()

        if isinstance(result, str):
            print(f"[-] [YouTube Media CEO]: {result}")
            return {"status": "NO_TASKS", "message": result}

        task = result["task"]
        print(f"[+] [YouTube Media CEO]: Получено ТЗ на продвижение '{task['promote_product']}' для слота {task['target_youtube_slot']}!")
        
        script = self.generate_viral_shorts_script(task)
        self.bridge.record_production_result(script)
        print("[+] [YouTube Media CEO]: Виральный сценарий Shorts сгенерирован и зафиксирован в мосте!")
        
        return {
            "status": "SUCCESS",
            "task": task,
            "script": script
        }


# =============================================================================
# 4. АВТОНОМНЫЙ QA-АГЕНТ (QUALITY ASSURANCE GATEWAY)
# =============================================================================

class QABridgeAgent:
    """
    Автономный QA-Агент.
    Контролирует чистоту передачи ссылок (валидный HTTPS, домен eduhub, UTM),
    отсутствие запрещенных транслитов и орфографическую корректность.
    """

    FORBIDDEN_TERMS = ["asbob", "zashchita", "analiz", "undefined", "null", "localhost", "127.0.0.1"]

    @classmethod
    def audit_bridge_state(cls, bridge_file: str = "api_inter_bridge.json") -> Dict[str, Any]:
        print("\n" + "=" * 70)
        print("🛡️  QA-AGENT AUDIT: ПРОВЕРКА МОСТА EDUHUB <-> YOUTUBE")
        print("=" * 70)

        if not os.path.exists(bridge_file):
            print("[-] FAIL: Файл моста не найден!")
            return {"passed": False, "errors": ["File missing"]}

        with open(bridge_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        errors = []
        checks = []

        # 1. Проверка структуры
        required_keys = ["timestamp", "trigger_event", "data", "status"]
        missing = [k for k in required_keys if k not in data]
        if missing:
            errors.append(f"Пропущены обязательные ключи: {missing}")
        else:
            checks.append("Структура payload соответствует протоколу inter-agent API")

        # 2. Проверка destination_url
        url = data.get("data", {}).get("destination_url", "")
        if not url.startswith("https://eduhub-ai.onrender.com"):
            errors.append(f"Недопустимый домен в destination_url: {url}")
        elif "utm_source=youtube_shorts" not in url:
            errors.append(f"Отсутствуют обязательные UTM-метки в destination_url: {url}")
        else:
            checks.append("Destination URL валиден (HTTPS + корректный production домен + UTM-метки)")

        # 3. Проверка чистоты текстов на запрещенные слова и транслит
        text_corpus = json.dumps(data, ensure_ascii=False).lower()
        for bad in cls.FORBIDDEN_TERMS:
            if bad in text_corpus:
                errors.append(f"Обнаружен запрещенный/неотфильтрованный термин '{bad}'")
        if not any(b in text_corpus for b in cls.FORBIDDEN_TERMS):
            checks.append("Лингвистическая чистота подтверждена (нет транслита, undefined и localhost)")

        # 4. Проверка сгенерированного сценария
        production = data.get("youtube_production")
        if production:
            if not production.get("storyboard") or len(production.get("storyboard")) < 3:
                errors.append("Сценарий не содержит полной раскадровки (Hook, Problem, Solution, CTA)")
            else:
                checks.append("Раскадровка Shorts полностью укомплектована таймингами и CTA")

            pinned = production.get("pinned_comment", "")
            if url not in pinned:
                errors.append("Закрепленный комментарий не содержит целевой ссылки destination_url")
            else:
                checks.append("Закрепленный комментарий синхронизирован с целевой ссылкой")

        passed = (len(errors) == 0)
        
        for c in checks:
            print(f"  ✅ {c}")
        for e in errors:
            print(f"  ❌ {e}")

        print("-" * 70)
        if passed:
            print("🎯 РЕЗУЛЬТАТ QA: СЕРТИФИЦИРОВАНО (100% ВАЛИДНОСТЬ МОСТА)")
        else:
            print("⚠️ РЕЗУЛЬТАТ QA: ОБНАРУЖЕНЫ ОШИБКИ")
        print("=" * 70 + "\n")

        return {
            "passed": passed,
            "checks": checks,
            "errors": errors
        }


# =============================================================================
# 5. ТОЧКА ВХОДА (CLI И ДЕМОНСТРАЦИЯ)
# =============================================================================

def main():
    bridge = InterAgentBridge()
    
    # Пример 1 из задания: EduHub сообщает, что нужно продвинуть "AI E-com Factory"
    print("=" * 70)
    print("🚀 ЭТАП 1: EduHub SaaS отправляет триггер в мост...")
    print("=" * 70)
    sync_msg = bridge.sync_projects(
        product_name="AI E-com Factory", 
        hook_pain="Как создать 30 сценариев для Reels и карточки Uzum за 1 клик", 
        target_channel="Channel_5_Marketplace_AI"
    )
    print(sync_msg)

    # Пример 2 из задания: YouTube-робот считывает задание
    print("\n" + "=" * 70)
    print("🎬 ЭТАП 2: YouTube Media считывает мост и генерирует Shorts...")
    print("=" * 70)
    yt_agent = YouTubeMediaAgent(bridge)
    prod_result = yt_agent.process_bridge_queue()

    # Пример 3: QA-контроль
    print("=" * 70)
    print("🛡️  ЭТАП 3: QA-Агент проверяет ссылки и тексты перелива трафика...")
    print("=" * 70)
    QABridgeAgent.audit_bridge_state(bridge.bridge_file)


if __name__ == "__main__":
    main()
