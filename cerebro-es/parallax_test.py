"""Test de parallaxe 2.5D sur une planche (sans IA, sans crédits).

Carte de profondeur « faite main » : fond noir = loin, papier = milieu,
gravure dense (tête, cerveau) = près. Puis la caméra bouge lentement et
chaque pixel se déplace selon sa profondeur.
Sorties : parallax_test.mp4 (planche seule), parallax_comparaison.mp4
(gauche : sans parallaxe / droite : avec), parallax_profondeur.png
"""
import math, subprocess
from pathlib import Path
import numpy as np
import cv2

HERE = Path(__file__).parent
W, H, FPS, DUR = 1080, 1920, 30, 8.0

src = cv2.imread(str(HERE / "imagenes" / "01.png"))
s = max(W / src.shape[1], H / src.shape[0]) * 1.12
src = cv2.resize(src, (int(src.shape[1] * s), int(src.shape[0] * s)), interpolation=cv2.INTER_LANCZOS4)
sh, sw = src.shape[:2]

# ---------- carte de profondeur ----------
gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
# carte = tout ce qui n'est pas le fond noir relié au bord (les encres sombres à l'intérieur restent dans la carte)
dark = (cv2.GaussianBlur(gray, (0, 0), 6) < 0.22).astype(np.uint8)
ff = dark.copy(); mask = np.zeros((sh + 2, sw + 2), np.uint8)
for x, y in [(0, 0), (sw - 1, 0), (0, sh - 1), (sw - 1, sh - 1)]:
    if ff[y, x] == 1:
        cv2.floodFill(ff, mask, (x, y), 2)
card = (ff != 2).astype(np.float32)
card = cv2.GaussianBlur(card, (0, 0), 3)
ink = cv2.GaussianBlur((1 - gray) * card, (0, 0), 28)
inside = ink[card > 0.5]
lo, hi = np.percentile(inside, 5), np.percentile(inside, 97)
dens = np.clip((ink - lo) / (hi - lo), 0, 1)
depth = card * (0.35 + 0.65 * dens)
depth = cv2.GaussianBlur(depth, (0, 0), 14)
cv2.imwrite(str(HERE / "parallax_profondeur.png"), (depth * 255).astype(np.uint8))


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2


def noise1(t, seed):
    return (math.sin(t * 0.9 + seed) + 0.5 * math.sin(t * 2.3 + seed * 2.1)) / 1.5


yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
_v = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
VIG = np.clip(1.15 - 0.55 * _v ** 2, 0.3, 1.0)[..., None]
rng = np.random.default_rng(1)
GRAIN = [cv2.resize(rng.normal(0, 18, (H // 2, W // 2)).astype(np.float32), (W, H)) for _ in range(6)]


def render(t, parallax=True):
    p = ease(t / DUR)
    z = 1.0 + 0.06 * p                       # léger rapprochement
    ox = -60 + 120 * p                       # la caméra glisse de gauche à droite (px)
    oy = 25 * math.sin(math.pi * p)          # en arc, pas en ligne droite
    cx, cy = sw / 2 + 1.5 * noise1(t * 1.3, 1), sh / 2 + 2 * noise1(t * 1.1, 2)
    mx = cx + (xx - W / 2) / z
    my = cy + (yy - H / 2) / z
    if parallax:
        d = cv2.remap(depth, mx, my, cv2.INTER_LINEAR)
        mx = mx + ox * (d - 0.35)            # le papier sert de plan de référence
        my = my + oy * (d - 0.35)
    else:
        mx = mx + ox * 0.3
        my = my + oy * 0.3
    out = cv2.remap(src, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT).astype(np.float32)
    out *= 1 + 0.02 * noise1(t * 5, 3)
    out += GRAIN[int(t * FPS) % 6][..., None] * 0.6
    out *= VIG
    return np.clip(out, 0, 255).astype(np.uint8)


def encode(path, size, frames):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24",
                          "-s", f"{size[0]}x{size[1]}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
                          "-crf", "22", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(path)],
                         stdin=subprocess.PIPE)
    for f in frames:
        p.stdin.write(f.tobytes())
    p.stdin.close(); p.wait()


def label(img, txt):
    cv2.putText(img, txt, (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 0, 0), 8, cv2.LINE_AA)
    cv2.putText(img, txt, (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (200, 230, 245), 3, cv2.LINE_AA)
    return img


n = int(DUR * FPS)
encode(HERE / "parallax_test.mp4", (W, H), (render(i / FPS) for i in range(n)))
encode(HERE / "parallax_comparaison.mp4", (W, H // 2),
       (np.hstack([label(cv2.resize(render(i / FPS, False), (W // 2, H // 2)), "sin parallax"),
                   label(cv2.resize(render(i / FPS, True), (W // 2, H // 2)), "con parallax")]) for i in range(n)))
print("OK")
