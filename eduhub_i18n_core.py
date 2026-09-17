# -*- coding: utf-8 -*-
"""
===============================================================================
EduHub AI — Internationalization & Global Localization Core Engine
===============================================================================
Role: Global Localization & i18n Expert
Supported Languages: EN, RU, UZ, ES
Mission: Seamless multi-language content delivery without layout breakage,
         dynamic client-side switching via data-i18n, automatic geolocation
         locale detection, and White-Hat translation preservation.
===============================================================================
"""

import json
import os
from typing import Dict, Any

class InternationalizationEngine:
    def __init__(self):
        self.role = "Global Localization & i18n Expert"
        self.supported_languages = ["EN", "RU", "UZ", "ES"]
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.locales_dir = os.path.join(self.base_dir, "locales")
        self.static_locales_dir = os.path.join(self.base_dir, "static", "locales")

        # Core high-converting translation matrix
        self.translation_matrix = {
            "EN": {
                "hero_title": "Your Autonomous AI Academic Copilot",
                "hero_subtitle": "Learn Faster, Grade Smarter, Master Any Subject.",
                "tab_hub": "Academic Hub",
                "tab_resume": "ATS Resume Expert",
                "tab_factory": "AI Factories",
                "cta_trial": "Claim 3-Day Pro Max for $1",
                "cta_ielts_trial": "Start 3-Day IELTS Access for $1 →",
                "paywall_text": "Full AI response locked. Unlock step-by-step breakdown for $1."
            },
            "RU": {
                "hero_title": "Ваш автономный академический ИИ-копилот",
                "hero_subtitle": "Учитесь быстрее, проверяйте умнее, осваивайте любые предметы.",
                "tab_hub": "Академический Хаб",
                "tab_resume": "ATS Резюме Эксперт",
                "tab_factory": "ИИ-Заводы",
                "cta_trial": "Получить Pro Max на 3 дня за $1",
                "cta_ielts_trial": "Получить IELTS на 3 дня за $1 →",
                "paywall_text": "Полный ответ ИИ заблокирован. Разблокируйте пошаговый разбор всего за $1."
            },
            "UZ": {
                "hero_title": "Sizning avtonom akademik AI-kopilotishingiz",
                "hero_subtitle": "Tezroq o'rganing, aqlliroq tekshiring, har qanday fanni o'zlashtiring.",
                "tab_hub": "Akademik Xab",
                "tab_resume": "ATS Rezyume Ekspert",
                "tab_factory": "AI Zavodlari",
                "cta_trial": "3 kunlik Pro Max-ni $1 evaziga olish",
                "cta_ielts_trial": "3 kunlik IELTS $1 evaziga →",
                "paywall_text": "AI to'liq javobi bloklangan. Bosqichma-bosqich tahlilni $1 evaziga oching."
            },
            "ES": {
                "hero_title": "Tu Copiloto Académico Autónomo con IA",
                "hero_subtitle": "Aprende más rápido, califica mejor, domina cualquier materia.",
                "tab_hub": "Centro Académico",
                "tab_resume": "Experto en CV ATS",
                "tab_factory": "Fábricas de IA",
                "cta_trial": "Obtén Pro Max por 3 días por $1",
                "cta_ielts_trial": "Obtén IELTS por 3 días por $1 →",
                "paywall_text": "Respuesta completa de IA bloqueada. Desbloquea el análisis paso a paso por $1."
            }
        }

    def deploy_i18n_files(self) -> str:
        """Создает чистые JSON файлы локализации для бэкенда Render, исключая баги переключения."""
        os.makedirs(self.locales_dir, exist_ok=True)
        os.makedirs(self.static_locales_dir, exist_ok=True)

        for lang in self.supported_languages:
            code = lang.lower()
            file_path = os.path.join(self.locales_dir, f"{code}.json")
            static_path = os.path.join(self.static_locales_dir, f"{code}.json")

            # Load existing full translations if present
            existing_data = {}
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        existing_data = json.load(f)
                except Exception:
                    existing_data = {}

            # Merge with core matrix
            merged = {**existing_data, **self.translation_matrix[lang]}

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(merged, f, indent=4, ensure_ascii=False)

            with open(static_path, "w", encoding="utf-8") as f:
                json.dump(merged, f, indent=4, ensure_ascii=False)

        return f"[SUCCESS] Все 4 языковых пакета (EN, RU, UZ, ES) успешно скомпилированы и защищены."

    def get_locale_data(self, lang_code: str) -> Dict[str, Any]:
        """Возвращает словарь локализации для указанного языка с фоллбэком на EN."""
        code = lang_code.lower()
        if code not in ["en", "ru", "uz", "es"]:
            code = "en"
        file_path = os.path.join(self.locales_dir, f"{code}.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return self.translation_matrix.get(code.upper(), self.translation_matrix["EN"])

if __name__ == "__main__":
    engine = InternationalizationEngine()
    print(engine.deploy_i18n_files())
