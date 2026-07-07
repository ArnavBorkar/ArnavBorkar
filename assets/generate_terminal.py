#!/usr/bin/env python3
"""Generates assets/terminal.svg, the animated fake terminal in this profile README.

GitHub strips JavaScript from READMEs but renders SVG through its image proxy,
and CSS animations inside an SVG survive that. So every keystroke you see is a
CSS keyframe computed by this script. Run `python3 generate_terminal.py` and
commit the output.
"""

# ---------------------------------------------------------------- geometry --
W = 800                 # viewBox width
PAD_X = 24              # left padding inside the terminal
TITLEBAR_H = 40
LINE_H = 22             # px per line
FONT_SIZE = 14
CW = 8.43               # forced char width via textLength, keeps columns aligned
                        # on every platform font (Menlo, Consolas, DejaVu...)

# ------------------------------------------------------------------ timing --
CPS = 17                # typed characters per second
GAP_AFTER_TYPE = 0.35   # pause between a command finishing and its output
GAP_AFTER_BLOCK = 0.55  # pause before the next prompt appears
OUTPUT_STAGGER = 0.07   # cascade between multi-line output rows
START = 0.6             # boot pause before the first prompt

# ------------------------------------------------------------------ colors --
BG = "#161b22"
BORDER = "#30363d"
TITLE_FG = "#8b949e"
PROMPT_FG = "#7ee787"
CMD_FG = "#e6edf3"
OUT_FG = "#8b949e"
ACCENT = "#79c0ff"
CURSOR = "#79c0ff"

PROMPT = "arnav@github ~ %"

# The session. ("cmd", text) types itself; ("out", text, color?) prints.
SESSION = [
    ("cmd", "whoami"),
    ("out", "Arnav Borkar. I build data platforms and AI systems.", CMD_FG),
    ("blank",),
    ("cmd", 'duckdb -c "SELECT layer, currently FROM me.stack ORDER BY joy DESC"'),
    ("table", ("layer", "currently"), [
        ("query engines", "making SQL go brrr"),
        ("lakehouse", "Apache Iceberg everything"),
        ("AI agents", "putting them to real work"),
        ("distributed systems", "Raft, Kafka, sane retries"),
    ]),
    ("blank",),
    ("cmd", "rm -rfv ~/old-readme/languages-and-tools-badges"),
    ("out", "removed 26 shiny icons. nobody clicked them anyway.", OUT_FG),
    ("blank",),
    ("cmd", "cat ~/.plan"),
    ("out", "linkedin   linkedin.com/in/arnavborkar", ACCENT),
    ("out", "x          x.com/arnavborkar", ACCENT),
    ("out", "mail       arnav.n.borkar@gmail.com", ACCENT),
    ("blank",),
    ("prompt_idle",),
]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text_el(x, y, s, fill, cls=""):
    tl = f' textLength="{len(s) * CW:.1f}" lengthAdjust="spacingAndGlyphs"' if s else ""
    c = f' class="{cls}"' if cls else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" fill="{fill}"{tl}{c} '
            f'xml:space="preserve">{esc(s)}</text>')


