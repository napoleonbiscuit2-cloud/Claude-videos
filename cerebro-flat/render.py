"""Vidéo complète « Partes del cerebro » — style motion design plat.

Tout est dessiné en code (cairo). Mouvements : ressorts + easing, caméra douce
qui suit le sujet, aucun effet brusque. Audio : ../cerebro-es/narracion.mp3
Aperçu d'une image : python3 render.py 12.5
"""
import json, math, random, subprocess, sys
from pathlib import Path
import cairo
import numpy as np

HERE = Path(__file__).parent
ES = HERE.parent / "cerebro-es"
W, H, FPS = 1080, 1920, 30
FONT = "DejaVu Sans"
B = cairo.FONT_WEIGHT_BOLD
N = cairo.FONT_WEIGHT_NORMAL

words = json.loads((ES / "palabras.json").read_text())
DUR = float(subprocess.check_output([
    "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
    str(ES / "narracion.mp3")]).decode()) + 0.6


def at(txt, after=0.0):
    for w in words:
        if w["start"] >= after and w["text"].lower().strip(".,:¡!¿?").startswith(txt):
            return w["start"]
    raise SystemExit(txt)


T = dict(
    d2=at("2%"), d20=at("20%"), mira=at("mira"),
    front=at("lóbulo"), jefe=at("jefe"), dec=at("decides"), plan=at("planeas"), ctrl=at("controlas"),
    dato=at("dato"), a25=at("25"),
    occ=at("lóbulo", 20), ojos=at("ojos"), pero=at("pero", 26), luz=at("luz"), imag=at("imágenes"),
    hipo=at("hipocampo"), mem=at("memoria"), recu=at("recuerdos"), taxi=at("taxistas"), calles=at("calles"),
    grande=at("grande"),
    amig=at("amígdala"), alm=at("almendra"), alarma=at("alarma"), paciente=at("paciente"), nosiente=at("no", 54),
    cereb=at("cerebelo"), equi=at("equilibrio"), neur=at("neuronas"), resto=at("resto"), cosq=at("cosquillas"),
    yasabe=at("ya", 67),
    hipot=at("hipotálamo"), termo=at("termostato"), hambre=at("hambre"), sed=at("sed"), temp=at("temperatura"),
    reloj=at("reloj"),
    tronco=at("tronco"), resp=at("respiras"), coraz=at("corazón"), duer=at("duermes"),
    fin=at("y", 88), dolor=at("dolor"), despiertas=at("despiertas"), sig=at("sígueme"),
)
SECTIONS = ["hook", "front", "occ", "hipo", "amig", "cereb", "hipot", "tronco", "fin"]
STARTS = [0.0, T["front"], T["occ"], T["hipo"], T["amig"], T["cereb"], T["hipot"], T["tronco"], T["fin"]]


def window(name):
    i = SECTIONS.index(name)
    return STARTS[i], (STARTS[i + 1] if i + 1 < len(STARTS) else DUR + 1)


# ---------- mouvement ----------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(x):
    x = clamp(x)
    return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2


def spring(t, k=170.0, c=14.0):
    if t <= 0:
        return 0.0
    w0 = math.sqrt(k); z = c / (2 * w0)
    if z >= 1:
        return 1 - math.exp(-w0 * t) * (1 + w0 * t)
    wd = w0 * math.sqrt(1 - z * z)
    return 1 - math.exp(-z * w0 * t) * (math.cos(wd * t) + z * w0 / wd * math.sin(wd * t))


def pop(t, t0, t1=None, k=200, c=15):
    v = spring(t - t0, k, c)
    if t1 is not None:
        v *= 1 - ease((t - t1 + 0.15) / 0.4)
    return v


def in_sec(t, name, k=180, c=15):
    s0, s1 = window(name)
    return pop(t, s0, s1, k, c)


def noise1(t, seed):
    return (math.sin(t * 0.7 + seed) + 0.5 * math.sin(t * 1.3 + seed * 2.1) + 0.25 * math.sin(t * 2.9 + seed * 3.7)) / 1.75


def lerp(a, b, k):
    return a + (b - a) * k


# ---------- couleurs ----------
def rgb(h, a=1.0):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (a,)


BG1, BG2 = rgb("#16204a"), rgb("#2b1c52")
PINK, PINK_D = rgb("#ff9fb6"), rgb("#e0708e")
BLUE, BLUE_L = rgb("#4fb3ff"), rgb("#9fd8ff")
GREEN = rgb("#5ee08a")
YELLOW, GOLD, GOLD_D = rgb("#ffe066"), rgb("#ffd54a"), rgb("#e0a82e")
RED = rgb("#ff4d5e")
ORANGE = rgb("#ffa040")
CYAN = rgb("#3fe0e0")
PURPLE = rgb("#b48cff")
WHITE = rgb("#ffffff")
SKIN = rgb("#7d86c9")
TEAL = rgb("#3ecfb2")
CORAL = rgb("#ff6b8b")
AMBER = rgb("#ffb347")
GREY = rgb("#9aa0b8")

SEC_COLOR = dict(hook=WHITE, front=BLUE_L, occ=GREEN, hipo=YELLOW, amig=RED, cereb=ORANGE,
                 hipot=CYAN, tronco=PURPLE, fin=GOLD)
TITLES = dict(front=("LÓBULO FRONTAL", "el jefe"), occ=("LÓBULO OCCIPITAL", "la visión"),
              hipo=("HIPOCAMPO", "la memoria"), amig=("AMÍGDALA", "el miedo"),
              cereb=("CEREBELO", "el equilibrio"), hipot=("HIPOTÁLAMO", "el termostato"),
              tronco=("TRONCO ENCEFÁLICO", "el piloto automático"), fin=("LO MÁS LOCO…", ""))

# ---------- cerveau ----------
CEREBRUM = [(-230, -20, 170), (-95, -130, 190), (90, -130, 190), (235, -30, 170),
            (150, 105, 150), (-20, 90, 175), (-205, 95, 130)]


def cerebrum_path(cr):
    for x, y, r in CEREBRUM:
        cr.new_sub_path(); cr.arc(x, y, r, 0, 2 * math.pi)


def glow_circle(cr, x, y, r, col, a):
    if a <= 0.01:
        return
    g = cairo.RadialGradient(x, y, r * 0.15, x, y, r)
    g.add_color_stop_rgba(0, *col[:3], 0.55 * a); g.add_color_stop_rgba(1, *col[:3], 0)
    cr.set_source(g); cr.arc(x, y, r, 0, 2 * math.pi); cr.fill()


