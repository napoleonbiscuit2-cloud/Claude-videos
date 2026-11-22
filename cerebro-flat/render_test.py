"""Test de style « motion design plat » — scène 1 (accroche + lóbulo frontal).

Tout est dessiné en code avec cairo ; mouvements par ressorts (spring physics)
et easing, jamais linéaires. Audio : ../cerebro-es/narracion.mp3 (0 → ~22 s).
Aperçu d'une image : python3 render_test.py 12.5
"""
import json, math, random, subprocess, sys
from pathlib import Path
import cairo
import numpy as np

HERE = Path(__file__).parent
ES = HERE.parent / "cerebro-es"
W, H, FPS = 1080, 1920, 30
END = 22.25  # juste avant « Lóbulo occipital »
FONT = "DejaVu Sans"

words = [w for w in json.loads((ES / "palabras.json").read_text()) if w["start"] < END]


def at(txt, after=0.0):
    for w in words:
        if w["start"] >= after and w["text"].lower().strip(".,:").startswith(txt):
            return w["start"]
    raise SystemExit(txt)


T2, T20, TMIRA = at("2%"), at("20%"), at("mira")
TFRONT, TJEFE = at("lóbulo"), at("jefe")
TDEC, TPLAN, TCTRL = at("decides"), at("planeas"), at("controlas")
TDATO, T25 = at("dato"), at("25")


# ---------- outils de mouvement ----------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(x):  # ease in-out (cubique)
    x = clamp(x)
    return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2


def spring(t, k=170.0, c=14.0):
    """Réponse d'un ressort amorti (0 → 1, avec léger dépassement)."""
    if t <= 0:
        return 0.0
    w0 = math.sqrt(k)
    z = c / (2 * w0)
    if z >= 1:
        return 1 - math.exp(-w0 * t) * (1 + w0 * t)
    wd = w0 * math.sqrt(1 - z * z)
    return 1 - math.exp(-z * w0 * t) * (math.cos(wd * t) + z * w0 / wd * math.sin(wd * t))


def pop(t, t0, t1=None, **kw):
    """Apparition par ressort à t0, disparition douce à t1."""
    v = spring(t - t0, **kw)
    if t1 is not None:
        v *= 1 - ease((t - t1) / 0.35)
    return v


def noise1(t, seed):
    """Bruit lisse (somme de sinus) pour une dérive naturelle."""
    return (math.sin(t * 0.7 + seed) + 0.5 * math.sin(t * 1.3 + seed * 2.1) + 0.25 * math.sin(t * 2.9 + seed * 3.7)) / 1.75


# ---------- couleurs ----------
def rgb(h, a=1.0):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (a,)


BG1, BG2 = rgb("#16204a"), rgb("#2b1c52")
PINK, PINK_D, PINK_L = rgb("#ff9fb6"), rgb("#e0708e"), rgb("#ffc9d6")
BLUE, BLUE_L = rgb("#4fb3ff"), rgb("#9fd8ff")
GOLD, GOLD_D = rgb("#ffd54a"), rgb("#e0a82e")
WHITE = rgb("#ffffff")
SKIN = rgb("#7d86c9")

# ---------- cerveau (coordonnées locales, ~760 px de large) ----------
CEREBRUM = [(-230, -20, 170), (-95, -130, 190), (90, -130, 190), (235, -30, 170),
            (150, 105, 150), (-20, 90, 175), (-205, 95, 130)]


def cerebrum_path(cr):
    for x, y, r in CEREBRUM:
        cr.new_sub_path()
        cr.arc(x, y, r, 0, 2 * math.pi)


