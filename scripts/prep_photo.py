"""Remove background, boost local contrast, composite on white.

Usage: python scripts/prep_photo.py source-photo.jpg
Output: source-prepped.png
"""
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove

src = sys.argv[1] if len(sys.argv) > 1 else "source-photo.jpg"

img = Image.open(src).convert("RGB")
cut = remove(img)  # RGBA, background transparent

rgb = np.array(cut.convert("RGB"))
alpha = np.array(cut.split()[-1]).astype(np.float32) / 255.0

# CLAHE on luminance so face details survive the ASCII downsample
lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
l, a, b = cv2.split(lab)
l = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8)).apply(l)
rgb = cv2.cvtColor(cv2.merge((l, a, b)), cv2.COLOR_LAB2RGB).astype(np.float32)

white = np.full_like(rgb, 255.0)
out = rgb * alpha[..., None] + white * (1 - alpha[..., None])

# crop to subject bbox with a little padding
ys, xs = np.where(alpha > 0.1)
pad = 20
y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad, out.shape[0])
x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad, out.shape[1])
Image.fromarray(out[y0:y1, x0:x1].astype(np.uint8)).save("source-prepped.png")
print(f"source-prepped.png ({x1 - x0}x{y1 - y0})")