def mix(c1, c2, k):
    return tuple(lerp(c1[i], c2[i], k) for i in range(3)) + (1,)


def draw_brain(cr, t, st):
    """st : dict d'états (0..1) pour chaque partie."""
    glow_circle(cr, 0, 0, 560, GOLD, st["energy"])
    xr = st["xray"]  # 0 = opaque, 1 = on voit l'intérieur
    # tronc
    stem_col = mix(PINK_D, PURPLE, st["stem"])
    glow_circle(cr, 105, 270, 200, PURPLE, st["stem"] * (0.8 + 0.2 * math.sin(t * 3)))
    cr.set_source_rgba(*stem_col)
    cr.move_to(70, 150); cr.line_to(140, 150); cr.line_to(130, 340)
    cr.curve_to(128, 370, 82, 370, 80, 340); cr.close_path(); cr.fill()
    # cervelet
    glow_circle(cr, 215, 190, 230, ORANGE, st["cereb"])
    cr.set_source_rgba(*mix(PINK_D, ORANGE, st["cereb"]))
    cr.arc(215, 190, 95, 0, 2 * math.pi); cr.fill()
    cr.set_source_rgba(0, 0, 0, 0.15); cr.set_line_width(7); cr.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(4):
        cr.arc(215, 175 + i * 4, 60 - i * 12, math.radians(200), math.radians(340)); cr.stroke()
    # hémisphère (devient translucide en mode « rayons X »)
    cr.push_group()
    cr.set_source_rgba(*PINK); cerebrum_path(cr); cr.fill()
    for name, sign, col in (("front", -1, BLUE), ("occ", 1, GREEN)):
        p = st[name]
        if p <= 0:
            continue
        cr.save(); cerebrum_path(cr); cr.clip()
        if sign < 0:
            xe = -420 + 380 * p
            cr.move_to(-460, -400); cr.line_to(xe + 40, -400)
            cr.curve_to(xe - 20, -150, xe + 30, 80, xe - 40, 320); cr.line_to(-460, 320)
        else:
            xe = 420 - 250 * p
            cr.move_to(460, -400); cr.line_to(xe - 20, -400)
            cr.curve_to(xe + 30, -150, xe - 20, 60, xe + 30, 320); cr.line_to(460, 320)
        cr.close_path()
        c = mix(col, BLUE_L, st["front_mature"]) if name == "front" else col
        cr.set_source_rgba(*c[:3], 1); cr.fill(); cr.restore()
    cr.save(); cerebrum_path(cr); cr.clip()
    cr.set_source_rgba(1, 1, 1, 0.18); cr.arc(-120, -230, 210, 0, 2 * math.pi); cr.fill(); cr.restore()
    cr.set_source_rgba(0, 0, 0, 0.13); cr.set_line_width(10); cr.set_line_cap(cairo.LINE_CAP_ROUND)
    for pts in [((-300, -60), (-250, -140), (-180, -60), (-120, -150)),
                ((-60, -250), (-20, -170), (40, -260), (90, -180)),
                ((130, -220), (200, -150), (260, -200), (300, -110)),
                ((-260, 80), (-180, 20), (-120, 90), (-40, 30)),
                ((20, -40), (80, -100), (140, -20), (210, -60)),
                ((-10, 150), (60, 90), (120, 170), (200, 120))]:
        cr.move_to(*pts[0]); cr.curve_to(*pts[1], *pts[2], *pts[3]); cr.stroke()
    cr.set_line_width(12); cr.move_to(-30, -315); cr.curve_to(-60, -200, 10, -120, -40, 20); cr.stroke()
    cr.pop_group_to_source(); cr.paint_with_alpha(1 - 0.62 * xr)
    if xr > 0.01:  # contour extérieur propre quand il est translucide
        cr.push_group()
        cr.set_source_rgba(*PINK[:3], 1)
        for x, y, r in CEREBRUM:
            cr.new_sub_path(); cr.arc(x, y, r + 5, 0, 2 * math.pi)
        cr.fill()
        cr.set_operator(cairo.OPERATOR_CLEAR)
        for x, y, r in CEREBRUM:
            cr.new_sub_path(); cr.arc(x, y, r - 4, 0, 2 * math.pi)
        cr.fill()
        cr.set_operator(cairo.OPERATOR_OVER)
        cr.pop_group_to_source(); cr.paint_with_alpha(0.9 * xr)
    # structures profondes
    if st["hipo"] > 0.01:
        s = st["hipo"] * st["hipo_big"]
        cr.save(); cr.translate(70, 60); cr.scale(s, s)
        glow_circle(cr, 0, 0, 170, YELLOW, 0.8)
        cr.set_source_rgba(*YELLOW); cr.set_line_width(34); cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.move_to(-110, -20); cr.curve_to(-60, 60, 40, 70, 80, 0)
        cr.curve_to(110, -50, 60, -90, 30, -50); cr.curve_to(10, -25, 40, 0, 55, -15); cr.stroke()
        cr.restore()
    if st["amig"] > 0.01:
        s = st["amig"]; col = mix(RED, GREY, st["amig_grey"])
        cr.save(); cr.translate(-70, 75); cr.scale(s, s)
        glow_circle(cr, 0, 0, 120, col, st["amig_pulse"])
        cr.set_source_rgba(*col); cr.scale(1.5, 1); cr.arc(0, 0, 26, 0, 2 * math.pi); cr.fill()
        cr.restore()
    if st["hipot"] > 0.01:
        s = st["hipot"]
        cr.save(); cr.translate(35, 125); cr.scale(s, s)
        glow_circle(cr, 0, 0, 130, CYAN, 0.9)
        cr.set_source_rgba(*CYAN); cr.arc(0, 0, 30, 0, 2 * math.pi); cr.fill()
        cr.restore()


def draw_person(cr, alpha):
    cr.set_source_rgba(*SKIN[:3], alpha)
    cr.arc(0, 0, 150, 0, 2 * math.pi); cr.fill()
    cr.move_to(-200, 520); cr.line_to(-200, 380)
    cr.curve_to(-200, 220, 200, 220, 200, 380); cr.line_to(200, 520); cr.close_path(); cr.fill()


