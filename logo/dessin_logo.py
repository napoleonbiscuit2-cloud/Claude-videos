"""Logo « biscuit docteur » dessiné entièrement en code (sans IA).

3 couleurs seulement : brun biscuit, blanc glaçage/blouse, turquoise.
Formes simples, puis une très légère déformation lisse pour un rendu
« fait à la main » (pas de contours parfaits de logiciel).
Sorties : logo_main.png (1024, fond rond, coins transparents) + tailles 800 / 512.
"""
import math
from pathlib import Path
import cairo
import numpy as np
import cv2

HERE = Path(__file__).parent
S = 2048  # dessin en grand, réduit à la fin

BROWN = (0xC0 / 255, 0x6E / 255, 0x34 / 255)
WHITE = (0xFB / 255, 0xF6 / 255, 0xEE / 255)
TEAL = (0x2F / 255, 0xA4 / 255, 0x9C / 255)


def capsule(cr, x0, y0, x1, y1, w):
    cr.set_line_width(w); cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.move_to(x0, y0); cr.line_to(x1, y1); cr.stroke()


def wave(cr, x0, y0, x1, y1, amp, n, w):
    """Zigzag de glaçage arrondi, perpendiculaire au segment."""
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy); nx, ny = -dy / L, dx / L
    cr.set_line_width(w); cr.set_line_cap(cairo.LINE_CAP_ROUND); cr.set_line_join(cairo.LINE_JOIN_ROUND)
    for i in range(0, 61):
        u = i / 60
        o = amp * math.sin(u * n * 2 * math.pi)
        x, y = x0 + dx * u + nx * o, y0 + dy * u + ny * o
        cr.line_to(x, y) if i else cr.move_to(x, y)
    cr.stroke()


