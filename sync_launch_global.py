import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('launch_production_suite.sh', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

index_html = read_file('static/index.html')
i18n_js = read_file('static/js/i18n.js')
conversion_js = read_file('static/js/conversion-engine.js')
pwa_js = read_file('static/js/pwa-install.js')
viral_js = read_file('static/js/viral-share.js')
manifest_json = read_file('static/manifest.json')
sw_js = read_file('static/sw.js')
essay_grader_html = read_file('static/tools/essay-grader.html')
homework_solver_html = read_file('static/tools/homework-solver.html')
pdf_summarizer_html = read_file('static/tools/pdf-summarizer.html')
language_tutor_html = read_file('static/tools/language-tutor.html')
gpa_calculator_html = read_file('static/tools/gpa-calculator.html')
citation_generator_html = read_file('static/tools/citation-generator.html')
app_main_py = read_file('app/main.py')

# Replace sections in launch_production_suite.sh
part1, rest = content.split("cat << 'HTMLEOF' > static/index.html\n", 1)
_, rest = rest.split("\nHTMLEOF\n", 1)

part2, rest = rest.split("cat << 'I18NEOF' > static/js/i18n.js\n", 1)
_, rest = rest.split("\nI18NEOF\n", 1)

# PWA and Viral assets block
pwa_block = f"""
cat << 'MANIFESTEOF' > static/manifest.json
{manifest_json}
MANIFESTEOF

cat << 'SWEOF' > static/sw.js
{sw_js}
SWEOF

cat << 'PWAJSEOF' > static/js/pwa-install.js
{pwa_js}
PWAJSEOF

cat << 'VIRALJSEOF' > static/js/viral-share.js
{viral_js}
VIRALJSEOF
"""

# Clean up old manifest/sw if present in rest
for old_marker in ['MANIFESTEOF', 'SWEOF', 'PWAJSEOF', 'VIRALJSEOF', 'CONVENGINEOF']:
    if f"cat << '{old_marker}'" in rest:
        b_part, r_part = rest.split(f"cat << '{old_marker}'", 1)
        _, rest = r_part.split(f"\n{old_marker}\n", 1)

# Tool files
p_t1_before, rest = rest.split("cat << 'TOOL1EOF' > static/tools/pdf-summarizer.html\n", 1)
_, rest = rest.split("\nTOOL1EOF\n", 1)

p_t2_before, rest = rest.split("cat << 'TOOL2EOF' > static/tools/homework-solver.html\n", 1)
_, rest = rest.split("\nTOOL2EOF\n", 1)

p_t3_before, rest = rest.split("cat << 'TOOL3EOF' > static/tools/gpa-calculator.html\n", 1)
_, rest = rest.split("\nTOOL3EOF\n", 1)

p_t4_before, rest = rest.split("cat << 'TOOL4EOF' > static/tools/citation-generator.html\n", 1)
_, rest = rest.split("\nTOOL4EOF\n", 1)

p_t5_before, rest = rest.split("cat << 'TOOL5EOF' > static/tools/essay-grader.html\n", 1)
_, rest = rest.split("\nTOOL5EOF\n", 1)

p_t6_before, rest = rest.split("cat << 'TOOL6EOF' > static/tools/language-tutor.html\n", 1)
_, rest = rest.split("\nTOOL6EOF\n", 1)

# app/main.py
p_py_before, rest = rest.split("cat << 'PYEOF' > app/main.py\n", 1)
_, part_tail = rest.split("\nPYEOF\n", 1)

new_content = (
    part1 +
    "cat << 'HTMLEOF' > static/index.html\n" +
    index_html +
    "\nHTMLEOF\n" +
    part2 +
    "cat << 'I18NEOF' > static/js/i18n.js\n" +
    i18n_js +
    "\nI18NEOF\n\n" +
    f"cat << 'CONVENGINEOF' > static/js/conversion-engine.js\n{conversion_js}\nCONVENGINEOF\n" +
    pwa_block +
    p_t1_before +
    "cat << 'TOOL1EOF' > static/tools/pdf-summarizer.html\n" +
    pdf_summarizer_html +
    "\nTOOL1EOF\n" +
    p_t2_before +
    "cat << 'TOOL2EOF' > static/tools/homework-solver.html\n" +
    homework_solver_html +
    "\nTOOL2EOF\n" +
    p_t3_before +
    "cat << 'TOOL3EOF' > static/tools/gpa-calculator.html\n" +
    gpa_calculator_html +
    "\nTOOL3EOF\n" +
    p_t4_before +
    "cat << 'TOOL4EOF' > static/tools/citation-generator.html\n" +
    citation_generator_html +
    "\nTOOL4EOF\n" +
    p_t5_before +
    "cat << 'TOOL5EOF' > static/tools/essay-grader.html\n" +
    essay_grader_html +
    "\nTOOL5EOF\n" +
    p_t6_before +
    "cat << 'TOOL6EOF' > static/tools/language-tutor.html\n" +
    language_tutor_html +
    "\nTOOL6EOF\n" +
    p_py_before +
    "cat << 'PYEOF' > app/main.py\n" +
    app_main_py +
    "\nPYEOF\n" +
    part_tail
)

with open('launch_production_suite.sh', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("SUCCESS: launch_production_suite.sh fully synchronized with all global scaling assets!")