# ---------- texte ----------
def text(cr, s, x, y, size, color=WHITE, scale=1.0, alpha=1.0, weight=B, align="c"):
    if scale <= 0.01 or alpha <= 0.01:
        return
    cr.save(); cr.translate(x, y); cr.scale(scale, scale)
    cr.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, weight); cr.set_font_size(size)
    dx = -cr.text_extents(s).x_advance / 2 if align == "c" else 0
    cr.move_to(dx + 4, 6); cr.set_source_rgba(0, 0, 0, 0.35 * alpha); cr.show_text(s)
    cr.move_to(dx, 0); cr.set_source_rgba(*color[:3], alpha); cr.show_text(s)
    cr.restore()


# ---------- icônes ----------
def icon_begin(cr, x, y, s, rot=0.0):
    cr.save(); cr.translate(x, y); cr.rotate(rot); s = max(s, 1e-3); cr.scale(s, s)
    cr.set_line_cap(cairo.LINE_CAP_ROUND); cr.set_line_join(cairo.LINE_JOIN_ROUND)


def disc(cr, col, r=78):
    cr.set_source_rgba(0, 0, 0, 0.25); cr.arc(0, 8, r, 0, 2 * math.pi); cr.fill()
    cr.set_source_rgba(*col); cr.arc(0, 0, r, 0, 2 * math.pi); cr.fill()
    cr.set_source_rgba(1, 1, 1, 1); cr.set_line_width(12)


def badge(cr, x, y, s, col, kind, label="", t=0.0):
    if s <= 0.01:
        return
    icon_begin(cr, x, y, s); disc(cr, col)
    if kind == "check":
        cr.move_to(-32, 2); cr.line_to(-8, 28); cr.line_to(36, -26); cr.stroke()
    elif kind == "list":
        for i in range(3):
            cr.arc(-28, -26 + i * 26, 6, 0, 2 * math.pi); cr.fill()
            cr.move_to(-10, -26 + i * 26); cr.line_to(32, -26 + i * 26); cr.stroke()
    elif kind == "stop":
        cr.arc(0, 0, 36, 0, 2 * math.pi); cr.stroke(); cr.move_to(-25, 25); cr.line_to(25, -25); cr.stroke()
    elif kind == "food":  # bol + cuillère
        cr.move_to(-42, -5); cr.curve_to(-42, 45, 42, 45, 42, -5); cr.close_path(); cr.fill()
        cr.move_to(20, -12); cr.line_to(40, -45); cr.stroke()
        for dx in (-18, 0):
            cr.move_to(dx, -22); cr.curve_to(dx - 6, -32, dx + 6, -40, dx, -50); cr.stroke()
    elif kind == "drop":
        cr.move_to(0, -45); cr.curve_to(30, -5, 40, 15, 0, 40); cr.curve_to(-40, 15, -30, -5, 0, -45); cr.fill()
    elif kind == "thermo":
        cr.set_line_width(14); cr.move_to(0, -42); cr.line_to(0, 14); cr.stroke()
        cr.arc(0, 26, 20, 0, 2 * math.pi); cr.fill()
        for i in range(3):
            cr.set_line_width(6); cr.move_to(14, -30 + i * 14); cr.line_to(24, -30 + i * 14); cr.stroke()
    elif kind == "clock":
        cr.arc(0, 0, 40, 0, 2 * math.pi); cr.stroke()
        a = t * 2.0
        cr.move_to(0, 0); cr.line_to(22 * math.sin(a), -22 * math.cos(a)); cr.stroke()
        cr.move_to(0, 0); cr.line_to(30 * math.sin(a * 12), -30 * math.cos(a * 12)); cr.stroke()
    cr.restore()
    if label:
        text(cr, label, x, y + 125, 40, alpha=clamp(s))


def crown(cr, x, y, s, rot):
    if s <= 0.01:
        return
    icon_begin(cr, x, y, s, rot)
    cr.set_source_rgba(*GOLD)
    cr.move_to(-80, 40); cr.line_to(-90, -40); cr.line_to(-45, 0); cr.line_to(0, -60)
    cr.line_to(45, 0); cr.line_to(90, -40); cr.line_to(80, 40); cr.close_path(); cr.fill()
    cr.set_source_rgba(*GOLD_D); cr.rectangle(-80, 28, 160, 18); cr.fill()
    for px, py in [(-90, -40), (0, -60), (90, -40)]:
        cr.set_source_rgba(*CORAL); cr.arc(px, py, 11, 0, 2 * math.pi); cr.fill()
    cr.restore()


def eye(cr, x, y, s, blink):
    if s <= 0.01:
        return
    icon_begin(cr, x, y, s)
    cr.save(); cr.scale(1, max(0.08, 1 - blink))
    cr.set_source_rgba(1, 1, 1, 1)
    cr.move_to(-80, 0); cr.curve_to(-40, -55, 40, -55, 80, 0); cr.curve_to(40, 55, -40, 55, -80, 0); cr.fill()
    cr.set_source_rgba(*BLUE); cr.arc(10, 0, 30, 0, 2 * math.pi); cr.fill()
    cr.set_source_rgba(0.08, 0.1, 0.2, 1); cr.arc(10, 0, 14, 0, 2 * math.pi); cr.fill()
    cr.set_source_rgba(1, 1, 1, 0.9); cr.arc(18, -8, 6, 0, 2 * math.pi); cr.fill()
    cr.restore(); cr.restore()


def picture(cr, x, y, s):
    if s <= 0.01:
        return
    icon_begin(cr, x, y, s)
    cr.set_source_rgba(0, 0, 0, 0.25); rrect(cr, -95, -65 + 8, 190, 130, 18); cr.fill()
    cr.set_source_rgba(1, 1, 1, 1); rrect(cr, -95, -65, 190, 130, 18); cr.fill()
    cr.set_source_rgba(*rgb("#bfe6ff")); rrect(cr, -80, -50, 160, 100, 10); cr.fill()
    cr.set_source_rgba(*GOLD); cr.arc(40, -20, 16, 0, 2 * math.pi); cr.fill()
    cr.set_source_rgba(*GREEN); cr.move_to(-80, 50); cr.line_to(-30, -10); cr.line_to(10, 30)
    cr.line_to(35, 10); cr.line_to(80, 50); cr.close_path(); cr.fill()
    cr.restore()


def rrect(cr, x, y, w, h, r):
    cr.new_sub_path()
    cr.arc(x + w - r, y + r, r, -math.pi / 2, 0); cr.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    cr.arc(x + r, y + h - r, r, math.pi / 2, math.pi); cr.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    cr.close_path()


