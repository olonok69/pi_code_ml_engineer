#!/usr/bin/env python3
"""
Render agents.png — Pi's subagent extension vs parallel pi processes — in the deck style.
Offline, Pillow only (same as ../methodology/render_flow.py).

    uv run --with pillow python examples/subagents/render_agents.py   # -> examples/subagents/agents.png

The editable conceptual source is agents.mmd; if you change the architecture, update both.
"""
from PIL import Image, ImageDraw, ImageFont

SS = 2
BG     = (15, 20, 26)
PANEL  = (26, 33, 43)
PANEL2 = (34, 43, 56)
STROKE = (46, 57, 72)
CORAL  = (217, 119, 87)
BLUE   = (122, 162, 199)
GREEN  = (140, 194, 140)
TEXT   = (232, 234, 237)
MUTED  = (154, 164, 178)

W, H = 1560, 760
img = Image.new("RGB", (W * SS, H * SS), BG)
d = ImageDraw.Draw(img)


def font(size, bold=False):
    import os
    windir = os.environ.get("WINDIR", r"C:\Windows")
    candidates = (
        ["DejaVuSans-Bold.ttf", os.path.join(windir, "Fonts", "seguisb.ttf"),
         os.path.join(windir, "Fonts", "arialbd.ttf")]
        if bold else
        ["DejaVuSans.ttf", os.path.join(windir, "Fonts", "segoeui.ttf"),
         os.path.join(windir, "Fonts", "arial.ttf")]
    )
    for name in candidates:
        try:
            return ImageFont.truetype(name, size * SS)
        except OSError:
            continue
    return ImageFont.load_default()


def rr(x, y, w, h, r=14, fill=PANEL, outline=STROKE, width=1):
    d.rounded_rectangle([x*SS, y*SS, (x+w)*SS, (y+h)*SS], radius=r*SS,
                        fill=fill, outline=outline, width=width*SS)


def ctext(cx, cy, txt, fnt, fill=TEXT):
    b = d.textbbox((0, 0), txt, font=fnt)
    d.text((cx*SS - (b[2]-b[0])/2, cy*SS - (b[3]-b[1])/2 - b[1]), txt, font=fnt, fill=fill)


def ltext(x, y, txt, fnt, fill=TEXT):
    d.text((x*SS, y*SS), txt, font=fnt, fill=fill)


def arrow(x1, y1, x2, y2, color=MUTED, width=2, both=False):
    d.line([x1*SS, y1*SS, x2*SS, y2*SS], fill=color, width=width*SS)
    import math
    ang = math.atan2(y2-y1, x2-x1)
    for (tx, ty, a) in ([(x2, y2, ang)] + ([(x1, y1, ang + math.pi)] if both else [])):
        p = [(tx*SS, ty*SS)]
        for da in (2.6, -2.6):
            p.append(((tx - 12*math.cos(a+da*0.5))*SS, (ty - 12*math.sin(a+da*0.5))*SS))
        d.polygon(p, fill=color)


f_t  = font(24, True)
f_h  = font(17, True)
f_b  = font(14, True)
f_s  = font(12)
f_xs = font(11)

ltext(40, 28, "Pi: no built-in subagents — two substitutes", f_t, TEXT)
ltext(40, 66, "Left: the official example extension (examples/extensions/subagent).  Right: parallel pi processes (tmux / pi -p / RPC).", f_s, MUTED)

# ---------------- left panel: subagent extension ----------------
rr(40, 110, 700, 560, r=18, fill=(20, 26, 34), outline=STROKE)
ltext(66, 130, "SUBAGENT EXTENSION (example, install it yourself)", f_h, BLUE)
ltext(66, 160, "each subagent = a separate pi subprocess with an isolated context", f_xs, MUTED)

rr(80, 210, 240, 170, fill=PANEL2, outline=BLUE, width=2)
ctext(200, 250, "Main pi session", f_b, TEXT)
ctext(200, 280, "your context", f_s, MUTED)
ctext(200, 305, "(stays clean)", f_s, MUTED)

subs = [("scout / refactor-scout", "tools: read, grep, find, ls"), ("planner / reviewer", "agent .md files"),
        ("worker", "single · parallel (max 8, 4 at once) · chain")]
for i, (t, sub) in enumerate(subs):
    y = 200 + i * 150
    rr(430, y, 280, 100, fill=PANEL, outline=STROKE)
    ctext(570, y + 32, t, f_b, TEXT)
    ctext(570, y + 62, sub, f_xs, MUTED)
    arrow(320, 270, 430, y + 35, color=MUTED)
    arrow(430, y + 72, 322, 320, color=GREEN)
ltext(340, 190, "task with context", f_xs, MUTED)
ltext(90, 420, "only the RESULT comes back", f_xs, GREEN)
ltext(66, 630, "Agent files: ~/.pi/agent/agents/*.md; .pi/agents/ only with agentScope project|both.", f_xs, CORAL)

# ---------------- right panel: parallel processes ----------------
rr(790, 110, 730, 560, r=18, fill=(20, 26, 34), outline=STROKE)
ltext(816, 130, "PARALLEL PI PROCESSES (no agent teams)", f_h, CORAL)
ltext(816, 160, "no shared inbox or task list in Pi — NOT DOCUMENTED; you integrate", f_xs, MUTED)

rr(1040, 205, 230, 105, fill=PANEL2, outline=CORAL, width=2)
ctext(1155, 240, "You (or a script)", f_b, TEXT)
ctext(1155, 270, "the integrator", f_s, MUTED)

rr(850, 400, 230, 105, fill=PANEL, outline=STROKE)
ctext(965, 435, "tmux pane: pi", f_b, TEXT)
ctext(965, 465, "full session, own files", f_s, MUTED)
rr(1230, 400, 230, 105, fill=PANEL, outline=STROKE)
ctext(1345, 435, "pi -p / --mode rpc", f_b, TEXT)
ctext(1345, 465, "headless child process", f_s, MUTED)

arrow(1090, 310, 985, 400, color=MUTED, both=True)
arrow(1220, 310, 1325, 400, color=MUTED, both=True)
ctext(1155, 532, "no messaging between them", f_xs, BLUE)

rr(940, 560, 430, 72, fill=PANEL2, outline=GREEN, width=2)
ctext(1155, 583, "Partitioned files / branches", f_b, GREEN)
ctext(1155, 610, "each process owns its own files", f_xs, MUTED)
for x in (965, 1345):
    d.line([x*SS, 505*SS, x*SS, 560*SS], fill=STROKE, width=2*SS)

ltext(816, 645, "Read-only child: pi -p --tools read,grep,find,ls --no-session \"...\" </dev/null", f_xs, CORAL)

ltext(40, 706, "Side-quests -> subagent extension.  Parallel work -> several pi processes + partitioned files.  Teams -> not in Pi.", f_s, GREEN)

import os
img = img.resize((W, H), Image.LANCZOS)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agents.png")
img.save(out)
print(f"OK -> {out}  ({W}x{H})")
