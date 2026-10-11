"""Neofetch-style info card as an animated SVG.

Lines fade + slide in on a stagger. STATIC=1 renders the final frame.

Usage: python scripts/make_info_card.py
Output: info-card.svg
"""
import os
from html import escape

OUT = "info-card.svg"
STATIC = os.environ.get("STATIC") == "1"

W, H = 490, 462
PAD_X = 22
LINE_H = 25
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

BG = "#0d1117"
BAR = "#161b22"
BORDER = "#30363d"
FG = "#c9d1d9"
MUTED = "#8b949e"
GREEN = "#3fb950"
BLUE = "#58a6ff"
RED = "#ff7b72"

INFO = [
    ("Role", "Senior Software Engineer"),
    ("Company", "Adapta.org"),
    ("Founder", "Jogga Sport Hub"),
    ("Backend", "Node.js · NestJS · Go · Java"),
    ("Frontend", "Next.js · React · Angular"),
    ("Data", "PostgreSQL · Prisma · MySQL"),
    ("Infra", "Docker · Dokploy · GH Actions"),
    ("AI", "Multi-agent · Claude Code · n8n"),
    ("Langs", "TypeScript · Go · Python · Java"),
    ("LinkedIn", "in/carlos--moraes"),
]
SWATCHES = ["#ff7b72", "#ffa657", "#d29922", "#3fb950", "#58a6ff", "#bc8cff", "#c9d1d9"]

STEP = 0.12  # seconds between lines
START = 0.5


def anim(i):
    """Fade + 6px slide-in, staggered by line index."""
    if STATIC:
        return "", ""
    begin = START + i * STEP
    return (
        ' opacity="0"',
        f'<animate attributeName="opacity" from="0" to="1" begin="{begin:.2f}s" dur="0.35s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" from="-6 0" to="0 0" '
        f'begin="{begin:.2f}s" dur="0.35s" fill="freeze"/>',
    )


out = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
    f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>',
    # title bar
    f'<path d="M0.5 10.5a10 10 0 0 1 10-10h{W - 21}a10 10 0 0 1 10 10v22h-{W - 1}z" fill="{BAR}"/>',
    f'<line x1="0.5" y1="32.5" x2="{W - 0.5}" y2="32.5" stroke="{BORDER}"/>',
    '<circle cx="20" cy="17" r="5.5" fill="#ff5f56"/>',
    '<circle cx="38" cy="17" r="5.5" fill="#ffbd2e"/>',
    '<circle cx="56" cy="17" r="5.5" fill="#27c93f"/>',
    f'<text x="{W / 2}" y="21" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{MUTED}">carlos@moraes: ~</text>',
    f'<g font-family="{FONT}" font-size="13.5" xml:space="preserve">',
]

y = 62
i = 0
op, a = anim(i)
out.append(
    f'<g{op}><text x="{PAD_X}" y="{y}"><tspan fill="{GREEN}">$</tspan>'
    f'<tspan fill="{FG}"> neofetch</tspan></text>{a}</g>'
)
y += LINE_H + 8
i += 1

op, a = anim(i)
out.append(
    f'<g{op}><text x="{PAD_X}" y="{y}" font-weight="700"><tspan fill="{GREEN}">carlos</tspan>'
    f'<tspan fill="{FG}">@</tspan><tspan fill="{GREEN}">moraes</tspan></text>{a}</g>'
)
y += 10
i += 1
op, a = anim(i)
out.append(f'<g{op}><line x1="{PAD_X}" y1="{y}" x2="{PAD_X + 128}" y2="{y}" stroke="{BORDER}" stroke-width="1.5"/>{a}</g>')
y += LINE_H + 2

for key, val in INFO:
    i += 1
    op, a = anim(i)
    out.append(
        f'<g{op}><text x="{PAD_X}" y="{y}"><tspan fill="{BLUE}" font-weight="700">{escape(key)}</tspan>'
        f'<tspan fill="{MUTED}">:</tspan></text>'
        f'<text x="{PAD_X + 96}" y="{y}" fill="{FG}">{escape(val)}</text>{a}</g>'
    )
    y += LINE_H

y += 10
i += 1
op, a = anim(i)
sw = "".join(
    f'<rect x="{PAD_X + k * 26}" y="{y - 12}" width="22" height="14" rx="2" fill="{c}"/>' for k, c in enumerate(SWATCHES)
)
out.append(f"<g{op}>{sw}{a}</g>")

# prompt with blinking cursor
y = H - 22
i += 1
op, a = anim(i)
blink = (
    ""
    if STATIC
    else '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1s" repeatCount="indefinite"/>'
)
out.append(
    f'<g{op}><text x="{PAD_X}" y="{y}" fill="{GREEN}">$</text>'
    f'<rect x="{PAD_X + 14}" y="{y - 12}" width="8" height="15" fill="{FG}">{blink}</rect>{a}</g>'
)

out.append("</g></svg>")
open(OUT, "w").write("\n".join(out))
print(f"{OUT} ({W}x{H}px, {i + 1} animated lines)")
