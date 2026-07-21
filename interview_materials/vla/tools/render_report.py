"""Render canonical VLA Markdown reports into deterministic HTML.

This implements only the repository's small Markdown subset so that Markdown
stays canonical and each rendered file can be regenerated and hash-checked.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import re
from pathlib import Path


def inline(text: str) -> str:
    text = html.escape(text, quote=False)
    code: list[str] = []
    math: list[str] = []

    def hold(match: re.Match[str]) -> str:
        code.append(f"<code>{match.group(1)}</code>")
        return f"\x00CODE{len(code) - 1}\x00"

    text = re.sub(r"`([^`]+)`", hold, text)

    def hold_math(match: re.Match[str]) -> str:
        math.append(match.group(0))
        return f"\x00MATH{len(math) - 1}\x00"

    # Keep complete inline MathJax spans opaque while Markdown emphasis and
    # links are expanded. This prevents LaTeX punctuation from becoming HTML.
    text = re.sub(r"\\\(.*?\\\)", hold_math, text)
    text = re.sub(r"(?<!\$)\$(?!\$).*?(?<!\$)\$(?!\$)", hold_math, text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"\x00MATH(\d+)\x00", lambda m: math[int(m.group(1))], text)
    text = re.sub(r"\x00CODE(\d+)\x00", lambda m: code[int(m.group(1))], text)
    return text


def slug(text: str, number: int) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return value or f"section-{number}"


def split_table(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def render_body(lines: list[str]) -> tuple[str, list[tuple[str, str]]]:
    out: list[str] = []
    toc: list[tuple[str, str]] = []
    used_ids: dict[str, int] = {}
    i = 0
    section_no = 0
    first_h1 = False
    while i < len(lines):
        line = lines[i].rstrip("\n")
        if not line.strip():
            i += 1
            continue
        if line.strip() == '<details class="qa">':
            out.append('<details class="qa">')
            i += 1
            continue
        if re.fullmatch(r"<summary>.*</summary>", line.strip()):
            # Question-card summaries use a small, repository-owned HTML subset
            # for badges and stable IDs. Keep it raw so the cards stay foldable.
            out.append(line.strip())
            i += 1
            continue
        if line.strip() == "</details>":
            out.append("</details>")
            i += 1
            continue
        if line.startswith("```"):
            language = line[3:].strip() or "text"
            block: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                block.append(lines[i].rstrip("\n"))
                i += 1
            if i < len(lines):
                i += 1
            code_text = "\n".join(block)
            out.append(f'<pre><code class="language-{html.escape(language)}">{html.escape(code_text)}</code></pre>')
            continue
        match = re.match(r"^(#{1,4})\s+(.+?)\s*$", line)
        if match:
            level, title = len(match.group(1)), match.group(2)
            if level == 1:
                if first_h1:
                    raise ValueError("canonical Markdown contains more than one H1")
                first_h1 = True
                out.append(f"<h1>{inline(title)}</h1>")
            else:
                section_no += 1
                base_ident = slug(title, section_no)
                used_ids[base_ident] = used_ids.get(base_ident, 0) + 1
                ident = base_ident if used_ids[base_ident] == 1 else f"{base_ident}-{used_ids[base_ident]}"
                toc.append((ident, title))
                out.append(f'<h{level} id="{ident}">{inline(title)}</h{level}>')
            i += 1
            continue
        if line.startswith(">"):
            quote: list[str] = []
            while i < len(lines) and lines[i].startswith(">"):
                quote.append(lines[i][1:].strip())
                i += 1
            out.append(f'<div class="meta">{inline(" ".join(quote))}</div>')
            continue
        if line.startswith("\\[") or line.startswith("$$"):
            closer = "\\]" if line.startswith("\\[") else "$$"
            block = [line]
            i += 1
            while i < len(lines):
                block.append(lines[i].rstrip("\n"))
                if lines[i].strip() == closer:
                    i += 1
                    break
                i += 1
            formula = "\n".join(html.escape(x) for x in block)
            out.append(f'<div class="formula">{formula}</div>')
            continue
        if line.startswith("|") and i + 1 < len(lines) and lines[i + 1].lstrip().startswith("|"):
            header = split_table(line)
            delimiter = split_table(lines[i + 1])
            if delimiter and all(re.fullmatch(r":?-{3,}:?", x) for x in delimiter):
                rows: list[list[str]] = []
                i += 2
                while i < len(lines) and lines[i].strip().startswith("|"):
                    rows.append(split_table(lines[i]))
                    i += 1
                out.append("<table><thead><tr>" + "".join(f"<th>{inline(x)}</th>" for x in header) + "</tr></thead><tbody>")
                for row in rows:
                    out.append("<tr>" + "".join(f"<td>{inline(x)}</td>" for x in row) + "</tr>")
                out.append("</tbody></table>")
                continue
        if re.match(r"^\s*(?:[-*]|\d+\.)\s+", line):
            ordered = bool(re.match(r"^\s*\d+\.\s+", line))
            items: list[str] = []
            pattern = r"^\s*\d+\.\s+(.*)$" if ordered else r"^\s*[-*]\s+(.*)$"
            while i < len(lines):
                match = re.match(pattern, lines[i])
                if not match:
                    break
                items.append(match.group(1))
                i += 1
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
            continue
        paragraph = [line.strip()]
        i += 1
        while i < len(lines):
            nxt = lines[i].rstrip("\n")
            if not nxt.strip() or nxt.startswith(("```", ">", "\\[", "$$", "|")) or re.match(r"^#{1,4}\s+", nxt) or re.match(r"^\s*(?:[-*]|\d+\.)\s+", nxt):
                break
            paragraph.append(nxt.strip())
            i += 1
        out.append(f"<p>{inline(' '.join(paragraph))}</p>")
    if not first_h1:
        raise ValueError("canonical Markdown has no H1")
    return "\n".join(out), toc


def render(source: Path, target: Path) -> None:
    raw = source.read_text(encoding="utf-8")
    sha = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    lines = raw.splitlines()
    title = next((x[2:] for x in lines if x.startswith("# ")), source.stem)
    body, toc = render_body(lines)
    toc_html = "".join(f'<li><a href="#{ident}">{html.escape(text)}</a></li>' for ident, text in toc)
    page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<meta name="generator" content="ARIS render-html (academic, v1)">
<meta name="aris:source-path" content="{html.escape(str(source))}">
<meta name="aris:source-sha256" content="{sha}">
<meta name="aris:generated-at" content="2026-07-16">
<script>
window.MathJax = {{
  tex: {{ inlineMath: [['\\\\(', '\\\\)'], ['$', '$']], displayMath: [['\\\\[', '\\\\]'], ['$$', '$$']] }},
  options: {{ skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code'] }}
}};
</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js" async></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/styles/atom-one-light.min.css">
<script src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/highlight.min.js"></script>
<script>document.addEventListener('DOMContentLoaded', () => hljs.highlightAll());</script>
<style>
:root {{
  --bg:#fdfcf7; --bg-soft:#f4f1ea; --bg-code:#f8f5ec;
  --ink:#1a1a1a; --ink-soft:#4a4a4a; --ink-muted:#6b6b6b;
  --primary:#1a4a8c; --primary-soft:#2d6cb8; --accent:#b8390e;
  --border:#d6d0c0; --border-soft:#e8e3d5;
}}
* {{ box-sizing:border-box; }}
html {{ scroll-behavior:smooth; }}
body {{
  margin:0; padding:0; color:var(--ink); background:var(--bg);
  font:16px/1.65 "Source Serif Pro","Source Serif 4","Crimson Pro","Georgia","Songti SC","STSong",serif;
}}
article {{ max-width:1280px; margin:0 auto; padding:40px 32px; display:flow-root; }}
article > :not(nav.toc) {{ margin-left:308px; max-width:calc(100% - 308px); }}
article > .meta:first-child {{ display:none; }}
nav.toc {{
  position:sticky; top:24px; float:left; width:260px; max-height:calc(100vh - 48px);
  overflow-y:auto; padding:0 16px 14px 0; border-right:1px solid var(--border-soft);
  background:transparent; font-size:13px;
}}
nav.toc h2 {{
  margin:0 0 12px; padding:0; border:0; background:none; color:var(--ink-muted);
  font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:.08em;
}}
nav.toc h2::after {{ content:" / Contents"; }}
nav.toc ol {{ columns:1; list-style:none; margin:0; padding:0; counter-reset:toc; }}
nav.toc li {{ margin:5px 0; line-height:1.45; counter-increment:toc; }}
nav.toc li::before {{ content:counter(toc) ". "; color:var(--ink-muted); margin-right:4px; }}
nav.toc a {{ color:var(--ink-soft); text-decoration:none; border-bottom:1px dotted transparent; }}
nav.toc a:hover {{ color:var(--primary); border-bottom-color:var(--primary); }}
h1 {{
  margin:0 0 32px; padding:0 0 24px; border-bottom:3px double var(--primary);
  color:var(--ink); font-size:32px; line-height:1.2; font-weight:700; letter-spacing:-.01em;
}}
h1::before {{
  content:"VLA Interview · Evidence-First Notes"; display:block; margin:0 0 8px;
  color:var(--accent); font-size:13px; line-height:1.4; font-weight:600;
  text-transform:uppercase; letter-spacing:.12em;
}}
h2 {{
  margin:44px 0 14px; padding:0 0 8px; border:0; border-bottom:1px solid var(--border);
  background:none; color:var(--ink); font-size:24px; font-weight:700;
}}
h3 {{ margin:28px 0 10px; color:var(--primary); font-size:19px; font-weight:600; }}
h4 {{ margin:20px 0 8px; color:var(--ink); font-size:16px; font-weight:600; }}
p {{ margin:10px 0; }}
ul,ol {{ margin:10px 0; padding-left:22px; }}
li {{ margin:4px 0; }}
ul li::marker {{ color:var(--primary); }}
strong {{ color:var(--accent); font-weight:600; }}
em {{ color:var(--ink-soft); }}
a {{ color:var(--primary); overflow-wrap:anywhere; }}
a:hover {{ color:var(--accent); }}
code:not(.hljs) {{
  padding:1px 5px; border:1px solid var(--border-soft); border-radius:3px;
  color:var(--accent); background:var(--bg-code);
  overflow-wrap:anywhere; word-break:break-word;
  font:.86em "JetBrains Mono","SF Mono","Menlo","Consolas",monospace;
}}
pre {{
  margin:14px 0; padding:0; overflow-x:auto; max-width:100%; background:#fafaf6;
  border:1px solid var(--border); border-left:4px solid var(--primary); border-radius:4px;
}}
pre code, pre code.hljs {{
  display:block; padding:14px 18px !important; background:transparent !important;
  color:var(--ink); font:13px/1.55 "JetBrains Mono","SF Mono","Menlo",monospace;
}}
.formula {{
  margin:14px 0; padding:12px 18px; overflow-x:auto; max-width:100%; white-space:pre-wrap;
  background:#fafaf6; border:1px solid var(--border); border-left:4px solid var(--primary); border-radius:4px;
}}
.formula em {{ font-style:normal; color:inherit; }}
mjx-container[display="true"] {{ margin:12px 0 !important; }}
.meta {{
  margin:16px 0; padding:12px 16px; color:var(--ink-soft); background:#dbeafe;
  border-left:4px solid var(--primary); border-radius:4px; font-size:15px;
}}
table {{
  display:block; width:100%; max-width:100%; margin:16px 0; border-collapse:collapse;
  overflow-x:auto; overflow-y:hidden; overflow-wrap:anywhere;
  border:1px solid var(--border); border-radius:4px; font-size:14px;
}}
thead {{ color:#fff; background:var(--primary); }}
th,td {{ padding:9px 12px; text-align:left; vertical-align:top; border-bottom:1px solid var(--border-soft); }}
th {{ background:transparent; font-size:13px; font-weight:600; letter-spacing:.02em; }}
tbody tr:nth-child(even) {{ background:var(--bg-soft); }}
tbody tr:last-child td {{ border-bottom:0; }}
details.qa, details {{
  margin:10px 0; padding:0; background:#fff; border:1px solid var(--border-soft); border-radius:6px;
}}
details summary {{ padding:11px 14px; cursor:pointer; color:var(--ink); font-size:14.5px; font-weight:600; }}
details > :not(summary) {{ margin-left:14px; margin-right:14px; }}
.lv,.freq {{
  display:inline-block; margin-right:6px; padding:1px 7px; border:1px solid var(--border-soft);
  border-radius:3px; background:var(--bg-soft); color:var(--ink-soft);
  font:600 11px/1.5 "JetBrains Mono","SF Mono","Menlo",monospace;
}}
@media (max-width:900px) {{
  article {{ display:block; padding:20px 16px; }}
  article > :not(nav.toc) {{ margin-left:0; max-width:100%; }}
  nav.toc {{
    position:static; float:none; width:auto; max-height:none; margin-bottom:24px;
    padding:0 0 14px; border-right:0; border-bottom:1px solid var(--border-soft);
  }}
  h1 {{ font-size:24px; }} h2 {{ font-size:20px; }}
  table {{ overflow-x:auto; }}
  pre,.formula {{ overflow-x:auto; }}
}}
@media print {{
  nav.toc, article > .meta:first-child {{ display:none; }}
  article {{ display:block; max-width:none; padding:0; }}
  article > :not(nav.toc) {{ margin-left:0; max-width:none; }}
  body {{ background:#fff; }}
}}
</style>
</head>
<body><article>
<div class="meta">Canonical Markdown SHA-256：<code>{sha}</code>；生成自：<code>{html.escape(str(source))}</code></div>
<nav class="toc" aria-label="目录"><h2>目录</h2><ol>{toc_html}</ol></nav>
{body}
</article></body></html>
"""
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(page, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    args = parser.parse_args()
    render(args.source, args.target)
