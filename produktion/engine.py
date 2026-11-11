"""Gemeinsame Zeichen-/Animations-Engine der Krimi-Serie (2D-Ebenen, Kamera, Figuren, Untertitel).

Alles wird prozedural mit Pillow gezeichnet – keine Fremdmedien. Die Figuren-Funktionen hier
sind die verbindliche visuelle Referenz für wiederkehrende Charaktere (siehe serien_bibel.json).
"""
import math, os, random
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops, ImageOps

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
OL = (8, 11, 20)                       # Konturfarbe
YEL = (255, 201, 60)
TEAL = (95, 208, 255)
RED = (214, 34, 44)


@lru_cache(None)
def font(name, size):
    f = {"title": "Anton.ttf", "sub": "Montserrat-ExtraBold.ttf", "mono": "ShareTechMono.ttf"}[name]
    return ImageFont.truetype(os.path.join(HERE, "fonts", f), int(size))


# ---------------------------------------------------------------- Mathe
def clamp(x, a=0.0, b=1.0): return a if x < a else b if x > b else x
def lerp(a, b, t): return a + (b - a) * t
def seg(t, a, b): return clamp((t - a) / (b - a))
def ease(t): t = clamp(t); return t * t * (3 - 2 * t)
def eout(t): t = clamp(t); return 1 - (1 - t) ** 3
def eback(t):
    t = clamp(t); c = 1.9
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2
def mix(c1, c2, t): return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))


# ---------------------------------------------------------------- Bild-Helfer
def vgrad(w, h, stops):
    ys = np.linspace(0, 1, h)
    pos = [p for p, _ in stops]
    arr = np.stack([np.interp(ys, pos, [c[i] for _, c in stops]) for i in range(3)], 1)
    return Image.fromarray(np.repeat(arr[:, None, :], w, 1).astype(np.uint8), "RGB")


def glow(w, h, cx, cy, r, color, power=2.0, strength=1.0, ry=None):
    """Additiver Lichtfleck (RGB auf Schwarz)."""
    ry = ry or r
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((x - cx) / r) ** 2 + ((y - cy) / ry) ** 2)
    a = np.clip(1 - d, 0, 1) ** power * strength
    return Image.fromarray((a[..., None] * np.array(color, np.float32)).clip(0, 255).astype(np.uint8), "RGB")


def add(a, b): return ImageChops.add(a, b)
def dim(img, f): return img.point(lambda v: int(v * f))


def tint_dim(img, fr, fg, fb):
    r, g, b = img.split()
    return Image.merge("RGB", (r.point(lambda v: int(v * fr)), g.point(lambda v: int(v * fg)), b.point(lambda v: int(v * fb))))


def view(layer, cx, cy, zoom, k=1.0, out=(W, H), rs=Image.BILINEAR):
    """Kamera: Ausschnitt um (cx,cy) in Weltkoordinaten; k = Pixel pro Welteinheit der Ebene."""
    bw, bh = out[0] / zoom * k, out[1] / zoom * k
    x0 = clamp(cx * k - bw / 2, 0, max(0, layer.width - bw))
    y0 = clamp(cy * k - bh / 2, 0, max(0, layer.height - bh))
    return layer.resize(out, rs, box=(x0, y0, min(layer.width, x0 + bw), min(layer.height, y0 + bh)))


def over(base, layer, xy=(0, 0), alpha=1.0):
    """RGBA-Ebene auf RGB-Bild legen."""
    m = layer.getchannel("A")
    if alpha < 0.999:
        m = m.point(lambda v: int(v * alpha))
    base.paste(layer, (int(xy[0]), int(xy[1])), m)
    return base


def put(base, spr, cx, cy, alpha=1.0, scale=1.0, rot=0.0):
    """Sprite zentriert platzieren (mit Skalierung/Rotation)."""
    if alpha <= 0.004: return base
    if abs(scale - 1) > 0.004:
        spr = spr.resize((max(1, int(spr.width * scale)), max(1, int(spr.height * scale))), Image.BILINEAR)
    if abs(rot) > 0.01:
        spr = spr.rotate(rot, Image.BICUBIC, expand=True)
    return over(base, spr, (cx - spr.width / 2, cy - spr.height / 2), alpha)


