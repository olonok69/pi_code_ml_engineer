#!/usr/bin/env python
"""Build `presentation/Pi_Presentation.pptx` — the Pi course deck (English).

    uv run --with python-pptx --with pillow python presentation/build_pptx_pi.py
    # or: pip install python-pptx pillow && python presentation/build_pptx_pi.py

36 slides 16:9 in three parts (1 Pi · 2 methodology · 3 ticket knowledge graph).
Slide 34 embeds `presentation/kg_graph.png`, produced by `capture_kg_graph.py`.

Adapted from the Cursor volume's `build_pptx_cursor_en.py`: the visual system and the
components are unchanged; only the content layer (one `slide_NN()` per slide) differs.
Every Pi claim comes from `docs/research/PI_FINDINGS_2026-10-17.md` (Pi 1.3.0,
verified 2026-10-17 — Pi moves fast, re-check before reuse).

The file is organized in three layers:

1. **Visual system** — shared palette, type, and geometry (`CHROME`).
2. **Components** — `rect`, `tb`, `card`, `code_block`, `quote`… Each reproduces
   a pattern used across the deck; measurements match the original design.
3. **Content** — one `slide_NN()` function per slide. To edit the deck, change
   those: text lives in component calls, not in the components.
"""

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

HERE = Path(__file__).resolve().parent
OUT = HERE / "Pi_Presentation.pptx"
KG_IMAGE = HERE / "kg_graph.png"

# --------------------------------------------------------------------------- #
# 1. Visual system
# --------------------------------------------------------------------------- #

BG = "0F141A"       # slide background
PANEL = "1A212B"    # cards / panels
BORDER = "2E3948"   # panel border
CODE_BG = "0A0E13"  # code blocks
BAND = "222B38"     # quote band and highlights
TEXT = "E8EAED"     # primary text
MUTED = "9AA4B2"    # secondary text
DIM = "66707E"      # footer
ACCENT = "D97757"   # coral — Part 1 and gates
BLUE = "7AA2C7"     # Part 2
GREEN = "8CC28C"    # Part 3 and "this is good"

UI = "Segoe UI"
MONO = "Consolas"

SLIDE_W, SLIDE_H = 13.333, 7.5
FOOTER = "Pi · Course / Workshop"

THIN = Pt(0.75)  # normal border
THICK = Pt(1.0)  # emphasis border


def In(v):
    """Inches → EMU, accepting fractions."""
    return Emu(int(round(v * 914400)))


def R(text, size, color, bold=False, font=UI):
    """Run spec: (text, size, color, bold, font)."""
    return (text, size, color, bold, font)


# --------------------------------------------------------------------------- #
# 2. Components
# --------------------------------------------------------------------------- #


def rect(slide, x, y, w, h, fill, border=None, border_w=THIN):
    """Rectangle with no shadow. `fill=None` => transparent."""
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, In(x), In(y), In(w), In(h))
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid()
        sh.fill.fore_color.rgb = RGBColor.from_string(fill)
    if border is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = RGBColor.from_string(border)
        sh.line.width = border_w
    sh.shadow.inherit = False
    return sh


