"""Rendu de la vidéo verticale « Les parties du cerveau » (FR).

Entrées : narration.mp3 + words.json (horodatage mot par mot, ElevenLabs Scribe).
Sortie  : cerveau_fr.mp4 (1080x1920, 30 fps).
"""
import json, math, subprocess, sys, unicodedata, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = Path(__file__).parent
W, H, FPS = 1080, 1920, 30
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

BG_TOP, BG_BOT = (14, 16, 40), (40, 14, 52)
DIM = (120, 96, 140)
YELLOW = (255, 214, 0)

# ---------- mots / timing ----------
words = json.loads((HERE / "words.json").read_text())
words = [w for w in words if w.get("type", "word") == "word" and w["text"].strip()]
DUR = float(subprocess.check_output([
    "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
    str(HERE / "narration.mp3")]).decode()) + 0.6


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in s if unicodedata.category(c) != "Mn"))


def find(seq, after=0.0):
    """Début du premier enchaînement de mots `seq` après `after`."""
    seq = [norm(x) for x in seq.split()]
    n = [norm(w["text"]) for w in words]
    for i in range(len(words) - len(seq) + 1):
        if words[i]["start"] >= after and all(n[i + k].endswith(seq[k]) or n[i + k].startswith(seq[k]) for k in range(len(seq))):
            return words[i]["start"]
    raise SystemExit(f"introuvable: {seq}")


t = {}
t["frontal"] = find("lobe frontal")
t["occipital"] = find("lobe occipital", t["frontal"])
t["hippo"] = find("hippocampe", t["occipital"])
t["amyg"] = find("amygdale", t["hippo"])
t["cerv"] = find("cervelet", t["amyg"])
t["chat"] = find("chatouiller", t["cerv"])
t["hypo"] = find("hypothalamus", t["cerv"])
t["tronc"] = find("tronc cérébral", t["hypo"])
t["fin"] = find("plus fou", t["tronc"])
t["abo"] = find("abonne", t["fin"])
t["londres"] = find("londres", t["hippo"])
t["patiente"] = find("patiente", t["amyg"])
t["25"] = find("25", t["frontal"])
SECTIONS = [
    (0, "hook"), (t["frontal"], "frontal"), (t["occipital"], "occipital"),
    (t["hippo"], "hippo"), (t["amyg"], "amyg"), (t["cerv"], "cerv"),
    (t["hypo"], "hypo"), (t["tronc"], "tronc"), (t["fin"], "fin"),
]
print({k: round(v, 2) for k, v in t.items()}, "durée", round(DUR, 2))


def section_at(time):
    cur, start = SECTIONS[0][1], 0.0
    for s, name in SECTIONS:
        if time >= s - 0.05:
            cur, start = name, s
    return cur, start


# ---------- polices / emojis ----------
_fonts = {}


def font(size):
    if size not in _fonts:
        _fonts[size] = ImageFont.truetype(BOLD, size)
    return _fonts[size]


_emo_font = ImageFont.truetype(EMOJI, 109)
_emo = {}


def emoji(ch, size):
    key = (ch, size)
    if key not in _emo:
        im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((10, 10), ch, font=_emo_font, embedded_color=True)
        im = im.crop(im.getbbox())
        _emo[key] = im.resize((size, int(size * im.height / im.width)), Image.LANCZOS)
    return _emo[key]