def draw(cr):
    """Proportions et pose relevées sur le logo ElevenLabs (logo_1.png), utilisé comme croquis."""
    cr.set_source_rgb(*TEAL); cr.arc(0, 0, 1000, 0, 2 * math.pi); cr.fill()

    # ---- biscuit (brun) ----
    cr.set_source_rgb(*BROWN)
    cr.save(); cr.translate(0, -470); cr.scale(1.0, 0.93); cr.arc(0, 0, 345, 0, 2 * math.pi); cr.restore(); cr.fill()  # grosse tête
    cr.move_to(-300, -170); cr.curve_to(-340, 60, -330, 300, -260, 420)                     # corps
    cr.line_to(260, 420); cr.curve_to(330, 300, 340, 60, 300, -170); cr.close_path(); cr.fill()
    capsule(cr, -280, -150, -560, -360, 210)                                                 # bras levé
    cr.save(); cr.translate(-650, -500); cr.rotate(-0.25)                                     # main qui salue (moufle droite)
    cr.scale(0.9, 1.2); cr.arc(0, 0, 120, 0, 2 * math.pi); cr.restore(); cr.fill()
    capsule(cr, -570, -450, -520, -540, 90)                                                  # pouce vers l'intérieur
    capsule(cr, 280, -120, 540, -60, 210)                                                     # bras droit
    cr.arc(610, -70, 120, 0, 2 * math.pi); cr.fill()                                          # poing
    capsule(cr, 625, -150, 640, -290, 95)                                                    # pouce levé
    capsule(cr, -170, 380, -270, 690, 280)                                                    # jambes
    capsule(cr, 170, 380, 270, 690, 280)

    # ---- blouse (blanc) ----
    cr.set_source_rgb(*WHITE)
    capsule(cr, -280, -150, -470, -290, 235)                                                 # manches
    capsule(cr, 280, -120, 470, -80, 235)
    for side in (-1, 1):                                                                      # deux pans ouverts
        cr.move_to(side * 95, -200)
        cr.curve_to(side * 220, -215, side * 330, -180, side * 345, -60)
        cr.line_to(side * 385, 470); cr.curve_to(side * 300, 500, side * 200, 500, side * 120, 470)
        cr.line_to(side * 100, -40); cr.close_path(); cr.fill()

    cr.set_source_rgb(*TEAL); cr.set_line_cap(cairo.LINE_CAP_ROUND); cr.set_line_join(cairo.LINE_JOIN_ROUND)
    for side in (-1, 1):                                                                      # revers
        cr.set_line_width(20)
        cr.move_to(side * 110, -185); cr.line_to(side * 215, -80); cr.line_to(side * 115, -10); cr.stroke()
    cr.set_line_width(18)                                                                     # poches
    for side in (-1, 1):
        x0, x1 = (side * 190, side * 330)
        cr.move_to(x0, 250); cr.line_to(x0, 360); cr.line_to(x1 - side * 8, 360); cr.line_to(x1, 250); cr.stroke()

    # ---- boutons (turquoise) ----
    for y in (-40, 150):
        cr.arc(0, y, 52, 0, 2 * math.pi); cr.fill()

    # ---- stéthoscope ----
    cr.set_line_width(30)
    cr.move_to(-170, -200); cr.curve_to(-250, -80, -250, 60, -190, 160); cr.stroke()         # tube gauche
    cr.arc(-190, 160, 20, 0, 2 * math.pi); cr.fill()
    cr.move_to(-150, 160); cr.curve_to(-130, 220, -80, 240, -70, 190); cr.stroke()
    cr.move_to(170, -200); cr.curve_to(270, -80, 300, 0, 270, 70); cr.stroke()               # tube droit
    cr.arc(270, 100, 62, 0, 2 * math.pi); cr.fill()                                           # pavillon
    cr.set_source_rgb(*WHITE); cr.arc(270, 100, 26, 0, 2 * math.pi); cr.fill()

    # ---- miroir frontal ----
    cr.save()                                                                                  # bandeau, limité à la tête
    cr.save(); cr.translate(0, -470); cr.scale(1.0, 0.93); cr.arc(0, 0, 345, 0, 2 * math.pi); cr.restore(); cr.clip()
    cr.set_source_rgb(*TEAL); cr.set_line_width(75); cr.set_line_cap(cairo.LINE_CAP_BUTT)
    cr.move_to(-400, -540); cr.curve_to(-200, -625, 200, -625, 400, -540); cr.stroke()
    cr.restore()
    cr.set_source_rgb(*TEAL); cr.arc(0, -630, 112, 0, 2 * math.pi); cr.fill()
    cr.set_source_rgb(*WHITE); cr.arc(0, -630, 84, 0, 2 * math.pi); cr.fill()
    cr.set_source_rgb(*TEAL); cr.arc(0, -630, 27, 0, 2 * math.pi); cr.fill()

    # ---- glaçage (blanc) ----
    cr.set_source_rgb(*WHITE)
    cr.arc(-110, -455, 42, 0, 2 * math.pi); cr.fill()                                          # yeux
    cr.arc(110, -455, 42, 0, 2 * math.pi); cr.fill()
    cr.set_line_width(42); cr.set_line_cap(cairo.LINE_CAP_ROUND)                               # sourire
    cr.arc(0, -420, 150, math.radians(30), math.radians(150)); cr.stroke()
    wave(cr, -585, -390, -505, -445, 16, 2, 22)                                                # poignet levé
    wave(cr, 505, -10, 520, -125, 16, 2, 22)                                                   # poignet droit
    wave(cr, -90, 330, 90, 330, 16, 2.5, 22)                                                   # taille
    wave(cr, -390, 720, -170, 760, 18, 3, 24)                                                  # chevilles
    wave(cr, 170, 760, 390, 720, 18, 3, 24)


def main():
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, S, S)
    cr = cairo.Context(surf); cr.set_antialias(cairo.ANTIALIAS_BEST)
    cr.translate(S / 2, S / 2); cr.scale(0.96, 0.96)
    draw(cr)
    img = np.ndarray((S, S, 4), np.uint8, surf.get_data()).copy()

    # légère déformation lisse : les bords ne sont plus parfaitement mathématiques
    rng = np.random.default_rng(12)
    def field(cells, amp):
        f = rng.normal(0, 1, (cells, cells)).astype(np.float32)
        return cv2.resize(f, (S, S), interpolation=cv2.INTER_CUBIC) * amp
    dx = field(9, 4.0) + field(40, 1.2)
    dy = field(9, 4.0) + field(40, 1.2)
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    img = cv2.remap(img, xx + dx, yy + dy, cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))

    # le rond de fond reste net (masque parfait, appliqué après la déformation)
    mask = np.zeros((S, S), np.uint8)
    cv2.circle(mask, (S // 2, S // 2), int(1000 * 0.96), 255, -1, cv2.LINE_AA)
    img[..., 3] = np.minimum(img[..., 3], mask)

    bgra = img  # cairo = BGRA prémultiplié ; fond plein donc sans souci
    for size, name in [(1024, "logo_main.png"), (800, "logo_main_800.png"), (512, "logo_main_512.png")]:
        out = cv2.resize(bgra, (size, size), interpolation=cv2.INTER_AREA)
        cv2.imwrite(str(HERE / name), out)
    print("OK")


if __name__ == "__main__":
    main()