def draw_brain(cr, t, frontal=0.0, frontal_glow=0.0, glow=0.0):
    # halo (énergie)
    if glow > 0:
        g = cairo.RadialGradient(0, 0, 100, 0, 0, 560)
        g.add_color_stop_rgba(0, *GOLD[:3], 0.45 * glow)
        g.add_color_stop_rgba(1, *GOLD[:3], 0)
        cr.set_source(g)
        cr.arc(0, 0, 560, 0, 2 * math.pi)
        cr.fill()
    # tronc + cervelet
    cr.set_source_rgba(*PINK_D)
    cr.move_to(70, 150); cr.line_to(140, 150); cr.line_to(130, 340)
    cr.curve_to(128, 370, 82, 370, 80, 340); cr.close_path(); cr.fill()
    cr.set_source_rgba(*PINK_D)
    cr.arc(215, 190, 95, 0, 2 * math.pi); cr.fill()
    cr.set_source_rgba(*rgb("#c95f7c"))
    cr.set_line_width(7); cr.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(4):
        cr.arc(215, 175 + i * 4, 60 - i * 12, math.radians(200), math.radians(340)); cr.stroke()
    # hémisphère
    cr.set_source_rgba(*PINK)
    cerebrum_path(cr); cr.fill()
    # lobe frontal qui se remplit de l'avant vers l'arrière
    if frontal > 0:
        cr.save()
        cerebrum_path(cr); cr.clip()
        x_edge = -420 + 380 * frontal
        cr.move_to(-460, -400); cr.line_to(x_edge + 40, -400)
        cr.curve_to(x_edge - 20, -150, x_edge + 30, 80, x_edge - 40, 320)
        cr.line_to(-460, 320); cr.close_path()
        col = [BLUE[i] * (1 - frontal_glow) + BLUE_L[i] * frontal_glow for i in range(3)]
        cr.set_source_rgba(*col, 1); cr.fill()
        cr.restore()
    # reflet
    cr.save(); cerebrum_path(cr); cr.clip()
    cr.set_source_rgba(1, 1, 1, 0.18)
    cr.arc(-120, -230, 210, 0, 2 * math.pi); cr.fill()
    cr.restore()
    # circonvolutions
    cr.set_source_rgba(0, 0, 0, 0.13)
    cr.set_line_width(10); cr.set_line_cap(cairo.LINE_CAP_ROUND)
    for pts in [((-300, -60), (-250, -140), (-180, -60), (-120, -150)),
                ((-60, -250), (-20, -170), (40, -260), (90, -180)),
                ((130, -220), (200, -150), (260, -200), (300, -110)),
                ((-260, 80), (-180, 20), (-120, 90), (-40, 30)),
                ((20, -40), (80, -100), (140, -20), (210, -60)),
                ((-10, 150), (60, 90), (120, 170), (200, 120))]:
        cr.move_to(*pts[0]); cr.curve_to(*pts[1], *pts[2], *pts[3]); cr.stroke()
    # sillon central
    cr.set_line_width(12)
    cr.move_to(-30, -315); cr.curve_to(-60, -200, 10, -120, -40, 20); cr.stroke()


def draw_person(cr, alpha):
    cr.set_source_rgba(*SKIN[:3], alpha)
    # corps (pilule) + tête
    cr.arc(0, 0, 150, 0, 2 * math.pi); cr.fill()
    cr.move_to(-200, 520); cr.line_to(-200, 380)
    cr.curve_to(-200, 220, 200, 220, 200, 380); cr.line_to(200, 520)
    cr.close_path(); cr.fill()


def text(cr, s, x, y, size, color=WHITE, align="c", scale=1.0, alpha=1.0, weight=cairo.FONT_WEIGHT_BOLD):
    if scale <= 0.01 or alpha <= 0.01:
        return
    cr.save()
    cr.translate(x, y); cr.scale(scale, scale)
    cr.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, weight)
    cr.set_font_size(size)
    ext = cr.text_extents(s)
    dx = -ext.x_advance / 2 if align == "c" else 0
    # ombre douce
    cr.move_to(dx + 4, 6); cr.set_source_rgba(0, 0, 0, 0.35 * alpha); cr.show_text(s)
    cr.move_to(dx, 0); cr.set_source_rgba(*color[:3], alpha); cr.show_text(s)
    cr.restore()


def badge(cr, x, y, s, color, kind, label):
    if s <= 0.01:
        return
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    cr.set_source_rgba(0, 0, 0, 0.25); cr.arc(0, 8, 78, 0, 2 * math.pi); cr.fill()
    cr.set_source_rgba(*color); cr.arc(0, 0, 78, 0, 2 * math.pi); cr.fill()
    cr.set_source_rgba(1, 1, 1, 1); cr.set_line_width(13)
    cr.set_line_cap(cairo.LINE_CAP_ROUND); cr.set_line_join(cairo.LINE_JOIN_ROUND)
    if kind == "check":
        cr.move_to(-32, 2); cr.line_to(-8, 28); cr.line_to(36, -26); cr.stroke()
    elif kind == "list":
        for i in range(3):
            cr.arc(-28, -26 + i * 26, 6, 0, 2 * math.pi); cr.fill()
            cr.move_to(-10, -26 + i * 26); cr.line_to(32, -26 + i * 26); cr.stroke()
    elif kind == "stop":
        cr.arc(0, 0, 36, 0, 2 * math.pi); cr.stroke()
        cr.move_to(-25, 25); cr.line_to(25, -25); cr.stroke()
    cr.restore()
    text(cr, label, x, y + 125, 40, alpha=clamp(s))