def polaroid(cr, x, y, s, rot, col):
    if s <= 0.01:
        return
    icon_begin(cr, x, y, s, rot)
    cr.set_source_rgba(0, 0, 0, 0.25); rrect(cr, -55, -60 + 6, 110, 125, 8); cr.fill()
    cr.set_source_rgba(1, 1, 1, 1); rrect(cr, -55, -60, 110, 125, 8); cr.fill()
    cr.set_source_rgba(*col); rrect(cr, -45, -50, 90, 85, 5); cr.fill()
    cr.set_source_rgba(1, 1, 1, 0.8); cr.arc(0, -15, 16, 0, 2 * math.pi); cr.fill()
    cr.move_to(-30, 35); cr.curve_to(-30, 5, 30, 5, 30, 35); cr.fill()
    cr.restore()


def taxi(cr, x, y, s):
    if s <= 0.01:
        return
    icon_begin(cr, x, y, s)
    cr.set_source_rgba(*GOLD); rrect(cr, -90, -30, 180, 60, 18); cr.fill()
    cr.move_to(-50, -30); cr.line_to(-30, -70); cr.line_to(35, -70); cr.line_to(55, -30); cr.close_path(); cr.fill()
    cr.set_source_rgba(*rgb("#bfe6ff")); cr.move_to(-38, -34); cr.line_to(-24, -62); cr.line_to(0, -62)
    cr.line_to(0, -34); cr.close_path(); cr.fill()
    cr.move_to(8, -34); cr.line_to(8, -62); cr.line_to(30, -62); cr.line_to(44, -34); cr.close_path(); cr.fill()
    cr.set_source_rgba(0.1, 0.1, 0.15, 1)
    for wx in (-50, 50):
        cr.arc(wx, 32, 22, 0, 2 * math.pi); cr.fill()
    cr.set_source_rgba(*GREY); [cr.arc(wx, 32, 9, 0, 2 * math.pi) or cr.fill() for wx in (-50, 50)]
    cr.set_source_rgba(0.1, 0.1, 0.15, 1); rrect(cr, -22, -88, 44, 18, 4); cr.fill()
    cr.restore()


def almond(cr, x, y, s, col=rgb("#c98a52")):
    if s <= 0.01:
        return
    icon_begin(cr, x, y, s, -0.5)
    cr.set_source_rgba(*col)
    cr.move_to(0, -60); cr.curve_to(45, -30, 45, 40, 0, 60); cr.curve_to(-45, 40, -45, -30, 0, -60); cr.fill()
    cr.set_source_rgba(0, 0, 0, 0.15); cr.set_line_width(4)
    for i in range(3):
        cr.move_to(-15 + i * 15, -35); cr.curve_to(-20 + i * 15, 0, -15 + i * 15, 20, -10 + i * 15, 40); cr.stroke()
    cr.restore()


def face(cr, x, y, s, calm=1.0):
    if s <= 0.01:
        return
    icon_begin(cr, x, y, s)
    cr.set_source_rgba(*SKIN); cr.arc(0, 0, 70, 0, 2 * math.pi); cr.fill()
    cr.set_source_rgba(1, 1, 1, 1); cr.set_line_width(8)
    for ex in (-24, 24):  # yeux fermés, sereins
        cr.arc(ex, -10, 12, math.radians(200), math.radians(340)); cr.stroke()
    cr.arc(0, 15, 26, math.radians(20), math.radians(160)); cr.stroke()
    cr.restore()


def feather(cr, x, y, s, rot):
    if s <= 0.01:
        return
    icon_begin(cr, x, y, s, rot)
    cr.set_source_rgba(*rgb("#e9ecff"))
    cr.move_to(0, -110); cr.curve_to(55, -60, 45, 40, 0, 90); cr.curve_to(-45, 40, -55, -60, 0, -110); cr.fill()
    cr.set_source_rgba(*GREY); cr.set_line_width(6)
    cr.move_to(0, -100); cr.line_to(0, 130); cr.stroke()
    for i in range(5):
        yy = -70 + i * 30
        cr.move_to(0, yy + 10); cr.line_to(-28, yy - 8); cr.stroke(); cr.move_to(0, yy + 10); cr.line_to(28, yy - 8); cr.stroke()
    cr.restore()


def bubble(cr, x, y, s, txt):
    if s <= 0.01:
        return
    icon_begin(cr, x, y, s)
    cr.set_source_rgba(1, 1, 1, 1); rrect(cr, -170, -55, 340, 110, 40); cr.fill()
    cr.arc(-120, 80, 16, 0, 2 * math.pi); cr.fill(); cr.arc(-150, 110, 9, 0, 2 * math.pi); cr.fill()
    cr.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, B); cr.set_font_size(46)
    cr.set_source_rgba(*rgb("#2b1c52")); w = cr.text_extents(txt).x_advance
    cr.move_to(-w / 2, 16); cr.show_text(txt)
    cr.restore()


def lungs(cr, x, y, s, breath):
    if s <= 0.01:
        return
    icon_begin(cr, x, y, s)
    cr.set_source_rgba(*CORAL)
    for side in (-1, 1):
        cr.save(); cr.translate(side * 45, 20); cr.scale(1 + 0.1 * breath, 1 + 0.08 * breath)
        cr.move_to(0, -70); cr.curve_to(side * 60, -60, side * 70, 40, side * 40, 70)
        cr.curve_to(side * 10, 80, 0, 40, 0, -70); cr.fill(); cr.restore()
    cr.set_line_width(14); cr.move_to(0, -90); cr.line_to(0, -20); cr.stroke()
    cr.restore()


def heart(cr, x, y, s, beat):
    if s <= 0.01:
        return
    icon_begin(cr, x, y, s * (1 + 0.14 * beat))
    cr.set_source_rgba(*RED)
    cr.move_to(0, 60); cr.curve_to(-90, 0, -60, -70, 0, -30); cr.curve_to(60, -70, 90, 0, 0, 60); cr.fill()
    cr.restore()


def moon(cr, x, y, s):
    if s <= 0.01:
        return
    icon_begin(cr, x, y, s)
    cr.set_source_rgba(*YELLOW); cr.arc(0, 0, 55, 0, 2 * math.pi); cr.fill()
    cr.set_operator(cairo.OPERATOR_SOURCE)
    cr.restore()


def heartbeat(t):
    """Battement : double pulsation douce, ~70 bpm."""
    ph = (t * 1.15) % 1.0
    return math.exp(-((ph - 0.05) / 0.05) ** 2) + 0.6 * math.exp(-((ph - 0.25) / 0.05) ** 2)


