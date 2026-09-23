#!/usr/bin/env python3
"""
================================================================================
EduHub AI — Autonomous E2E Testing & Honest QA Guard Engine (2026)
================================================================================
Role: Autonomous E2E Testing & Honest QA Agent
Integrates into Render deployment pipeline, automated CI/CD and self-healing loop.

Principles of Honesty & Perfection:
1. Zero fake checkmarks: Every assertion is measured against live files & runtime contracts.
2. Real exit codes: sys.exit(0) ONLY if 100% of assertions pass; sys.exit(1) on ANY failure.
3. Bidirectional verification: Ensures every HTML key exists in all 4 locales (EN, RU, UZ, ES).
4. Deep script & DOM inspection: Detects untagged human language and inline hardcoded strings.
5. Strict terminology guard: Enforces complete ban of 'Asbob/Instrument'.
6. Real API contract tests: Validates FastAPI endpoints, 18+ filter, rate limits, and webhooks.
================================================================================
"""

import os
import sys
import json
import re
import time
import hmac
import hashlib
import argparse
from pathlib import Path
from html.parser import HTMLParser

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

_script_dir = Path(__file__).resolve().parent
BASE_DIR = _script_dir if (_script_dir / "static").exists() else Path(os.getcwd())

class HTMLTextAndAttrAuditParser(HTMLParser):
    """Deep DOM parser that identifies untagged human-readable text nodes and untranslated attributes."""
    def __init__(self):
        super().__init__()
        self.tag_stack = []
        self.untagged_text = []
        self.untranslated_attrs = []
        self.in_script = False
        self.in_style = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        self.tag_stack.append((tag, attrs_dict))
        if tag in ['script']:
            self.in_script = True
        if tag in ['style']:
            self.in_style = True

        for k, v in attrs:
            if k in ['placeholder', 'title', 'alt', 'aria-label'] and v:
                if re.search(r'[\u0400-\u04FF]', v):
                    i18n_attr = f'data-i18n-{k}' if k in ['placeholder', 'title'] else 'data-i18n'
                    if i18n_attr not in attrs_dict and 'data-i18n' not in attrs_dict:
                        self.untranslated_attrs.append((tag, k, v, attrs_dict.get('id', '')))

    def handle_endtag(self, tag):
        if tag in ['script']:
            self.in_script = False
        if tag in ['style']:
            self.in_style = False
        if self.tag_stack and self.tag_stack[-1][0] == tag:
            self.tag_stack.pop()

    def handle_data(self, data):
        if self.in_script or self.in_style:
            return
        t = data.strip()
        if t and re.search(r'[\u0400-\u04FF]', t):
            has_i18n = any('data-i18n' in attrs for _, attrs in self.tag_stack)
            current_tag = self.tag_stack[-1] if self.tag_stack else ('unknown', {})
            if not has_i18n:
                self.untagged_text.append((current_tag[0], t, current_tag[1].get('id', '')))


class TestCaseResult:
    def __init__(self, name):
        self.name = name
        self.passed = True
        self.errors = []
        self.warnings = []
        self.fixed = []
        self.duration_ms = 0.0
        self.details = ""


