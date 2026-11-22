"""Vídeo vertical « Partes del cerebro » — estilo placas antiguas (Muybridge).

Entradas : narracion.mp3, palabras.json (tiempos por palabra), imagenes/01..09.png
Salida   : cerebro_es.mp4 (1080x1920, 30 fps)
Vista previa de un fotograma : python3 render.py 12.5
"""
import json, math, random, re, subprocess, sys, unicodedata
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = Path(__file__).parent
W, H, FPS = 1080, 1920, 30
SERIF = "/usr/share/fonts/truetype/crosextra/Caladea-Bold.ttf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
CREAM, AMBER = (245, 234, 208), (255, 196, 84)

words = json.loads((HERE / "palabras.json").read_text())
DUR = float(subprocess.check_output([
    "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
    str(HERE / "narracion.mp3")]).decode()) + 0.5


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in s if unicodedata.category(c) != "Mn"))


def at(word, after=0.0):
    for w in words:
        if w["start"] >= after and norm(w["text"]).startswith(norm(word)):
            return w["start"]
    raise SystemExit(f"no encontrado: {word}")


T = {}
T["frontal"] = at("lobulo")
T["occipital"] = at("lobulo", T["frontal"] + 1)
T["hipo"] = at("hipocampo")
T["amig"] = at("amigdala")
T["cereb"] = at("cerebelo")
T["hipot"] = at("hipotalamo")
T["tronco"] = at("tronco")
T["cierre"] = at("loco") - 0.5
T["25"] = at("25")
T["londres"] = at("londres")
T["paciente"] = at("paciente")
T["cosquillas"] = at("cosquillas")
T["hambre"] = at("hambre")
T["sed"] = at("sed", T["hambre"])
T["temp"] = at("temperatura")
T["reloj"] = at("reloj")
T["sigueme"] = at("sigueme")
T["20"] = at("20")

# (inicio, imagen, título, subtítulo, movimiento)
SCENES = [
    (0.0, "01", "TU CEREBRO", "", "in"),
    (T["frontal"], "02", "LÓBULO FRONTAL", "el jefe", "out"),
    (T["occipital"], "03", "LÓBULO OCCIPITAL", "la visión", "pan_r"),
    (T["hipo"], "04", "HIPOCAMPO", "la memoria", "up"),
    (T["amig"], "05", "AMÍGDALA", "el miedo", "in"),
    (T["cereb"], "06", "CEREBELO", "el equilibrio", "out"),
    (T["hipot"], "07", "HIPOTÁLAMO", "el termostato", "pan_l"),
    (T["tronco"], "08", "TRONCO ENCEFÁLICO", "el piloto automático", "down"),
    (T["cierre"], "09", "LO MÁS LOCO…", "", "in"),
]
# golpes de zoom en momentos clave
PUNCHES = [T["20"], T["25"], T["londres"], T["paciente"], T["cosquillas"], at("dolor")]
TRANS = 0.4  # duración de la transición (s)
print({k: round(v, 2) for k, v in T.items()}, "duración", round(DUR, 2))

# ---------- recursos ----------
_fonts = {}
def font(size):
    if size not in _fonts:
        _fonts[size] = ImageFont.truetype(SERIF, size)
    return _fonts[size]

_efont = ImageFont.truetype(EMOJI, 109)
_emo = {}
def emoji(ch, size):
    if (ch, size) not in _emo:
        im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((10, 10), ch, font=_efont, embedded_color=True)
        im = im.crop(im.getbbox())
        _emo[(ch, size)] = im.resize((size, int(size * im.height / im.width)), Image.LANCZOS)
    return _emo[(ch, size)]

ZOOM_BASE = 1.18  # margen para mover la cámara
IMGS = {}
for _, key, *_ in SCENES:
    im = Image.open(HERE / "imagenes" / f"{key}.png").convert("RGB")
    s = max(W / im.width, H / im.height) * ZOOM_BASE
    IMGS[key] = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)