# ---------- décor ----------
rnd = random.Random(3)
PARTS = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(2, 7), rnd.uniform(0.2, 1.0), rnd.uniform(0, 99)) for _ in range(70)]

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
    s = 0.85 + 0.15 * spring(t - words[g[0]]["start"], k=260, c=20)
    cr.save(); cr.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, B); cr.set_font_size(70)
    total = cr.text_extents(" ".join(words[i]["text"] for i in g)).x_advance
    cr.translate(W / 2, 1700); cr.scale(s, s)
    x = -total / 2
    for i in g:
        tx = words[i]["text"]
        cr.move_to(x + 4, 6); cr.set_source_rgba(0, 0, 0, 0.4); cr.show_text(tx)
        cr.move_to(x, 0); cr.set_source_rgba(*(GOLD if i == idx else WHITE)); cr.show_text(tx)
        x += cr.text_extents(tx + " ").x_advance
    cr.restore()


# caméra (espace écran) : (temps, dx, dy, échelle)
CAM = [(0, 0, 0, 1.0), (T["occ"], 90, 0, 0.9), (T["hipo"], 0, -10, 1.05), (T["amig"], 30, -10, 1.05),
       (T["cereb"], -70, -40, 0.95), (T["hipot"], 0, -30, 1.0), (T["tronco"], 0, -150, 0.88), (T["fin"], 0, -40, 0.95)]


def camera(t):
    dx, dy, s = CAM[0][1:]
    for (t0, x0, y0, s0), (t1, x1, y1, s1) in zip(CAM, CAM[1:]):
        k = ease((t - t1 + 0.4) / 1.2)
        dx, dy, s = lerp(dx, x1, k), lerp(dy, y1, k), lerp(s, s1, k)
    return dx, dy, s


