"""Turn source-prepped.png into an animated ASCII-art SVG portrait.

Each row wipes in left-to-right behind a block cursor (SMIL), staggered
top-to-bottom. STATIC=1 renders the final frame with no animation.

Usage: python scripts/make_ascii_svg.py [source-prepped.png]
Output: ascii-portrait.svg
"""
import os
import sys
from html import escape

import numpy as np
from PIL import Image

SRC = sys.argv[1] if len(sys.argv) > 1 else "source-prepped.png"
OUT = "ascii-portrait.svg"
STATIC = os.environ.get("STATIC") == "1"

COLS = 120
CHAR_W, CHAR_H = 4.8, 8.0  # monospace cell ~0.6em wide
FONT_SIZE = 8
PAD = 16
BG = "#0d1117"
FG = "#c9d1d9"
CURSOR = "#3fb950"

# sparse -> dense; dark pixels get dense glyphs (classic negative look on a dark bg)
RAMP = " .`:-=+*cs#%@"

ROW_DELAY = 0.035  # seconds between rows starting
ROW_DUR = 0.55  # seconds for one row to wipe in

img = Image.open(SRC).convert("L")
w, h = img.size
rows = int(COLS * (h / w) * (CHAR_W / CHAR_H))
small = np.asarray(img.resize((COLS, rows), Image.LANCZOS), dtype=np.float32) / 255.0

# white background in the prepped photo marks "not subject"
subject = small < 0.97
# stretch contrast inside the subject, then invert: dark hair/beard/glasses -> dense
lo, hi = np.percentile(small[subject], [3, 97])
norm = 1 - np.clip((small - lo) / (hi - lo), 0, 1) ** 0.9
level = np.clip(0.08 + 0.92 * norm, 0, 1)
idx = np.where(subject, (level * (len(RAMP) - 1)).round().astype(int), 0)
# NBSP so renderers never collapse runs of spaces (textLength relies on exact column count)
lines = ["".join(RAMP[i] for i in row).replace(" ", "\u00a0") for row in idx]

W = PAD * 2 + COLS * CHAR_W
H = PAD * 2 + rows * CHAR_H
row_w = COLS * CHAR_W

out = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" viewBox="0 0 {W:.0f} {H:.0f}">',
    f'<rect width="100%" height="100%" rx="10" fill="{BG}"/>',
    f'<g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="{FONT_SIZE}" fill="{FG}" xml:space="preserve">',
]
if not STATIC:
    out.append("<defs>")
    for r in range(rows):
        y = PAD + r * CHAR_H
        begin = r * ROW_DELAY
        out.append(
            f'<clipPath id="c{r}"><rect x="{PAD}" y="{y:.1f}" width="0" height="{CHAR_H}">'
            f'<animate attributeName="width" from="0" to="{row_w:.1f}" begin="{begin:.3f}s" dur="{ROW_DUR}s" fill="freeze"/>'
            f"</rect></clipPath>"
        )
    out.append("</defs>")

for r, line in enumerate(lines):
    if not line.replace("\u00a0", "").strip():
        continue
    y = PAD + r * CHAR_H
    clip = "" if STATIC else f' clip-path="url(#c{r})"'
    out.append(
        f'<text x="{PAD}" y="{y + CHAR_H * 0.8:.1f}" textLength="{row_w:.1f}" '
        f'lengthAdjust="spacingAndGlyphs"{clip}>{escape(line)}</text>'
    )
    if not STATIC:
        begin = r * ROW_DELAY
        out.append(
            f'<rect x="{PAD}" y="{y:.1f}" width="{CHAR_W}" height="{CHAR_H}" fill="{CURSOR}" opacity="0">'
            f'<set attributeName="opacity" to="1" begin="{begin:.3f}s"/>'
            f'<animate attributeName="x" from="{PAD}" to="{PAD + row_w:.1f}" begin="{begin:.3f}s" dur="{ROW_DUR}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0" begin="{begin + ROW_DUR:.3f}s"/>'
            f"</rect>"
        )

out.append("</g></svg>")
open(OUT, "w").write("\n".join(out))
print(f"{OUT} ({COLS}x{rows} chars, {W:.0f}x{H:.0f}px)")