def tb(slide, x, y, w, h, paras, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
       sa=4, ls=1.0):
    """Text box with no margins. `paras` is a list of lists of `R(...)` runs."""
    box = slide.shapes.add_textbox(In(x), In(y), In(w), In(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    for i, runs in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(sa)
        p.space_before = Pt(0)
        p.line_spacing = ls
        for text, size, color, bold, font in runs:
            run = p.add_run()
            run.text = text
            run.font.name = font
            run.font.size = Pt(size)
            run.font.bold = bold
            run.font.color.rgb = RGBColor.from_string(color)
    return box


def line(slide, x, y, w, h, runs, **kw):
    """Shortcut for a single-paragraph text box."""
    return tb(slide, x, y, w, h, [runs], **kw)


# --- slide chrome ----------------------------------------------------------- #


def new_slide(prs, banded=False):
    """Background + side chrome. `banded` = top/bottom stripes (title and
    part dividers); otherwise left vertical bar (content slides)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank
    rect(slide, -0.1, -0.1, 13.53, SLIDE_H + 0.2, BG)
    if banded:
        rect(slide, 0, 0, SLIDE_W, 0.16, ACCENT)
        rect(slide, 0, SLIDE_H - 0.16, SLIDE_W, 0.16, ACCENT)
    else:
        rect(slide, 0, 0, 0.22, SLIDE_H, ACCENT)
    return slide


def page_number(slide, n):
    line(slide, 11.8, 7.02, 1.2, 0.35, [R(str(n), 9.5, DIM, True)], align=PP_ALIGN.RIGHT)


def chrome(prs, eyebrow, title, page):
    """Content slide: left bar, eyebrow, title, rule, and footer."""
    slide = new_slide(prs)
    line(slide, 0.7, 0.55, 11.0, 0.4, [R(eyebrow, 12, ACCENT, True)])
    line(slide, 0.68, 0.92, 12.0, 1.1, [R(title, 30, TEXT, True)])
    rect(slide, 0.72, 1.72, 1.1, 0.045, ACCENT)
    line(slide, 0.7, 7.02, 8.0, 0.35, [R(FOOTER, 9.5, DIM)])
    page_number(slide, page)
    return slide


def part_divider(prs, part, title, subtitle, chips, page):
    """Part divider: stripes, part number, large title, and index chips."""
    slide = new_slide(prs, banded=True)
    line(slide, 1.0, 1.3, 11.0, 0.5, [R(part, 16, ACCENT, True)])
    line(slide, 0.95, 1.8, 11.5, 1.2, [R(title, 44, TEXT, True)])
    rect(slide, 1.02, 2.85, 1.4, 0.05, ACCENT)
    line(slide, 1.0, 3.05, 11.3, 0.6, [R(subtitle, 15, MUTED)], ls=1.1)
    for i, text in enumerate(chips):
        x = 1.0 if i % 2 == 0 else 7.0
        y = 3.85 + 0.62 * (i // 2)
        rect(slide, x, y, 5.7, 0.52, PANEL, BORDER)
        line(slide, x + 0.25, y + 0.05, 5.3, 0.42, [R(text, 12.5, TEXT)],
             anchor=MSO_ANCHOR.MIDDLE)
    page_number(slide, page)
    return slide


# --- reusable blocks -------------------------------------------------------- #


def quote(slide, text, y=6.35):
    """Closing quote band at the foot of the slide."""
    rect(slide, 0.7, y, 11.95, 0.52, BAND, BORDER)
    rect(slide, 0.7, y, 0.09, 0.52, ACCENT)
    line(slide, 0.95, y + 0.03, 11.6, 0.46,
         [R("“ ", 13, ACCENT, True), R(text, 12.5, TEXT), R(" ”", 13, ACCENT, True)],
         anchor=MSO_ANCHOR.MIDDLE)


def panel(slide, x, y, w, h, border=BORDER, border_w=THIN, fill=PANEL):
    return rect(slide, x, y, w, h, fill, border, border_w)


def bullets(slide, x, y, w, h, items, color, size=11.5, ls=1.05):
    """List with ▸ marker in the section color."""
    paras = [[R("▸  ", size, color, True), R(t, size, TEXT)] for t in items]
    return tb(slide, x, y, w, h, paras, sa=6, ls=ls)


def card(slide, x, y, w, h, title, items, color, items_h, size=11.5):
    """Panel with colored header + bullet list."""
    panel(slide, x, y, w, h)
    line(slide, x + 0.3, y + 0.22, w - 0.5, 0.4, [R(title, 14, color, True)])
    bullets(slide, x + 0.3, y + 0.72, w - 0.55, items_h, items, color, size)


def num_card(slide, x, y, w, h, badge, title, desc, desc_h):
    """Card with square badge (number, letter, or icon) + title + description."""
    panel(slide, x, y, w, h)
    rect(slide, x + 0.22, y + 0.22, 0.5, 0.5, ACCENT)
    line(slide, x + 0.22, y + 0.24, 0.5, 0.46, [R(badge, 15, BG, True)],
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    line(slide, x + 0.9, y + 0.16, w - 1.05, 0.4, [R(title, 14.5, TEXT, True)])
    line(slide, x + 0.9, y + 0.5, w - 1.05, desc_h, [R(desc, 11, MUTED)], ls=1.02)


def code_block(slide, x, y, w, h, lines):
    """Code block: dark box + monospace lines.

    `lines` is a list of strings or `(text, color)` tuples — color is used
    for gray comments.
    """
    rect(slide, x, y, w, h, CODE_BG, BORDER)
    paras = []
    for item in lines:
        text, color = item if isinstance(item, tuple) else (item, TEXT)
        paras.append([R(text, 11.5, color, font=MONO)])
    tb(slide, x + 0.28, y + 0.2, w - 0.5, h - 0.35, paras, sa=2, ls=1.12)


def label(slide, x, y, w, text, color=BLUE, size=11):
    """Small label above a block."""
    return line(slide, x, y, w, 0.3, [R(text, size, color, True)])


def stack_row(slide, y, name, desc, note, x=0.7, w=7.6, h=0.48):
    """Stacked row (context anatomy): name · description · note on the right."""
    panel(slide, x, y, w, h)
    line(slide, x + 0.25, y + 0.04, 2.6, 0.4, [R(name, 11.5, BLUE, True)],
         anchor=MSO_ANCHOR.MIDDLE)
    line(slide, 3.6, y + 0.04, 4.0, 0.4, [R(desc, 10.5, TEXT)], anchor=MSO_ANCHOR.MIDDLE)
    line(slide, 7.35, y + 0.04, 0.85, 0.4, [R(note, 9.0, MUTED)],
         align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)


def flag_row(slide, y, verdict, headline, detail):
    """Wide row with colored left tab (green = good, coral = watch out)."""
    color = GREEN if verdict else ACCENT
    panel(slide, 0.7, y, 11.95, 0.58)
    rect(slide, 0.7, y, 0.08, 0.58, color)
    line(slide, 0.95, y + 0.05, 4.6, 0.48, [R(headline, 11.5, color, True)],
         anchor=MSO_ANCHOR.MIDDLE)
    line(slide, 5.7, y + 0.05, 6.8, 0.48, [R(detail, 11.5, TEXT)],
         anchor=MSO_ANCHOR.MIDDLE)


def step_row(slide, y, label_text, detail):
    """Real-example row: stage + what happened."""
    panel(slide, 0.7, y, 11.95, 0.48)
    rect(slide, 0.7, y, 0.08, 0.48, ACCENT)
    line(slide, 0.95, y + 0.04, 2.4, 0.4, [R(label_text, 11.5, BLUE, True)],
         anchor=MSO_ANCHOR.MIDDLE)
    line(slide, 3.5, y + 0.04, 9.0, 0.4, [R(detail, 11, TEXT)], anchor=MSO_ANCHOR.MIDDLE)


def tool_row(slide, y, phase, tool, note, highlight=False):
    """Tool-prevalence row: phase · tool · cost."""
    if highlight:
        panel(slide, 0.7, y, 11.95, 0.5, border=ACCENT, border_w=THICK, fill=BAND)
    else:
        panel(slide, 0.7, y, 11.95, 0.5)
    line(slide, 0.95, y + 0.05, 2.9, 0.4,
         [R(phase, 11.5, ACCENT if highlight else BLUE, True)], anchor=MSO_ANCHOR.MIDDLE)
    line(slide, 3.95, y + 0.05, 7.0, 0.4, [R(tool, 11.5, TEXT)], anchor=MSO_ANCHOR.MIDDLE)
    line(slide, 11.1, y + 0.05, 1.4, 0.4, [R(note, 9.5, MUTED)],
         align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)


def compare_row(slide, y, field, left, right):
    """Comparative table row: two options side by side."""
    panel(slide, 0.7, y, 11.95, 0.52)
    line(slide, 0.95, y + 0.05, 3.3, 0.42, [R(field, 11.5, TEXT, True)],
         anchor=MSO_ANCHOR.MIDDLE)
    line(slide, 4.6, y + 0.05, 3.7, 0.42, [R(left, 11, MUTED)],
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    line(slide, 8.6, y + 0.05, 3.7, 0.42, [R(right, 11, MUTED)],
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


def flow_step(slide, x, y, number, text, gate=False):
    """Step in the 11-stage flow. Coral stages are gates."""
    panel(slide, x, y, 5.85, 0.56,
          border=ACCENT if gate else BORDER, border_w=THICK if gate else THIN)
    rect(slide, x + 0.14, y + 0.11, 0.34, 0.34, ACCENT if gate else BAND)
    line(slide, x + 0.14, y + 0.11, 0.34, 0.34,
         [R(number, 11, BG if gate else TEXT, True)],
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    line(slide, x + 0.62, y + 0.06, 5.1, 0.46, [R(text, 11.5, TEXT)],
         anchor=MSO_ANCHOR.MIDDLE)


def summary_card(slide, x, y, number, title, desc, color):
    """Compact closing card."""
    panel(slide, x, y, 5.85, 0.85)
    rect(slide, x + 0.2, y + 0.18, 0.44, 0.44, color)
    line(slide, x + 0.2, y + 0.19, 0.44, 0.42, [R(number, 13, BG, True)],
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    line(slide, x + 0.8, y + 0.1, 5.0, 0.35, [R(title, 12.5, TEXT, True)])
    line(slide, x + 0.8, y + 0.43, 5.0, 0.38, [R(desc, 10, MUTED)])


# --------------------------------------------------------------------------- #
# 3. Content — one function per slide
# --------------------------------------------------------------------------- #


def slide_01(prs):
    """Title slide."""
    slide = new_slide(prs, banded=True)
    line(slide, 1.0, 1.4, 11.0, 0.5,
         [R("COURSE / WORKSHOP · DEVELOPER TOOLING", 14, ACCENT, True)])
    tb(slide, 0.95, 2.0, 11.5, 2.0, [
        [R("Pi", 60, TEXT, True)],
        [R("a minimal agent, ", 26, MUTED), R("the same discipline", 26, TEXT, True)],
    ], sa=10)
    rect(slide, 1.02, 4.2, 1.4, 0.05, ACCENT)
    tb(slide, 1.0, 4.45, 11.5, 1.7, [
        [R("PART 1 — ", 15, ACCENT, True),
         R("Pi: install · modes · AGENTS.md · safety by design · sessions · context & "
           "caching · MCP · skills · subagents · extensions · automation", 13.5, MUTED)],
        [R("PART 2 — ", 15, BLUE, True),
         R("The methodology (tool-agnostic): gated flow · CodeGraph / Serena / GSD · "
           "transfer to Pi · ops (machine-sync + S3)", 13.5, MUTED)],
        [R("PART 3 — ", 15, GREEN, True),
         R("The ticket knowledge graph, built with graphify: pipeline, "
           "skills kg / kg-refresh, and the real graph", 13.5, MUTED)],
    ], sa=8)
    line(slide, 1.0, 6.7, 11.0, 0.4,
         [R("Course volume 3 (after Claude Code and Cursor): verified against pi.dev/docs "
            "on 2026-10-17, Pi 1.3.0 — Pi moves fast, re-check before reuse.", 11, DIM)])


def slide_02(prs):
    """Agenda."""
    slide = chrome(prs, "AGENDA", "One course, three parts", 2)

    def column(x, y0, heading, color, items):
        line(slide, x, y0, 5.85, 0.4, [R(heading, 14, color, True)])
        for i, text in enumerate(items):
            y = y0 + 0.45 + 0.56 * i
            panel(slide, x, y, 5.85, 0.48)
            line(slide, x + 0.25, y + 0.04, 5.5, 0.4, [R(text, 12, TEXT)],
                 anchor=MSO_ANCHOR.MIDDLE)

    column(0.7, 1.95, "PART 1 · Pi", ACCENT, [
        "01  Install, auth, modes, models",
        "02  Memory, permissions (by design), sessions",
        "03  Context: window, compaction, prompt caching",
        "04  MCP — built in since 0.99",
        "05  Skills, prompt templates, packages",
        "06  Subagents (not built in — the options)",
        "07  Extensions as hooks + automation",
    ])
    column(6.8, 1.95, "PART 2 · The methodology (tool-agnostic)", BLUE, [
        "08  The 11-stage flow + five-check gate",
        "09  The method's tools",
        "10  Transfer: from Claude Code to Pi",
        "11  Ops: machine-sync + S3 record",
    ])
    column(6.8, 4.75, "PART 3 · The ticket graph (graphify)", GREEN, [
        "12  Design · pipeline · skills kg / kg-refresh · the real graph",
        "13  Close",
    ])


def slide_03(prs):
    part_divider(
        prs, "PART 1", "Pi",
        "The tool: a minimal terminal agent — what it ships, and what it leaves to you.",
        ["01 · Install, auth, modes", "02 · Memory, permissions, sessions",
         "03 · Context and prompt caching", "04 · MCP",
         "05 · Skills and packages", "06 · Subagents",
         "07 · Extensions + automation"],
        3)


def slide_04(prs):
    slide = chrome(prs, "PART 1 · 01 · INSTALL AND AUTH",
                   "Install in one line, log in once", 4)
    cards = [
        ("1", "Installer (pins deps)",
         "curl -fsSL https://pi.dev/install.sh | sh  ·  Windows: install.ps1 · later: pi update"),
        ("2", "npm (Node >= 22.19)",
         "npm install -g --ignore-scripts @earendil-works/pi-coding-agent"),
        ("3", "Auth: /login or env vars",
         "OAuth or API key → ~/.pi/agent/auth.json · ANTHROPIC_API_KEY, OPENAI_API_KEY…"),
        ("4", "~40 providers + local",
         "Bedrock, Vertex, Azure, OpenRouter… · llama.cpp (/llama), Ollama via models.json"),
    ]
    for i, (badge, title, desc) in enumerate(cards):
        x = 0.7 if i % 2 == 0 else 6.815
        y = 2.05 + 1.28 * (i // 2)
        num_card(slide, x, y, 5.835, 1.0, badge, title, desc, 0.45)

    label(slide, 0.7, 4.51, 5.9, "Start in any project")
    code_block(slide, 0.7, 4.85, 5.9, 1.3, [
        "cd your-project && pi",
        "/login            # pick provider",
        "/model            # pick model",
    ])
    card(slide, 6.9, 4.51, 5.75, 1.55, "Naming gotcha (old tutorials)", [
        "badlogic/pi-mono → earendil-works/pi",
        "@mariozechner/… deprecated → @earendil-works/…",
        "Binary is still pi · MIT licence",
    ], BLUE, 0.65)
    quote(slide, "Install is trivial; the interesting part is what Pi chose NOT to build.")


def slide_05(prs):
    slide = chrome(prs, "PART 1 · 01 · MODES AND MODELS",
                   "Five ways to drive it; any model, any effort", 5)
    rows = [
        ("Interactive TUI", "pi — fullscreen; !cmd sends output to the model", "humans"),
        ("Print", 'pi -p "…" — final text; non-zero on error/abort/length', "scripts"),
        ("JSON events", 'pi --mode json "…" — JSONL event stream', "tooling"),
        ("RPC", "pi --mode rpc — JSONL commands on stdin, events on stdout", "long-lived"),
        ("SDK", "createAgentSession() — in-process Node / Bun", "your app"),
    ]
    for i, (name, desc, note) in enumerate(rows):
        stack_row(slide, 2.0 + 0.58 * i, name, desc, note)

    label(slide, 8.6, 2.01, 4.05, "Models and thinking")
    code_block(slide, 8.6, 2.35, 4.05, 2.55, [
        "/model · Ctrl+L · Ctrl+P",
        "/thinking · Shift+Tab",
        "pi --model sonnet:high",
        "pi --list-models [search]",
        ("# off|minimal|low|medium", MUTED),
        ("#   |high|xhigh|max", MUTED),
    ])
    line(slide, 0.7, 5.05, 11.95, 0.9, [
        R("Thinking levels are clamped to what the model supports; ", 12, TEXT, True),
        R("default is medium. Sessions record model and thinking changes, so resuming "
          "a session restores them.", 12, MUTED),
    ], ls=1.1)
    quote(slide, "One binary, five surfaces — the TUI for you, -p / JSON / RPC / SDK "
                 "for everything else.")


def slide_06(prs):
    slide = chrome(prs, "PART 1 · 02 · MEMORY AND INSTRUCTIONS",
                   "AGENTS.md: walk UP, one file per directory", 6)
    label(slide, 0.7, 1.81, 6.0, "What Pi loads (global first, then root → cwd)")
    code_block(slide, 0.7, 2.15, 6.0, 2.35, [
        "~/.pi/agent/AGENTS.md        # global",
        "/…/parent/AGENTS.md          # every ancestor",
        "./AGENTS.md                  # cwd",
        ("# per directory, FIRST hit only:", MUTED),
        "AGENTS.override.md > AGENTS.md",
        "  > AGENTS.MD > CLAUDE.md > CLAUDE.MD",
    ])
    card(slide, 7.0, 1.82, 5.65, 2.55, "Differences vs Claude Code / Cursor", [
        "NO nested discovery below cwd",
        "NO scoped rules (.mdc globs, .claude/rules)",
        "NO @imports (NOT DOCUMENTED) — plain text",
        "AGENTS.md shadows CLAUDE.md in the same dir",
    ], ACCENT, 1.65)
    card(slide, 0.7, 4.6, 11.95, 1.5,
         "The two-level pattern still works — with pointers", [
             "Level 1: small ~/.pi/agent/AGENTS.md + repo-root AGENTS.md (pointers only). "
             "Level 2: data/changes/** on demand.",
             "Pi does not read ~/.claude/CLAUDE.md — symlink or copy it. Context files load "
             "regardless of trust (-nc to disable).",
         ], BLUE, 0.6)


def slide_07(prs):
    slide = chrome(prs, "PART 1 · 02 · SYSTEM PROMPT AND MEMORY",
                   "SYSTEM.md, APPEND_SYSTEM.md — and no auto-memory", 7)
    card(slide, 0.7, 2.0, 5.85, 2.6, "Own the system prompt", [
        "SYSTEM.md REPLACES Pi's default prompt",
        "APPEND_SYSTEM.md APPENDS to it",
        "~/.pi/agent/ or .pi/ — trusted project file wins, not combined",
        "CLI: --system-prompt · --append-system-prompt",
    ], ACCENT, 1.7)
    card(slide, 6.8, 2.0, 5.85, 2.6, "Cross-session memory: not built in", [
        "Homepage: memory belongs in extensions",
        "Sessions persist as JSONL and resume (pi -c)",
        "[3rd-party] pi-memory, pi-observational-memory… untested",
        "The method's substitute: write-once ledgers",
    ], BLUE, 1.7)
    card(slide, 0.7, 4.8, 11.95, 1.35, "The methodology's answer (unchanged)", [
        "STATUS.md · FOLLOWUPS.md · SHARP_EDGES.md under data/changes/ — "
        "durable, greppable, tool-independent. Plus PI_SESSION_FILE for the raw trail.",
    ], GREEN, 0.5)
    quote(slide, "A small default prompt you can replace — and memory you write on purpose.")


def slide_08(prs):
    slide = chrome(prs, "PART 1 · 02 · PERMISSIONS AND SAFETY",
                   "No permission popups — by design", 8)
    panel(slide, 0.7, 1.95, 11.95, 0.62, border=ACCENT, fill=BAND)
    line(slide, 0.95, 2.0, 11.5, 0.52, [
        R("pi.dev: ", 12.5, ACCENT, True),
        R("“No permission popups — Run in a container, or build your own confirmation "
          "flow with extensions.”", 12.5, TEXT),
    ], anchor=MSO_ANCHOR.MIDDLE)
    rows = [
        (True, "Containers / Docker Sandboxes",
         "Mount only the workspace; never mount host ~/.pi/agent"),
        (True, "Extensions as gates",
         "permission-gate.ts, protected-paths.ts, sandbox/ examples; tool_call → block"),
        (True, "Static tool restriction",
         "--tools read,grep,find,ls · --exclude-tools · defaultTools · MCP hidden"),
        (False, "Project trust is NOT a sandbox",
         "/trust only gates .pi/ resources; -p/JSON/RPC skip them unless --approve"),
        (False, "Regex gates can be bypassed",
         "sh -c, aliases, scripts — OS isolation for real guarantees"),
    ]
    for i, (verdict, headline, detail) in enumerate(rows):
        flag_row(slide, 2.75 + 0.66 * i, verdict, headline, detail)
    quote(slide, "Pi gives you mechanisms, not a policy: the human-owns-external policy "
                 "is yours to enforce.")


def slide_09(prs):
    slide = chrome(prs, "PART 1 · 02 · SESSIONS",
                   "Sessions are a tree, not a log", 9)
    cards = [
        ("⌂", "Storage",
         "~/.pi/agent/sessions/--<cwd>--/<ts>_<id>.jsonl — JSONL tree (id/parentId), v3."),
        ("↻", "Resume",
         "pi -c (latest for this cwd) · pi -r / /resume picker · --session · --no-session."),
        ("⑂", "Branch",
         "/tree moves within the file (+ summary) · /fork from a user msg · /clone · Esc-Esc."),
        ("⇪", "Export / share",
         "/export (HTML/JSONL) · pi --export · /share → gist via gh, or Radius artifact."),
    ]
    for i, (badge, title, desc) in enumerate(cards):
        x = 0.7 if i % 2 == 0 else 6.815
        y = 2.15 + 1.38 * (i // 2)
        num_card(slide, x, y, 5.835, 1.1, badge, title, desc, 0.55)
    line(slide, 0.7, 4.95, 11.95, 0.9, [
        R("Shell tools see PI_SESSION_ID / PI_SESSION_FILE / PI_MODEL: ", 12, TEXT, True),
        R("your scripts can cite the exact session that produced a change. No "
          "cross-surface handoff — a handoff.ts example extension starts a focused "
          "session instead.", 12, MUTED),
    ], ls=1.1)
    quote(slide, "Side quest? /tree or /fork — and the main branch stays clean.")


def slide_10(prs):
    slide = chrome(prs, "PART 1 · 03 · CONTEXT",
                   "Context window and compaction", 10)
    rows = [
        ("System prompt", "Small by design (+ SYSTEM/APPEND_SYSTEM)", "fixed"),
        ("AGENTS.md chain", "Global + ancestors + cwd — you control it", "you decide"),
        ("Skills", "Only name + description + path until used", "tiny"),
        ("MCP", "codemode default: a one-line server summary", "tiny"),
        ("Conversation + results", "Files read, command output… grows", "grows"),
    ]
    for i, (name, desc, note) in enumerate(rows):
        stack_row(slide, 2.0 + 0.58 * i, name, desc, note)

    label(slide, 8.6, 2.01, 4.05, "Compaction controls")
    code_block(slide, 8.6, 2.35, 4.05, 2.55, [
        "/compact [focus]",
        ("# settings.json:", MUTED),
        "compaction.enabled",
        "compaction.reserveTokens",
        "compaction.keepRecentTokens",
        ("# 16384 / 20000 defaults", MUTED),
    ])
    line(slide, 0.7, 5.05, 11.95, 0.9, [
        R("Auto-compaction fires when contextTokens > window - reserveTokens: ", 12, TEXT,
          True),
        R("a structured summary (Goal / Progress / Key Decisions / Next Steps…) replaces "
          "older turns — the originals stay in the JSONL file.", 12, MUTED),
    ], ls=1.1)
    quote(slide, "The footer shows usage; compaction is a summary you can steer with "
                 "/compact instructions.")


def slide_11(prs):
    slide = chrome(prs, "PART 1 · 03 · CONTEXT",
                   "Prompt caching: automatic — with knobs", 11)
    line(slide, 0.7, 1.9, 11.95, 0.55, [
        R("Anthropic API economics still apply (write 1.25× / 2× for 1 h, read 0.1×). "
          "Pi places the markers for you: ", 12.5, MUTED),
        R("system · last tool · last message", 12.5, ACCENT, True, MONO),
        R(".", 12.5, MUTED),
    ])
    rows = [
        (True, "Automatic cache_control / prompt_cache_key",
         "Anthropic markers; OpenAI session affinity"),
        (True, "PI_CACHE_RETENTION=long",
         "Extended retention where supported (e.g. 1 h)"),
        (True, 'cacheWarming: "off" | "streaming" | "idle"',
         "Keeps caches warm when saving is ≥ $0.05 (global)"),
        (True, "showCacheMissNotices: true",
         "See misses, warm-ups, compaction usage · /session"),
        (False, "Switching models mid-session",
         "Loses the cache; compaction requests do not write it"),
    ]
    for i, (verdict, headline, detail) in enumerate(rows):
        flag_row(slide, 2.6 + 0.66 * i, verdict, headline, detail)
    quote(slide, "Runnable mechanism demo: examples/prompt-caching/cache_demo.py — "
                 "the API, not Pi.")


def slide_12(prs):
    slide = chrome(prs, "PART 1 · 03 · CONTEXT",
                   "Keeping context lean: Pi's own levers", 12)
    cards = [
        ("1", "Four default tools",
         "read · bash · edit · write. Add or drop with --tools / defaultTools."),
        ("2", "Skills load lazily",
         "Only name + description in the prompt; SKILL.md is read when used."),
        ("3", "MCP codemode",
         "Tools are not declared; scripts filter big output before the model sees it."),
        ("4", "Big results truncated",
         "MCP text > 20 KB is middle-truncated, full text saved to a temp file."),
        ("5", "/tree and /fork",
         "Side quests live on a branch; the main line stays short."),
        ("6", "Minimal runs",
         "--no-context-files · --no-skills · --no-extensions · --no-session."),
    ]
    for i, (badge, title, desc) in enumerate(cards):
        x = 0.7 if i % 2 == 0 else 6.815
        y = 2.0 + 1.46 * (i // 2)
        num_card(slide, x, y, 5.835, 1.18, badge, title, desc, 0.63)
    quote(slide, "Part 2's tool prevalence is, at bottom, context policy — "
                 "Pi just starts leaner.")


def slide_13(prs):
    slide = chrome(prs, "PART 1 · 04 · MCP",
                   "MCP: built in since 0.99 (2026-09-29)", 13)
    line(slide, 0.7, 1.9, 11.95, 0.6, [
        R("Gotcha: much web material still says “Pi has no MCP” — out of date. "
          "Same mcpServers shape as Claude Code/Cursor, in ", 12.5, MUTED),
        R(".pi/mcp.json", 12.5, ACCENT, True, MONO),
        R(" (trusted) or ~/.pi/agent/mcp.json.", 12.5, MUTED),
    ])
    cards = [
        ("C", "codemode (DEFAULT)", "Not declared as tools — callable from QuickJS scripts."),
        ("D", "direct", "Declared like a built-in — use for tools the agent must reach for."),
        ("T", "deferred", "Loaded on demand via tool_search."),
        ("H", "hidden", "Unreachable — hide destructive tools."),
    ]
    for i, (badge, title, desc) in enumerate(cards):
        x = 0.7 if i % 2 == 0 else 6.785
        y = 2.55 + 1.07 * (i // 2)
        num_card(slide, x, y, 5.865, 0.85, badge, title, desc, 0.3)

    label(slide, 0.7, 4.62, 11.95,
          "stdio + streamable HTTP (SSE rejected) · tools named mcp__server__tool")
    code_block(slide, 0.7, 4.96, 11.95, 1.1, [
        "pi mcp add codegraph -- codegraph serve --path <repo> --mcp   # then: pi mcp list",
        '"toolExposure": { "codegraph_explore": "direct" }   # per tool, globs allowed',
    ])


def slide_14(prs):
    slide = chrome(prs, "PART 1 · 05 · SKILLS AND PACKAGES",
                   "Skills: the Agent Skills standard", 14)
    cards = [
        ("1", "Skills",
         "<dir>/SKILL.md with name + description. ~/.pi/agent/skills, .pi/skills, "
         ".agents/skills, \"skills\" setting."),
        ("2", "Invoke: /skill:name [args]",
         "Not /name. The model also auto-loads by description (it reads SKILL.md)."),
        ("3", "Interop with Claude/Cursor",
         "Unknown frontmatter keys ignored silently [TESTED]. .claude/skills not "
         "auto-found — add it via settings."),
        ("4", "Prompt templates + packages",
         "prompts/<n>.md → /<n> · pi install npm:… / git:… · gallery pi.dev/packages."),
    ]
    for i, (badge, title, desc) in enumerate(cards):
        x = 0.7 if i % 2 == 0 else 6.815
        y = 2.05 + 1.43 * (i // 2)
        num_card(slide, x, y, 5.835, 1.15, badge, title, desc, 0.6)

    line(slide, 0.7, 4.75, 11.95, 0.9, [
        R("Measured: ", 12.5, ACCENT, True),
        R("pointing \"skills\" at all of ~/.claude/skills loaded ~85 skills — every "
          "description lands in the prompt. List the directories you want, one by one. "
          "Name collisions: first one wins.", 12.5, MUTED),
    ], ls=1.05)
    quote(slide, "Same SKILL.md as Claude Code and Cursor — only the invocation "
                 "changes: /skill:day start.")


def slide_15(prs):
    slide = chrome(prs, "PART 1 · 06 · SUBAGENTS",
                   "Subagents: not built in — on purpose", 15)
    card(slide, 0.7, 2.0, 5.85, 2.2, "pi.dev, “What we didn't build”", [
        "“No sub-agents — Spawn Pi instances via tmux,",
        "  or build your own with extensions, or install",
        "  a package.” (Same for plan mode.)",
        "So: pick one of three options",
    ], ACCENT, 1.3)
    label(slide, 6.8, 2.01, 5.85, "Official example extension (subagent/)")
    code_block(slide, 6.8, 2.35, 5.85, 2.2, [
        ("# ~/.pi/agent/agents/scout.md", MUTED),
        "---",
        "name: scout",
        "description: Read-only recon",
        "tools: read, grep, find, ls",
        "---",
        "Use CodeGraph first, then Serena…",
    ])
    card(slide, 0.7, 4.75, 11.95, 1.4, "The three options", [
        "1) examples/extensions/subagent — each subagent is a separate pi process; single, "
        "parallel (max 8, 4 at once), chain",
        "2) [3rd-party] pi-subagents (untested)   ·   3) tmux / parallel pi -p processes",
    ], BLUE, 0.6)


def slide_16(prs):
    slide = chrome(prs, "PART 1 · 06 · SUBAGENTS",
                   "A read-only subagent, two ways", 16)
    card(slide, 0.7, 2.0, 5.85, 2.6, "A · Agent file (subagent extension)", [
        "tools: read, grep, find, ls — no bash/edit/write",
        "~/.pi/agent/agents/*.md always loaded",
        ".pi/agents/*.md only with agentScope project|both",
        "Note: the shipped scout DOES include bash",
    ], BLUE, 1.7)
    label(slide, 6.8, 1.81, 5.85, "B · A disposable child process (documented flags)")
    code_block(slide, 6.8, 2.15, 5.85, 1.9, [
        "pi -p --no-session \\",
        "  --tools read,grep,find,ls \\",
        '  "map the callers of parse_header" \\',
        "  </dev/null",
    ])
    card(slide, 6.8, 4.25, 5.85, 1.9, "Why it matters", [
        "Isolated context: only the answer returns",
        "No write tools = no surprise edits",
        "</dev/null — or it waits for stdin EOF",
    ], ACCENT, 1.0)
    line(slide, 0.7, 4.75, 5.85, 1.3, [
        R("Same refactor-scout procedure as the other volumes: ", 11.5, MUTED),
        R("CodeGraph → Serena → grep, packaged as an agent file in "
          "examples/subagents/.", 11.5, TEXT),
    ], ls=1.1)
    quote(slide, "Read-only is a tool list, not a promise — remove the write tools.")


def slide_17(prs):
    slide = chrome(prs, "PART 1 · 06 · SUBAGENTS",
                   "Subagent extension or parallel processes?", 17)
    line(slide, 4.6, 2.0, 3.7, 0.4, [R("SUBAGENT EXTENSION", 13, BLUE, True)],
         align=PP_ALIGN.CENTER)
    line(slide, 8.6, 2.0, 3.7, 0.4, [R("PARALLEL pi / RPC", 13, ACCENT, True)],
         align=PP_ALIGN.CENTER)
    rows = [
        ("Context", "Isolated; returns a result", "Full session per process"),
        ("Communication", "Result → main session", "None (no inbox, no teams)"),
        ("Orchestration", "single · parallel · chain", "tmux, your script, RpcClient"),
        ("Use it for", "Side-quests: scout, review", "Long or partitioned work"),
        ("Config", "~/.pi/agent/agents/*.md", "pi -p / --mode rpc flags"),
    ]
    for i, (field, left, right) in enumerate(rows):
        compare_row(slide, 2.45 + 0.62 * i, field, left, right)
    line(slide, 0.7, 5.68, 11.95, 0.5, [
        R("No Agent Teams (NOT DOCUMENTED): ", 11.5, GREEN, True),
        R("partition by branch/file before launching parallel processes; a human (or the "
          "main session) integrates the results.", 11.5, MUTED),
    ])
    quote(slide, "Subagent so noise dies outside; parallel processes for real "
                 "parallelism. The cost is not the same.")


def slide_18(prs):
    slide = chrome(prs, "PART 1 · 07 · EXTENSIONS",
                   "Extensions are the hooks — in TypeScript", 18)
    card(slide, 0.7, 2.0, 5.85, 3.1, "The extension contract", [
        "~/.pi/agent/extensions/*.ts or .pi/extensions/ (trusted)",
        "Loaded via jiti — no build step · /reload hot-reloads",
        "pi.on(event, handler): tool_call, tool_result, user_bash,",
        "  before_agent_start, session_*, context…",
        "tool_call → { block: true, reason } — also nested/MCP calls",
        "Handler throws → the tool is BLOCKED (fail-safe)",
    ], ACCENT, 2.2)
    label(slide, 6.8, 2.01, 5.85, "block-external-git.ts  [TESTED on 1.3.0]")
    code_block(slide, 6.8, 2.35, 5.85, 2.4, [
        'pi.on("tool_call", async (event) => {',
        '  if (event.toolName !== "bash") return;',
        "  const cmd = String(event.input.command);",
        "  const hit = EXTERNAL.find(r => r.test(cmd));",
        "  if (hit) return { block: true,",
        '    reason: "Blocked by policy: external…" };',
        "});",
        ("// EXTERNAL = git push, gh pr create|merge…", MUTED),
    ])
    quote(slide, "AGENTS.md asks it to behave; an extension guarantees it — and runs "
                 "with full OS permissions, so install it globally.")


def slide_19(prs):
    slide = chrome(prs, "PART 1 · 07 · AUTOMATION",
                   "Print, JSON, RPC, SDK — and four gotchas", 19)
    cards = [
        ("a", "</dev/null  [TESTED]",
         "Non-TTY stdin never closed → pi -p waits for EOF and looks hung."),
        ("b", "--approve",
         "-p / JSON / RPC can't show the trust prompt: .pi/ resources skipped silently."),
        ("c", "JSON mode exit code",
         "A failed run does not by itself exit non-zero — inspect the events."),
        ("d", "SDK has no MCP by default",
         "Add createMcpExtension() etc. via DefaultResourceLoader + bindExtensions()."),
    ]
    for i, (badge, title, desc) in enumerate(cards):
        x = 0.7 if i % 2 == 0 else 6.785
        y = 2.05 + 1.17 * (i // 2)
        num_card(slide, x, y, 5.865, 0.95, badge, title, desc, 0.4)

    label(slide, 0.7, 4.34, 11.95,
          "CI pattern (no official GitHub Action — NOT DOCUMENTED; post results from a human-owned step)")
    code_block(slide, 0.7, 4.68, 11.95, 1.3, [
        "npm i -g --ignore-scripts @earendil-works/pi-coding-agent@<pin>",
        'pi -p --no-session --approve --model anthropic/<id> "review the diff" </dev/null',
        ("# SDK: const { session } = await createAgentSession(); await session.prompt(\"…\");",
         MUTED),
    ])


def slide_20(prs):
    part_divider(
        prs, "PART 2", "The methodology",
        "Tool-agnostic: demonstrated with Pi, but the discipline travels.",
        ["08 · The 11-stage flow + five-check gate",
         "09 · The method's tools",
         "10 · Transfer: from Claude Code to Pi",
         "11 · Ops: machine-sync + shared record (S3)"],
        20)


def slide_21(prs):
    slide = chrome(prs, "PART 2 · 08 · THE METHODOLOGY",
                   "The agent is a disciplined collaborator", 21)
    panel(slide, 0.7, 2.0, 11.95, 1.15, border=ACCENT, border_w=THICK, fill=BAND)
    line(slide, 1.0, 2.18, 11.4, 0.85,
         [R("“Autonomy is earned decision-by-decision, not granted in bulk.”", 17, TEXT,
            True)],
         anchor=MSO_ANCHOR.MIDDLE)
    card(slide, 0.7, 3.4, 5.85, 2.05, "The agent owns", [
        "Investigation and diagnosis",
        "Plans and implementation",
        "Tests and documentation",
    ], BLUE, 1.15)
    card(slide, 6.8, 3.4, 5.85, 2.05, "The human owns", [
        "Go/no-go decisions and scope",
        "Every external action: push, PR, deploy",
        "Plan approval",
    ], GREEN, 1.15)
    line(slide, 0.72, 5.62, 11.9, 0.5, [
        R("Tool-agnostic:  ", 11.5, ACCENT, True),
        R("this is not a Pi flow — it is a way of working with ANY agent. In Pi it matters "
          "more: there are no approval prompts, so the policy must be written down "
          "and enforced.", 11, MUTED),
    ], ls=1.03)
    quote(slide, "The model does not earn trust for free: it earns it decision by decision, "
                 "with evidence.")


def slide_22(prs):
    slide = chrome(prs, "PART 2 · 08 · THE METHODOLOGY", "The real 11-stage flow", 22)
    steps = [
        ("1", "Orient: /skill:kg + history-first + status-first", False),
        ("2", "Inbound triage: is the symptom in the contract?", True),
        ("3", "Regression vs. pre-existing (prove it)", True),
        ("4", "Investigate: cheap deterministic oracle", False),
        ("5", "Plan in data/changes/ → explicit human agreement", True),
        ("6", "Implement: TDD RED → GREEN, minimal", False),
        ("7", "Verify: outbound gate ×5 (instrument → list → image → look)", True),
        ("8", "Document — each thing once", False),
        ("9", "Sanitize — added lines (/skill:sanitise-diff)", False),
        ("10", "Handoff: the human does push / PR", False),
        ("11", "Review + persist lessons (/skill:kg-refresh)", True),
    ]
    for i, (number, text, gate) in enumerate(steps):
        x = 0.7 if i < 6 else 6.85
        y = 2.05 + 0.66 * (i if i < 6 else i - 6)
        flow_step(slide, x, y, number, text, gate)
    line(slide, 0.7, 6.02, 11.95, 0.3, [
        R("■ ", 11, ACCENT, True),
        R("Coral boxes are GATES. Pi has no plan mode: the plan gate is a FILE the human "
          "agrees (or the plan-mode/ example extension).", 11, MUTED),
    ])
    quote(slide, "The agent orchestrates and is where inference lives; the expensive work "
                 "concentrates in plan/code/verify, not in search.")


def slide_23(prs):
    slide = chrome(prs, "PART 2 · 08 · THE METHODOLOGY",
                   "The outbound gate is five checks", 23)
    rows = [
        ("0 · Instrument",
         "Canary every _diag_*/_sweep_* on a KNOWN-ANSWER case before trusting it"),
        ("1 · Real stage",
         "Reproduce at the wrapper that builds the contract — not an internal extract()"),
        ("2 · Member list",
         "Assert on titles/ids, never on a total: +1 and -1 cancel exactly"),
        ("3 · Deployed image",
         "Re-run inside the runtime image — green tests ≠ what ships"),
        ("4 · Look at it",
         "Render the output and read it; before/after for geometry changes"),
    ]
    for i, (label_text, detail) in enumerate(rows):
        step_row(slide, 2.0 + 0.6 * i, label_text, detail)
    panel(slide, 0.7, 5.08, 11.95, 1.05, border=ACCENT, fill=BAND)
    line(slide, 0.95, 5.15, 11.5, 0.9, [
        R("Five ways a green gate proves nothing: ", 11.5, ACCENT, True),
        R("a broken instrument · a total that matches · a gate that couldn't fail · a canary "
          "that never applied the real perturbation · a structural gate read as a semantic "
          "one.", 11.5, TEXT),
    ], ls=1.08)
    quote(slide, "Identical role in Claude Code, Cursor and Pi — only which agent runs "
                 "it changes.")


def slide_24(prs):
    slide = chrome(prs, "PART 2 · 09 · METHOD TOOLS",
                   "Which tool the agent uses, and when", 24)
    line(slide, 0.7, 1.9, 11.95, 0.5, [
        R("Rule in AGENTS.md (Pi has no scoped rules): ", 12, MUTED),
        R("codegraph_explore FIRST · Serena find_referencing_symbols before rename. ",
          12, TEXT, True),
        R("Order: cheap → expensive, deterministic → probabilistic.", 12, MUTED),
    ])
    rows = [
        ("Orient",
         "/skill:kg (ticket graph → danger zone) · STATUS.md · git · gh",
         "no inference", False),
        ("Navigate (survey)",
         "CodeGraph codegraph_explore (MCP, toolExposure direct) — source + blast radius",
         "1 call", False),
        ("Refactor-check",
         "Serena find_referencing_symbols (MCP, direct) — disambiguates by class",
         "precise", False),
        ("Diagnose", "Deterministic oracle: parser / validator / _diag_*.py",
         "no inference", False),
        ("Environment (logs, config)",
         "Cloud CLI, read-only profile — logs · function config · queues", "read-only",
         False),
        ("Output contract", "Playwright MCP (deferred) against the consumer's endpoint",
         "reproduce", False),
        ("Only at the end",
         "The agent's roll — to VERIFY the fix, not to diagnose",
         "metered", True),
    ]
    for i, (phase, tool, note, highlight) in enumerate(rows):
        tool_row(slide, 2.5 + 0.6 * i, phase, tool, note, highlight)


def slide_25(prs):
    slide = chrome(prs, "PART 2 · 09 · METHOD TOOLS",
                   "CodeGraph in Pi: make it DIRECT", 25)
    card(slide, 0.7, 2.0, 5.85, 2.4, "tree-sitter → SQLite index (.codegraph/)", [
        "Symbols + edges (calls, imports, inheritance)",
        "Deterministic (from the AST), no API keys",
        "Returns: source + paths + blast radius + coverage",
        "Treat what it prints as ALREADY read",
    ], BLUE, 1.5)
    label(slide, 6.8, 1.86, 5.85, "Register + verify  [TESTED]")
    code_block(slide, 6.8, 2.2, 5.85, 1.85, [
        "pi mcp add codegraph -- codegraph \\",
        "  serve --path <repo> --mcp",
        "pi mcp list",
        ("# codegraph: connected, 1 tool", MUTED),
        ("#   (codemode, global) …", MUTED),
        ("#   tools: codegraph_explore", MUTED),
    ])
    panel(slide, 6.8, 4.25, 5.85, 1.1)
    line(slide, 7.05, 4.38, 5.4, 0.95, [
        R("Why direct:  ", 11, ACCENT, True),
        R("codemode (the default) hides it as a tool; the method wants it used unprompted. "
          "toolExposure: { codegraph_explore: \"direct\" }.", 11, TEXT),
    ], ls=1.03)
    tb(slide, 0.7, 4.6, 5.85, 1.4, [
        [R("No ${workspaceFolder} variable", 13, GREEN, True)],
        [R("(not documented) — absolute --path in .pi/mcp.json, or cwd. [3rd-party] "
           "@henryqw/pi-codegraph exposes it natively.", 10.5, MUTED)],
    ])
    quote(slide, "One query instead of grep→open→follow-import→repeat — if the tool "
                 "is visible to the model.")


def slide_26(prs):
    slide = chrome(prs, "PART 2 · 09 · METHOD TOOLS",
                   "Serena: semantic navigation, precise check", 26)
    card(slide, 0.7, 2.0, 5.85, 2.6, "Semantic navigation via LSP (MCP)", [
        "Operates on SYMBOLS, not text: IDE precision",
        "find_symbol (body=true) — one method from a big file",
        "get_symbols_overview — skeleton of a file",
        "find_referencing_symbols — who references, BY CLASS",
        "search_for_pattern · activate_project (multi-repo)",
    ], BLUE, 1.7)
    label(slide, 6.8, 2.01, 5.85, "~/.pi/agent/mcp.json — args NOT tested under Pi")
    code_block(slide, 6.8, 2.35, 5.85, 1.35, [
        '"serena": {"command":"uvx","args":["--from",',
        '  "git+https://github.com/oraios/serena",',
        '  "serena","start-mcp-server"],',
        '  "toolExposure":{"find_referencing_symbols":"direct"}}',
    ])
    panel(slide, 6.8, 4.0, 5.85, 1.55, border=ACCENT)
    line(slide, 7.05, 4.15, 5.4, 1.3, [
        R("Why it is MANDATORY pre-rename:  ", 11, ACCENT, True),
        R("CodeGraph's flat impact mixes homonymous methods (Invoice.process vs "
          "Refund.process); Serena disambiguates by class. Complementary, "
          "not rivals.", 11, TEXT),
    ], ls=1.05)
    line(slide, 0.7, 4.85, 5.85, 0.9, [
        R("[3rd-party] @bacnh85/pi-serena ", 11.5, GREEN, True),
        R("wraps it as a Pi package — untested. The config shape is copied from the Cursor "
          "guide.", 11.5, MUTED),
    ], ls=1.05)
    quote(slide, "CodeGraph answers 'what breaks?'; Serena answers "
                 "'exactly who calls THIS process()?'")


def slide_27(prs):
    slide = chrome(prs, "PART 2 · 09 · METHOD TOOLS",
                   "GSD: Claude Code only — not ported to Pi", 27)
    card(slide, 0.7, 2.0, 5.85, 3.3, "What GSD is", [
        "Claude Code plugin for phased project management",
        "Cycle: discuss → plan (gate) → execute → verify",
        "Subagents gsd-planner, gsd-executor, gsd-verifier…",
        "Versioned state in .planning/",
        "Official targets: Claude Code, OpenCode, Gemini, Codex",
        "[3rd-party] pi-gsd: unofficial port, untested",
    ], ACCENT, 2.4)
    card(slide, 6.8, 2.0, 5.85, 3.3, "Pi substitute", [
        "Phase/plan files in data/changes/ (human agrees)",
        "Prompt templates: .pi/prompts/plan-phase.md → /plan-phase",
        "Subagent example's /implement chain for roles",
        "/skill:methodology-plan fills the template",
        "Don't load ~/.claude/skills/gsd-*: they call Claude-only tools",
    ], BLUE, 2.4)
    quote(slide, "Same method, without the plugin: files + templates + a subagent chain "
                 "replicate GSD's gates.")


def slide_28(prs):
    slide = chrome(prs, "PART 2 · 09 · METHOD TOOLS",
                   "Oracles, Playwright, Context7 — and kg", 28)
    cards = [
        ("Or", "Oracles → diagnose",
         "Own parsers/validators/_diag_*.py: cheap, reproducible answer before "
         "spending the agent's roll."),
        ("Pw", "Playwright (MCP) → triage and outbound",
         "Reproduce where the consumer sees it. \"exposure\": \"deferred\" — loaded "
         "via tool_search when needed."),
        ("C7", "Context7 (MCP) → library docs",
         "Live docs instead of training-cutoff guesses. Streamable HTTP url, "
         "deferred exposure."),
        ("kg", "/skill:kg → orient",
         "Project MEMORY graph (graphify): tickets + sharp edges. History-first "
         "without LLM (Part 3)."),
        ("CG", "CodeGraph → investigate",
         "Survey in 1 call: source + callers + blast radius + coverage (direct)."),
        ("Se", "Serena → pre-refactor",
         "find_referencing_symbols disambiguates by class (direct)."),
    ]
    for i, (badge, title, desc) in enumerate(cards):
        x = 0.7 if i % 2 == 0 else 6.815
        y = 2.0 + 1.46 * (i // 2)
        num_card(slide, x, y, 5.835, 1.18, badge, title, desc, 0.63)
    quote(slide, "The classic inversion — the model diagnoses — is what this order "
                 "avoids: the model verifies; oracles diagnose.")


def slide_29(prs):
    slide = chrome(prs, "PART 2 · 10 · TRANSFER",
                   "The real proof: from Claude Code to Pi", 29)
    card(slide, 0.7, 2.0, 5.85, 2.75, "Travels UNCHANGED (the 5 rules)", [
        "Plan → agree → implement",
        "Verify on the CONSUMER's contract",
        "Solve the general class, not one input",
        "Durable trail: why, what, how it was verified",
        "The human owns the external (merge, deploy)",
    ], GREEN, 1.85)
    card(slide, 6.8, 2.0, 5.85, 2.75, "What DOES change: the surface", [
        "CLAUDE.md → AGENTS.md (cwd + ancestors only)",
        "Skills → .pi/skills/ (same SKILL.md, /skill:name)",
        "Hooks + allowlist → TS extension + containers",
        "Plan mode → plan file (or plan-mode/ example)",
        "Subagents → subagent extension / pi -p (no Teams)",
        "claude -p → pi -p … </dev/null",
    ], BLUE, 1.85)
    card(slide, 0.7, 4.95, 11.95, 1.25,
         "The starter kit: PI_ADAPTATION.md (docs/ai-agents-code-methodology/)", [
             "Mapping + pi/ (AGENTS.md, mcp.json, settings.json, block-external-git.ts, "
             "skills day/atlassian/evidence/preview/kg…) ready to copy",
             "kg-refresh caveat: its extraction step needs subagents → extension, or keep "
             "that one step in Claude Code",
         ], ACCENT, 0.35)
    quote(slide, "Third agent, same discipline: Claude Code → Cursor → Pi, "
                 "and the gates did not move.")


def slide_30(prs):
    slide = chrome(prs, "PART 2 · 11 · OPS",
                   "From transporting (tarball) to sharing (S3)", 30)
    card(slide, 0.7, 2.0, 5.85, 2.55, "A · Bring-up: tarball + USB", [
        "Outbound = full copy; inbound = data/ delta only",
        "Add ~/.pi/agent/: settings, mcp.json, extensions, skills",
        "auth.json · mcp-auth.json · trust.json = machine-local",
        "Re-pin the CodeGraph --path in mcp.json on the target",
    ], BLUE, 1.65)
    card(slide, 6.8, 2.0, 5.85, 2.55, "B · Day to day: S3-backed record", [
        "Narrow scope: changes/**/*.md + graph (no client data)",
        "Write via sync; read via READ-ONLY mount",
        "Dry-run by default; guard BOTH directions",
        "ONE publisher. Derived is per file, not per folder",
    ], GREEN, 1.65)
    card(slide, 0.7, 4.7, 11.95, 1.5,
         "Agent-specific: machine-local IDENTITY.md", [
             "Each machine declares MACHINE_NAME + MACHINE_ROLE (publisher | contributor)",
             "AGENTS.md points to IDENTITY.md — the session reads its role BEFORE acting; "
             "/skill:day start | end packages the habit",
         ], ACCENT, 0.55)
    quote(slide, "When the durable trail moves from one machine to a team, the agent "
                 "must know which machine it is on before acting.")


def slide_31(prs):
    part_divider(
        prs, "PART 3", "The ticket graph",
        "A full case built with graphify — project memory, navigable "
        "from Pi.",
        ["12a · The problem and the design (spike)",
         "12b · Pipeline and skills (kg, kg-refresh)",
         "12c · The real graph, visualized",
         "12d · Usage and how it hooks into the methodology"],
        31)


def slide_32(prs):
    slide = chrome(prs, "PART 3 · 12A · TICKET GRAPH",
                   "The problem, and why graphify", 32)
    card(slide, 0.7, 2.0, 5.85, 2.5, "The problem", [
        "~540 writeup files, sharp edges, runbooks, memory",
        "A 'new' bug almost always has prior context that constrains the fix",
        "Finding it by hand = remembering it exists + grep",
        "The graph makes it EXPLICIT and queryable in 1 call",
    ], ACCENT, 1.6)
    card(slide, 6.8, 2.0, 5.85, 2.5, "The corpus: manifest, not glob", [
        "DIFFABLE manifest.txt: ~116 files, ~196k words",
        "Per-ticket writeups · hubs · runbooks · memory",
        "Hard exclusions: binaries, repeated handovers, stale copies",
        "Density without new knowledge = noise",
    ], BLUE, 1.6)
    panel(slide, 0.7, 4.75, 11.95, 1.35, border=GREEN, fill=BAND)
    line(slide, 1.0, 4.92, 11.4, 1.05, [
        R("The technology is graphify — CodeGraph is only the analogy.  ", 12.5, GREEN,
          True),
        R("Same role (queryable graph before touching anything), different domain (tickets, not "
          "code), different tool. Built originally in Claude Code; query and refresh live "
          "as skills kg / kg-refresh — the same SKILL.md loads in Pi [TESTED].", 11.5, TEXT),
    ], ls=1.12)
    quote(slide, "Full material (design, scripts, tests, real output): "
                 "docs/knowledge-graph/.")


def slide_33(prs):
    slide = chrome(prs, "PART 3 · 12B · TICKET GRAPH",
                   "Pipeline and skills — kg and kg-refresh in Pi", 33)
    label(slide, 0.7, 1.91, 6.35, "Build (/skill:kg-refresh)")
    code_block(slide, 0.7, 2.25, 6.35, 2.15, [
        "kg_refresh.sh prepare   # manifest -> stage",
        "                        # -> scratch OUTSIDE the repo",
        ("# semantic extraction — needs SUBAGENTS:", MUTED),
        ("#   subagent extension, or Claude Code", MUTED),
        "kg_refresh.sh finalize  # output/ + leak-check",
    ])
    card(slide, 7.35, 1.92, 5.3, 2.5, "In Pi", [
        "/skill:kg — works unchanged (deterministic scripts)",
        "/skill:kg-refresh — bookends work; the extraction step assumes Claude Code's Agent tool",
        "graphify support for Pi: UNVERIFIED",
        "test_kg_*.py — the bookends, TESTED",
    ], BLUE, 1.6)
    panel(slide, 0.7, 4.62, 11.95, 1.5)
    tb(slide, 1.0, 4.78, 11.4, 1.2, [
        [R("The gotcha that holds it up:  ", 12, ACCENT, True),
         R("graphify respects .gitignore and all of data/ is gitignored → running the detector "
           "in place finds 0 files. So the corpus is staged in a scratch outside "
           "the repo and artifacts are copied back.", 11.5, TEXT)],
        [R("Honest split for Pi:  ", 12, GREEN, True),
         R("keep Pi for the deterministic bookends and queries; run the semantic step "
           "from Claude Code, or adapt it to the subagent extension.", 11.5, TEXT)],
    ], sa=8, ls=1.12)
    quote(slide, "Staging with provenance: <ticket>__<ticket>.md, hub__STATUS.md, "
                 "memory__x.md — every node traces to its source.")


def slide_34(prs):
    slide = chrome(prs, "PART 3 · 12C · TICKET GRAPH",
                   "The real graph: 507 nodes, 35 communities", 34)
    rect(slide, 0.68, 1.93, 8.84, 4.99, None, BORDER, THICK)
    if not KG_IMAGE.exists():
        raise SystemExit(
            f"Missing {KG_IMAGE.name}: generate it with "
            "`uv run --with playwright python presentation/capture_kg_graph.py`."
        )
    slide.shapes.add_picture(str(KG_IMAGE), In(0.7), In(1.95), In(8.8), In(4.95))

    card(slide, 9.7, 1.95, 2.95, 3.4, "The real output", [
        "507 nodes · 672 edges",
        "35 communities",
        "92% EXTRACTED (reliable)",
        "7% INFERRED (conf. 0.7)",
        "116 files, ~196k words",
    ], GREEN, 2.5)
    tb(slide, 9.7, 5.5, 2.95, 0.8, [
        [R("Interactive graph.html:", 11, BLUE, True)],
        [R("node search, filter by community (vis-network). Names pseudonymised.", 10,
           MUTED)],
    ], ls=1.05)
    quote(slide, "Communities map to real danger zones; god-nodes are "
                 "the free onboarding list.")


def slide_35(prs):
    slide = chrome(prs, "PART 3 · 12D · TICKET GRAPH",
                   "How it is used — and where it hooks in", 35)
    label(slide, 0.7, 1.91, 6.35, "Query: ZERO LLM (kg_query.sh reads graph.json)")
    code_block(slide, 0.7, 2.25, 6.35, 2.0, [
        "kg_query.sh explain <ticket|topic>  # neighbors",
        "kg_query.sh path <A> <B>            # path",
        "kg_query.sh find <substr>           # exact name",
        ("# in Pi: /skill:kg explain <topic>", MUTED),
    ])
    card(slide, 7.35, 1.92, 5.3, 2.5, "Where it hooks in", [
        "Stage 1 (Orient) of the 11-stage flow",
        "history-first rule in AGENTS.md:",
        "/skill:kg <ticket|topic> BEFORE grep",
        "Points to WHAT to read; does not replace reading",
    ], ACCENT, 1.6)
    line(slide, 0.7, 4.45, 6.35, 0.9, [
        R("Real example: kg explain get_letter_end ", 12, GREEN, True),
        R("→ the full danger zone instantly: the 5–6 tickets that share that "
          "code.", 11.5, MUTED),
    ], ls=1.1)
    card(slide, 0.7, 5.2, 11.95, 1.0, "Honesty and lifecycle", [
        "Recall in dense zones · EXTRACTED = reliable, INFERRED = hint · internal "
        "(data/) · derived rebuilds, but hand-authored travels",
    ], BLUE, 0.1)
    quote(slide, "One semantic step at build time, zero LLM at query time. The graph is "
                 "the map; the agent, the guide.")


def slide_36(prs):
    slide = chrome(prs, "CLOSE", "From assistant to system, in any agent", 36)
    line(slide, 0.7, 1.95, 5.85, 0.4, [R("PART 1 · the tool", 13, ACCENT, True)])
    left = [
        ("1", "Install + memory",
         "pi in one line; AGENTS.md walks up; SYSTEM.md is yours; no auto-memory."),
        ("2", "Safety by design",
         "No popups, no sandbox: containers + extensions + --tools enforce the policy."),
        ("3", "Context, caching, MCP, skills",
         "Lean by default; caching automatic; MCP codemode → direct; /skill:name."),
        ("4", "Subagents + automation",
         "Extension or parallel pi; -p </dev/null, --approve, RPC, SDK."),
    ]
    for i, (number, title, desc) in enumerate(left):
        summary_card(slide, 0.7, 2.35 + 0.95 * i, number, title, desc, ACCENT)

    line(slide, 6.8, 1.95, 5.85, 0.4,
         [R("PART 2 + 3 · the method and the graph", 13, BLUE, True)])
    right = [
        ("5", "The 11-stage flow",
         "Deterministic gates; five-check outbound; the human owns the decisions."),
        ("6", "The method's tools",
         "CodeGraph · Serena · oracles: cheap→expensive; GSD stays in Claude Code."),
        ("7", "Transferable, even in ops",
         "PI_ADAPTATION.md + pi/; machine-sync + S3 record with per-machine identity."),
        ("8", "The series",
         "Claude Code → Cursor → Pi → GitHub Copilot next: same SKILL.md, same gates."),
    ]
    for i, (number, title, desc) in enumerate(right):
        summary_card(slide, 6.8, 2.35 + 0.95 * i, number, title, desc, BLUE)

    line(slide, 0.7, 6.35, 12.0, 0.4, [
        R("References:  pi.dev/docs/latest  ·  github.com/earendil-works/pi  ·  "
          "pi.dev/packages  ·  github.com/colbymchenry/codegraph  ·  "
          "github.com/oraios/serena", 11, DIM)])


SLIDES = [
    slide_01, slide_02, slide_03, slide_04, slide_05, slide_06, slide_07, slide_08,
    slide_09, slide_10, slide_11, slide_12, slide_13, slide_14, slide_15, slide_16,
    slide_17, slide_18, slide_19, slide_20, slide_21, slide_22, slide_23, slide_24,
    slide_25, slide_26, slide_27, slide_28, slide_29, slide_30, slide_31, slide_32,
    slide_33, slide_34, slide_35, slide_36,
]


def build():
    prs = Presentation()
    prs.slide_width = Inches(SLIDE_W)
    prs.slide_height = Inches(SLIDE_H)
    for make in SLIDES:
        make(prs)
    prs.save(str(OUT))
    return len(SLIDES)


if __name__ == "__main__":
    n = build()
    print(f"OK  {OUT}  ({n} slides)")
