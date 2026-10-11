"""Render data/contributions.json as an animated heatmap SVG.

One-shot diagonal reveal (CSS keyframes, no loop), legend and stats footer.

Usage: python scripts/render_heatmap_svg.py
Output: contrib-heatmap.svg
"""
import json
from datetime import date, timedelta

OUT = "contrib-heatmap.svg"
data = json.load(open("data/contributions.json"))
days, stats = data["days"], data["stats"]

W = 860
CELL, GAP = 11, 3.4
PAD_X, TOP = 30, 46
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
BG, BORDER, FG, MUTED, GREEN = "#0d1117", "#30363d", "#c9d1d9", "#8b949e", "#3fb950"
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

first = date.fromisoformat(days[0]["date"])
week0 = first - timedelta(days=(first.weekday() + 1) % 7)  # GitHub rows start on Sunday
cells, months = [], {}
for i, d in enumerate(days):
    # position from the date itself, so gaps in the scraped data can't shift cells
    dt = date.fromisoformat(d["date"])
    col, row = (dt - week0).days // 7, (dt.weekday() + 1) % 7
    cells.append((col, row, d))
    if dt.day <= 7 and row == 0 or i == 0:
        months.setdefault(col, dt.strftime("%b"))

cols = cells[-1][0] + 1
grid_w = cols * (CELL + GAP) - GAP
x0 = PAD_X + (W - 2 * PAD_X - grid_w) / 2
grid_h = 7 * (CELL + GAP) - GAP
H = int(TOP + grid_h + 70)

out = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
    "<style>",
    "@keyframes drop{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none}}",
    ".c{opacity:0;animation:drop .45s ease-out forwards}",
    "@keyframes fade{to{opacity:1}}",
    ".f{opacity:0;animation:fade .6s ease-out forwards}",
    "</style>",
    f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>',
    f'<g font-family="{FONT}" font-size="11" fill="{MUTED}">',
]

for col, label in months.items():
    if col < cols - 2:
        out.append(f'<text x="{x0 + col * (CELL + GAP):.1f}" y="{TOP - 10}">{label}</text>')
for row, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
    out.append(
        f'<text x="{x0 - 8:.1f}" y="{TOP + row * (CELL + GAP) + CELL - 2:.1f}" text-anchor="end" font-size="9">{label}</text>'
    )
out.append("</g>")

for col, row, d in cells:
    x = x0 + col * (CELL + GAP)
    y = TOP + row * (CELL + GAP)
    delay = (col + row) * 0.018
    tip = f'{d["count"]} on {d["date"]}'
    out.append(
        f'<rect class="c" style="animation-delay:{delay:.3f}s" x="{x:.1f}" y="{y:.1f}" width="{CELL}" height="{CELL}" '
        f'rx="2.5" fill="{PALETTE[d["level"]]}"><title>{tip}</title></rect>'
    )

reveal_end = (cols + 7) * 0.018 + 0.3
fy = TOP + grid_h + 30
best = stats["best_day"]
best_txt = f'{best["count"]} ({date.fromisoformat(best["date"]).strftime("%b %d")})' if best["count"] else "-"
parts = [
    ("total", f'{stats["total"]:,}'),
    ("streak", f'{stats["current_streak"]}d'),
    ("longest", f'{stats["longest_streak"]}d'),
    ("best day", best_txt),
]
out.append(
    f'<g class="f" style="animation-delay:{reveal_end:.2f}s" font-family="{FONT}" font-size="12">'
)
tx = x0
for k, v in parts:
    out.append(
        f'<text x="{tx:.1f}" y="{fy}"><tspan fill="{MUTED}">{k} </tspan><tspan fill="{GREEN}" font-weight="700">{v}</tspan></text>'
    )
    tx += 9 + 7.3 * (len(k) + len(v) + 3)

lx = x0 + grid_w - 5 * (CELL + GAP) - 34
out.append(f'<text x="{lx - 8:.1f}" y="{fy}" text-anchor="end" fill="{MUTED}" font-size="11">less</text>')
for i, c in enumerate(PALETTE):
    out.append(f'<rect x="{lx + i * (CELL + GAP):.1f}" y="{fy - 10}" width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"/>')
out.append(f'<text x="{lx + 5 * (CELL + GAP) + 4:.1f}" y="{fy}" fill="{MUTED}" font-size="11">more</text>')
out.append(
    f'<text x="{x0:.1f}" y="{fy + 20}" fill="{MUTED}" font-size="10" opacity="0.7">updated {data["fetched"]} · github.com/{data["user"]}</text>'
)
out.append("</g></svg>")

open(OUT, "w").write("\n".join(out))
print(f"{OUT} ({W}x{H}px, {len(cells)} cells)")
