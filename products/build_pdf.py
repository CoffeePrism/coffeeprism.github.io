#!/usr/bin/env python3
"""Build PDF from markdown files using weasyprint with custom styling."""

import sys
import re
from pathlib import Path
import markdown
from weasyprint import HTML, CSS

PROJECT_DIR = Path(__file__).parent
STYLE = PROJECT_DIR / "pdf-style.css"
ASSETS_DIR = PROJECT_DIR / "assets"


def render_cover(title, subtitle, meta_lines):
    """Render the cover page HTML."""
    meta_html = "<br>".join(meta_lines)
    return f"""
<div class="cover">
  <div>
    <div class="cover-top">Coffee Prism · 2026 Edition</div>
    <h1 class="cover-title">{title}</h1>
    <div class="cover-divider"></div>
    <p class="cover-subtitle">{subtitle}</p>
  </div>
  <div>
    <div class="cover-meta">{meta_html}</div>
    <div class="cover-brand">COFFEEPRISM.COM</div>
  </div>
</div>
"""


def convert_md_file(md_path):
    """Convert a markdown file to HTML, skipping the cover marker."""
    text = md_path.read_text(encoding="utf-8")
    # Remove cover-intro top h1 (handled separately via cover) if marked
    md = markdown.Markdown(
        extensions=["tables", "fenced_code", "attr_list", "toc", "md_in_html"]
    )
    html = md.convert(text)

    # Process relative image paths → absolute file:// URLs
    def fix_src(match):
        src = match.group(2)
        if src.startswith("http") or src.startswith("/") or src.startswith("file:"):
            return match.group(0)
        resolved = (md_path.parent / src).resolve()
        if not resolved.exists():
            resolved = (ASSETS_DIR / src).resolve()
        return f'{match.group(1)}"{resolved.as_uri()}"'

    html = re.sub(r'(<img[^>]*?\ssrc=)"([^"]+)"', fix_src, html)

    # Inline SVG files as <embed> or direct SVG
    def inline_svg(match):
        src = match.group(1)
        if not src.endswith(".svg"):
            return match.group(0)
        svg_path = (md_path.parent / src).resolve()
        if not svg_path.exists():
            svg_path = (ASSETS_DIR / src).resolve()
        if svg_path.exists():
            svg_content = svg_path.read_text(encoding="utf-8")
            # Remove XML declaration for inline use
            svg_content = re.sub(r'<\?xml[^>]*\?>', '', svg_content).strip()
            return f'<figure>{svg_content}</figure>'
        return match.group(0)

    html = re.sub(r'<img[^>]*src="([^"]+\.svg)"[^>]*>', inline_svg, html)

    return html


def build_book(source_files, output_pdf, cover_config=None, has_back_cover=True):
    """Combine markdown files, apply template, render to PDF."""
    body_parts = []

    if cover_config:
        body_parts.append(render_cover(**cover_config))

    # Skip first file's cover if we already rendered one
    start_idx = 1 if cover_config else 0

    for md_file in source_files[start_idx:]:
        md_path = PROJECT_DIR / md_file
        if not md_path.exists():
            print(f"  WARNING: {md_file} not found, skipping")
            continue
        body_parts.append(convert_md_file(md_path))

    if has_back_cover:
        body_parts.append("""
<div class="back-cover">
  <h2>致谢</h2>
  <p>感谢每一位支持 Coffee Prism 的读者。</p>
  <p>你的购买让我们能持续撰写更多深入、准确、实用的咖啡内容。</p>
  <br><br>
  <p>如有反馈、建议或勘误，欢迎通过网站联系我们。</p>
  <br><br>
  <p style="font-size: 13pt; color: #d4a574; letter-spacing: 3px;">COFFEEPRISM.COM</p>
  <p style="font-size: 9pt; opacity: 0.7;">© 2026 Coffee Prism. 本手册仅供个人学习使用，禁止商业转载。</p>
</div>
""")

    html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>{cover_config['title'] if cover_config else 'Coffee Guide'}</title>
</head>
<body>
{''.join(body_parts)}
</body>
</html>
"""

    # Debug: write intermediate HTML
    debug_html = PROJECT_DIR / f"{output_pdf.stem}_debug.html"
    debug_html.write_text(html, encoding="utf-8")

    print(f"  Rendering {output_pdf.name}...")
    HTML(string=html, base_url=str(PROJECT_DIR)).write_pdf(
        output_pdf,
        stylesheets=[CSS(filename=str(STYLE))]
    )
    print(f"  ✓ {output_pdf.name} ({output_pdf.stat().st_size // 1024} KB)")


def build_comprehensive():
    """Build the comprehensive guide PDF."""
    cover = {
        "title": "咖啡冲煮<br>完全指南",
        "subtitle": "从零基础到进阶：一本让你真正做出好咖啡的实战手册",
        "meta_lines": [
            "2026 年 4 月 · 修订版 1.0",
            "作者：Coffee Prism 编辑部",
            "字数：约 25,000 字 · 页数：约 60 页",
        ]
    }

    files = sorted((PROJECT_DIR / "comprehensive").glob("*.md"))
    files = [str(f.relative_to(PROJECT_DIR)) for f in files]

    print(f"Building comprehensive guide with {len(files)} chapters:")
    for f in files:
        print(f"  - {f}")

    output = PROJECT_DIR / "咖啡冲煮完全指南-2026.pdf"
    build_book(files, output, cover_config=cover)


def build_pourover():
    """Build the pour-over specialist guide PDF."""
    cover = {
        "title": "手冲咖啡<br>大师之路",
        "subtitle": "从参数到感官：深度剖析手冲的每一个细节",
        "meta_lines": [
            "2026 年 4 月 · 第一版",
            "作者：Coffee Prism 编辑部",
            "适读对象：已掌握基础冲煮的爱好者",
            "字数：约 22,000 字 · 页数：约 50 页",
        ]
    }

    files = sorted((PROJECT_DIR / "pourover").glob("*.md"))
    files = [str(f.relative_to(PROJECT_DIR)) for f in files]

    print(f"\nBuilding pour-over guide with {len(files)} chapters:")
    for f in files:
        print(f"  - {f}")

    output = PROJECT_DIR / "手冲咖啡大师之路.pdf"
    build_book(files, output, cover_config=cover)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "both"
    if mode in ("both", "comprehensive"):
        build_comprehensive()
    if mode in ("both", "pourover"):
        build_pourover()
    print("\nDone.")