def text_center(d, y, txt, size, fill=(255, 255, 255), stroke=8):
    f = font(size)
    w = d.textlength(txt, font=f)
    d.text(((W - w) / 2, y), txt, font=f, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


def wrap(d, txt, size, maxw):
    f, lines, cur = font(size), [], ""
    for wd in txt.split():
        test = (cur + " " + wd).strip()
        if d.textlength(test, font=f) > maxw and cur:
            lines.append(cur)
            cur = wd
        else:
            cur = test
    return lines + [cur]


# ---------- cerveau (vue de profil, front à gauche) ----------
CX, CY = 540, 860
def mask(draw_fn):
    m = Image.new("L", (W, H), 0)
    draw_fn(ImageDraw.Draw(m))
    return m

cerebrum = mask(lambda d: d.ellipse((CX - 390, CY - 290, CX + 390, CY + 260), fill=255))
frontal = Image.composite(cerebrum, Image.new("L", (W, H), 0),
                          mask(lambda d: d.polygon([(0, 0), (500, 0), (430, 1300), (0, 1300)], fill=255)))
occipital = Image.composite(cerebrum, Image.new("L", (W, H), 0),
                            mask(lambda d: d.polygon([(820, 0), (W, 0), (W, 1300), (760, 1300)], fill=255)))
cerebellum = mask(lambda d: d.ellipse((CX + 110, CY + 150, CX + 380, CY + 330), fill=255))
stem = mask(lambda d: d.polygon([(CX + 40, CY + 170), (CX + 130, CY + 170), (CX + 150, CY + 480), (CX + 70, CY + 480)], fill=255))
hippo = mask(lambda d: d.arc((CX - 10, CY - 10, CX + 230, CY + 170), 20, 200, fill=255, width=34))
amyg = mask(lambda d: d.ellipse((CX - 60, CY + 60, CX + 10, CY + 105), fill=255))
hypo = mask(lambda d: d.ellipse((CX - 110, CY - 10, CX - 50, CY + 45), fill=255))

REGIONS = {
    "frontal": (frontal, (80, 170, 255)),
    "occipital": (occipital, (80, 230, 140)),
    "cerv": (cerebellum, (255, 150, 60)),
    "tronc": (stem, (200, 120, 255)),
    "hippo": (hippo, (255, 220, 60)),
    "amyg": (amyg, (255, 40, 60)),
    "hypo": (hypo, (60, 220, 230)),
}


def build_base():
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        k = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(BG_TOP[i] * (1 - k) + BG_BOT[i] * k) for i in range(3)))
    # tronc + cervelet derrière, puis cerveau
    for m, col in [(stem, (150, 110, 160)), (cerebellum, (175, 125, 165)), (cerebrum, (205, 140, 170))]:
        img.paste(col, (0, 0), m)
    # gyri (circonvolutions)
    g = ImageDraw.Draw(img)
    for i, (x, y, r, a0, a1) in enumerate([
        (CX - 250, CY - 150, 70, 180, 360), (CX - 120, CY - 220, 80, 200, 340), (CX + 40, CY - 230, 90, 190, 350),
        (CX + 200, CY - 180, 80, 200, 360), (CX + 300, CY - 60, 70, 240, 420), (CX - 300, CY + 20, 60, 120, 300),
        (CX - 170, CY - 50, 70, 180, 340), (CX + 10, CY - 90, 80, 190, 350), (CX + 180, CY - 40, 60, 200, 380),
        (CX - 230, CY + 150, 60, 200, 360), (CX + 260, CY + 90, 50, 180, 340)]):
        g.arc((x - r, y - r, x + r, y + r), a0, a1, fill=(165, 100, 135), width=9)
    for k in range(5):  # stries du cervelet
        g.arc((CX + 130 + k * 8, CY + 175 + k * 22, CX + 360 - k * 8, CY + 300 - k * 4), 200, 340, fill=(140, 95, 130), width=6)
    # sillon central / scissure latérale
    g.line([(CX - 60, CY - 285), (CX - 20, CY - 120), (CX - 50, CY - 40)], fill=(150, 85, 120), width=10)
    g.line([(CX - 260, CY + 90), (CX - 40, CY + 40), (CX + 160, CY + 60)], fill=(150, 85, 120), width=10)
    # structures profondes en filigrane
    for key in ("hippo", "amyg", "hypo"):
        img.paste((180, 120, 150), (0, 0), REGIONS[key][0])
    return img


BASE = build_base()
GLOWS = {k: m.filter(ImageFilter.GaussianBlur(28)) for k, (m, _) in REGIONS.items()}

LABELS = {
    "hook": ("TON CERVEAU", (255, 255, 255)),
    "frontal": ("LOBE FRONTAL", REGIONS["frontal"][1]),
    "occipital": ("LOBE OCCIPITAL", REGIONS["occipital"][1]),
    "hippo": ("HIPPOCAMPE", REGIONS["hippo"][1]),
    "amyg": ("AMYGDALE", REGIONS["amyg"][1]),
    "cerv": ("CERVELET", REGIONS["cerv"][1]),
    "hypo": ("HYPOTHALAMUS", REGIONS["hypo"][1]),
    "tronc": ("TRONC CÉRÉBRAL", REGIONS["tronc"][1]),
    "fin": ("LE PLUS FOU…", (255, 255, 255)),
}
SUBS = {
    "hook": "", "frontal": "le patron", "occipital": "la vision", "hippo": "la mémoire",
    "amyg": "la peur", "cerv": "l'équilibre", "hypo": "le thermostat",
    "tronc": "le pilote automatique", "fin": "",
}


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