def build():
    body, css = [], []
    t = START
    y = TITLEBAR_H + 34
    prompt_w = len(PROMPT) * CW
    n = 0
    prev = None

    for entry in SESSION:
        kind = entry[0]
        # pause between a block's output and the next prompt appearing
        if kind in ("cmd", "prompt_idle") and prev in ("out", "blank"):
            t += GAP_AFTER_BLOCK
        prev = kind

        if kind == "blank":
            y += LINE_H
            continue

        if kind == "prompt_idle":
            g = "idle"
            body.append(f'<g class="b {g}">')
            body.append(text_el(PAD_X, y, PROMPT, PROMPT_FG))
            body.append(f'<rect class="blink" x="{PAD_X + prompt_w + CW:.1f}" '
                        f'y="{y - 12}" width="9" height="16" fill="{CURSOR}"/>')
            body.append("</g>")
            css.append(f".{g}{{opacity:0;animation:show .01s linear {t:.2f}s forwards}}")
            continue

        if kind == "cmd":
            n += 1
            cmd = entry[1]
            dur = max(len(cmd) / CPS, 0.4)
            g = f"c{n}"
            cx = PAD_X + prompt_w + CW  # command starts one space after prompt
            cmd_w = len(cmd) * CW

            body.append(f'<g class="b {g}">')
            body.append(text_el(PAD_X, y, PROMPT, PROMPT_FG))
            body.append(text_el(cx, y, cmd, CMD_FG))
            # cover slides right in per-char steps, revealing the command;
            # the cursor block rides on its leading edge
            body.append(f'<g class="cov {g}v">'
                        f'<rect x="{cx:.1f}" y="{y - 16}" width="{W - cx + cmd_w:.1f}" '
                        f'height="{LINE_H}" fill="{BG}"/>'
                        f'<rect class="cur {g}u" x="{cx:.1f}" y="{y - 12}" '
                        f'width="9" height="16" fill="{CURSOR}"/></g>')
            body.append("</g>")

            css.append(f".{g}{{opacity:0;animation:show .01s linear {t:.2f}s forwards}}")
            css.append(f".{g}v{{animation:sl{n} {dur:.2f}s steps({len(cmd)},end) "
                       f"{t + 0.15:.2f}s forwards}}")
            css.append(f"@keyframes sl{n}{{to{{transform:translateX({cmd_w:.1f}px)}}}}")
            css.append(f".{g}u{{animation:hide .01s linear {t + 0.15 + dur:.2f}s forwards}}")

            t += 0.15 + dur + GAP_AFTER_TYPE
            y += LINE_H
            continue

        if kind == "table":
            # duckdb-style result box, but the frame is real SVG strokes so
            # the corners join cleanly on every platform font
            header, rows = entry[1], entry[2]
            tx = PAD_X
            divx = tx + 24 * CW
            rxx = divx + 34 * CW
            c1x = tx + 1.5 * CW
            c2x = divx + 1.5 * CW
            top = y - 15
            frame_h = (1 + len(rows)) * LINE_H + 14
            g = f"tb{n}"
            stroke = "#4d565f"

            body.append(f'<g class="b {g}">')
            body.append(f'<rect x="{tx}" y="{top}" width="{rxx - tx:.1f}" '
                        f'height="{frame_h}" rx="4" fill="none" stroke="{stroke}"/>')
            body.append(f'<line x1="{divx:.1f}" y1="{top}" x2="{divx:.1f}" '
                        f'y2="{top + frame_h}" stroke="{stroke}"/>')
            body.append(f'<line x1="{tx}" y1="{y + 7}" x2="{rxx:.1f}" y2="{y + 7}" '
                        f'stroke="{stroke}"/>')
            body.append(text_el(c1x, y, header[0], ACCENT))
            body.append(text_el(c2x, y, header[1], ACCENT))
            body.append("</g>")
            css.append(f".{g}{{opacity:0;animation:show .01s linear {t:.2f}s forwards}}")
            t += OUTPUT_STAGGER
            y += LINE_H

            for r1, r2 in rows:
                g = f"tr{len(body)}"
                body.append(f'<g class="b {g}">{text_el(c1x, y, r1, CMD_FG)}'
                            f'{text_el(c2x, y, r2, CMD_FG)}</g>')
                css.append(f".{g}{{opacity:0;animation:show .01s linear {t:.2f}s forwards}}")
                t += OUTPUT_STAGGER
                y += LINE_H
            y += 10  # frame bottom padding
            prev = "out"
            continue

        if kind == "out":
            s, color = entry[1], entry[2]
            g = f"o{len(body)}"
            body.append(f'<g class="b {g}">{text_el(PAD_X, y, s, color)}</g>')
            css.append(f".{g}{{opacity:0;animation:show .01s linear {t:.2f}s forwards}}")
            t += OUTPUT_STAGGER
            y += LINE_H
            continue

    height = y + 8
    total = t
    css_common = f"""
text{{font-family:'SF Mono',SFMono-Regular,Menlo,Consolas,'Liberation Mono','DejaVu Sans Mono',monospace;font-size:{FONT_SIZE}px}}
@keyframes show{{to{{opacity:1}}}}
@keyframes hide{{to{{opacity:0}}}}
@keyframes blinkk{{0%,45%{{opacity:1}}50%,95%{{opacity:0}}100%{{opacity:1}}}}
.blink{{animation:blinkk 1.1s step-end {total:.2f}s infinite}}
@media (prefers-reduced-motion:reduce){{*{{animation-duration:.01s !important;animation-delay:0s !important}}.blink{{animation:none !important}}}}
"""
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height}" width="{W}" role="img" aria-label="Animated terminal: Arnav Borkar builds data platforms and AI systems">
<style>{css_common}{chr(10).join(css)}</style>
<rect x="1" y="1" width="{W - 2}" height="{height - 2}" rx="12" fill="{BG}" stroke="{BORDER}" stroke-width="2"/>
<circle cx="26" cy="{TITLEBAR_H // 2}" r="6" fill="#ff5f56"/>
<circle cx="48" cy="{TITLEBAR_H // 2}" r="6" fill="#ffbd2e"/>
<circle cx="70" cy="{TITLEBAR_H // 2}" r="6" fill="#27c93f"/>
<text x="{W // 2}" y="{TITLEBAR_H // 2 + 5}" fill="{TITLE_FG}" text-anchor="middle">arnav@github: ~</text>
<line x1="1" y1="{TITLEBAR_H}" x2="{W - 1}" y2="{TITLEBAR_H}" stroke="{BORDER}" stroke-width="1"/>
{chr(10).join(body)}
<rect x="1" y="1" width="{W - 2}" height="{height - 2}" rx="12" fill="none" stroke="{BORDER}" stroke-width="2"/>
<rect x="1" y="1" width="{W - 2}" height="{height - 2}" rx="12" fill="url(#scan)" pointer-events="none"/>
<defs><pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">
<rect width="4" height="2" fill="#ffffff" opacity="0.015"/>
<rect y="2" width="4" height="2" fill="#000000" opacity="0.05"/>
</pattern></defs>
</svg>
"""
    return svg


if __name__ == "__main__":
    import pathlib
    out = pathlib.Path(__file__).parent / "terminal.svg"
    out.write_text(build(), encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size} bytes)")