class D:
    """ImageDraw mit Transformation (Skalierung/Versatz) – erlaubt Supersampling und Figuren-Platzierung."""
    def __init__(s, img, sc=1.0, ox=0.0, oy=0.0):
        s.img, s.sc, s.ox, s.oy = img, sc, ox, oy
        s.d = ImageDraw.Draw(img, "RGBA" if img.mode == "RGB" else None)

    def sub(s, ox, oy, sc=1.0): return D(s.img, s.sc * sc, s.ox + ox * s.sc, s.oy + oy * s.sc)
    def P(s, p): return (s.ox + p[0] * s.sc, s.oy + p[1] * s.sc)
    def w(s, v): return max(1, int(round(v * s.sc))) if v else 0

    def poly(s, pts, fill=None, outline=None, width=0):
        s.d.polygon([s.P(p) for p in pts], fill=fill, outline=outline, width=s.w(width))

    def line(s, pts, fill, width=4, cap=True):
        q = [s.P(p) for p in pts]; w = s.w(width)
        s.d.line(q, fill=fill, width=w, joint="curve")
        if cap and w > 3:
            for x, y in (q[0], q[-1]):
                s.d.ellipse((x - w / 2 + .5, y - w / 2 + .5, x + w / 2 - .5, y + w / 2 - .5), fill=fill)

    def ell(s, cx, cy, rx, ry=None, fill=None, outline=None, width=0):
        ry = rx if ry is None else ry
        x, y = s.P((cx, cy))
        s.d.ellipse((x - rx * s.sc, y - ry * s.sc, x + rx * s.sc, y + ry * s.sc), fill=fill, outline=outline, width=s.w(width))

    def rect(s, x0, y0, x1, y1, fill=None, outline=None, width=0, r=0):
        a, b = s.P((x0, y0)), s.P((x1, y1))
        box = (min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]))
        if r: s.d.rounded_rectangle(box, r * s.sc, fill=fill, outline=outline, width=s.w(width))
        else: s.d.rectangle(box, fill=fill, outline=outline, width=s.w(width))

    def arc(s, cx, cy, rx, ry, a0, a1, fill, width=4):
        x, y = s.P((cx, cy))
        s.d.arc((x - rx * s.sc, y - ry * s.sc, x + rx * s.sc, y + ry * s.sc), a0, a1, fill=fill, width=s.w(width))

    def chord(s, cx, cy, rx, ry, a0, a1, fill):
        x, y = s.P((cx, cy))
        s.d.chord((x - rx * s.sc, y - ry * s.sc, x + rx * s.sc, y + ry * s.sc), a0, a1, fill=fill)

    def soft(s, fn):
        """Halbtransparente Formen korrekt überblenden."""
        ov = Image.new("RGBA", s.img.size, (0, 0, 0, 0))
        fn(D(ov, s.sc, s.ox, s.oy))
        if s.img.mode == "RGBA": s.img.alpha_composite(ov)
        else: s.img.paste(ov, (0, 0), ov)

    def text(s, x, y, txt, fnt, fill, anchor="la", stroke=0, sfill=(0, 0, 0)):
        s.d.text(s.P((x, y)), txt, font=fnt, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=sfill)


def layer(w=W, h=H, ss=2, bg=(0, 0, 0, 0)):
    img = Image.new("RGBA", (int(w * ss), int(h * ss)), bg)
    return img, D(img, ss)


def fin(img, w=W, h=H, keep=1.0):
    return img.resize((int(w * keep), int(h * keep)), Image.LANCZOS)