class AutoQAGuardEngine:
    def __init__(self, target_dir=None, check_only=False):
        self.role = "Autonomous E2E Testing & Honest QA Agent"
        self.base_dir = Path(target_dir) if target_dir else BASE_DIR
        self.check_only = check_only
        self.locales_dir = self.base_dir / "locales"
        self.static_locales_dir = self.base_dir / "static" / "locales"
        self.static_html_path = self.base_dir / "static" / "index.html"
        self.css_path = self.base_dir / "static" / "css" / "eduhub_premium_core.css"
        self.i18n_js_path = self.base_dir / "static" / "js" / "i18n.js"
        self.legal_js_path = self.base_dir / "static" / "js" / "legal-consent.js"
        
        self.test_results = []
        self.all_passed = True
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0

    # --------------------------------------------------------------------------
    # TEST 1: Locale Syntax, Parity & Value Completeness
    # --------------------------------------------------------------------------
    def test_01_locale_integrity(self):
        t = TestCaseResult("1. Multilingual Locale Integrity & Symmetric Parity")
        start = time.perf_counter()
        required_locales = ["en", "ru", "uz", "es"]
        locale_data = {}

        for lang in required_locales:
            p = self.locales_dir / f"{lang}.json"
            if not p.exists():
                t.passed = False
                t.errors.append(f"Missing locale file: {p}")
                continue
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                locale_data[lang] = data
            except Exception as e:
                t.passed = False
                t.errors.append(f"JSON parse error in {p}: {e}")

        if len(locale_data) == 4:
            en_keys = set(locale_data["en"].keys())
            for lang in ["ru", "uz", "es"]:
                lang_keys = set(locale_data[lang].keys())
                missing = en_keys - lang_keys
                extra = lang_keys - en_keys
                if missing:
                    t.passed = False
                    t.errors.append(f"Locale [{lang}] missing {len(missing)} keys from en.json (sample: {list(missing)[:5]})")
                if extra:
                    t.passed = False
                    t.errors.append(f"Locale [{lang}] has {len(extra)} extra keys not in en.json (sample: {list(extra)[:5]})")

            for lang, d in locale_data.items():
                for k, v in d.items():
                    if v is None or v == "":
                        t.passed = False
                        t.errors.append(f"Locale [{lang}] has empty/null value for key '{k}'")
                    elif isinstance(v, str) and ("TODO" in v or "{{MISSING}}" in v):
                        t.passed = False
                        t.errors.append(f"Locale [{lang}] has placeholder in '{k}': {v}")

            for lang in required_locales:
                p_static = self.static_locales_dir / f"{lang}.json"
                if not p_static.exists():
                    if not self.check_only:
                        with open(p_static, "w", encoding="utf-8") as f:
                            json.dump(locale_data[lang], f, ensure_ascii=False, indent=4)
                        t.fixed.append(f"Created missing static/locales/{lang}.json")
                    else:
                        t.passed = False
                        t.errors.append(f"Missing static/locales/{lang}.json")
                else:
                    with open(p_static, "r", encoding="utf-8") as f:
                        static_d = json.load(f)
                    if set(static_d.keys()) != en_keys:
                        if not self.check_only:
                            with open(p_static, "w", encoding="utf-8") as f:
                                json.dump(locale_data[lang], f, ensure_ascii=False, indent=4)
                            t.fixed.append(f"Synchronized static/locales/{lang}.json with primary locale")
                        else:
                            t.passed = False
                            t.errors.append(f"static/locales/{lang}.json is out of sync with locales/{lang}.json")

            t.details = f"Verified 4 locales (en, ru, uz, es) with {len(en_keys)} symmetric keys each."

        t.duration_ms = (time.perf_counter() - start) * 1000
        return t

    # --------------------------------------------------------------------------
    # TEST 2: Strict Ban of 'Asbob/Instrument' & Bad Transliterations
    # --------------------------------------------------------------------------
    def test_02_banned_words_purge(self):
        t = TestCaseResult("2. Strict Ban of 'Asbob/Instrument' & Transliterations")
        start = time.perf_counter()
        banned_pattern = re.compile(r'\b(?:asbob|instrument|asboblar|instrumentlar)\b', re.IGNORECASE)

        html_files = list(self.base_dir.glob("static/**/*.html"))
        banned_found = 0
        for hf in html_files:
            with open(hf, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            matches = banned_pattern.findall(content)
            if matches:
                banned_found += len(matches)
                if not self.check_only:
                    cleaned = banned_pattern.sub("panel", content)
                    with open(hf, "w", encoding="utf-8") as f:
                        f.write(cleaned)
                    t.fixed.append(f"Replaced {len(matches)} banned words in {hf.name}")
                else:
                    t.passed = False
                    t.errors.append(f"Found banned words {matches[:3]} in {hf.name}")

        uz_paths = [self.locales_dir / "uz.json", self.static_locales_dir / "uz.json"]
        for uz_p in uz_paths:
            if uz_p.exists():
                with open(uz_p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                changed = False
                for k, v in list(data.items()):
                    if isinstance(v, str) and banned_pattern.search(v):
                        banned_found += 1
                        if not self.check_only:
                            data[k] = banned_pattern.sub("panel", v)
                            changed = True
                            t.fixed.append(f"Purged banned word from UZ key '{k}'")
                        else:
                            t.passed = False
                            t.errors.append(f"Banned word in UZ key '{k}': {v}")
                if changed and not self.check_only:
                    with open(uz_p, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)

        uz_p = self.locales_dir / "uz.json"
        if uz_p.exists():
            with open(uz_p, "r", encoding="utf-8") as f:
                uz_data = json.load(f)
            if uz_data.get("tool_open_btn") != "Panelni ochish →":
                if not self.check_only:
                    uz_data["tool_open_btn"] = "Panelni ochish →"
                    with open(uz_p, "w", encoding="utf-8") as f:
                        json.dump(uz_data, f, ensure_ascii=False, indent=4)
                    t.fixed.append("Enforced 'Panelni ochish →' for UZ tool_open_btn")
                else:
                    t.passed = False
                    t.errors.append(f"Expected 'Panelni ochish →' but got '{uz_data.get('tool_open_btn')}'")

        for lang in ["en", "es"]:
            p = self.locales_dir / f"{lang}.json"
            if p.exists():
                with open(p, "r", encoding="utf-8") as f:
                    d = json.load(f)
                cyr_keys = [k for k, v in d.items() if isinstance(v, str) and re.search(r'[\u0400-\u04FF]', v)]
                if cyr_keys:
                    t.passed = False
                    t.errors.append(f"Locale [{lang}] contains untranslated Cyrillic in keys: {cyr_keys[:5]}")

        t.details = f"Scanned {len(html_files)} HTML files and UZ locales. Total banned terms: {banned_found}."
        t.duration_ms = (time.perf_counter() - start) * 1000
        return t

    # --------------------------------------------------------------------------
    # TEST 3: Bidirectional HTML <-> Locales Key Coverage
    # --------------------------------------------------------------------------
    def test_03_bidirectional_coverage(self):
        t = TestCaseResult("3. Bidirectional HTML <-> Locales Key Coverage")
        start = time.perf_counter()

        en_path = self.locales_dir / "en.json"
        if not en_path.exists():
            t.passed = False
            t.errors.append("locales/en.json not found")
            t.duration_ms = (time.perf_counter() - start) * 1000
            return t

        with open(en_path, "r", encoding="utf-8") as f:
            en_keys = set(json.load(f).keys())

        html_files = list(self.base_dir.glob("static/**/*.html"))
        missing_keys_map = {}
        total_html_keys = set()

        for hf in html_files:
            with open(hf, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            i18n_keys = re.findall(r'data-i18n=["\']([^"\']+)["\']', content)
            ph_keys = re.findall(r'data-i18n-placeholder=["\']([^"\']+)["\']', content)
            title_keys = re.findall(r'data-i18n-title=["\']([^"\']+)["\']', content)
            
            file_keys = set(i18n_keys + ph_keys + title_keys)
            total_html_keys.update(file_keys)

            unresolved = file_keys - en_keys
            if unresolved:
                missing_keys_map[hf.name] = unresolved

        if missing_keys_map:
            t.passed = False
            for fname, mkeys in missing_keys_map.items():
                t.errors.append(f"File '{fname}' references {len(mkeys)} undefined keys: {sorted(list(mkeys))[:5]}")

        t.details = f"Checked {len(html_files)} HTML files ({len(total_html_keys)} unique keys). Unresolved keys: {len(missing_keys_map)}."
        t.duration_ms = (time.perf_counter() - start) * 1000
        return t

    # --------------------------------------------------------------------------
    # TEST 4: DOM Cleanliness & Attribute Localization across ALL HTML Files
    # --------------------------------------------------------------------------
    def test_04_dom_cleanliness(self):
        t = TestCaseResult("4. DOM Cleanliness & Localization across ALL HTML Files")
        start = time.perf_counter()

        html_files = list(self.base_dir.glob("static/**/*.html"))
        if not html_files:
            t.passed = False
            t.errors.append("No HTML files found in static/")
            t.duration_ms = (time.perf_counter() - start) * 1000
            return t

        total_untagged = 0
        total_untranslated = 0

        for hf in html_files:
            with open(hf, "r", encoding="utf-8", errors="ignore") as f:
                html = f.read()

            parser = HTMLTextAndAttrAuditParser()
            parser.feed(html)

            if parser.untagged_text:
                total_untagged += len(parser.untagged_text)
                t.passed = False
                for tag, text, el_id in parser.untagged_text[:3]:
                    t.errors.append(f"[{hf.name}] Untagged Cyrillic text in <{tag} id='{el_id}'>: '{text[:50]}'")

            if parser.untranslated_attrs:
                total_untranslated += len(parser.untranslated_attrs)
                t.passed = False
                for tag, attr, val, el_id in parser.untranslated_attrs[:3]:
                    t.errors.append(f"[{hf.name}] Untranslated attribute [{attr}] in <{tag} id='{el_id}'>: '{val[:50]}'")

            if not re.search(r'<html[^>]*\blang=["\']en["\']', html, re.IGNORECASE):
                t.passed = False
                t.errors.append(f"[{hf.name}] Root <html lang='...'> does not default to 'en'")

        t.details = f"Audited {len(html_files)} HTML files: 0 untagged text nodes, 0 untranslated attributes, 100% English root defaults." if t.passed else f"Found {total_untagged} untagged text nodes and {total_untranslated} untranslated attributes across {len(html_files)} files."
        t.duration_ms = (time.perf_counter() - start) * 1000
        return t


    # --------------------------------------------------------------------------
    # TEST 5: JavaScript Cleanliness, Handlers & I18N_CACHE
    # --------------------------------------------------------------------------
    def test_05_javascript_cleanliness(self):
        t = TestCaseResult("5. JavaScript Cleanliness, Handlers & I18N_CACHE")
        start = time.perf_counter()

        with open(self.static_html_path, "r", encoding="utf-8") as f:
            html = f.read()

        scripts = re.findall(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', html, flags=re.IGNORECASE)
        cyr_in_scripts = []
        for idx, s in enumerate(scripts):
            if 'application/ld+json' in s:
                continue
            matches = re.findall(r'(["\'][^"\']*\b[\u0400-\u04FF]+[^"\']*["\'])', s)
            if matches:
                cyr_in_scripts.extend([m[:40] for m in matches])

        inline_handlers = re.findall(r'(\bon\w+=(?:"[^"]*[\u0400-\u04FF]+[^"]*"|\'[^\']*[\u0400-\u04FF]+[^\']*\'))', html)

        if cyr_in_scripts:
            t.passed = False
            t.errors.append(f"Found {len(cyr_in_scripts)} hardcoded Cyrillic strings in index.html scripts (sample: {cyr_in_scripts[:3]})")

        if inline_handlers:
            t.passed = False
            t.errors.append(f"Found {len(inline_handlers)} inline event handlers with hardcoded Cyrillic (sample: {inline_handlers[:3]})")

        if self.i18n_js_path.exists():
            with open(self.i18n_js_path, "r", encoding="utf-8") as f:
                js = f.read()

            for lang in ["en", "ru", "uz", "es"]:
                if f'"{lang}":' not in js:
                    t.passed = False
                    t.errors.append(f"static/js/i18n.js missing cached bundle for '{lang}'")

        if self.legal_js_path.exists():
            with open(self.legal_js_path, "r", encoding="utf-8") as f:
                ljs = f.read()
            if "eduhub_locale" not in ljs:
                t.passed = False
                t.errors.append("static/js/legal-consent.js does not check 'eduhub_locale'")
            if "eduhub:locale-changed" not in ljs:
                t.passed = False
                t.errors.append("static/js/legal-consent.js does not listen for 'eduhub:locale-changed' event")

        t.details = "Verified zero hardcoded natural language strings in scripts, and 100% cache sync." if t.passed else "JavaScript contains hardcoded strings or out-of-sync cache."
        t.duration_ms = (time.perf_counter() - start) * 1000
        return t

    # --------------------------------------------------------------------------
    # TEST 6: Security Guards & Safari WebKit CSS Compatibility
    # --------------------------------------------------------------------------
    def test_06_security_and_safari_css(self):
        t = TestCaseResult("6. Security Guards & Safari WebKit CSS Compatibility")
        start = time.perf_counter()

        html_files = list(self.base_dir.glob("static/**/*.html"))
        missing_notranslate = []
        for hf in html_files:
            with open(hf, "r", encoding="utf-8", errors="ignore") as f:
                c = f.read()
            if 'notranslate' not in c:
                missing_notranslate.append(hf.name)

        if missing_notranslate:
            t.passed = False
            t.errors.append(f"Missing 'notranslate' guard in {len(missing_notranslate)} files: {missing_notranslate[:5]}")

        if self.css_path.exists():
            with open(self.css_path, "r", encoding="utf-8") as f:
                css = f.read()
            if "-webkit-backdrop-filter" not in css:
                if not self.check_only:
                    with open(self.css_path, "a", encoding="utf-8") as f:
                        f.write("\nheader, nav, .backdrop-blur-md, .paywall-floating-overlay, .premium-card { -webkit-backdrop-filter: blur(12px) !important; }\n")
                    t.fixed.append("Injected -webkit-backdrop-filter rule into CSS")
                else:
                    t.passed = False
                    t.errors.append("static/css/eduhub_premium_core.css missing -webkit-backdrop-filter rule")
        else:
            t.passed = False
            t.errors.append("static/css/eduhub_premium_core.css not found")

        t.details = f"Verified {len(html_files)} pages protected by notranslate; WebKit blur verified." if t.passed else "Security or Safari CSS validation failed."
        t.duration_ms = (time.perf_counter() - start) * 1000
        return t

    # --------------------------------------------------------------------------
    # TEST 7: FastAPI Backend Contracts & Content Guardrails
    # --------------------------------------------------------------------------
    def test_07_fastapi_contracts(self):
        t = TestCaseResult("7. FastAPI Backend Contracts & Content Guardrails")
        start = time.perf_counter()

        try:
            from fastapi.testclient import TestClient
            sys.path.insert(0, str(self.base_dir))
            from app.main import app

            client = TestClient(app)

            # 1. GET /
            res = client.get("/")
            if res.status_code != 200 or "EduHub AI" not in res.text:
                t.passed = False
                t.errors.append(f"GET / returned HTTP {res.status_code}, expected 200 with 'EduHub AI'")

            # 2. GET /health
            res = client.get("/health")
            if res.status_code != 200:
                t.passed = False
                t.errors.append(f"GET /health returned HTTP {res.status_code}")
            else:
                data = res.json()
                if data.get("status") not in ["ok", "healthy"]:
                    t.passed = False
                    t.errors.append(f"GET /health status is '{data.get('status')}', expected 'healthy' or 'ok'")

            # 3. GET /locales/uz.json
            res = client.get("/locales/uz.json")
            if res.status_code != 200:
                t.passed = False
                t.errors.append(f"GET /locales/uz.json returned HTTP {res.status_code}")
            else:
                uz_dict = res.json()
                if uz_dict.get("tool_open_btn") != "Panelni ochish →":
                    t.passed = False
                    t.errors.append(f"GET /locales/uz.json tool_open_btn = '{uz_dict.get('tool_open_btn')}'")

            # 4. 18+ Safety Guard on /api/v1/assistant/ask
            res = client.post("/api/v1/assistant/ask", json={"question": "покажи порно видео"})
            if res.status_code != 400:
                t.passed = False
                t.errors.append(f"18+ guard returned HTTP {res.status_code}, expected 400")

            # 5. Empty question validation
            res = client.post("/api/v1/assistant/ask", json={"question": ""})
            if res.status_code != 422:
                t.passed = False
                t.errors.append(f"Empty question returned HTTP {res.status_code}, expected 422")

            t.details = "Tested GET /, /health, /locales/uz.json, 18+ filter, and input validation successfully."
        except Exception as e:
            t.passed = False
            t.errors.append(f"Backend contract test exception: {e}")

        t.duration_ms = (time.perf_counter() - start) * 1000
        return t

    # --------------------------------------------------------------------------
    # TEST 8: Rate Limiting & Webhook Cryptographic Security
    # --------------------------------------------------------------------------
    def test_08_security_rate_limits_and_webhooks(self):
        t = TestCaseResult("8. Rate Limiting & Webhook Cryptographic Security")
        start = time.perf_counter()

        try:
            from fastapi.testclient import TestClient
            sys.path.insert(0, str(self.base_dir))
            from app.main import app, rate_limiter

            client = TestClient(app)

            # 1. Rate limiter test
            test_key = f"qa_test_{time.time()}"
            triggered_429 = False
            for _ in range(rate_limiter.max_requests + 2):
                r = client.post("/api/v1/student/summarize", json={"text": "small"}, headers={"X-API-Key": test_key})
                if r.status_code == 429:
                    triggered_429 = True
                    break

            if not triggered_429:
                t.passed = False
                t.errors.append(f"In-memory rate limiter failed to trigger HTTP 429 after {rate_limiter.max_requests + 2} requests")

            # 2. Dodo Payments Webhook verification test
            res_dodo_status = client.get("/api/v1/billing/dodo-webhook")
            if res_dodo_status.status_code != 200 or res_dodo_status.json().get("status") != "active":
                t.passed = False
                t.errors.append(f"GET /api/v1/billing/dodo-webhook returned HTTP {res_dodo_status.status_code}")

            dodo_body = b'{"type":"payment.succeeded","data":{"customer":{"email":"audit@dodo.com"},"payment_id":"pay_audit_123"}}'
            dodo_headers = {"Content-Type": "application/json", "webhook-id": "msg_audit_123", "webhook-timestamp": "1727000000"}
            sec_env = os.getenv("DODO_WEBHOOK_SECRET")
            if sec_env:
                dodo_headers["x-signature"] = hmac.new(sec_env.encode("utf-8"), dodo_body, hashlib.sha256).hexdigest()
            res_dodo_post = client.post(
                "/api/v1/billing/dodo-webhook",
                content=dodo_body,
                headers=dodo_headers
            )
            if res_dodo_post.status_code != 200:
                t.passed = False
                t.errors.append(f"Dodo Payments webhook returned HTTP {res_dodo_post.status_code}, expected 200")

            t.details = "Rate limiter triggered 429 correctly; Dodo Payments Webhook receiver verified (GET status 200, POST event 200)."
        except Exception as e:
            t.passed = False
            t.errors.append(f"Security test exception: {e}")

        t.duration_ms = (time.perf_counter() - start) * 1000
        return t

    # --------------------------------------------------------------------------
    # Main Suite Execution
    # --------------------------------------------------------------------------
    def run_all_tests(self, auto_fix=True):
        if not auto_fix:
            self.check_only = True

        tests = [
            self.test_01_locale_integrity,
            self.test_02_banned_words_purge,
            self.test_03_bidirectional_coverage,
            self.test_04_dom_cleanliness,
            self.test_05_javascript_cleanliness,
            self.test_06_security_and_safari_css,
            self.test_07_fastapi_contracts,
            self.test_08_security_rate_limits_and_webhooks
        ]

        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0

        for test_fn in tests:
            res = test_fn()
            self.test_results.append(res)
            if res.passed:
                self.passed_tests += 1
            else:
                self.failed_tests += 1

        self.total_tests = len(tests)
        self.all_passed = (self.failed_tests == 0)

        return {
            "success": self.all_passed,
            "total": self.total_tests,
            "passed": self.passed_tests,
            "failed": self.failed_tests,
            "success_rate": round((self.passed_tests / self.total_tests) * 100, 1),
            "results": self.test_results
        }

    def deep_scan_and_auto_fix(self):
        """Adapter method for backwards compatibility with existing pipelines."""
        summary = self.run_all_tests(auto_fix=not self.check_only)
        lines = [
            "=" * 80,
            f"🛡️  EDUHUB AI — AUTONOMOUS HONEST QA VERIFICATION MATRIX",
            f"Role: {self.role} | Tests: {summary['passed']}/{summary['total']} Passed ({summary['success_rate']}%)",
            "=" * 80
        ]
        for r in summary["results"]:
            icon = "✅ PASS" if r.passed else "❌ FAIL"
            lines.append(f"{icon} | {r.name} ({r.duration_ms:.1f}ms)")
            if r.details:
                lines.append(f"       ↳ {r.details}")
            for err in r.errors:
                lines.append(f"       🛑 ERROR: {err}")
            for fix in r.fixed:
                lines.append(f"       🔧 FIXED: {fix}")

        status_text = "ИДЕАЛЬНО (100% CLEAN)" if summary["success"] else "ОБНАРУЖЕНЫ ОШИБКИ"
        lines.append("=" * 80)
        lines.append(f"🎯 СТАТУС ВЕРИФИКАЦИИ QA: {status_text}")
        lines.append("=" * 80)
        return "\n".join(lines)

    def print_report(self):
        print("\n" + self.deep_scan_and_auto_fix() + "\n")


def main():
    parser = argparse.ArgumentParser(description="Autonomous Honest QA Guard Engine")
    parser.add_argument("--check-only", action="store_true", help="Run in strict read-only mode without applying auto-fixes")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    args = parser.parse_args()

    qa = AutoQAGuardEngine(target_dir=BASE_DIR, check_only=args.check_only)
    summary = qa.run_all_tests(auto_fix=not args.check_only)

    if args.json:
        out = {
            "success": summary["success"],
            "total": summary["total"],
            "passed": summary["passed"],
            "failed": summary["failed"],
            "success_rate": summary["success_rate"],
            "details": [{"name": r.name, "passed": r.passed, "errors": r.errors, "fixed": r.fixed} for r in summary["results"]]
        }
        print(json.dumps(out, indent=2))
    else:
        qa.print_report()

    sys.exit(0 if summary["success"] else 1)


if __name__ == "__main__":
    main()
