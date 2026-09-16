import os
import sys
import json
import requests
import subprocess
import xml.etree.ElementTree as ET
import re

if hasattr(sys.stdout, 'reconfigure'):

    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test_global_growth_engine():
    print("==================================================================")
    print("🌍 AUDIT: GLOBAL GROWTH ENGINE (PWA, pSEO, VIRAL OMNI-SHARE)")
    print("==================================================================")

    # 1. PWA Manifest & Service Worker Verification
    print("\n--- 1. PWA Manifest & Service Worker Validation ---")
    res_manifest = requests.get(f"{BASE_URL}/static/manifest.json", timeout=5)
    assert res_manifest.status_code == 200, f"manifest.json failed: {res_manifest.status_code}"
    manifest_data = res_manifest.json()
    assert manifest_data.get("display") == "standalone", "manifest display must be standalone"
    assert "EduHub AI" in manifest_data.get("name", ""), "manifest name invalid"
    assert len(manifest_data.get("icons", [])) >= 2, "manifest must contain at least 2 icons"
    print("  [PASS] /static/manifest.json -> HTTP 200 OK (Standalone mode + icons verified)")

    res_sw = requests.get(f"{BASE_URL}/static/sw.js", timeout=5)
    assert res_sw.status_code == 200, f"sw.js failed: {res_sw.status_code}"
    assert "CACHE_NAME" in res_sw.text, "sw.js missing CACHE_NAME"
    assert "addEventListener('fetch'" in res_sw.text, "sw.js missing fetch listener"
    print("  [PASS] /static/sw.js -> HTTP 200 OK (ServiceWorker caching verified)")

    # 2. PWA Install & Viral Share Scripts Syntax Validation
    print("\n--- 2. PWA & Viral Share Client Scripts ---")
    pwa_js = os.path.join(BASE_DIR, "static", "js", "pwa-install.js")
    viral_js = os.path.join(BASE_DIR, "static", "js", "viral-share.js")
    for script_file, name in [(pwa_js, "pwa-install.js"), (viral_js, "viral-share.js")]:
        res_node = subprocess.run(["node", "-c", script_file], capture_output=True, text=True)
        assert res_node.returncode == 0, f"Syntax error in {name}: {res_node.stderr}"
        print(f"  [PASS] {name} -> Syntax validated with 0 errors")

    # 3. Dynamic Sitemap.xml Verification
    print("\n--- 3. Dynamic Sitemap.xml Validation ---")
    res_sitemap = requests.get(f"{BASE_URL}/sitemap.xml", timeout=5)
    assert res_sitemap.status_code == 200, f"sitemap.xml failed: {res_sitemap.status_code}"
    assert "application/xml" in res_sitemap.headers.get("content-type", ""), "Content-Type must be XML"
    
    # Parse XML
    root = ET.fromstring(res_sitemap.text)
    namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urls = root.findall('ns:url', namespace)
    assert len(urls) >= 15, f"Expected at least 15 URLs in sitemap, got {len(urls)}"
    locs = [u.find('ns:loc', namespace).text for u in urls]
    assert "https://eduhub.ai/" in locs
    assert "https://eduhub.ai/tools/essay-grader" in locs
    assert "https://eduhub.ai/topics/ielts/technology-in-education-essay" in locs
    print(f"  [PASS] /sitemap.xml -> HTTP 200 OK (Valid XML with {len(urls)} indexed pages)")

    # 4. Programmatic SEO (pSEO) Landing Pages & Paywall
    print("\n--- 4. Programmatic SEO (pSEO) Dynamic Topic Routes ---")
    topics_to_test = [
        ("/topics/ielts/technology-in-education-essay", "Technology in Education", "ielts"),
        ("/topics/ielts/environmental-protection-responsibility", "Environmental Protection", "ielts"),
        ("/topics/math/calculus-chain-rule-derivative-steps", "Calculus: Step-by-Step Chain Rule", "math"),
        ("/topics/math/integration-by-parts-formula-examples", "Integration by Parts", "math"),
        ("/topics/sat/digital-sat-reading-inference-strategies", "Digital SAT Reading", "sat")
    ]

    for route, expected_title, cat in topics_to_test:
        r = requests.get(f"{BASE_URL}{route}", timeout=5)
        assert r.status_code == 200, f"Failed for {route}: {r.status_code}"
        html = r.text
        assert expected_title in html, f"Title '{expected_title}' not in {route}"
        assert 'application/ld+json' in html, f"Schema.org missing in {route}"
        assert 'hreflang="en"' in html and 'hreflang="es"' in html, f"Hreflang missing in {route}"
        assert 'Pro Max Exclusive' in html or 'Start 3-Day Pro Access' in html, f"Paywall missing in {route}"
        assert 'EduHubShare.shareToWhatsApp' in html, f"WhatsApp share missing in {route}"
        assert 'EduHubShare.shareToTelegram' in html, f"Telegram share missing in {route}"
        assert 'manifest.json' in html, f"PWA manifest missing in {route}"
        print(f"  [PASS] {route:52} -> HTTP 200 OK (Schema.org + Paywall + Viral Share verified)")

    # 5. Omni-Channel Viral Share in Standalone Tools
    print("\n--- 5. Omni-Channel Viral Share Buttons in Standalone Tools ---")
    tools = [
        "/tools/essay-grader",
        "/tools/homework-solver",
        "/tools/pdf-summarizer",
        "/tools/language-tutor",
        "/tools/gpa-calculator",
        "/tools/citation-generator"
    ]
    for t_route in tools:
        res_t = requests.get(f"{BASE_URL}{t_route}", timeout=5)
        assert res_t.status_code == 200
        t_html = res_t.text
        assert 'shareToWhatsApp' in t_html, f"WhatsApp button missing in {t_route}"
        assert 'shareToTelegram' in t_html, f"Telegram button missing in {t_route}"
        assert 'generateStoriesCard' in t_html, f"Stories Card generator missing in {t_route}"
        assert 'pwa-install.js' in t_html, f"PWA install script missing in {t_route}"
        print(f"  [PASS] {t_route:28} -> WhatsApp + Telegram + Stories Card + PWA verified")

    # 6. Multi-Language Parity Check (100% match)
    print("\n--- 6. Multi-Language i18n Parity (EN, RU, UZ, ES) ---")
    with open(os.path.join(BASE_DIR, "static", "index.html"), "r", encoding="utf-8") as f:
        html_content = f.read()
    dom_keys = set(re.findall(r'data-i18n=["\']([^"\']+)["\']', html_content))

    node_verify = """
    const fs = require('fs');
    const code = fs.readFileSync('static/js/i18n.js', 'utf8');
    const vm = require('vm');
    const ctx = { console, localStorage: { getItem: () => null, setItem: () => {} }, navigator: { language: 'en' }, document: { querySelectorAll: () => [], addEventListener: () => {}, documentElement: {} } };
    vm.createContext(ctx);
    vm.runInContext(code + '\\n; globalThis.DICT = I18N_DICTIONARY;', ctx);
    const locales = ['en', 'ru', 'uz', 'es'];
    const results = {};
    for (const l of locales) {
        results[l] = Object.keys(ctx.DICT[l]);
    }
    console.log(JSON.stringify(results));
    """
    res_node_i18n = subprocess.run(["node", "-e", node_verify], cwd=BASE_DIR, capture_output=True, text=True, encoding="utf-8")
    assert res_node_i18n.returncode == 0, f"Failed to extract dict: {res_node_i18n.stderr}"
    dict_by_lang = json.loads(res_node_i18n.stdout.strip())
    
    for lang in ['en', 'ru', 'uz', 'es']:
        missing = [k for k in dom_keys if k not in dict_by_lang[lang]]
        assert len(missing) == 0, f"Missing keys in {lang}: {missing}"
    print(f"  [PASS] 100% i18n Parity: All {len(dom_keys)} HTML keys translated across EN, RU, UZ, ES")


    # 7. Full Platform Route Audit (All 11 Core Routes HTTP 200)
    print("\n--- 7. Full Platform Integrity Audit ---")
    core_routes = [
        "/", "/privacy", "/terms", "/refund", "/payment-success",
        "/tools/pdf-summarizer", "/tools/homework-solver", "/tools/gpa-calculator",
        "/tools/citation-generator", "/tools/essay-grader", "/tools/language-tutor"
    ]
    for cr in core_routes:
        res_cr = requests.get(f"{BASE_URL}{cr}", timeout=5)
        assert res_cr.status_code == 200, f"Route {cr} failed with status {res_cr.status_code}"
        print(f"  [PASS] HTTP 200: {cr:28} ({len(res_cr.text)} bytes)")

    print("\n==================================================================")
    print("🎉 ALL GLOBAL GROWTH ENGINE & PWA CHECKS PASSED (100%)")
    print("==================================================================")

if __name__ == "__main__":
    test_global_growth_engine()