def crown(cr, x, y, s, rot):
    if s <= 0.01:
        return
    cr.save(); cr.translate(x, y); cr.rotate(rot); cr.scale(max(s, 1e-3), max(s, 1e-3))
    cr.set_source_rgba(*GOLD)
    cr.move_to(-80, 40); cr.line_to(-90, -40); cr.line_to(-45, 0); cr.line_to(0, -60)
    cr.line_to(45, 0); cr.line_to(90, -40); cr.line_to(80, 40); cr.close_path(); cr.fill()
    cr.set_source_rgba(*GOLD_D); cr.rectangle(-80, 28, 160, 18); cr.fill()
    for px, py in [(-90, -40), (0, -60), (90, -40)]:
        cr.set_source_rgba(*rgb("#ff6b8b")); cr.arc(px, py, 11, 0, 2 * math.pi); cr.fill()
    cr.restore()


# particules d'arrière-plan (profondeur : les lointaines bougent moins)
rnd = random.Random(3)
PARTS = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(2, 7), rnd.uniform(0.2, 1.0), rnd.uniform(0, 99)) for _ in range(70)]

# sous-titres : groupes de 3 mots max, coupés après la ponctuation
GROUPS, cur = [], []
for i, w in enumerate(words):
    cur.append(i)
    if len(cur) == 3 or w["text"].endswith((".", ",", ":")):
        GROUPS.append(cur); cur = []
if cur:
    GROUPS.append(cur)


def captions(cr, t):
    idx = None
    for i, w in enumerate(words):
        if w["start"] <= t + 0.02:
            idx = i
    if idx is None or t > words[idx]["end"] + 0.6:
        return
    g = next(g for g in GROUPS if idx in g)
    t0 = words[g[0]]["start"]
    s = 0.85 + 0.15 * spring(t - t0, k=260, c=20)
    cr.save()
    cr.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    cr.set_font_size(70)
    full = " ".join(words[i]["text"] for i in g)
    total = cr.text_extents(full).x_advance
    cr.translate(W / 2, 1640); cr.scale(s, s)
    x = -total / 2
    for i in g:
        tx = words[i]["text"]
        col = GOLD if i == idx else WHITE
        cr.move_to(x + 4, 6); cr.set_source_rgba(0, 0, 0, 0.4); cr.show_text(tx)
        cr.move_to(x, 0); cr.set_source_rgba(*col); cr.show_text(tx)
        x += cr.text_extents(tx + " ").x_advance
    cr.restore()