def frame(t):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    cr = cairo.Context(surf); cr.set_antialias(cairo.ANTIALIAS_BEST)
    g = cairo.LinearGradient(0, 0, 0, H)
    night = ease((t - T["duer"] + 0.3) / 0.8) * (1 - ease((t - T["fin"]) / 0.8))
    g.add_color_stop_rgba(0, *mix(BG1, rgb("#0a0f26"), night)); g.add_color_stop_rgba(1, *mix(BG2, rgb("#120c2a"), night))
    cr.set_source(g); cr.paint()

    zoom_p = ease((t - T["mira"] + 0.3) / 2.2)
    zoom = 1.0 + 2.0 * zoom_p
    cdx, cdy, cs = camera(t)
    for px, py, r, depth, sd in PARTS:
        x = (px + 12 * noise1(t * 0.3, sd) - (zoom - 1) * (px - W / 2) * 0.15 * depth - cdx * 0.3 * depth) % W
        y = (py - t * 8 * depth + 10 * noise1(t * 0.3, sd + 5)) % H
        cr.set_source_rgba(1, 1, 1, 0.08 + 0.12 * depth); cr.arc(x, y, r * (0.8 + 0.4 * depth), 0, 2 * math.pi); cr.fill()

    head = (540, 700)
    bscale = max(0.3 * spring(t - 0.15, k=150, c=12) * (1 + 0.012 * math.sin(t * 1.6)), 1e-3)

    def b2s(x, y):  # coordonnées cerveau → écran
        px, py = 540 + zoom * bscale * x, 860 + zoom * bscale * y
        return 540 + cdx + cs * (px - 540), 860 + cdy + cs * (py - 860)

    # états du cerveau
    st = dict(
        energy=ease((t - T["d20"] + 0.1) / 0.6) * (1 - ease((t - T["front"]) / 0.8)) * (0.85 + 0.15 * math.sin(t * 3)),
        front=ease((t - T["front"]) / 0.9) * (1 - ease((t - T["occ"] + 0.2) / 0.8)),
        front_mature=ease((t - T["a25"] + 2.5) / 3.0),
        occ=ease((t - T["occ"]) / 0.9) * (1 - ease((t - T["hipo"] + 0.2) / 0.8)),
        xray=ease((t - T["hipo"] + 0.2) / 0.9) * (1 - ease((t - T["cereb"] + 0.2) / 0.8)) +
             ease((t - T["hipot"] + 0.2) / 0.9) * (1 - ease((t - T["tronco"] + 0.2) / 0.8)),
        hipo=pop(t, T["hipo"] + 0.3, T["amig"], k=160, c=13),
        hipo_big=1 + 0.35 * ease((t - T["grande"]) / 0.7),
        amig=pop(t, T["amig"] + 0.3, T["cereb"], k=160, c=13),
        amig_pulse=0.4 + 0.6 * (0.5 + 0.5 * math.sin(t * 6)) * (1 - ease((t - T["paciente"]) / 1.0)),
        amig_grey=ease((t - T["nosiente"] + 1.2) / 1.0),
        cereb=ease((t - T["cereb"]) / 0.8) * (1 - ease((t - T["hipot"] + 0.2) / 0.8)) * (0.85 + 0.15 * math.sin(t * 2.5)),
        hipot=pop(t, T["hipot"] + 0.3, T["tronco"], k=160, c=13),
        stem=ease((t - T["tronco"]) / 0.8) * (1 - ease((t - T["fin"] + 0.2) / 0.8)),
    )

    cr.save()
    cr.translate(540 + cdx + 6 * noise1(t * 0.5, 1), 860 + cdy + 8 * noise1(t * 0.5, 2))
    cr.scale(cs, cs); cr.translate(-540, -860)
    cr.translate(540, 860); cr.scale(zoom, zoom); cr.translate(-head[0], -head[1])
    pa = 1 - ease((t - T["mira"]) / 1.2)
    if pa > 0:
        pin = spring(t, k=120, c=13)
        cr.save(); cr.translate(540, 700 + 60 * (1 - pin)); draw_person(cr, pa * clamp(pin)); cr.restore()
    cr.save(); cr.translate(*head); cr.scale(bscale, bscale)
    draw_brain(cr, t, st)
    if t >= T["jefe"]:
        cs_ = spring(t - T["jefe"], k=200, c=11) * (1 - ease((t - T["occ"] + 0.15) / 0.4))
        rot = 0.25 * math.exp(-3 * (t - T["jefe"])) * math.sin(9 * (t - T["jefe"])) - 0.18
        crown(cr, -200, -420 - 300 * (1 - spring(t - T["jefe"], k=200, c=11)), 1.4 * clamp(cs_ * 1.2), rot)
    cr.restore(); cr.restore()

    # ================= accroche =================
    if t < T["mira"] + 0.6:
        out = 1 - ease((t - T["mira"]) / 0.5)
        s2 = spring(t - T["d2"], k=220, c=15)
        text(cr, "2%", 250, 560, 120, scale=s2, alpha=out); text(cr, "del peso", 250, 625, 44, scale=s2, alpha=out)
        s20 = spring(t - T["d20"], k=220, c=15)
        text(cr, "20%", 830, 560, 120, color=GOLD, scale=s20, alpha=out)
        text(cr, "de la energía", 830, 625, 44, color=GOLD, scale=s20, alpha=out)
        b = s20 * out
        if b > 0.01:
            cr.save(); cr.translate(830, 760); cr.scale(b, b)
            cr.set_line_width(8); cr.set_source_rgba(*GOLD); cr.rectangle(-60, -110, 120, 220); cr.stroke()
            cr.rectangle(-25, -128, 50, 18); cr.fill()
            lvl = 0.2 * ease((t - T["d20"]) / 0.9); cr.rectangle(-48, 98 - 196 * lvl, 96, 196 * lvl); cr.fill()
            cr.restore()

    # ================= titres =================
    for name, (ttl, sub) in TITLES.items():
        s0, s1 = window(name)
        if s0 - 0.1 <= t < s1 + 0.5:
            out = 1 - ease((t - s1 + 0.15) / 0.35)
            text(cr, ttl, W / 2, 250, 84 if len(ttl) < 16 else 72, color=SEC_COLOR[name],
                 scale=spring(t - s0, k=200, c=16) * out, alpha=out)
            if sub:
                ts = at(sub.split()[-1], s0)
                text(cr, sub, W / 2, 330, 54, color=GOLD, scale=spring(t - ts, k=200, c=16) * out, alpha=out)

    # ================= lóbulo frontal =================
    for x, t0, col, kind, lab in [(270, T["dec"], AMBER, "check", "decides"), (540, T["plan"], TEAL, "list", "planeas"),
                                  (810, T["ctrl"], CORAL, "stop", "controlas")]:
        badge(cr, x, 1330, pop(t, t0, T["dato"], k=230, c=15), col, kind, lab)
    tl = pop(t, T["dato"] + 0.35, T["occ"])
    if tl > 0.01:
        a = clamp(tl); x0, x1, y = 150, 930, 1380
        cr.set_line_width(10); cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.set_source_rgba(1, 1, 1, 0.3 * a); cr.move_to(x0, y); cr.line_to(x0 + (x1 - x0) * ease(tl), y); cr.stroke()
        for i, age in enumerate([0, 5, 10, 15, 20, 25]):
            text(cr, str(age), x0 + (x1 - x0) * i / 5, y + 70, 36, alpha=a * 0.8, weight=N)
        p = ease((t - (T["dato"] + 0.8)) / (T["a25"] - T["dato"] - 0.6)); mx = x0 + (x1 - x0) * p
        cr.set_source_rgba(*BLUE_L[:3], a); cr.move_to(x0, y); cr.line_to(mx, y); cr.stroke()
        cr.arc(mx, y, 22, 0, 2 * math.pi); cr.fill()
        text(cr, f"{int(round(25 * p))} años", mx, y - 45, 46, color=BLUE_L, alpha=a)
        if t >= T["a25"] - 0.05:
            text(cr, "¡Listo a los 25!", W / 2, 1250, 62, color=GOLD, scale=spring(t - T["a25"], k=260, c=13) * a)

    # ================= lóbulo occipital =================
    occ_on = in_sec(t, "occ")
    if occ_on > 0.01:
        ex, ey = b2s(-470, -10)
        ox, oy = b2s(300, -60)
        se = pop(t, T["ojos"], T["hipo"], k=200, c=14)
        blink = math.exp(-((t - T["ojos"] - 1.2) / 0.08) ** 2)
        eye(cr, ex, ey, 0.9 * se, blink)
        # chemin de la lumière : de l'œil vers l'arrière du cerveau
        p = ease((t - T["pero"]) / 1.6) * (1 - ease((t - T["hipo"] + 0.15) / 0.4))
        if p > 0:
            pts = []
            for i in range(61):
                u = i / 60 * p
                c1, c2 = (ex + 40, ey - 420), (ox - 40, oy - 420)
                x = (1 - u) ** 3 * ex + 3 * (1 - u) ** 2 * u * c1[0] + 3 * (1 - u) * u * u * c2[0] + u ** 3 * ox
                y = (1 - u) ** 3 * (ey - 40) + 3 * (1 - u) ** 2 * u * c1[1] + 3 * (1 - u) * u * u * c2[1] + u ** 3 * oy
                pts.append((x, y))
            cr.set_source_rgba(*YELLOW); cr.set_line_width(10); cr.set_line_cap(cairo.LINE_CAP_ROUND)
            cr.set_dash([2, 26], -t * 60)
            cr.move_to(*pts[0]); [cr.line_to(*q) for q in pts[1:]]; cr.stroke(); cr.set_dash([])
            hx, hy = pts[-1]; cr.arc(hx, hy, 14, 0, 2 * math.pi); cr.fill()
        # rayons de lumière qui entrent dans l'œil
        lr = pop(t, T["luz"] - 0.2, T["hipo"])
        for i in range(3):
            if lr > 0.01:
                yy = ey - 40 + i * 40
                ph = ((t * 1.2 + i * 0.33) % 1.0)
                cr.set_source_rgba(*YELLOW[:3], 0.8 * lr * (1 - ph)); cr.set_line_width(8)
                cr.move_to(ex - 300 + 200 * ph, yy); cr.line_to(ex - 220 + 200 * ph, yy); cr.stroke()
        picture(cr, ox + 40, oy - 280, pop(t, T["imag"], T["hipo"], k=220, c=13))

    # ================= hipocampo =================
    hx, hy = b2s(70, 60)
    for i, (dx, rot, col) in enumerate([(-260, -0.2, BLUE), (0, 0.05, CORAL), (260, 0.2, TEAL)]):
        t0 = T["recu"] + i * 0.25
        k = ease((t - t0) / 1.0)
        s = pop(t, t0, T["taxi"], k=180, c=13)
        polaroid(cr, lerp(hx, 540 + dx, k), lerp(hy, 470 + abs(dx) * 0.1, k), s, rot, col)
    city = pop(t, T["taxi"] - 0.2, T["amig"])
    if city > 0.01:
        a = clamp(city)
        cr.set_line_width(14); cr.set_source_rgba(1, 1, 1, 0.12 * a)
        for i in range(5):  # rues qui se dessinent
            k = ease((t - T["taxi"] - i * 0.15) / 0.8)
            y = 1290 + i * 55
            cr.move_to(80, y); cr.line_to(80 + 920 * k, y); cr.stroke()
        for i in range(6):
            k = ease((t - T["taxi"] - 0.4 - i * 0.12) / 0.8)
            x = 140 + i * 160
            cr.move_to(x, 1270); cr.line_to(x, 1270 + 260 * k); cr.stroke()
        drive = ease((t - T["taxi"]) / (T["calles"] - T["taxi"] + 1.0))
        taxi(cr, lerp(-120, 760, drive), 1390 + 4 * math.sin(t * 14), 0.9 * a)
        text(cr, "Londres", 540, 1245, 52, color=GOLD, scale=spring(t - T["taxi"] - 0.5, k=220, c=15) * a)
    if t >= T["grande"] - 0.1:
        text(cr, "+ grande", hx + 210, hy - 110, 54, color=YELLOW, scale=pop(t, T["grande"], T["amig"], k=240, c=13))

    # ================= amígdala =================
    ax, ay = b2s(-70, 75)
    sa = pop(t, T["alm"], T["paciente"], k=220, c=13)
    almond(cr, 200, 1330, sa)
    text(cr, "almendra", 200, 1460, 40, color=rgb("#e8b98a"), scale=sa)
    al = pop(t, T["alarma"], T["paciente"]) * clamp(1 - (t - T["paciente"]) / 0.5 if t > T["paciente"] else 1)
    if al > 0.01:
        for i in range(3):  # ondes d'alarme qui partent de l'amygdale
            ph = ((t - T["alarma"]) * 0.9 + i / 3) % 1.0
            cr.set_source_rgba(*RED[:3], 0.7 * (1 - ph) * al); cr.set_line_width(8)
            cr.new_sub_path(); cr.arc(ax, ay, 40 + 380 * ease(ph), 0, 2 * math.pi); cr.stroke()
        text(cr, "¡PELIGRO!", 640, 1360, 80, color=RED, scale=spring(t - T["alarma"], k=240, c=13) * al)
    fs = pop(t, T["paciente"] + 0.2, T["cereb"])
    if fs > 0.01:
        face(cr, 540, 1350, fs)
        text(cr, "sin miedo", 540, 1490, 52, color=GREY, scale=spring(t - T["nosiente"], k=220, c=14) * clamp(fs))

    # ================= cerebelo =================
    if in_sec(t, "cereb") > 0.01:
        # balance qui oscille puis se stabilise (ressort amorti)
        bal = pop(t, T["equi"], T["neur"] - 0.3)
        if bal > 0.01:
            tt = t - T["equi"]
            ang = 0.35 * math.exp(-1.8 * tt) * math.cos(6 * tt)
            cr.save(); cr.translate(540, 1330); cr.scale(bal, bal)
            cr.set_source_rgba(*ORANGE); cr.move_to(0, 0); cr.line_to(-40, 70); cr.line_to(40, 70); cr.close_path(); cr.fill()
            cr.rotate(ang); cr.set_line_width(16); cr.set_line_cap(cairo.LINE_CAP_ROUND)
            cr.set_source_rgba(1, 1, 1, 1); cr.move_to(-300, 0); cr.line_to(300, 0); cr.stroke()
            for sx in (-260, 260):
                cr.arc(sx, -40, 36, 0, 2 * math.pi); cr.fill()
            cr.restore()
        # comparaison des neurones
        nb = pop(t, T["neur"], T["cosq"] - 0.4)
        if nb > 0.01:
            a = clamp(nb)
            g1 = ease((t - T["neur"]) / 1.4); g2 = ease((t - T["resto"]) / 1.0)
            cr.set_source_rgba(*ORANGE[:3], a); rrect(cr, 150, 1250, 700 * g1, 70, 35); cr.fill()
            cr.set_source_rgba(*PINK[:3], a); rrect(cr, 150, 1380, 700 * 0.25 * g2 + 1, 70, 35); cr.fill()
            text(cr, "cerebelo  ≈ 69 000 millones", 150, 1230, 38, color=ORANGE, alpha=a, align="l")
            text(cr, "resto del cerebro  ≈ 17 000 millones", 150, 1360, 38, color=PINK, alpha=a * clamp(g2 * 3), align="l")
        fe = pop(t, T["cosq"] - 0.5, T["hipot"])
        if fe > 0.01:
            fx, fy = b2s(330, 260)
            feather(cr, fx + 120, fy + 60 + 15 * math.sin(t * 5), fe, 0.5 + 0.35 * math.sin(t * 7))
            bubble(cr, 600, 1330, pop(t, T["yasabe"], T["hipot"], k=220, c=14), "¡Ya lo sé!")

    # ================= hipotálamo =================
    if in_sec(t, "hipot") > 0.01:
        px, py = b2s(35, 125)
        # thermostat : cadran qui tourne et se pose
        th = pop(t, T["termo"], T["hambre"] - 0.2)
        if th > 0.01:
            cr.save(); cr.translate(540, 1330); cr.scale(th, th)
            cr.set_source_rgba(*CYAN); cr.arc(0, 0, 90, 0, 2 * math.pi); cr.fill()
            cr.set_source_rgba(1, 1, 1, 1); cr.arc(0, 0, 66, 0, 2 * math.pi); cr.fill()
            ang = -2.2 + 2.6 * spring(t - T["termo"] - 0.2, k=60, c=7)
            cr.set_source_rgba(*rgb("#2b1c52")); cr.set_line_width(12); cr.set_line_cap(cairo.LINE_CAP_ROUND)
            cr.move_to(0, 0); cr.line_to(50 * math.sin(ang), -50 * math.cos(ang)); cr.stroke()
            cr.restore()
        items = [("hambre", AMBER, "food", "hambre"), ("sed", BLUE, "drop", "sed"),
                 ("temp", CORAL, "thermo", "temperatura"), ("reloj", TEAL, "clock", "reloj")]
        for i, (key, col, kind, lab) in enumerate(items):
            x = 150 + i * 260
            s = pop(t, T[key], T["tronco"], k=230, c=15)
            if s > 0.01:
                cr.set_source_rgba(*CYAN[:3], 0.35 * clamp(s)); cr.set_line_width(5); cr.set_dash([10, 12], -t * 30)
                cr.move_to(px, py); cr.line_to(x, 1300); cr.stroke(); cr.set_dash([])
            badge(cr, x, 1330, s * 0.85, col, kind, lab, t=t)

    # ================= tronco encefálico =================
    if in_sec(t, "tronco") > 0.01:
        sx_, sy_ = b2s(105, 340)
        for x, t0, kind in [(330, T["resp"], "lungs"), (750, T["coraz"], "heart")]:
            s = pop(t, t0, T["fin"], k=200, c=14)
            if s > 0.01:
                cr.set_source_rgba(*PURPLE[:3], 0.5 * clamp(s)); cr.set_line_width(6); cr.set_dash([10, 12], -t * 30)
                cr.move_to(sx_, sy_); cr.curve_to(sx_, sy_ + 120, x, 1180, x, 1250); cr.stroke(); cr.set_dash([])
                if kind == "lungs":
                    lungs(cr, x, 1370, s, 0.5 + 0.5 * math.sin(t * 2.2))
                    text(cr, "respirar", x, 1520, 42, alpha=clamp(s))
                else:
                    heart(cr, x, 1370, s, heartbeat(t))
                    text(cr, "latir", x, 1520, 42, alpha=clamp(s))
        ms = pop(t, T["duer"] - 0.3, T["fin"])
        if ms > 0.01:
            cr.save(); cr.translate(880, 520); cr.scale(ms, ms)
            cr.set_source_rgba(*YELLOW); cr.arc(0, 0, 60, 0, 2 * math.pi); cr.fill()
            cr.set_source_rgba(*mix(BG1, rgb("#0a0f26"), night)); cr.arc(28, -20, 52, 0, 2 * math.pi); cr.fill()
            cr.restore()
            for i in range(3):
                ph = ((t - T["duer"]) * 0.5 + i / 3) % 1.0
                text(cr, "z", 760 - 70 * ph + 20 * math.sin(t * 2 + i), 620 - 160 * ph, 40 + 30 * ph,
                     color=WHITE, alpha=ms * (1 - ph) * 0.9)

    # ================= final =================
    if t >= T["fin"] - 0.1:
        bx, by = b2s(0, 330)
        ps = pop(t, T["dolor"] - 0.3, T["despiertas"])
        if ps > 0.01:  # éclair de douleur barré
            cr.save(); cr.translate(540, 1360); cr.scale(ps, ps)
            cr.set_source_rgba(*YELLOW); cr.move_to(-10, -90); cr.line_to(-50, 10); cr.line_to(-5, 10)
            cr.line_to(-25, 90); cr.line_to(45, -20); cr.line_to(5, -20); cr.line_to(25, -90); cr.close_path(); cr.fill()
            cr.set_source_rgba(*RED); cr.set_line_width(16); cr.set_line_cap(cairo.LINE_CAP_ROUND)
            cr.arc(0, 0, 110, 0, 2 * math.pi); cr.stroke(); cr.move_to(-78, 78); cr.line_to(78, -78); cr.stroke()
            cr.restore()
            text(cr, "0 dolor", 540, 1540, 56, color=GOLD, scale=clamp(ps))
        aw = pop(t, T["despiertas"] - 0.6, T["sig"] - 0.1)
        if aw > 0.01:
            face_awake(cr, 540, 1360, aw, t)
            bubble(cr, 760, 1220, pop(t, T["despiertas"] + 0.2, T["sig"] - 0.1, k=220, c=14), "¡Hola!")
        if t >= T["sig"] - 0.1:
            s = spring(t - T["sig"], k=200, c=12)
            cr.save(); cr.translate(540, 1380); cr.scale(max(s, 1e-3), max(s, 1e-3))
            cr.set_source_rgba(0, 0, 0, 0.3); rrect(cr, -260, -70 + 10, 520, 140, 70); cr.fill()
            cr.set_source_rgba(*CORAL); rrect(cr, -260, -70, 520, 140, 70); cr.fill()
            cr.restore()
            text(cr, "Sígueme", 540, 1405, 72, scale=s)
            text(cr, "para más", 540, 1520, 48, color=GOLD, scale=spring(t - T["sig"] - 0.3, k=200, c=14))

    captions(cr, t)
    if t > DUR - 0.6:
        cr.set_source_rgba(0, 0, 0, ease((t - DUR + 0.6) / 0.6)); cr.paint()
    buf = np.ndarray((H, W, 4), np.uint8, surf.get_data())
    return buf[..., [2, 1, 0]].copy()