# groupes de sous-titres : 4 mots max, coupés après la ponctuation
GROUPS, cur = [], []
for _i, _w in enumerate(words):
    cur.append(_i)
    if len(cur) == 4 or _w["text"].rstrip().endswith((".", ",", "?", "!", ":", "…")) and len(cur) >= 2:
        GROUPS.append(cur); cur = []
if cur:
    GROUPS.append(cur)


def caption_group(time):
    idx = None
    for i, w in enumerate(words):
        if w["start"] <= time + 0.02:
            idx = i
    if idx is None or time > words[idx]["end"] + 0.8:
        return None, None
    g = next(g for g in GROUPS if idx in g)
    return [words[i] for i in g], idx


def frame(time):
    sec, s0 = section_at(time)
    local = time - s0
    img = BASE.copy()
    d = ImageDraw.Draw(img)

    # zoom/entrée du cerveau au début
    if sec == "hook":
        # tout le cerveau pulse doucement (énergie)
        a = int(90 + 60 * math.sin(time * 5))
        glow = Image.eval(cerebrum, lambda v: v * a // 600)
        img.paste((255, 210, 90), (0, 0), glow)

    if sec in REGIONS:
        m, col = REGIONS[sec]
        speed = 9 if sec == "amyg" else 4
        pulse = 0.55 + 0.45 * math.sin(local * speed) if sec == "amyg" else 0.8 + 0.2 * math.sin(local * speed)
        a = ease(local / 0.4) * pulse
        img.paste(col, (0, 0), Image.eval(GLOWS[sec], lambda v: int(v * a)))
        img.paste(col, (0, 0), Image.eval(m, lambda v: int(v * min(1, a + 0.15))))

    # ---- en-tête ----
    lab, col = LABELS[sec]
    pop = ease(local / 0.35)
    size = int(96 * (0.7 + 0.3 * pop))
    text_center(d, 170, lab, size, fill=col, stroke=10)
    if SUBS[sec]:
        text_center(d, 290, SUBS[sec], 62, fill=(255, 255, 255), stroke=7)

    # ---- visuels par section ----
    if sec == "hook":
        y = 1290
        text_center(d, y, "2 % du poids", 84, fill=(255, 255, 255))
        if time > 1.2:
            text_center(d, y + 105, "→ 20 % de l'énergie", 84, fill=YELLOW)
            e = emoji("⚡", 110)
            img.paste(e, (W // 2 - 55, 380), e)
    elif sec == "frontal":
        if time >= t["25"] - 0.3:
            text_center(d, 1290, "Mature vers 25 ans", 74, fill=YELLOW)
            e = emoji("🎂", 110); img.paste(e, (W // 2 - 55, 1390), e)
    elif sec == "occipital":
        # œil devant + flèche vers la nuque
        e = emoji("👁️", 120)
        img.paste(e, (40, CY - 40), e)
        prog = ease((local - 0.6) / 1.5)
        x0, x1 = 170, 170 + (CX + 330 - 170) * prog
        if prog > 0:
            yarr = CY - 330
            d.line([(x0, yarr + 220), (x0 + 60, yarr), (x1, yarr)], fill=YELLOW, width=14, joint="curve")
            if prog > 0.95:
                d.polygon([(x1 + 30, yarr), (x1 - 15, yarr - 28), (x1 - 15, yarr + 28)], fill=YELLOW)
                d.line([(x1 + 10, yarr), (x1 + 10, CY - 120)], fill=YELLOW, width=14)
                d.polygon([(x1 + 10, CY - 90), (x1 - 18, CY - 135), (x1 + 38, CY - 135)], fill=YELLOW)
        text_center(d, 1290, "On voit avec l'arrière", 72)
        text_center(d, 1380, "de la tête", 72, fill=YELLOW)
    elif sec == "hippo":
        if time >= t["londres"] - 0.3:
            e = emoji("🚕", 110); img.paste(e, (W // 2 - 380, 1290), e)
            d.text((W // 2 - 250, 1310), "Londres =", font=font(70), fill=(255, 255, 255), stroke_width=7, stroke_fill=(0, 0, 0))
            text_center(d, 1420, "hippocampe plus grand", 70, fill=YELLOW)
    elif sec == "amyg":
        e = emoji("🌰", 100); img.paste(e, (W // 2 - 50, 1290), e)
        text_center(d, 1410, "ton alarme de danger", 70, fill=(255, 90, 90))
        if time >= t["patiente"] - 0.2:
            e = emoji("😐", 90); img.paste(e, (W // 2 - 45, 1510), e)
    elif sec == "cerv":
        text_center(d, 1290, "+ de neurones que", 70)
        text_center(d, 1380, "tout le reste réuni", 70, fill=YELLOW)
        if time >= t["chat"] - 1.0:
            for i, ln in enumerate(["Pourquoi tu ne peux pas", "te chatouiller ? 🤔"[:-2]]):
                text_center(d, 385 + i * 78, ln, 60, fill=YELLOW)
            e = emoji("🤔", 70); img.paste(e, (W // 2 + 275, 455), e)
    elif sec == "hypo":
        icons = ["🍔", "💧", "🌡️", "⏰"]
        for i, ch in enumerate(icons):
            appear = ease((local - 1.2 - i * 0.5) / 0.3)
            if appear > 0:
                sz = int(130 * appear)
                e = emoji(ch, max(sz, 2))
                x = 140 + i * 220 + (130 - sz) // 2
                img.paste(e, (x, 1310 + (130 - sz) // 2), e)
    elif sec == "tronc":
        b = 1 + 0.12 * max(0, math.sin(local * 7))
        e = emoji("❤️", int(110 * b)); img.paste(e, (W // 2 - 220 - e.width // 2, 1300 - e.height // 2 + 55), e)
        e = emoji("🫁", 110); img.paste(e, (W // 2 - 55, 1300), e)
        e = emoji("😴", 110); img.paste(e, (W // 2 + 165, 1300), e)
    elif sec == "fin":
        if time < t["abo"] - 0.2:
            e = emoji("🤯", 130); img.paste(e, (W // 2 - 65, 1270), e)
            text_center(d, 1420, "Ton cerveau ne sent", 70)
            text_center(d, 1505, "pas la douleur", 70, fill=YELLOW)
        else:
            pop2 = ease((time - t["abo"]) / 0.3)
            text_center(d, 1330, "Abonne-toi", int(110 * (0.6 + 0.4 * pop2)), fill=YELLOW, stroke=10)
            text_center(d, 1460, "pour en savoir plus", 66)
            e = emoji("🧠", 120); img.paste(e, (W // 2 - 60, 1550), e)

    # ---- sous-titres mot par mot ----
    grp, idx = caption_group(time)
    if grp:
        f = font(66)
        parts = [w["text"].strip() for w in grp]
        lines = [[]]
        for w in grp:
            test = " ".join(x["text"].strip() for x in lines[-1] + [w])
            if d.textlength(test, font=f) > W - 140 and lines[-1]:
                lines.append([])
            lines[-1].append(w)
        y = 1660
        for ln in lines:
            total = d.textlength(" ".join(x["text"].strip() for x in ln), font=f)
            x = (W - total) / 2
            for w in ln:
                txt = w["text"].strip()
                active = words.index(w) == idx
                d.text((x, y), txt, font=f, fill=YELLOW if active else (255, 255, 255),
                       stroke_width=8, stroke_fill=(0, 0, 0))
                x += d.textlength(txt + " ", font=f)
            y += 82

    # barre de progression
    d.rectangle((0, H - 14, int(W * time / DUR), H), fill=YELLOW)
    return img


def main():
    out = HERE / "cerveau_fr.mp4"
    if len(sys.argv) > 1:  # aperçu : python render.py 12.5
        frame(float(sys.argv[1])).save(HERE / "preview.png")
        return
    n = int(DUR * FPS)
    p = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
        "-r", str(FPS), "-i", "-", "-i", str(HERE / "narration.mp3"),
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-af", "apad", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)], stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(frame(i / FPS).tobytes())
        if i % 300 == 0:
            print(f"{i}/{n}", flush=True)
    p.stdin.close()
    p.wait()
    print("OK", out)


if __name__ == "__main__":
    main()