def frame(t):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    cr = cairo.Context(surf)
    cr.set_antialias(cairo.ANTIALIAS_BEST)
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgba(0, *BG1); g.add_color_stop_rgba(1, *BG2)
    cr.set_source(g); cr.paint()

    # caméra : de la personne entière au cerveau (ease in-out), plus une petite dérive lisse
    zoom_p = ease((t - TMIRA + 0.3) / 2.2)
    zoom = 1.0 + 2.0 * zoom_p
    head = (540, 700)
    focus_screen = (540 + 0 * zoom_p, 860 - 0 * zoom_p)
    drift_x, drift_y = 6 * noise1(t * 0.5, 1), 8 * noise1(t * 0.5, 2)

    for px, py, r, depth, sd in PARTS:
        x = (px + 12 * noise1(t * 0.3, sd) - (zoom - 1) * (px - W / 2) * 0.15 * depth) % W
        y = (py - t * 8 * depth + 10 * noise1(t * 0.3, sd + 5)) % H
        cr.set_source_rgba(1, 1, 1, 0.08 + 0.12 * depth)
        cr.arc(x, y, r * (0.8 + 0.4 * depth), 0, 2 * math.pi); cr.fill()

    cr.save()
    cr.translate(focus_screen[0] + drift_x, focus_screen[1] + drift_y)
    cr.scale(zoom, zoom)
    cr.translate(-head[0], -head[1])

    # personne (accroche), disparaît pendant le zoom
    person_in = spring(t, k=120, c=13)
    pa = 1 - ease((t - TMIRA) / 1.2)
    if pa > 0:
        cr.save(); cr.translate(540, 700 + 60 * (1 - person_in)); draw_person(cr, pa * clamp(person_in)); cr.restore()

    # cerveau (dans la tête), respiration lente
    breathe = 1 + 0.012 * math.sin(t * 1.6)
    bscale = max(0.3 * spring(t - 0.15, k=150, c=12) * breathe, 1e-3)
    glow = ease((t - T20 + 0.1) / 0.6) * (1 - ease((t - TFRONT) / 0.8)) * (0.85 + 0.15 * math.sin(t * 3))
    frontal = ease((t - TFRONT) / 0.9)
    fglow = ease((t - T25 + 2.5) / 3.0)
    cr.save(); cr.translate(*head); cr.scale(bscale, bscale)
    draw_brain(cr, t, frontal=frontal, frontal_glow=fglow, glow=glow)
    # couronne : tombe sur le lobe frontal avec un ressort, oscille puis se pose
    cs = spring(t - TJEFE, k=200, c=11)
    if t >= TJEFE:
        cy = -420 - 300 * (1 - cs)
        rot = 0.25 * math.exp(-3 * (t - TJEFE)) * math.sin(9 * (t - TJEFE)) - 0.18
        crown(cr, -200, cy, 1.4 * clamp(cs * 1.2), rot)
    cr.restore()
    cr.restore()

    # ---- textes d'accroche ----
    if t < TMIRA + 0.6:
        out = 1 - ease((t - TMIRA) / 0.5)
        s2 = spring(t - T2, k=220, c=15)
        text(cr, "2%", 250, 560, 120, color=WHITE, scale=s2, alpha=out)
        text(cr, "del peso", 250, 625, 44, scale=s2, alpha=out)
        s20 = spring(t - T20, k=220, c=15)
        text(cr, "20%", 830, 560, 120, color=GOLD, scale=s20, alpha=out)
        text(cr, "de la energía", 830, 625, 44, color=GOLD, scale=s20, alpha=out)
        # batterie qui se remplit jusqu'à 20 %
        b = s20 * out
        if b > 0.01:
            cr.save(); cr.translate(830, 760); cr.scale(b, b)
            cr.set_line_width(8); cr.set_source_rgba(*GOLD)
            cr.rectangle(-60, -110, 120, 220); cr.stroke()
            cr.rectangle(-25, -128, 50, 18); cr.fill()
            lvl = 0.2 * ease((t - T20) / 0.9)
            cr.rectangle(-48, 98 - 196 * lvl, 96, 196 * lvl); cr.fill()
            cr.restore()

    # ---- titre de section ----
    ts = spring(t - TFRONT, k=200, c=16)
    if t >= TFRONT:
        text(cr, "LÓBULO FRONTAL", W / 2, 250, 84, color=BLUE_L, scale=ts)
        text(cr, "el jefe", W / 2, 330, 54, color=GOLD, scale=spring(t - TJEFE, k=200, c=16))

    # ---- badges : decides / planeas / controlas (décalés) ----
    for x, t0, colr, kind, lab in [(270, TDEC, rgb("#ffb347"), "check", "decides"),
                                   (540, TPLAN, rgb("#3ecfb2"), "list", "planeas"),
                                   (810, TCTRL, rgb("#ff6b8b"), "stop", "controlas")]:
        badge(cr, x, 1290, pop(t, t0, TDATO, k=230, c=15), colr, kind, lab)

    # ---- frise des âges : maturité vers 25 ans ----
    tl = pop(t, TDATO + 0.35)
    if tl > 0.01:
        a = clamp(tl)
        x0, x1, y = 150, 930, 1330
        cr.set_line_width(10); cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.set_source_rgba(1, 1, 1, 0.3 * a)
        cr.move_to(x0, y); cr.line_to(x0 + (x1 - x0) * ease(tl), y); cr.stroke()
        for i, age in enumerate([0, 5, 10, 15, 20, 25]):
            xx = x0 + (x1 - x0) * i / 5
            text(cr, str(age), xx, y + 70, 36, alpha=a * 0.8, weight=cairo.FONT_WEIGHT_NORMAL)
        p = ease((t - (TDATO + 0.8)) / (T25 - TDATO - 0.6))
        mx = x0 + (x1 - x0) * p
        cr.set_source_rgba(*BLUE_L[:3], a); cr.set_line_width(10)
        cr.move_to(x0, y); cr.line_to(mx, y); cr.stroke()
        ms = 1 + 0.25 * (spring(t - T25, k=300, c=10) - 1 if t >= T25 else 0) * -1
        cr.arc(mx, y, 22 * ms, 0, 2 * math.pi); cr.fill()
        age = int(round(25 * p))
        text(cr, f"{age} años", mx, y - 45, 46, color=BLUE_L, alpha=a)
        if t >= T25 - 0.05:
            text(cr, "¡Listo a los 25!", W / 2, 1210, 62, color=GOLD, scale=spring(t - T25, k=260, c=13))

    captions(cr, t)

    # fondu de fin
    if t > END - 0.5:
        cr.set_source_rgba(0, 0, 0, ease((t - END + 0.5) / 0.5)); cr.paint()

    buf = np.ndarray((H, W, 4), np.uint8, surf.get_data())
    return buf[..., [2, 1, 0]].copy()  # BGRA → RGB


def main():
    if len(sys.argv) > 1:
        from PIL import Image
        Image.fromarray(frame(float(sys.argv[1]))).save(HERE / "preview.png")
        return
    out = HERE / "test_escena1.mp4"
    p = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
        "-r", str(FPS), "-i", "-", "-t", str(END), "-i", str(ES / "narracion.mp3"),
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)], stdin=subprocess.PIPE)
    for i in range(int(END * FPS)):
        p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait()
    print("OK", out)


if __name__ == "__main__":
    main()
