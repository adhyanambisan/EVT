import os
import re
import subprocess
import base64
import markdown

def convert_md_to_pdf():
    evt_dir = os.path.abspath(os.path.dirname(__file__))
    md_file = os.path.join(evt_dir, 'notebook_text.md')
    html_file = os.path.join(evt_dir, 'notebook_text.html')
    pdf_file = os.path.join(evt_dir, 'NIFTY50_Tail_Risk_Report.pdf')

    with open(md_file, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Pre-process callouts: > [!NOTE] and > [!IMPORTANT]
    def replace_callouts(text):
        lines = text.split('\n')
        out_lines = []
        in_callout = False
        callout_type = ''
        callout_body = []

        for line in lines:
            if line.startswith('> [!NOTE]') or line.startswith('> [!IMPORTANT]') or line.startswith('> [!WARNING]'):
                in_callout = True
                callout_type = 'important' if 'IMPORTANT' in line else ('warning' if 'WARNING' in line else 'note')
                continue
            elif in_callout and line.startswith('>'):
                callout_body.append(line.lstrip('> ').strip())
            else:
                if in_callout:
                    title = 'KEY TAKEAWAY' if callout_type == 'important' else 'NOTE'
                    body_html = '<br>'.join(callout_body)
                    out_lines.append(f'<div class="callout callout-{callout_type}"><div class="callout-title">{title}</div><div class="callout-content">{body_html}</div></div>\n')
                    in_callout = False
                    callout_body = []
                out_lines.append(line)
        if in_callout:
            title = 'KEY TAKEAWAY' if callout_type == 'important' else 'NOTE'
            body_html = '<br>'.join(callout_body)
            out_lines.append(f'<div class="callout callout-{callout_type}"><div class="callout-title">{title}</div><div class="callout-content">{body_html}</div></div>\n')

        return '\n'.join(out_lines)

    processed_md = replace_callouts(md_text)

    # Convert markdown to HTML
    html_body = markdown.markdown(processed_md, extensions=['extra', 'sane_lists'])

    # Embed images as base64 so there are zero path/rendering issues in headless browser
    def embed_images(html_str):
        img_pattern = re.compile(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>')
        matches = img_pattern.findall(html_str)
        for src in matches:
            img_path = os.path.normpath(os.path.join(evt_dir, src))
            if os.path.exists(img_path):
                ext = os.path.splitext(img_path)[1].lstrip('.').lower()
                mime = 'image/png' if ext == 'png' else ('image/jpeg' if ext in ['jpg', 'jpeg'] else 'image/svg+xml')
                with open(img_path, 'rb') as img_f:
                    b64 = base64.b64encode(img_f.read()).decode('utf-8')
                data_uri = f'data:{mime};base64,{b64}'
                html_str = html_str.replace(f'src="{src}"', f'src="{data_uri}"')
                html_str = html_str.replace(f"src='{src}'", f"src='{data_uri}'")
        return html_str

    html_body = embed_images(html_body)

    # Wrap figures and italic captions cleanly
    # Markdown output for *Figure X...* right after an <img> is <p><em>Figure ...</em></p>
    html_body = re.sub(
        r'(<p><img[^>]+></p>)\s*<p><em>(Figure[^<]+)</em></p>',
        r'<figure class="report-figure">\1<figcaption>\2</figcaption></figure>',
        html_body
    )

    full_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Tail Risk Modelling of NIFTY 50 Using Extreme Value Theory</title>
<style>
@page {{
    size: A4;
    margin: 20mm 18mm 20mm 18mm;
    @bottom-center {{
        content: counter(page);
    }}
}}

body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    background: #ffffff;
    line-height: 1.6;
    font-size: 10.5pt;
}}

/* Typography */
h1 {{
    font-size: 22pt;
    font-weight: 700;
    color: #0f172a;
    line-height: 1.25;
    margin-top: 0;
    margin-bottom: 6px;
    letter-spacing: -0.02em;
    border-bottom: 2px solid #2563eb;
    padding-bottom: 10px;
}}

h2 {{
    font-size: 14pt;
    font-weight: 600;
    color: #1e3a8a;
    margin-top: 24px;
    margin-bottom: 10px;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 5px;
    page-break-after: avoid;
}}

