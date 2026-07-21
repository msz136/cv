# Repository Instructions

## HTML rendering standard

The HTML artifacts in `interview_materials/vla/` are designed study and interview documents, not generic Markdown previews. All new pages and all re-renders must use the repository's academic layout described below.

### Canonical source and generated artifacts

- Treat the matching Markdown file as the canonical content source. Edit `*.md` first, then render the corresponding `*.html`.
- Keep formulas, citations, headings, tables, code, links, and question-card markup semantically identical between Markdown and HTML.
- Write the full SHA-256 of the canonical Markdown into the HTML metadata and keep the matching `*.review.json` SHA synchronized.
- Do not hand-edit generated HTML as the normal workflow. A direct HTML repair is allowed only to restore a broken artifact; then preserve or backport the fix into the rendering workflow so that the next render cannot erase it.

### Required visual template: ARIS academic v1

Use the existing `ARIS render-html (academic, v1)` design as the repository-wide HTML baseline. The following files are visual references:

- `interview_materials/vla/questions/vol_03_vla_action.html`
- `interview_materials/vla/knowledge/vol_03_vla_action.html`

Every rendered page must preserve these characteristics:

- warm paper background `#fdfcf7`, soft paper surface `#f4f1ea`, dark ink `#1a1a1a`;
- academic serif body stack: `Source Serif Pro`, `Source Serif 4`, `Crimson Pro`, `Georgia`, `Songti SC`, `STSong`, then `serif`;
- blue primary color `#1a4a8c` and rust-red accent `#b8390e`;
- desktop content width around `1280px`, with a `260px` sticky left table of contents and a readable main column;
- a compact eyebrow/subtitle area and an H1 separated by a blue double rule;
- H2 headings with a restrained bottom rule, blue H3 headings, and clear H1/H2/H3/H4 hierarchy;
- dark-blue table headers, paper-colored zebra rows, bordered academic tables;
- code blocks with Highlight.js `atom-one-light`, a blue left rule, horizontal overflow, and a monospaced font stack;
- display formulas in a dedicated `.formula` block with the same academic surface, border, padding, and horizontal overflow behavior;
- callouts or metadata blocks styled as deliberate academic notes, not default browser blockquotes;
- print rules that hide navigation and remove decorative backgrounds;
- a responsive breakpoint at approximately `900px` that collapses the page to one column, makes the TOC non-sticky, and keeps tables, code, and formulas usable on narrow screens.

Do not replace this design with the simplified white-page renderer (`Segoe UI`, centered `980px` article, blue left-bar H2 blocks, two-column in-body TOC). In particular, do not run `interview_materials/vla/tools/render_report.py` over an academic page if its current output template would wash out the ARIS layout. Upgrade or select the academic renderer/template first.

### MathJax and Markdown safety

- Use MathJax 3 and support inline `\(...\)` / `$...$` plus display `\[...\]` / `$$...$$` delimiters.
- Configure MathJax to skip `script`, `noscript`, `style`, `textarea`, `pre`, and `code` tags.
- Protect complete math spans before applying Markdown emphasis or other inline substitutions. LaTeX underscores must never be interpreted as HTML emphasis.
- Render important display equations as opaque formula blocks. For example, this must remain intact:

  ```latex
  \ell\!\left(\hat{\bar a}_{b,h,j},\bar a_{b,h,j}\right)
  ```

- A rendered `.formula` block must contain no accidental `<em>` nodes or Markdown-generated markup inside LaTeX.

### Required render checks

Before completing any HTML creation or re-render:

1. Confirm there is exactly one H1 and a valid heading hierarchy.
2. Confirm the academic palette, serif typography, sticky desktop TOC, and `900px` responsive rule are present.
3. Confirm MathJax delimiters are balanced and representative equations compile without visible source text or parser corruption.
4. Confirm `.formula em` count is zero and LaTeX subscripts such as `_{b,h,j}` remain literal in the HTML source.
5. Confirm tables, code blocks, and formulas scroll internally rather than forcing page-wide horizontal overflow.
6. Confirm all local links and anchors resolve.
7. Confirm the embedded source SHA matches the canonical Markdown and `*.review.json`.
8. Perform browser visual QA when the environment permits it, checking both desktop and narrow layouts.

If a renderer cannot satisfy these checks, do not use it to overwrite an existing academic artifact.
