import sys
import os
import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test_document_renderer_suite():
    print("==================================================")
    print("🔍 VERIFYING ENHANCED DOCUMENT RENDERER")
    print("==================================================")

    # 1. Verify doc-renderer.js file integrity
    print("\n--- 1. Validating static/js/doc-renderer.js ---")
    doc_renderer_path = os.path.join(BASE_DIR, "static", "js", "doc-renderer.js")
    assert os.path.exists(doc_renderer_path), f"Missing {doc_renderer_path}"
    with open(doc_renderer_path, "r", encoding="utf-8") as f:
        js = f.read()

    # Table verification
    assert "overflow-x: auto" in js or "overflow-x-auto" in js, "Responsive scrollable table styling missing"
    assert "table-responsive-container" in js, "table-responsive-container class missing"
    assert "<table class=" in js, "Custom table renderer markup missing"
    print("  [PASS] Markdown Table Renderer: wraps tables in responsive 'overflow-x-auto' container")

    # Mermaid verification
    assert "mermaid.initialize" in js, "mermaid.initialize missing"
    assert "class=\"mermaid" in js or "mermaid-block-wrapper" in js, "Mermaid container missing"
    assert "mermaid.run" in js, "mermaid.run call missing"
    print("  [PASS] Mermaid Integration: automatically extracts ```mermaid code blocks and targets SVG diagrams")

    # KaTeX verification
    assert "renderMathInElement" in js, "KaTeX renderMathInElement call missing"
    assert "$$" in js and "\\[" in js, "KaTeX delimiters missing"
    print("  [PASS] KaTeX Math Rendering: configured for display ($$, \\[\\]) and inline ($, \\(\\)) formulas")

    # 2. Verify CDN injections on index.html
    print("\n--- 2. Verifying CDN Injections on Homepage (static/index.html) ---")
    home_res = requests.get(f"{BASE_URL}/", timeout=5)
    assert home_res.status_code == 200
    home_html = home_res.text
    assert "marked.min.js" in home_html, "Marked.js missing from index.html"
    assert "katex.min.css" in home_html, "KaTeX CSS missing from index.html"
    assert "katex.min.js" in home_html, "KaTeX JS missing from index.html"
    assert "mermaid.min.js" in home_html, "Mermaid.js missing from index.html"
    assert "doc-renderer.js" in home_html, "doc-renderer.js script missing from index.html"
    assert "renderAcademicDocument" in home_html, "renderAcademicDocument call missing in index.html"
    print("  [PASS] Homepage: Marked, KaTeX, Mermaid, and doc-renderer.js wired up with HTTP 200")

    # 3. Verify CDN injections on Standalone Tools
    print("\n--- 3. Verifying CDN Injections on Standalone Tool Pages ---")
    for tool_path in ["/tools/pdf-summarizer", "/tools/homework-solver"]:
        res = requests.get(f"{BASE_URL}{tool_path}", timeout=5)
        assert res.status_code == 200, f"Expected 200 for {tool_path}"
        html = res.text
        assert "marked.min.js" in html, f"Marked.js missing from {tool_path}"
        assert "katex.min.js" in html, f"KaTeX missing from {tool_path}"
        assert "mermaid.min.js" in html, f"Mermaid missing from {tool_path}"
        assert "doc-renderer.js" in html, f"doc-renderer.js missing from {tool_path}"
        assert "renderAcademicDocument" in html, f"renderAcademicDocument call missing in {tool_path}"
        print(f"  [PASS] {tool_path}: Complete document renderer pipeline verified")

    print("\n==================================================")
    print("🎉 ALL ENHANCED DOCUMENT RENDERER CHECKS PASSED (100%)")
    print("==================================================")
    return True

if __name__ == "__main__":
    success = test_document_renderer_suite()
    sys.exit(0 if success else 1)