def face_awake(cr, x, y, s, t):
    icon_begin(cr, x, y, s)
    cr.set_source_rgba(*SKIN); cr.arc(0, 0, 80, 0, 2 * math.pi); cr.fill()
    blink = math.exp(-(((t % 3.0) - 1.5) / 0.06) ** 2)
    cr.set_source_rgba(1, 1, 1, 1)
    for ex in (-28, 28):
        cr.save(); cr.translate(ex, -12); cr.scale(1, max(0.1, 1 - blink)); cr.arc(0, 0, 14, 0, 2 * math.pi); cr.fill()
        cr.set_source_rgba(0.1, 0.1, 0.2, 1); cr.arc(2, 2, 7, 0, 2 * math.pi); cr.fill(); cr.set_source_rgba(1, 1, 1, 1)
        cr.restore()
    talk = 0.5 + 0.5 * math.sin(t * 14)
    cr.save(); cr.translate(0, 30); cr.scale(1, 0.3 + 0.7 * talk); cr.arc(0, 0, 16, 0, 2 * math.pi); cr.fill(); cr.restore()
    cr.restore()


def main():
    if len(sys.argv) > 1:
        from PIL import Image
        Image.fromarray(frame(float(sys.argv[1]))).save(HERE / "preview.png")
        return
    out = HERE / "cerebro_flat.mp4"
    p = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
        "-r", str(FPS), "-i", "-", "-i", str(ES / "narracion.mp3"),
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-af", "apad", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)],
        stdin=subprocess.PIPE)
    n = int(DUR * FPS)
    for i in range(n):
        p.stdin.write(frame(i / FPS).tobytes())
        if i % 600 == 0:
            print(f"{i}/{n}", flush=True)
    p.stdin.close(); p.wait()
    print("OK", out)


if __name__ == "__main__":
    main()