h3 {{
    font-size: 11.5pt;
    font-weight: 600;
    color: #334155;
    margin-top: 16px;
    margin-bottom: 8px;
    page-break-after: avoid;
}}

p {{
    margin-top: 0;
    margin-bottom: 10px;
    text-align: justify;
}}

hr {{
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 18px 0;
}}

/* Tables */
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 14px 0 18px 0;
    font-size: 9.5pt;
    page-break-inside: avoid;
}}

th {{
    background-color: #f1f5f9;
    color: #0f172a;
    font-weight: 600;
    text-align: left;
    padding: 8px 10px;
    border-top: 1.5px solid #cbd5e1;
    border-bottom: 1.5px solid #cbd5e1;
}}

td {{
    padding: 7px 10px;
    border-bottom: 1px solid #e2e8f0;
    color: #334155;
}}

tr:nth-child(even) td {{
    background-color: #f8fafc;
}}

/* Callouts / Alerts */
.callout {{
    border-radius: 6px;
    padding: 12px 14px;
    margin: 14px 0;
    font-size: 9.5pt;
    page-break-inside: avoid;
}}

.callout-title {{
    font-weight: 700;
    font-size: 8.5pt;
    letter-spacing: 0.05em;
    margin-bottom: 5px;
    text-transform: uppercase;
}}

.callout-note {{
    background-color: #eff6ff;
    border-left: 4px solid #3b82f6;
    color: #1e40af;
}}

.callout-note .callout-title {{
    color: #1d4ed8;
}}

.callout-important {{
    background-color: #fef2f2;
    border-left: 4px solid #ef4444;
    color: #991b1b;
}}

.callout-important .callout-title {{
    color: #b91c1c;
}}

.callout-content {{
    color: #334155;
}}

/* Figures */
.report-figure {{
    margin: 16px 0 20px 0;
    text-align: center;
    page-break-inside: avoid;
}}

.report-figure p {{
    margin: 0;
    text-align: center;
}}

.report-figure img {{
    max-width: 95%;
    height: auto;
    border-radius: 4px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}}

figcaption {{
    font-size: 8.5pt;
    color: #64748b;
    margin-top: 6px;
    font-style: italic;
    text-align: center;
}}

/* Lists */
ul, ol {{
    margin-top: 0;
    margin-bottom: 12px;
    padding-left: 20px;
}}

li {{
    margin-bottom: 4px;
}}

/* Subtitle header */
.doc-header {{
    margin-bottom: 20px;
}}

.subtitle {{
    font-size: 12pt;
    color: #64748b;
    font-weight: 500;
    margin-top: -4px;
    margin-bottom: 14px;
}}
</style>

<!-- MathJax Configuration for rendering math in headless browser -->
<script>
window.MathJax = {{
    tex: {{
        inlineMath: [['$', '$']],
        displayMath: [['$$', '$$']]
    }},
    svg: {{
        fontCache: 'global'
    }},
    startup: {{
        pageReady: () => {{
            return MathJax.startup.defaultPageReady().then(() => {{
                document.body.classList.add('mathjax-done');
            }});
        }}
    }}
}};
</script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
</head>
<body>

{html_body}

</body>
</html>'''

    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(full_html)

    print(f'HTML generated: {html_file}')

    # Run Edge headless to render PDF
    edge_exe = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    if not os.path.exists(edge_exe):
        edge_exe = r'C:\Program Files\Microsoft\Edge\Application\msedge.exe'

    cmd = [
        edge_exe,
        '--headless=new',
        '--disable-gpu',
        '--run-all-compositor-stages-before-draw',
        '--virtual-time-budget=8000',
        '--no-pdf-header-footer',
        f'--print-to-pdf={pdf_file}',
        f'file:///{html_file.replace(os.sep, "/")}'
    ]

    print('Rendering PDF with Edge...')
    result = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(pdf_file) and os.path.getsize(pdf_file) > 1000:
        print(f'SUCCESS: PDF created at {pdf_file} ({os.path.getsize(pdf_file)} bytes)')
    else:
        print(f'Failed to create PDF. Stdout: {result.stdout}, Stderr: {result.stderr}')

if __name__ == '__main__':
    convert_md_to_pdf()

