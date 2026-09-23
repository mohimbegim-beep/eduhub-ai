import os
import sys
import glob
import json
import re
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestStage10PerformanceAndSEO(unittest.TestCase):

    # --------------------------------------------------------------------------
    # 10.1: GZip Compression Middleware
    # --------------------------------------------------------------------------
    def test_10_1_gzip_compression_on_heavy_payloads(self):
        # 1. Запрос локали с Accept-Encoding: gzip (> 1000 байт)
        resp = client.get("/locales/en.json", headers={"Accept-Encoding": "gzip"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("content-encoding"), "gzip")

        # 2. Запрос главной страницы с Accept-Encoding: gzip (> 1000 байт)
        resp_root = client.get("/", headers={"Accept-Encoding": "gzip"})
        self.assertEqual(resp_root.status_code, 200)
        self.assertEqual(resp_root.headers.get("content-encoding"), "gzip")

    def test_10_1_no_gzip_when_client_does_not_request(self):
        resp = client.get("/locales/en.json", headers={"Accept-Encoding": "identity"})
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(resp.headers.get("content-encoding"))

    # --------------------------------------------------------------------------
    # 10.2: HTTP Caching & Cache-Control Headers
    # --------------------------------------------------------------------------
    def test_10_2_cache_control_headers_matrix(self):
        # Static & Locales: 1 day public cache
        res_loc = client.get("/locales/en.json")
        self.assertEqual(res_loc.status_code, 200)
        self.assertIn("max-age=86400", res_loc.headers.get("cache-control", ""))
        self.assertIn("public", res_loc.headers.get("cache-control", ""))

        # Landing & HTML: 1 hour public cache with must-revalidate
        res_root = client.get("/")
        self.assertEqual(res_root.status_code, 200)
        self.assertIn("max-age=3600", res_root.headers.get("cache-control", ""))
        self.assertIn("must-revalidate", res_root.headers.get("cache-control", ""))

        # API & Health: no-store / no-cache
        res_health = client.get("/health")
        self.assertEqual(res_health.status_code, 200)
        self.assertIn("no-store", res_health.headers.get("cache-control", ""))

    # --------------------------------------------------------------------------
    # 10.3: Social Share Cards (OpenGraph & Twitter Card)
    # --------------------------------------------------------------------------
    def test_10_3_opengraph_and_twitter_cards_across_all_pages(self):
        html_files = sorted(glob.glob(str(BASE_DIR / "static" / "**" / "*.html"), recursive=True))
        self.assertEqual(len(html_files), 24, "Expected exactly 24 HTML platform pages")

        for hf in html_files:
            p = Path(hf)
            with open(hf, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # OpenGraph Assertions
            self.assertTrue('property="og:title"' in content or "property='og:title'" in content, f"Missing og:title in {p.name}")
            self.assertTrue('property="og:description"' in content or "property='og:description'" in content, f"Missing og:description in {p.name}")
            self.assertTrue('property="og:image"' in content or "property='og:image'" in content, f"Missing og:image in {p.name}")
            self.assertTrue('property="og:url"' in content or "property='og:url'" in content, f"Missing og:url in {p.name}")

            # Twitter Card Assertions
            self.assertTrue('name="twitter:card"' in content or "name='twitter:card'" in content, f"Missing twitter:card in {p.name}")
            self.assertTrue('name="twitter:title"' in content or "name='twitter:title'" in content, f"Missing twitter:title in {p.name}")
            self.assertTrue('name="twitter:image"' in content or "name='twitter:image'" in content, f"Missing twitter:image in {p.name}")

    def test_10_3_og_banner_asset_exists_and_valid(self):
        og_asset = BASE_DIR / "static" / "img" / "og_banner.png"
        self.assertTrue(og_asset.exists(), "static/img/og_banner.png must exist on disk")
        self.assertGreater(og_asset.stat().st_size, 50000, "og_banner.png should be high-resolution (> 50KB)")

    # --------------------------------------------------------------------------
    # 10.4: JSON-LD Schema.org Structured Data
    # --------------------------------------------------------------------------
    def test_10_4_json_ld_schema_org_validity_across_all_pages(self):
        html_files = sorted(glob.glob(str(BASE_DIR / "static" / "**" / "*.html"), recursive=True))
        for hf in html_files:
            p = Path(hf)
            with open(hf, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            matches = list(re.finditer(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>([\s\S]*?)</script>', content, re.I))
            self.assertGreater(len(matches), 0, f"Page {p.name} must have at least one JSON-LD schema block")

            for idx, m in enumerate(matches):
                raw = m.group(1).strip()
                try:
                    data = json.loads(raw)
                except Exception as ex:
                    self.fail(f"Invalid JSON in {p.name} block {idx+1}: {ex}")

                self.assertEqual(data.get("@context"), "https://schema.org", f"Missing @context https://schema.org in {p.name}")
                has_type = bool(data.get("@type") or data.get("@graph"))
                self.assertTrue(has_type, f"Missing @type or @graph in {p.name}")

    def test_10_4_main_page_schema_org_entities(self):
        index_file = BASE_DIR / "static" / "index.html"
        with open(index_file, "r", encoding="utf-8") as f:
            content = f.read()

        match = re.search(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>([\s\S]*?)</script>', content, re.I)
        self.assertIsNotNone(match, "index.html must have JSON-LD script")
        data = json.loads(match.group(1).strip())

        graph_types = [node.get("@type") for node in data.get("@graph", [])]
        self.assertIn("SoftwareApplication", graph_types, "index.html must define SoftwareApplication")
        self.assertIn("Course", graph_types, "index.html must define Course")
        self.assertIn("FAQPage", graph_types, "index.html must define FAQPage")


if __name__ == "__main__":
    unittest.main()