@lru_cache(None)
def text_spr(txt, fname, size, fill, stroke=0, sfill=(0, 0, 0), glowc=None, track=0, pad=30):
    f = font(fname, size)
    if track:
        ws = [f.getlength(c) + track for c in txt]; tw = int(sum(ws))
    else:
        tw = int(f.getlength(txt))
    asc, desc = f.getmetrics()
    img = Image.new("RGBA", (tw + 2 * pad + 2 * stroke, asc + desc + 2 * pad + 2 * stroke), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = pad + stroke
    if track:
        for c, cw in zip(txt, ws):
            d.text((x, pad + stroke), c, font=f, fill=fill, stroke_width=stroke, stroke_fill=sfill); x += cw
    else:
        d.text((x, pad + stroke), txt, font=f, fill=fill, stroke_width=stroke, stroke_fill=sfill)
    if glowc:
        a = img.getchannel("A").filter(ImageFilter.GaussianBlur(pad / 2.5)).point(lambda v: min(255, int(v * 1.6)))
        g = Image.new("RGBA", img.size, glowc + (0,)); g.putalpha(a)
        g.alpha_composite(img); img = g
    return img


def pill(txt, size=50, fg=(10, 14, 24), bg=YEL, fname="title", padx=26, pady=12, border=None, r=14):
    f = font(fname, size)
    tw = int(f.getlength(txt)); asc, desc = f.getmetrics()
    img = Image.new("RGBA", (tw + 2 * padx + 8, asc + desc + 2 * pady + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((4, 4, img.width - 4, img.height - 4), r, fill=bg, outline=border, width=4 if border else 0)
    d.text((4 + padx, 4 + pady), txt, font=f, fill=fg)
    return img


# ---------------------------------------------------------------- Regen / Atmosphäre
_RAIN = {}
def rain(img, t, n=150, seed=1, slant=0.16, col=(170, 205, 255), amin=35, amax=110, speed=1.0, lmin=40, lmax=110, wmax=3):
    key = (n, seed)
    if key not in _RAIN:
        r = random.Random(seed)
        _RAIN[key] = [(r.random(), r.random(), r.random(), r.random()) for _ in range(n)]
    d = ImageDraw.Draw(img, "RGBA")
    for a, b, c, e in _RAIN[key]:
        depth = 0.35 + 0.65 * c
        ln = lerp(lmin, lmax, c)
        v = (900 + 1300 * c) * speed
        y = (b * (H + 300) + t * v) % (H + 300) - 150
        x = (a * (W + 400) - 200) - (y * slant)
        x = x % (W + 200) - 100
        d.line((x, y, x - ln * slant, y + ln), fill=col + (int(lerp(amin, amax, e) * depth),), width=1 if c < .45 else (2 if c < .85 else wmax))
    return img


@lru_cache(None)
def vignette(strength=0.75, w=W, h=H):
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((x - w / 2) / (w * .78)) ** 2 + ((y - h / 2) / (h * .72)) ** 2)
    a = 1 - np.clip(d - 0.35, 0, 1) ** 1.6 * strength * 1.9
    a = np.clip(a, 0.08, 1)
    return Image.fromarray((a * 255).astype(np.uint8), "L").convert("RGB")


def vig(img, strength=0.75): return ImageChops.multiply(img, vignette(strength, img.width, img.height))


@lru_cache(None)
def noise_frames(n=8, w=W // 2, h=H // 2, amp=70):
    rng = np.random.default_rng(7)
    return [Image.fromarray(rng.integers(128 - amp, 128 + amp, (h, w), np.uint8), "L").resize((w * 2, h * 2), Image.NEAREST).convert("RGB") for _ in range(n)]


@lru_cache(None)
def scanlines(w=W, h=H, period=4, dark=0.72):
    a = np.ones((h, w), np.float32)
    a[::period] = dark; a[1::period] = (1 + dark) / 2
    return Image.fromarray((a * 255).astype(np.uint8), "L").convert("RGB")


def cctv_grade(img, t, noise=0.13, bright=1.0):
    """Überwachungskamera-Look: entsättigt/teal, Zeilen, Rauschen, Rollbalken."""
    g = ImageOps.colorize(img.convert("L"), (3, 9, 13), (int(196 * bright), int(232 * bright), int(222 * bright)))
    img = Image.blend(g, img, 0.22)
    w, h = img.size
    if (w, h) == (W, H):
        img = ImageChops.multiply(img, scanlines())
        img = Image.blend(img, noise_frames()[int(t * FPS) % 8], noise)
    else:
        img = ImageChops.multiply(img, scanlines(w, h))
        nz = noise_frames()[int(t * FPS) % 8].crop((0, 0, w, h))
        img = Image.blend(img, nz, noise)
    d = ImageDraw.Draw(img, "RGBA")
    yb = (t * 260) % (h + 300) - 150
    d.rectangle((0, yb, w, yb + 90), fill=(255, 255, 255, 14))
    d.rectangle((0, yb + 90, w, yb + 96), fill=(255, 255, 255, 30))
    return img


def glitch(img, t, amount=1.0, seed=0):
    """Horizontale Zeilenversätze + Rauschen (Übergangseffekt)."""
    r = random.Random(int(t * FPS) * 31 + seed)
    out = img.copy()
    for _ in range(int(10 * amount) + 2):
        y = r.randint(0, H - 40); hh = r.randint(12, 140); dx = int(r.uniform(-160, 160) * amount)
        out.paste(img.crop((0, y, W, min(H, y + hh))), (dx, y))
    out = Image.blend(out, noise_frames()[r.randint(0, 7)], 0.25 * amount)
    rr, g, b = out.split()
    rr = ImageChops.offset(rr, int(10 * amount), 0); b = ImageChops.offset(b, -int(10 * amount), 0)
    return Image.merge("RGB", (rr, g, b))


# ---------------------------------------------------------------- Charaktere (Serien-Referenz)
OUTFITS = {
    # Daniel Weber – Kamera 1 (Haupteingang) und Porträt
    "daniel_jacke": dict(skin=(233, 183, 150), skin2=(198, 143, 116), hair=(75, 46, 26), top=(29, 42, 70), top2=(19, 28, 48),
                         shirt=(138, 147, 166), trousers=(24, 30, 46), shoes=(12, 14, 20), kind="jacke", glasses=True),
    # Daniel Weber – Kamera 2 (Aufzug)
    "daniel_hoodie": dict(skin=(233, 183, 150), skin2=(198, 143, 116), hair=(75, 46, 26), top=(196, 200, 210), top2=(150, 156, 172),
                          shirt=(196, 200, 210), trousers=(44, 58, 92), shoes=(214, 214, 220), kind="hoodie", glasses=True),
    # Kommissarin Lena Hartmann
    "hartmann": dict(skin=(240, 198, 170), skin2=(205, 158, 132), hair=(150, 66, 38), top=(186, 152, 106), top2=(140, 110, 74),
                     shirt=(40, 52, 80), trousers=(22, 26, 40), shoes=(14, 14, 18), kind="mantel", glasses=False, pony=True),
    # Kommissar Jonas Brandt
    "brandt": dict(skin=(214, 162, 122), skin2=(170, 122, 90), hair=(22, 22, 28), top=(60, 66, 80), top2=(40, 44, 56),
                   shirt=(150, 156, 170), trousers=(20, 22, 32), shoes=(10, 10, 14), kind="mantel", glasses=False, beard=True),
}


def draw_figure(d, o, phase=0.0, walk=0.0, pose="stand", look=0.0, lean=0.0):
    """Ganzkörperfigur von vorn. Einheit: Füße bei y=0, Scheitel bei ca. y=-425."""
    o = OUTFITS[o] if isinstance(o, str) else o
    sw = math.sin(phase) * walk
    bob = -abs(math.cos(phase)) * 6 * walk
    for side in (-1, 1):
        s_ = sw * side
        hip = (side * 22 + lean, -205 + bob)
        knee = (side * 25 + lean * .5, -105 + bob * .5 - max(0, s_) * 16)
        foot = (side * 27, -8 - max(0, s_) * 26)
        d.line([hip, knee, foot], OL, 46); d.line([hip, knee, foot], o["trousers"], 36)
        d.ell(foot[0], foot[1] + 3, 27, 13, fill=o["shoes"], outline=OL, width=4)
    top = -335 + bob
    bot = -112 if o["kind"] == "mantel" else (-178 if o["kind"] == "hoodie" else -186)
    x = lean
    if o["kind"] == "hoodie":
        d.ell(x, top + 8, 50, 26, fill=o["top2"], outline=OL, width=5)          # Kapuze im Nacken
    d.rect(x - 58, top, x + 58, bot, fill=o["top"], outline=OL, width=5, r=24)
    d.poly([(x + 16, top + 6), (x + 54, top + 14), (x + 54, bot - 8), (x + 26, bot - 4)], fill=o["top2"])   # Schattenseite
    if o["kind"] == "jacke":
        d.poly([(x - 22, top + 2), (x, top + 44), (x + 22, top + 2)], fill=o["shirt"])
        d.line([(x, top + 44), (x, bot - 4)], OL, 4, cap=False)
        d.line([(x - 22, top + 2), (x - 2, top + 44)], OL, 5); d.line([(x + 22, top + 2), (x + 2, top + 44)], OL, 5)
    elif o["kind"] == "hoodie":
        d.line([(x - 12, top + 20), (x - 14, top + 66)], (240, 240, 245), 4); d.line([(x + 12, top + 20), (x + 14, top + 66)], (240, 240, 245), 4)
        d.poly([(x - 40, bot - 14), (x - 30, bot - 58), (x + 30, bot - 58), (x + 40, bot - 14)], fill=o["top2"], outline=OL, width=4)
    else:
        d.poly([(x - 24, top + 2), (x, top + 70), (x + 24, top + 2)], fill=o["shirt"])
        d.line([(x - 24, top + 2), (x - 2, top + 70)], OL, 5); d.line([(x + 24, top + 2), (x + 2, top + 70)], OL, 5)
        d.line([(x, top + 70), (x, bot - 4)], OL, 4, cap=False)
        d.rect(x - 58, -212 + bob, x + 58, -196 + bob, fill=o["top2"], outline=OL, width=3)     # Gürtel
        for by in (top + 96, top + 150): d.ell(x - 14, by + bob * 0, 5, 5, fill=OL)
    for side in (-1, 1):
        sh = (x + side * 56, top + 24)
        if pose == "pockets":
            pts = [sh, (x + side * 74, top + 92), (x + side * 26, bot - 36)]
        elif pose == "flash" and side == 1:
            pts = [sh, (x + side * 78, top + 78), (x + side * 104, top + 52)]
        else:
            pts = [sh, (x + side * 68, top + 84 - sw * side * 6), (x + side * 70, top + 150 - sw * side * 22)]
        d.line(pts, OL, 36); d.line(pts, o["top"], 26)
        if pose != "pockets":
            d.ell(pts[-1][0], pts[-1][1] + 6, 13, 13, fill=o["skin"], outline=OL, width=4)
        if pose == "flash" and side == 1:
            hx, hy = pts[-1]
            d.poly([(hx - 6, hy - 14), (hx + 34, hy - 26), (hx + 40, hy + 2), (hx, hy + 12)], fill=(30, 32, 40), outline=OL, width=3)
    hy = -378 + bob - look * 5
    d.rect(x - 13, -352 + bob, x + 13, top + 6, fill=o["skin2"])
    for side in (-1, 1): d.ell(x + side * 34, hy + 4, 7, 11, fill=o["skin"], outline=OL, width=3)
    if o.get("pony"):
        d.poly([(x + 22, hy - 24), (x + 52, hy - 8), (x + 56, hy + 44), (x + 40, hy + 62), (x + 30, hy + 20)], fill=o["hair"], outline=OL, width=4)
    d.ell(x, hy, 34, 41, fill=o["skin"], outline=OL, width=5)
    if o.get("beard"):
        d.chord(x, hy, 31, 38, 20, 160, (40, 34, 34))
        d.line([(x - 9, hy + 22), (x + 9, hy + 22)], o["skin2"], 4)
    cap = [(-36, -2), (-38, -24), (-27, -44), (-6, -53), (16, -51), (32, -38), (38, -18), (36, -2), (30, -18), (17, -29), (-8, -31), (-27, -22)]
    d.poly([(x + px, hy + py) for px, py in cap], fill=o["hair"], outline=OL, width=4)
    ey = hy + 2 - look * 6
    for side in (-1, 1): d.ell(x + side * 13, ey, 4, 4, fill=OL)
    if o.get("glasses"):
        for side in (-1, 1):
            d.rect(x + side * 4, ey - 9, x + side * 25, ey + 9, outline=(14, 16, 22), width=4, r=3)
        d.line([(x - 4, ey - 2), (x + 4, ey - 2)], (14, 16, 22), 3, cap=False)
    if not o.get("beard"):
        d.line([(x - 8, hy + 22 - look * 3), (x + 8, hy + 22 - look * 3)], (120, 70, 60), 3)


def draw_daniel_bust(d, outfit="daniel_jacke", blink=0.0, look=(0, 0), shadow=True):
    """Porträt von Daniel Weber. Einheit: Gesichtsmitte (0,0), Kopf ca. 200 breit."""
    o = OUTFITS[outfit]
    hood = o["kind"] == "hoodie"
    if hood:
        d.ell(0, 150, 150, 80, fill=o["top2"], outline=OL, width=8)
    d.poly([(-250, 470), (-236, 250), (-200, 196), (-92, 150), (92, 150), (200, 196), (236, 250), (250, 470)], fill=o["top"], outline=OL, width=8)
    d.poly([(70, 160), (200, 200), (236, 252), (248, 470), (120, 470)], fill=o["top2"])
    d.rect(-40, 84, 40, 180, fill=o["skin2"], outline=OL, width=6)
    if hood:
        d.poly([(-70, 150), (0, 200), (70, 150), (40, 176), (0, 232), (-40, 176)], fill=o["top2"], outline=OL, width=6)
        d.line([(-22, 200), (-28, 330)], (244, 244, 248), 9); d.line([(22, 200), (28, 330)], (244, 244, 248), 9)
    else:
        d.poly([(-56, 150), (0, 236), (56, 150)], fill=o["shirt"], outline=OL, width=6)
        d.poly([(-96, 150), (-54, 146), (-4, 236), (-66, 262)], fill=o["top2"], outline=OL, width=7)
        d.poly([(96, 150), (54, 146), (4, 236), (66, 262)], fill=o["top2"], outline=OL, width=7)
        d.line([(0, 238), (0, 470)], OL, 6, cap=False)
        d.line([(-10, 300), (-10, 470)], (60, 74, 104), 4, cap=False)
    for sx in (-1, 1): d.ell(sx * 102, 8, 17, 28, fill=o["skin"], outline=OL, width=6)
    d.ell(0, 0, 100, 126, fill=o["skin"], outline=OL, width=8)
    if shadow:
        d.soft(lambda q: q.chord(0, 0, 94, 120, -62, 62, (40, 40, 90, 70)))
        d.soft(lambda q: q.chord(0, 0, 94, 120, 38, 142, (120, 60, 50, 40)))
    hair = [(-106, -6), (-112, -66), (-86, -124), (-34, -154), (38, -152), (92, -122), (112, -62), (106, -6), (94, -52), (72, -82),
            (22, -94), (-36, -84), (-80, -64), (-94, -40)]
    d.poly(hair, fill=o["hair"], outline=OL, width=8)
    d.line([(-60, -122), (-10, -138), (44, -128)], (104, 68, 40), 7)
    for sx in (-1, 1):
        d.line([(sx * 74, -44), (sx * 28, -40)], o["hair"], 11)
        if blink > 0.5:
            d.line([(sx * 48 - 16, -8), (sx * 48 + 16, -8)], OL, 6)
        else:
            d.ell(sx * 48, -10, 18, 13, fill=(246, 246, 240), outline=OL, width=4)
            d.ell(sx * 48 + look[0], -10 + look[1], 9, 9, fill=(52, 34, 22))
            d.ell(sx * 48 + look[0] - 3, -13 + look[1], 3, 3, fill=(255, 255, 255))
    d.line([(4, 4), (14, 40), (-4, 46)], o["skin2"], 7)
    d.line([(-26, 80), (0, 83), (24, 78)], (122, 66, 56), 7)
    G = (16, 18, 26)
    d.soft(lambda q: [q.rect(sx * 15, -40, sx * 88, 22, fill=(150, 190, 240, 46), r=14) for sx in (-1, 1)])
    for sx in (-1, 1):
        d.rect(sx * 15, -40, sx * 88, 22, outline=G, width=9, r=14)
        d.line([(sx * 88, -18), (sx * 104, -10)], G, 7)
    d.line([(-15, -14), (15, -14)], G, 8, cap=False)
    d.soft(lambda q: (q.line([(-74, -4), (-52, -30)], (255, 255, 255, 130), 6), q.line([(-58, 2), (-40, -20)], (255, 255, 255, 80), 4)))


def draw_back(d, who="hartmann", rim=(70, 150, 180), fill=(6, 10, 20)):
    """Rückenansicht als Silhouette mit Kantenlicht. Einheit: Kopfmitte (0,0)."""
    def shape(q, col, dy):
        if who == "hartmann":
            q.poly([(-330, 760), (-300, 250), (-210, 170), (-70, 120), (70, 120), (210, 170), (300, 250), (330, 760)], fill=col)
            q.poly([(-110, 150), (-80, 70), (80, 70), (110, 150), (0, 190)], fill=col)                    # Kragen
            q.ell(0, 0 + dy * 0, 104, 124, fill=col)
            q.poly([(-34, 60), (34, 60), (46, 190), (20, 330), (-6, 350), (-38, 200)], fill=col)          # Pferdeschwanz
            q.ell(0, 66, 40, 22, fill=col)
        else:
            q.poly([(-380, 760), (-350, 240), (-240, 150), (-80, 110), (80, 110), (240, 150), (350, 240), (380, 760)], fill=col)
            q.rect(-48, 60, 48, 150, fill=col)
            q.ell(0, 0, 108, 126, fill=col)
            for sx in (-1, 1): q.ell(sx * 108, 14, 18, 30, fill=col)
    shape(d.sub(0, -7), rim, 0)
    shape(d, fill, 0)


# ---------------------------------------------------------------- Untertitel
class Subtitles:
    def __init__(s, chunks, size=66, cy=1420, maxw=940):
        s.chunks, s.f, s.cy, s.maxw, s.size = chunks, font("sub", size), cy, maxw, size
        s.lay = [s._layout(c) for c in chunks]

    def _layout(s, c):
        sp = s.f.getlength(" ")
        lines, cur, cw = [], [], 0
        for i, (wd, _) in enumerate(c[2]):
            ww = s.f.getlength(wd)
            if cur and cw + sp + ww > s.maxw:
                lines.append((cur, cw)); cur, cw = [], 0
            cw = cw + (sp if cur else 0) + ww
            cur.append((i, wd, ww))
        lines.append((cur, cw))
        if len(lines) == 2 and len(lines[1][0]) == 1 and len(lines[0][0]) > 2:      # kein einzelnes Wort in Zeile 2
            cur0 = lines[0][0]; mv = cur0[-1]
            l0 = cur0[:-1]; l1 = [mv] + lines[1][0]
            if sum(x[2] for x in l1) + sp * (len(l1) - 1) <= s.maxw:
                lines = [(l0, sum(x[2] for x in l0) + sp * (len(l0) - 1)), (l1, sum(x[2] for x in l1) + sp * (len(l1) - 1))]
        lh = s.size * 1.22
        out = []
        y = s.cy - lh * len(lines) / 2
        for ws, lw in lines:
            x = W / 2 - lw / 2
            for i, wd, ww in ws:
                out.append((i, wd, x, y)); x += ww + sp
            y += lh
        return out

    def draw(s, img, t):
        for c, lay in zip(s.chunks, s.lay):
            if c[0] - 0.04 <= t < c[1]:
                d = ImageDraw.Draw(img)
                pop = eout(seg(t, c[0] - 0.04, c[0] + 0.1))
                dy = (1 - pop) * 18
                starts = [w[1] for w in c[2]]
                act = max([i for i, st in enumerate(starts) if st <= t + 0.03], default=0)
                for i, wd, x, y in lay:
                    d.text((x, y + dy), wd, font=s.f, fill=(0, 0, 0), stroke_width=10, stroke_fill=(0, 0, 0))
                for i, wd, x, y in lay:
                    d.text((x, y + dy), wd, font=s.f, fill=YEL if i == act else (255, 255, 255), stroke_width=1,
                           stroke_fill=YEL if i == act else (255, 255, 255))
                break
        return img