rng = np.random.default_rng(7)
GRAIN = [Image.fromarray((rng.normal(0, 22, (H // 2, W // 2))).clip(-60, 60).astype(np.int16).astype(np.uint8) + 128)
         .resize((W, H)) for _ in range(6)]
yy, xx = np.mgrid[0:H, 0:W]
_v = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
VIGNETTE = np.clip(1.15 - 0.55 * _v ** 2, 0.25, 1.0)
# bandas oscuras para que se lean títulos y subtítulos
_top = np.clip(0.35 + 0.65 * (yy / 420), 0, 1)
_bot = np.clip(1 - 0.62 * (yy - 1080) / 500, 0.38, 1)
VIGNETTE = (VIGNETTE * _top * _bot)[..., None].astype(np.float32)


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def scene_at(t):
    idx = 0
    for i, s in enumerate(SCENES):
        if t >= s[0]:
            idx = i
    return idx


def camera(idx, t):
    """Recorte animado (Ken Burns) de la imagen de la escena idx."""
    start = SCENES[idx][0]
    end = SCENES[idx + 1][0] if idx + 1 < len(SCENES) else DUR
    p = ease((t - start) / max(end - start, 0.1))
    img = IMGS[SCENES[idx][1]]
    mode = SCENES[idx][4]
    z = 1.0
    dx = dy = 0.0
    if mode == "in":
        z = 1.0 + 0.14 * p
    elif mode == "out":
        z = 1.14 - 0.14 * p
    elif mode == "pan_r":
        z, dx = 1.06, -1 + 2 * p
    elif mode == "pan_l":
        z, dx = 1.06, 1 - 2 * p
    elif mode == "up":
        z, dy = 1.06, 1 - 2 * p
    elif mode == "down":
        z, dy = 1.06, -1 + 2 * p
    # golpe de zoom
    for pt in PUNCHES:
        if start <= pt < end and 0 <= t - pt < 0.6:
            k = (t - pt) / 0.6
            z *= 1 + 0.07 * math.sin(math.pi * min(1, k * 2)) * (1 - k)
    cw, ch = W / z, H / z
    mx, my = (img.width - cw) / 2, (img.height - ch) / 2
    cx = img.width / 2 + dx * mx * 0.9
    cy = img.height / 2 + dy * my * 0.9
    # temblor de proyector
    f = int(t * FPS)
    r = random.Random(f // 2)
    cx += r.uniform(-4, 4) / z * (img.width / W)
    cy += r.uniform(-6, 6) / z * (img.height / H)
    box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
    return img.resize((W, H), Image.BILINEAR, box=box)


def film_fx(img, t):
    f = int(t * FPS)
    r = random.Random(f * 31 + 1)
    a = np.asarray(img).astype(np.float32)
    # parpadeo + grano + viñeta
    a *= r.uniform(0.9, 1.04)
    a += (np.asarray(GRAIN[f % len(GRAIN)]).astype(np.float32)[..., None] - 128) * 0.55
    a *= VIGNETTE
    out = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(out)
    # rayas verticales y polvo
    if r.random() < 0.35:
        x = r.randint(60, W - 60)
        d.line([(x, 0), (x + r.randint(-20, 20), H)], fill=(230, 220, 200) if r.random() < .5 else (30, 25, 20), width=r.choice([1, 2, 2, 3]))
    for _ in range(r.randint(0, 5)):
        x, y, s = r.randint(0, W), r.randint(0, H), r.randint(2, 7)
        d.ellipse((x, y, x + s, y + s * r.uniform(.5, 1.5)), fill=(15, 12, 10) if r.random() < .7 else (235, 225, 205))
    return out


def text_c(d, y, txt, size, fill=CREAM, stroke=6):
    f = font(size)
    w = d.textlength(txt, font=f)
    d.text(((W - w) / 2, y), txt, font=f, fill=fill, stroke_width=stroke, stroke_fill=(10, 8, 6))


def spaced(d, y, txt, size, fill=CREAM, spacing=8, stroke=6):
    f = font(size)
    widths = [d.textlength(c, font=f) for c in txt]
    total = sum(widths) + spacing * (len(txt) - 1)
    x = (W - total) / 2
    for c, cw in zip(txt, widths):
        d.text((x, y), c, font=f, fill=fill, stroke_width=stroke, stroke_fill=(10, 8, 6))
        x += cw + spacing


def paste_emoji(img, ch, size, cx, cy, alpha=1.0):
    e = emoji(ch, size)
    if alpha < 1:
        e = e.copy(); e.putalpha(e.getchannel("A").point(lambda v: int(v * alpha)))
    img.paste(e, (int(cx - e.width / 2), int(cy - e.height / 2)), e)


# subtítulos: grupos de 4 palabras máx., cortados tras puntuación
GROUPS, cur = [], []
for i, w in enumerate(words):
    cur.append(i)
    if len(cur) == 4 or (w["text"].endswith((".", ",", ":", "?", "!")) and len(cur) >= 2):
        GROUPS.append(cur); cur = []
if cur:
    GROUPS.append(cur)


def captions(d, t):
    idx = None
    for i, w in enumerate(words):
        if w["start"] <= t + 0.02:
            idx = i
    if idx is None or t > words[idx]["end"] + 0.7:
        return
    g = next(g for g in GROUPS if idx in g)
    f = font(74)
    txts = [words[i]["text"] for i in g]
    total = d.textlength(" ".join(txts), font=f)
    lines = [g] if total < W - 120 else [g[:2], g[2:]]
    y = 1470
    for ln in lines:
        lw = d.textlength(" ".join(words[i]["text"] for i in ln), font=f)
        x = (W - lw) / 2
        for i in ln:
            tx = words[i]["text"]
            d.text((x, y), tx, font=f, fill=AMBER if i == idx else CREAM, stroke_width=7, stroke_fill=(10, 8, 6))
            x += d.textlength(tx + " ", font=f)
        y += 88


def overlays(img, d, idx, t):
    key = SCENES[idx][1]
    local = t - SCENES[idx][0]
    title, sub = SCENES[idx][2], SCENES[idx][3]
    # título tipo intertítulo de cine mudo, aparece con escala
    p = ease(local / 0.35)
    if p > 0:
        spaced(d, 150 - int(30 * (1 - p)), title, int(84 * (0.85 + 0.15 * p)))
        if sub:
            text_c(d, 255, f"— {sub} —", 64, fill=AMBER)
    if key == "01" and t > 1.3:
        text_c(d, 1150, "2% del peso", 84)
        if t > T["20"] - 0.2:
            text_c(d, 1250, "20% de la energía", 84, fill=AMBER)
            paste_emoji(img, "⚡", 90, W / 2, 1400)
    elif key == "02" and t > T["25"] - 0.2:
        text_c(d, 1200, "Madura a los 25 años", 76, fill=AMBER)
    elif key == "04" and t > T["londres"] - 0.2:
        paste_emoji(img, "🚕", 100, W / 2 - 300, 1250)
        d.text((W / 2 - 230, 1210), "Londres =", font=font(76), fill=CREAM, stroke_width=6, stroke_fill=(10, 8, 6))
        text_c(d, 1305, "hipocampo más grande", 76, fill=AMBER)
    elif key == "05":
        # almendra que parpadea en rojo
        blink = 0.5 + 0.5 * math.sin(local * 9)
        glow = Image.new("RGB", (W, H), (200, 20, 20))
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).ellipse((W / 2 - 90, 1170, W / 2 + 90, 1290), fill=int(110 * blink))
        img.paste(glow, (0, 0), m.filter(ImageFilter.GaussianBlur(25)))
        text_c(d, 1190, "alarma de peligro", 76, fill=(255, 120, 100))
    elif key == "06" and t > T["cosquillas"] - 1.2:
        text_c(d, 1150, "¿Por qué no te puedes", 70, fill=AMBER)
        text_c(d, 1235, "hacer cosquillas?", 70, fill=AMBER)
        paste_emoji(img, "🤔", 80, W / 2, 1375)
    elif key == "07":
        for i, (ch, tk) in enumerate([("🍔", "hambre"), ("💧", "sed"), ("🌡️", "temp"), ("⏰", "reloj")]):
            k = ease((t - T[tk] + 0.1) / 0.25)
            if k > 0:
                paste_emoji(img, ch, int(120 * (0.5 + 0.5 * k) + 15 * (1 - k)), 165 + i * 250, 1260, k)
    elif key == "09" and t >= T["sigueme"] - 0.1:
        k = ease((t - T["sigueme"]) / 0.3)
        text_c(d, 1180, "Sígueme para más", int(96 * (0.7 + 0.3 * k)), fill=AMBER, stroke=8)


def transition(t):
    """Fogonazo + deslizamiento vertical de la película entre escenas."""
    for s in SCENES[1:]:
        dt = t - s[0]
        if -TRANS / 2 <= dt < TRANS / 2:
            k = 1 - abs(dt) / (TRANS / 2)
            return k, dt
    return 0.0, 0.0


def frame(t):
    idx = scene_at(t)
    img = camera(idx, t)
    k, dt = transition(t)
    if k > 0:
        # la película "salta": la imagen se desliza verticalmente con un fotograma negro
        shift = int((dt / (TRANS / 2)) * H * 0.18)
        canvas = Image.new("RGB", (W, H), (8, 6, 4))
        canvas.paste(img, (0, shift))
        img = Image.blend(canvas, Image.new("RGB", (W, H), (255, 244, 220)), 0.55 * k)
    img = film_fx(img, t)
    d = ImageDraw.Draw(img)
    overlays(img, d, idx, t)
    captions(d, t)
    return img


def main():
    if len(sys.argv) > 1:
        frame(float(sys.argv[1])).save(HERE / "preview.png")
        return
    out = HERE / "cerebro_es.mp4"
    n = int(DUR * FPS)
    p = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
        "-r", str(FPS), "-i", "-", "-i", str(HERE / "narracion.mp3"),
        "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-maxrate", "4.5M", "-bufsize", "9M", "-pix_fmt", "yuv420p",
        "-af", "apad", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)],
        stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(frame(i / FPS).tobytes())
        if i % 300 == 0:
            print(f"{i}/{n}", flush=True)
    p.stdin.close(); p.wait()
    print("OK", out)


if __name__ == "__main__":
    main()
