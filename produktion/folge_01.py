"""Folge 1 – «Der Mann, der zweimal existierte»: Szenen, Schnittplan und Untertitel."""
import math, random
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from engine import *

# ------------------------------------------------------------------ Schnittplan (Sekunden, an Sprecher-Audio ausgerichtet)
CUTS = [0.0, 4.0, 9.0, 14.0, 17.2, 21.2, 24.8, 32.6, 37.8, 47.3, 51.5, 58.6]
TRANS = [None, ("fade", .6), ("flash", .3), ("fade", .5), ("fade", .35), ("fade", .4), ("glitch", .3), ("glitch", .3),
         ("glitch", .3), ("fade", .4), ("fade", .5), ("flash", .3)]

SUBS = [
    (0.00, 2.30, [("23:47", 0.0), ("Uhr.", 1.32)]),
    (2.70, 3.75, [("Ravensbruck.", 2.86)]),
    (4.10, 5.24, [("In", 4.10), ("dieser", 4.28), ("kleinen", 4.52), ("Stadt", 4.84)]),
    (5.24, 6.98, [("ist", 5.24), ("gestern", 5.48), ("Nacht", 5.90), ("etwas", 6.10), ("passiert,", 6.40)]),
    (7.08, 8.85, [("das", 7.08), ("sich", 7.22), ("niemand", 7.42), ("erklären", 7.78), ("kann.", 8.22)]),
    (9.32, 11.28, [("Der", 9.32), ("29-jährige", 9.40), ("Daniel", 10.46), ("Weber", 10.88)]),
    (11.28, 13.75, [("ist", 11.28), ("spurlos", 11.66), ("aus", 12.26), ("seiner", 12.48), ("Wohnung", 12.72), ("verschwunden.", 12.98)]),
    (14.24, 15.74, [("Als", 14.24), ("die", 14.42), ("Polizei", 14.58), ("eintrifft,", 14.98)]),
    (15.78, 16.95, [("ist", 15.78), ("seine", 15.86), ("Wohnung", 16.14), ("leer.", 16.38)]),
    (17.26, 19.25, [("Die", 17.26), ("Tür", 17.36), ("ist", 17.62), ("von", 17.84), ("innen", 18.02), ("verschlossen,", 18.32)]),
    (19.34, 21.05, [("keine", 19.34), ("Spuren", 19.64), ("eines", 20.06), ("Einbruchs.", 20.30)]),
    (21.56, 22.56, [("Doch", 21.56), ("dann", 21.76), ("entdecken", 22.02)]),
    (22.56, 24.55, [("die", 22.56), ("Ermittler", 22.70), ("etwas", 23.06), ("Unglaubliches.", 23.38)]),
    (25.04, 27.18, [("Auf", 25.04), ("der", 25.24), ("Überwachungskamera", 25.38), ("am", 26.40), ("Haupteingang", 26.52)]),
    (27.18, 28.30, [("sieht", 27.18), ("man", 27.48), ("Daniel,", 27.66)]),
    (28.32, 30.44, [("wie", 28.32), ("er", 28.42), ("um", 28.52), ("genau", 28.64), ("23:47", 28.88), ("Uhr", 30.30)]),
    (30.44, 32.35, [("das", 30.44), ("Gebäude", 31.16), ("verlässt.", 31.60)]),
    (33.04, 34.50, [("Aber", 33.04), ("auf", 33.28), ("einer", 33.44), ("zweiten", 33.62), ("Kamera", 34.02)]),
    (34.50, 35.26, [("steht", 34.50), ("Daniel", 34.84)]),
    (35.26, 37.60, [("zur", 35.26), ("exakt", 35.48), ("gleichen", 36.00), ("Zeit", 36.40), ("im", 36.70), ("Aufzug.", 36.88)]),
    (38.02, 39.20, [("Derselbe", 38.02), ("Mann,", 38.58)]),
    (39.36, 40.85, [("zwei", 39.36), ("verschiedene", 39.60), ("Orte,", 40.10)]),
    (40.98, 42.20, [("dieselbe", 40.98), ("Uhrzeit.", 41.54)]),
    (42.60, 43.75, [("Und", 42.60), ("das", 42.76), ("Merkwürdigste?", 42.88)]),
    (44.00, 45.08, [("Auf", 44.00), ("beiden", 44.14), ("Aufnahmen", 44.48)]),
    (45.08, 47.05, [("trägt", 45.08), ("er", 45.44), ("unterschiedliche", 45.58), ("Kleidung.", 46.36)]),
    (47.86, 49.50, [("Jetzt", 47.86), ("seid", 48.18), ("ihr", 48.50), ("die", 48.80), ("Ermittler.", 48.96)]),
    (49.90, 51.45, [("Was", 49.90), ("sollen", 50.06), ("wir", 50.30), ("zuerst", 50.44), ("untersuchen?", 50.80)]),
    (51.82, 53.50, [("Die", 51.82), ("Aufnahmen", 51.92), ("der", 52.34), ("Überwachungskameras", 52.52)]),
    (53.50, 56.10, [("oder", 53.50), ("Daniels", 54.18), ("geheimnisvolle", 54.84), ("Wohnung?", 55.64)]),
    (56.48, 58.40, [("Schreibt", 56.48), ("eure", 56.84), ("Entscheidung", 57.02), ("in", 57.50), ("die", 57.72), ("Kommentare.", 57.80)]),
    (58.80, 59.96, [("Die", 58.80), ("meistgewählte", 58.92), ("Spur", 59.60)]),
    (59.96, 61.60, [("verfolgen", 59.96), ("wir", 60.48), ("in", 60.58), ("Folge", 60.74), ("2.", 60.90)]),
]


def lamp_post(d, x, base, top, side=1, sc=1.0):
    c = (9, 13, 24)
    d.line([(x, base), (x, top + 40 * sc)], c, 16 * sc)
    d.line([(x - 3 * sc, base), (x - 3 * sc, top + 60 * sc)], (26, 36, 60), 4 * sc)
    d.rect(x - 16 * sc, base - 40 * sc, x + 16 * sc, base, fill=c, r=4)
    d.line([(x, top + 40 * sc), (x + side * 20 * sc, top + 6 * sc), (x + side * 78 * sc, top)], c, 12 * sc)
    hx = x + side * 86 * sc
    d.poly([(hx - 36 * sc, top + 22 * sc), (hx - 22 * sc, top - 10 * sc), (hx + 22 * sc, top - 10 * sc), (hx + 36 * sc, top + 22 * sc)], fill=c)
    d.ell(hx, top + 26 * sc, 26 * sc, 12 * sc, fill=(255, 236, 170))
    return hx, top + 26 * sc


# ================================================================== SZENE 1 – Ravensbruck bei Nacht
class City:
    dur = 4.0

    def __init__(s):
        r = random.Random(3)
        sky = vgrad(W, H, [(0, (3, 6, 18)), (.38, (8, 20, 48)), (.6, (20, 42, 80)), (.72, (30, 56, 94)), (1, (10, 20, 40))])
        d = ImageDraw.Draw(sky)
        for _ in range(110):
            x, y = r.randint(0, W), r.randint(0, 900); b = r.randint(90, 220)
            d.ellipse((x, y, x + r.choice((2, 2, 3, 4)), y + r.choice((2, 2, 3))), fill=(b, b, min(255, b + 30)))
        sky = add(sky, glow(W, H, 790, 400, 420, (50, 80, 140), 2.0))
        d = ImageDraw.Draw(sky)
        d.ellipse((728, 338, 852, 462), fill=(228, 234, 242))
        for cx, cy, cr in ((765, 380, 13), (812, 420, 9), (790, 435, 6), (822, 372, 7)):
            d.ellipse((cx - cr, cy - cr, cx + cr, cy + cr), fill=(200, 208, 222))
        s.sky = sky
        c = Image.new("RGBA", (1900, 1100), (0, 0, 0, 0)); dd = ImageDraw.Draw(c)
        for _ in range(34):
            x, y = r.randint(0, 1900), r.randint(120, 880); rx, ry = r.randint(140, 330), r.randint(36, 86)
            dd.ellipse((x - rx, y - ry, x + rx, y + ry), fill=(12, 22, 46, r.randint(110, 190)))
        s.clouds = c.filter(ImageFilter.GaussianBlur(24))
        # ferne Silhouette mit Kirchturm
        img, d = layer()
        col = (22, 40, 78)
        x = -40
        while x < W + 40:
            w, h = r.randint(70, 150), r.randint(110, 250); base = 1200
            d.rect(x, base - h, x + w, base + 80, fill=col)
            if r.random() < .75:
                d.poly([(x - 8, base - h), (x + w / 2, base - h - r.randint(40, 90)), (x + w + 8, base - h)], fill=col)
            for wy in range(base - h + 24, base - 30, 46):
                for wx in range(x + 14, x + w - 22, 34):
                    if r.random() < .16: d.rect(wx, wy, wx + 12, wy + 18, fill=(255, 214, 130))
            x += w - 4
        d.rect(296, 690, 384, 1220, fill=col); d.poly([(286, 690), (340, 500), (394, 690)], fill=col)
        d.line([(340, 500), (340, 462)], col, 5); d.line([(326, 478), (354, 478)], col, 5)
        d.ell(340, 772, 30, fill=(238, 228, 184), outline=(8, 16, 34), width=4)
        d.line([(340, 772), (340 - .978 * 24, 772 - .208 * 24)], (10, 16, 30), 4)
        d.line([(340, 772), (340 - .113 * 16, 772 - .994 * 16)], (10, 16, 30), 5)
        d.rect(322, 840, 358, 900, fill=(8, 16, 36), r=16)
        s.far = fin(img)
        fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        fa = np.zeros((H, W), np.float32); yy = np.arange(H)
        fa[:] = (np.exp(-((yy - 1170) / 130.0) ** 2) * 110)[:, None]
        fog = Image.merge("RGBA", (Image.new("L", (W, H), 70), Image.new("L", (W, H), 104), Image.new("L", (W, H), 160), Image.fromarray(fa.astype(np.uint8))))
        s.far.alpha_composite(fog)
        # Häuserzeile
        img, d = layer()
        x = -60; i = 0
        while x < W + 60:
            w, h = r.randint(190, 270), r.randint(300, 470); base = 1430
            c0 = r.choice(((9, 17, 36), (11, 20, 42), (8, 15, 32)))
            d.rect(x, base - h, x + w, base + 20, fill=c0, outline=(4, 8, 18), width=4)
            rh = r.randint(70, 130)
            d.poly([(x - 14, base - h), (x + w / 2, base - h - rh), (x + w + 14, base - h)], fill=(6, 11, 24), outline=(4, 8, 18), width=4)
            d.line([(x - 14, base - h), (x + w / 2, base - h - rh)], (34, 56, 98), 4)
            d.rect(x + w * .68, base - h - rh * .8, x + w * .68 + 26, base - h - rh * .2, fill=(6, 11, 24))
            cols = 3 if w > 220 else 2
            for ry in range(base - h + 40, base - 150, 112):
                for ci in range(cols):
                    wx = x + 26 + ci * (w - 52 - 54) / max(1, cols - 1)
                    lit = r.random() < .22
                    d.rect(wx, ry, wx + 54, ry + 70, fill=(255, 206, 112) if lit else (16, 28, 56), outline=(4, 8, 18), width=4)
                    d.line([(wx + 27, ry), (wx + 27, ry + 70)], (4, 8, 18), 3, cap=False); d.line([(wx, ry + 32), (wx + 54, ry + 32)], (4, 8, 18), 3, cap=False)
                    if not lit: d.line([(wx + 8, ry + 26), (wx + 24, ry + 8)], (40, 62, 104), 3)
            d.rect(x + w / 2 - 28, base - 100, x + w / 2 + 28, base, fill=(5, 9, 20), outline=(4, 8, 18), width=4, r=4)
            x += w + r.randint(-6, 14); i += 1
        s.mid = fin(img)
        # Vordergrund: Gehweg, nasse Straße, Laternen
        img, d = layer()
        d.rect(-10, 1425, W + 10, 1512, fill=(15, 24, 44)); d.rect(-10, 1505, W + 10, 1522, fill=(28, 42, 70))
        d.rect(-10, 1522, W + 10, H + 10, fill=(7, 12, 25))
        for px in range(-100, W + 100, 120): d.line([(px, 1425), (px - 30, 1505)], (9, 15, 30), 3, cap=False)
        s.heads = [lamp_post(d, 150, 1500, 850, 1, 1.25), lamp_post(d, 955, 1490, 960, -1, 1.0)]
        fg = fin(img)
        refl = Image.new("RGB", (W, H), (0, 0, 0))
        for (hx, hy), rr in zip(s.heads, (1.0, .8)):
            refl = add(refl, glow(W, H, hx, 1700, 110 * rr, (255, 196, 96), 1.4, .55, ry=220))
        for px, py, pr in ((420, 1640, 150), (760, 1780, 200), (240, 1840, 130)):
            refl = add(refl, glow(W, H, px, py, pr, (40, 70, 120), 1.0, .5, ry=pr * .16))
        s.fg = fg
        g = Image.new("RGB", (W, H), (0, 0, 0))
        for (hx, hy), rr in zip(s.heads, (1.0, .8)):
            g = add(g, glow(W, H, hx, hy, 520 * rr, (255, 190, 90), 2.2, .75))
            g = add(g, glow(W, H, hx, hy, 90 * rr, (255, 240, 200), 1.2, 1.0))
            g = add(g, glow(W, H, hx, hy + 330 * rr, 300 * rr, (255, 180, 80), 1.6, .28, ry=420 * rr))
        s.glow = add(g, refl)
        s.time = text_spr("23:47 UHR", "mono", 170, (255, 240, 200), glowc=(255, 180, 60), pad=50)
        s.town = text_spr("RAVENSBRUCK", "title", 104, (255, 255, 255), stroke=3, sfill=(0, 0, 0), track=14, pad=24)

    def frame(s, t):
        e = ease(t / s.dur); z = lerp(1.04, 1.24, e)
        cy = lerp(930, 1010, e)
        fl = max(0, 1 - abs(t - .22) / .1) + .6 * max(0, 1 - abs(t - .5) / .14)
        sky = s.sky if fl <= 0 else add(s.sky, Image.new("RGB", (W, H), (int(110 * fl), int(130 * fl), int(170 * fl))))
        img = view(sky, 540, cy, 1 + (z - 1) * .15)
        over(img, s.clouds, (-560 + t * 26, -40))
        over(img, view(s.far, 540, cy, 1 + (z - 1) * .45))
        over(img, view(s.mid, 540, cy, 1 + (z - 1) * .75))
        over(img, view(s.fg, 540, cy, z))
        fk = .92 + .08 * math.sin(t * 23) * math.sin(t * 7.1)
        img = add(img, dim(view(s.glow, 540, cy, z), fk))
        rain(img, t, 190, 1)
        img = vig(img, .7)
        n = int(clamp(t / .7) * 9 + .999)
        if n:
            spr = text_spr("23:47 UHR"[:n] if n < 9 else "23:47 UHR", "mono", 170, (255, 240, 200), glowc=(255, 180, 60), pad=50)
            over(img, spr, (540 - s.time.width / 2, 330 - s.time.height / 2))
        a = eout(seg(t, 2.55, 3.0))
        if a > 0:
            put(img, s.town, 540, 520 + (1 - a) * 30, a)
            ImageDraw.Draw(img).rectangle((540 - 230 * a, 598, 540 + 230 * a, 604), fill=YEL)
        return img


# ================================================================== SZENE 2 – Wohnhaus, ein Fenster leuchtet
class Building:
    dur = 5.0
    WIN = (624, 910)

    def __init__(s, city):
        s.sky = city.sky; s.clouds = city.clouds
        r = random.Random(11)
        img, d = layer()
        d.rect(-200, 700, 150, 1700, fill=(7, 13, 28)); d.rect(930, 620, 1300, 1700, fill=(8, 14, 30))
        for wy in range(760, 1560, 150):
            d.rect(20, wy, 100, wy + 90, fill=(12, 22, 44)); d.rect(970, wy - 60, 1050, wy + 30, fill=(12, 22, 44))
        d.rect(170, 440, 910, 1640, fill=(18, 30, 58), outline=(5, 9, 20), width=6)
        d.rect(770, 440, 910, 1640, fill=(13, 23, 46))
        d.rect(150, 400, 930, 446, fill=(28, 44, 78), outline=(5, 9, 20), width=6)
        d.rect(250, 330, 330, 400, fill=(12, 20, 40), outline=(5, 9, 20), width=5)
        d.line([(700, 400), (700, 250)], (8, 13, 26), 6); d.line([(660, 290), (740, 290)], (8, 13, 26), 5); d.line([(672, 320), (728, 320)], (8, 13, 26), 5)
        for row in range(6):
            y = 500 + row * 175
            d.line([(170, y - 26), (910, y - 26)], (11, 20, 40), 4, cap=False)
            for c_ in range(4):
                x = 215 + c_ * 172
                if row == 5:
                    continue
                lit = (row, c_) == (2, 2)
                d.rect(x - 8, y - 8, x + 138, y + 128, fill=(34, 52, 90), outline=(5, 9, 20), width=5)
                if lit:
                    d.rect(x, y, x + 130, y + 120, fill=(255, 208, 116))
                    d.rect(x, y + 60, x + 130, y + 120, fill=(255, 190, 96))
                    d.poly([(x, y), (x + 34, y), (x + 20, y + 120), (x, y + 120)], fill=(226, 140, 62))
                    d.poly([(x + 130, y), (x + 96, y), (x + 110, y + 120), (x + 130, y + 120)], fill=(226, 140, 62))
                    d.rect(x + 52, y + 84, x + 78, y + 120, fill=(150, 84, 40)); d.poly([(x + 44, y + 84), (x + 54, y + 62), (x + 76, y + 62), (x + 86, y + 84)], fill=(170, 96, 44))
                else:
                    d.rect(x, y, x + 130, y + 120, fill=(8, 14, 30))
                    if r.random() < .3:
                        for by in range(y + 8, y + 120, 12): d.line([(x, by), (x + 130, by)], (20, 32, 60), 3, cap=False)
                    else:
                        d.line([(x + 14, y + 60), (x + 60, y + 10)], (30, 48, 86), 5); d.line([(x + 40, y + 76), (x + 78, y + 34)], (22, 38, 70), 4)
                d.line([(x + 65, y), (x + 65, y + 120)], (5, 9, 20) if not lit else (90, 50, 24), 5, cap=False)
                d.line([(x, y + 50), (x + 130, y + 50)], (5, 9, 20) if not lit else (90, 50, 24), 5, cap=False)
                d.rect(x - 14, y + 128, x + 144, y + 140, fill=(44, 64, 104), outline=(5, 9, 20), width=3)
                if c_ in (0, 3) and row % 2 == 1:
                    d.rect(x - 22, y + 96, x + 152, y + 150, outline=(5, 9, 20), width=5)
                    for bx in range(int(x - 22), int(x + 152), 16): d.line([(bx, y + 96), (bx, y + 150)], (5, 9, 20), 3, cap=False)
        d.poly([(400, 1392), (680, 1392), (710, 1424), (370, 1424)], fill=(30, 46, 80), outline=(5, 9, 20), width=5)
        d.rect(440, 1424, 640, 1640, fill=(8, 13, 26), outline=(5, 9, 20), width=6)
        d.rect(456, 1440, 536, 1630, fill=(52, 60, 70)); d.rect(544, 1440, 624, 1630, fill=(52, 60, 70))
        d.rect(215, 1440, 345, 1560, fill=(8, 14, 30), outline=(5, 9, 20), width=5); d.rect(731, 1440, 861, 1560, fill=(8, 14, 30), outline=(5, 9, 20), width=5)
        d.rect(-200, 1640, 1300, 1720, fill=(15, 24, 44)); d.rect(-200, 1716, 1300, 2000, fill=(7, 12, 25))
        d.rect(-200, 1712, 1300, 1726, fill=(28, 42, 70))
        s.b = img            # 2x-Auflösung für den Zoom
        g = glow(W, H, 624, 910, 330, (255, 176, 80), 2.0, .8)
        g = add(g, glow(W, H, 540, 1420, 160, (200, 190, 150), 1.6, .5))
        s.glow = g
        img, d = layer()
        hx, hy = lamp_post(d, 60, 1930, 500, 1, 2.2)
        s.fgl = fin(img)
        s.fgglow = add(glow(W, H, hx, hy, 620, (255, 190, 90), 2.2, .8), glow(W, H, hx, hy, 150, (255, 240, 200), 1.2, 1.0))

    def frame(s, t):
        e = ease(t / s.dur); z = lerp(1.0, 2.5, e)
        cx, cy = lerp(540, s.WIN[0], e), lerp(960, s.WIN[1] + 40, e)
        img = view(s.sky, 540, 700, 1 + (z - 1) * .12)
        over(img, s.clouds, (-700 + (t + 4) * 26, -80))
        over(img, view(s.b, cx, cy, z, k=2))
        fk = .86 + .14 * math.sin(t * 31) * math.sin(t * 5.3)
        if t > 4.2: fk *= .35 + .65 * (int(t * 15) % 2)
        img = add(img, dim(view(s.glow, cx, cy, z), fk))
        zf = 1 + (z - 1) * 2.0
        over(img, view(s.fgl, lerp(540, 760, e), cy, zf))
        img = add(img, view(s.fgglow, lerp(540, 760, e), cy, zf))
        rain(img, t + 4, 190, 1)
        return vig(img, .8)


# ================================================================== SZENE 3 – Porträt Daniel Weber / VERMISST
class Portrait:
    dur = 5.0

    def __init__(s):
        r = random.Random(5)
        bg = vgrad(W, H, [(0, (6, 12, 28)), (.5, (14, 26, 54)), (1, (5, 9, 22))])
        img, d = layer()
        for _ in range(9):
            x, y = r.randint(-60, 980), r.randint(60, 1700); w, h = r.randint(200, 340), r.randint(160, 300)
            a = r.uniform(-.2, .2)
            pts = [(x + px * math.cos(a) - py * math.sin(a), y + px * math.sin(a) + py * math.cos(a)) for px, py in ((0, 0), (w, 0), (w, h), (0, h))]
            d.poly(pts, fill=r.choice(((30, 46, 80), (36, 52, 84), (24, 38, 70))), outline=(8, 14, 30), width=4)
            d.ell(pts[0][0] + w / 2 * math.cos(a), pts[0][1] + 14, 9, fill=(170, 40, 46))
        d.line([(60, 300), (480, 150), (1000, 420)], (150, 30, 40), 5); d.line([(100, 1650), (540, 1500), (1040, 1700)], (150, 30, 40), 5)
        bg.paste(fin(img).filter(ImageFilter.GaussianBlur(5)), (0, 0), fin(img).filter(ImageFilter.GaussianBlur(5)))
        s.bg = add(dim(bg, .8), glow(W, H, 540, 700, 760, (40, 66, 120), 1.6, .8))
        s.cards = [s._card(b) for b in (0, 1)]
        st = Image.new("RGBA", (760, 300), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
        sd.rounded_rectangle((10, 10, 750, 290), 18, outline=RED + (255,), width=16)
        sd.text((380, 150), "VERMISST", font=font("title", 196), fill=RED + (255,), anchor="mm")
        nz = np.random.default_rng(2).random((300, 760)); a = np.asarray(st.getchannel("A")).astype(np.float32)
        a *= np.where(nz < .1, .25, 1) * .93
        st.putalpha(Image.fromarray(a.astype(np.uint8)))
        s.stamp = st

    def _card(s, blink):
        cw, ch = 800, 1040
        img, d = layer(cw, ch)
        d.rect(8, 8, cw - 8, ch - 8, fill=(233, 227, 211), outline=(60, 54, 44), width=5, r=10)
        ph = vgrad(680 * 2, 640 * 2, [(0, (44, 66, 108)), (1, (18, 28, 54))]).convert("RGBA")
        pd = D(ph, 2)
        for i in range(5): pd.line([(0, 110 + i * 110), (680, 110 + i * 110)], (60, 84, 128), 3, cap=False)
        draw_daniel_bust(pd.sub(340, 300, 1.08), "daniel_jacke", blink=blink)
        img.paste(ph, (120, 120))
        d.rect(60, 60, 740, 700, outline=(30, 28, 26), width=6)
        d.text(400, 716, "DANIEL WEBER", font("title", 104 * 2), (24, 26, 34), anchor="ma")
        d.text(400, 866, "29 JAHRE · RAVENSBRUCK", font("mono", 44 * 2), (60, 60, 66), anchor="ma")
        d.text(400, 926, "ZULETZT GESEHEN: 23:47 UHR", font("mono", 44 * 2), (150, 30, 36), anchor="ma")
        d.rect(330, -6, 470, 46, fill=(214, 196, 150), outline=(120, 104, 70), width=3)
        return fin(img, cw, ch).rotate(3, Image.BICUBIC, expand=True)

    def frame(s, t):
        e = t / s.dur
        img = view(s.bg, 540, 900, 1 + .06 * e)
        ent = eback(seg(t, 0.0, .5))
        blink = 1 if (1.5 < t < 1.62 or 3.9 < t < 4.0) else 0
        t0 = 2.5
        k = seg(t, t0, t0 + .14)
        sh = max(0, 1 - (t - t0 - .14) / .35) if t >= t0 + .14 else 0
        rr = random.Random(int(t * FPS))
        dx, dy = rr.uniform(-1, 1) * 16 * sh, rr.uniform(-1, 1) * 16 * sh
        put(img, s.cards[blink], 540 + dx, 740 + (1 - ent) * 1500 + dy, 1, 1.0 + .05 * e)
        if t >= t0:
            put(img, s.stamp, 560 + dx, 905 + dy, seg(t, t0, t0 + .07), lerp(3.4, 1.12, eout(k)), 13)
        if sh > 0:
            img = add(img, Image.new("RGB", (W, H), (int(120 * sh * sh), int(10 * sh), int(14 * sh))))
        return vig(img, .85)


def dark(o, f=.42, tintb=1.25):
    q = dict(OUTFITS[o])
    for k_, v in q.items():
        if isinstance(v, tuple): q[k_] = (int(v[0] * f), int(v[1] * f), min(255, int(v[2] * f * tintb)))
    return q


# ================================================================== SZENE 4a – Ermittler betreten die leere Wohnung
class Apartment:
    dur = 3.2

    def __init__(s):
        img, d = layer()
        d.rect(0, 0, W, H, fill=(12, 19, 36))
        d.poly([(0, 0), (W, 0), (900, 470), (180, 470)], fill=(11, 18, 36))
        d.rect(180, 470, 900, 1180, fill=(24, 38, 70))
        d.poly([(0, 0), (180, 470), (180, 1180), (0, 1500)], fill=(16, 27, 52))
        d.poly([(W, 0), (900, 470), (900, 1180), (W, 1500)], fill=(18, 30, 56))
        d.poly([(0, 1500), (180, 1180), (900, 1180), (W, 1500), (W, H), (0, H)], fill=(34, 40, 58))
        for i in range(-14, 15):
            xb = 540 + i * 52
            d.line([(xb, 1180), (540 + (xb - 540) * 3.4, H)], (22, 27, 42), 3, cap=False)
        for a, b in (((180, 470), (180, 1180)), ((900, 470), (900, 1180)), ((180, 470), (900, 470))):
            d.line([a, b], (8, 13, 26), 5, cap=False)
        d.line([(0, 1500), (180, 1180), (900, 1180), (W, 1500)], (8, 13, 26), 8)
        d.line([(0, 1470), (180, 1160), (900, 1160), (W, 1470)], (40, 58, 96), 4)
        # Fenster
        d.rect(590, 590, 830, 940, fill=(56, 78, 120), outline=(8, 13, 26), width=6)
        d.rect(606, 606, 814, 924, fill=(26, 50, 96))
        d.poly([(606, 924), (606, 840), (650, 840), (650, 800), (700, 800), (700, 860), (760, 860), (760, 820), (814, 820), (814, 924)], fill=(10, 20, 44))
        d.ell(672, 700, 20, fill=(214, 222, 236))
        d.line([(710, 606), (710, 924)], (56, 78, 120), 8, cap=False); d.line([(606, 760), (814, 760)], (56, 78, 120), 8, cap=False)
        d.poly([(560, 570), (612, 570), (598, 960), (560, 960)], fill=(40, 56, 92), outline=(8, 13, 26), width=4)
        d.poly([(860, 570), (808, 570), (822, 960), (860, 960)], fill=(40, 56, 92), outline=(8, 13, 26), width=4)
        d.line([(540, 566), (880, 566)], (8, 13, 26), 8)
        d.soft(lambda q: q.poly([(590, 1200), (840, 1200), (1010, 1640), (500, 1640)], fill=(70, 110, 190, 46)))
        # Möbel
        d.rect(486, 700, 548, 790, fill=(40, 56, 92), outline=(8, 13, 26), width=5); d.rect(496, 710, 538, 780, fill=(70, 90, 130))
        d.line([(540, 0), (540, 330)], (8, 13, 26), 5); d.poly([(486, 400), (512, 330), (568, 330), (594, 400)], fill=(30, 44, 76), outline=(8, 13, 26), width=5)
        d.ell(540, 1330, 250, 56, fill=(44, 34, 60), outline=(8, 13, 26), width=5); d.ell(540, 1330, 200, 40, outline=(70, 54, 90), width=4)
        d.poly([(700, 1130), (980, 1130), (1040, 1240), (690, 1240)], fill=(58, 44, 40), outline=(8, 13, 26), width=6)
        d.rect(690, 1240, 1040, 1262, fill=(40, 30, 28), outline=(8, 13, 26), width=4)
        for lx in (712, 1010): d.rect(lx, 1262, lx + 18, 1450, fill=(34, 26, 24), outline=(8, 13, 26), width=3)
        d.poly([(790, 1150), (900, 1150), (916, 1196), (780, 1196)], fill=(70, 76, 90), outline=(8, 13, 26), width=4)
        d.rect(796, 1070, 896, 1150, fill=(18, 22, 32), outline=(8, 13, 26), width=5, r=4)
        d.rect(940, 1100, 962, 1140, fill=(200, 200, 205), outline=(8, 13, 26), width=3)
        d.rect(560, 1290, 660, 1420, fill=(48, 38, 36), outline=(8, 13, 26), width=5, r=6)
        d.rect(560, 1180, 660, 1300, fill=(56, 44, 42), outline=(8, 13, 26), width=5, r=10)
        for lx in (566, 646): d.line([(lx, 1420), (lx, 1500)], (8, 13, 26), 8)
        # Türrahmen
        d.rect(232, 632, 478, 1180, fill=(44, 62, 100), outline=(8, 13, 26), width=6)
        s.room = fin(img).convert("RGB")
        s.dimroom = tint_dim(s.room, .42, .48, .68)
        img, d = layer()
        d.poly([(-40, 1420), (60, 1330), (330, 1330), (400, 1440), (420, 1960), (-40, 1960)], fill=(5, 8, 18))
        d.poly([(-40, 1200), (40, 1180), (110, 1330), (-40, 1380)], fill=(5, 8, 18))
        d.line([(60, 1330), (330, 1330), (400, 1440)], (30, 46, 80), 5)
        s.fg = fin(img)

    def frame(s, t):
        o = ease(seg(t, .35, 1.25))
        th = o * 1.35
        xe = 248 + 214 * math.cos(th)
        e = ease(seg(t, 1.0, 2.9))
        hs = lerp(.99, 1.2, e); hx, hy = lerp(322, 372, e), lerp(1180, 1300, e)
        bs = lerp(1.07, 1.26, e); bx, by = lerp(408, 500, e), lerp(1178, 1262, e)
        hand = (bx + 104 * bs, by - 283 * bs)
        # Lichtmaske (Taschenlampe)
        m = Image.new("L", (270, 480), 0); md = ImageDraw.Draw(m)
        fk = seg(t, 1.15, 1.5)
        if fk > 0:
            tx = lerp(430, 880, ease(seg(t, 1.3, 3.2))) + 30 * math.sin(t * 2.3); ty = 880 + 150 * math.sin(t * 1.5 + .6)
            vx, vy = tx - hand[0], ty - hand[1]; ln = math.hypot(vx, vy) or 1; nx, ny = -vy / ln * 170, vx / ln * 170
            c = int(255 * fk)
            md.polygon([(hand[0] / 4, hand[1] / 4), ((tx + nx) / 4, (ty + ny) / 4), ((tx - nx) / 4, (ty - ny) / 4)], fill=int(c * .55))
            md.ellipse(((tx - 210) / 4, (ty - 190) / 4, (tx + 210) / 4, (ty + 190) / 4), fill=c)
        w = Image.new("L", (270, 480), 0); wd = ImageDraw.Draw(w)
        if o > 0.02:
            wd.polygon([(xe / 4, 295), (462 / 4, 295), ((462 + 330 * o) / 4, 450), ((xe + 60) / 4, 450)], fill=int(200 * o))
        m = m.filter(ImageFilter.GaussianBlur(7)).resize((W, H), Image.BILINEAR)
        w = w.filter(ImageFilter.GaussianBlur(9)).resize((W, H), Image.BILINEAR)
        img = Image.composite(s.room, s.dimroom, ImageChops.lighter(m, w.point(lambda v: int(v * .5))))
        img = add(img, Image.merge("RGB", (m.point(lambda v: int(v * .16)), m.point(lambda v: int(v * .17)), m.point(lambda v: int(v * .2)))))
        img = add(img, Image.merge("RGB", (w.point(lambda v: int(v * .5)), w.point(lambda v: int(v * .34)), w.point(lambda v: int(v * .14)))))
        # dynamischer Ausschnitt: Flur, Ermittler, Türblatt
        px, py, pw, ph = 150, 540, 600, 860
        p, d0 = layer(pw, ph); d = d0.sub(-px, -py)
        if o > 0.01:
            d.rect(248, 648, 462, 1180, fill=(255, 208, 128))
            d.rect(280, 690, 440, 1110, fill=(244, 186, 104)); d.poly([(248, 1180), (280, 1110), (440, 1110), (462, 1180)], fill=(190, 130, 70))
            if t > .6:
                ph_ = t * 7.5; wk = 1 if 1.0 < t < 2.9 else 0
                draw_figure(d.sub(bx, by, bs), dark("brandt"), ph_ + 1.6, wk, "flash")
                draw_figure(d.sub(hx, hy, hs), dark("hartmann"), ph_, wk, "walk")
            if xe < 461:
                d.rect(xe, 640, 470, 648, fill=(44, 62, 100))
        sn = math.sin(th)
        d.poly([(248, 648), (xe, 648 - 46 * sn), (xe, 1180 + 80 * sn), (248, 1180)], fill=mix((30, 46, 80), (14, 22, 42), o), outline=(6, 10, 20), width=5)
        if o < .97:
            d.ell(lerp(248, xe, .84), 930 + 10 * sn, 9, 12, fill=(150, 130, 80))
        over(img, fin(p, pw, ph), (px, py))
        if o < .05:
            ImageDraw.Draw(img, "RGBA").rectangle((250, 1172, 460, 1180), fill=(255, 200, 120, 170))
        z = lerp(1.0, 1.14, ease(t / s.dur))
        img = view(img, 540, 960, z, rs=Image.BICUBIC)
        over(img, view(s.fg, 400, 1500, 1 + (z - 1) * 2.4))
        return vig(img, .9)


# ================================================================== SZENE 4b – Türschloss, unbeschädigt
class Lock:
    dur = 4.0

    def __init__(s):
        img, d = layer()
        d.rect(0, 0, 820, H, fill=(44, 66, 104))
        r = random.Random(4)
        for _ in range(70):
            x = r.randint(0, 800); y = r.randint(0, H); d.line([(x, y), (x + r.randint(-6, 6), y + r.randint(120, 500))], (38, 58, 94), 3, cap=False)
        for y0, y1 in ((120, 560), (1090, 1820)):
            d.rect(70, y0, 520, y1, fill=(38, 58, 94), outline=(22, 36, 64), width=8, r=6); d.rect(92, y0 + 22, 498, y1 - 22, outline=(60, 86, 130), width=4, r=4)
        d.rect(820, 0, 906, H, fill=(20, 32, 58)); d.rect(906, 0, W, H, fill=(34, 50, 84))
        d.rect(812, 0, 826, H, fill=(3, 6, 12))
        d.rect(950, 1240, 1030, 1370, fill=(200, 204, 210), outline=OL, width=5, r=6); d.rect(978, 1270, 1002, 1340, fill=(170, 174, 182), outline=OL, width=3)
        # Riegel (ausgefahren = verschlossen)
        d.rect(770, 742, 860, 792, fill=(182, 190, 204), outline=OL, width=5); d.line([(776, 752), (854, 752)], (236, 240, 246), 4, cap=False)
        # Drücker
        d.rect(640, 420, 770, 630, fill=(160, 168, 182), outline=OL, width=6, r=14)
        d.rect(440, 494, 730, 546, fill=(190, 198, 212), outline=OL, width=6, r=24); d.line([(470, 506), (700, 506)], (240, 244, 250), 5)
        d.ell(705, 520, 36, fill=(150, 158, 172), outline=OL, width=6)
        # Schlosskasten + Drehknauf
        d.rect(600, 660, 800, 876, fill=(186, 150, 78), outline=OL, width=7, r=18)
        d.rect(616, 676, 784, 860, outline=(226, 196, 120), width=4, r=12)
        d.ell(700, 768, 60, fill=(150, 116, 56), outline=OL, width=7)
        d.rect(634, 748, 766, 788, fill=(214, 180, 100), outline=OL, width=6, r=18); d.line([(650, 760), (750, 760)], (250, 226, 160), 5)
        for sx, sy in ((622, 682), (778, 682), (622, 854), (778, 854)): d.ell(sx, sy, 7, fill=(120, 92, 44), outline=OL, width=2)
        # Sicherungskette
        d.rect(470, 960, 720, 1004, fill=(170, 178, 192), outline=OL, width=6, r=8); d.rect(490, 976, 700, 988, fill=(40, 46, 58), r=4)
        d.rect(836, 900, 896, 976, fill=(170, 178, 192), outline=OL, width=6, r=8)
        for i in range(11):
            u = i / 10; cx = lerp(700, 864, u); cy = lerp(984, 944, u) + math.sin(u * math.pi) * 62
            d.ell(cx, cy, 13, 10 if i % 2 else 13, outline=(206, 212, 224), width=6); d.ell(cx, cy, 15, 12 if i % 2 else 15, outline=OL, width=2)
        s.b = fin(img).convert("RGB")
        s.dimb = tint_dim(s.b, .2, .25, .38)
        s.l1 = pill("VON INNEN VERSCHLOSSEN", 62, YEL, (6, 10, 20), border=YEL)
        s.l2 = pill("KEINE EINBRUCHSSPUREN", 62, (130, 240, 160), (6, 10, 20), border=(130, 240, 160))

    def frame(s, t):
        keys = [(0, 620, 520), (1.0, 700, 768), (2.3, 700, 768), (3.0, 800, 950), (3.6, 760, 800), (9, 760, 800)]
        for (ta, xa, ya), (tb, xb, yb) in zip(keys, keys[1:]):
            if ta <= t <= tb:
                u = ease((t - ta) / (tb - ta)); sx, sy = lerp(xa, xb, u), lerp(ya, yb, u); break
        sx += 12 * math.sin(t * 5.1); sy += 10 * math.sin(t * 3.7)
        m = Image.new("L", (270, 480), 26); md = ImageDraw.Draw(m)
        md.ellipse(((sx - 420) / 4, (sy - 420) / 4, (sx + 420) / 4, (sy + 420) / 4), fill=130)
        md.ellipse(((sx - 300) / 4, (sy - 300) / 4, (sx + 300) / 4, (sy + 300) / 4), fill=255)
        m = m.filter(ImageFilter.GaussianBlur(10)).resize((W, H), Image.BILINEAR)
        img = Image.composite(s.b, s.dimb, m)
        d = ImageDraw.Draw(img, "RGBA")
        a1 = eout(seg(t, .55, .9))
        if a1 > 0:
            d.line((700, 690, 700, lerp(690, 330, a1)), fill=YEL + (255,), width=5); d.ellipse((686, 754, 714, 782), outline=YEL + (255,), width=5)
            put(img, s.l1, 540, 270 - (1 - a1) * 20, a1)
        a2 = eout(seg(t, 2.25, 2.6))
        if a2 > 0:
            g = (130, 240, 160)
            d.line((818, 800, 818, lerp(800, 1150, a2)), fill=g + (255,), width=5); d.rectangle((760, 734, 870, 800), outline=g + (255,), width=5)
            put(img, s.l2, 540, 1200 + (1 - a2) * 20, a2)
            if a2 > .6:
                cx, cy = 540 + s.l2.width / 2 + 50, 1200
                d.ellipse((cx - 40, cy - 40, cx + 40, cy + 40), fill=g + (255,)); d.line((cx - 20, cy, cx - 5, cy + 16, cx + 22, cy - 16), fill=(6, 10, 20, 255), width=9)
        z = lerp(1.0, 1.1, ease(t / s.dur))
        return vig(view(img, 560, 900, z, rs=Image.BICUBIC), .8)


# ================================================================== Überwachungskameras (Rohbilder 540x960, in Farbe)
class Cam1:
    """Kamera 01 – Haupteingang (außen). Daniel verlässt das Gebäude in dunkler Jacke."""
    FREEZE = 5.2

    def __init__(s):
        img = Image.new("RGB", (540, 960), (44, 50, 64)); d = D(img, .5)
        for y in range(0, 1140, 44):
            d.line([(0, y), (W, y)], (34, 39, 52), 3, cap=False)
            for x in range((y // 44 % 2) * 60, W, 120): d.line([(x, y), (x, y + 44)], (34, 39, 52), 3, cap=False)
        d.rect(0, 1130, W, H, fill=(60, 64, 74))
        for i in range(-10, 11): d.line([(540 + i * 90, 1130), (540 + i * 260, H)], (48, 52, 62), 3, cap=False)
        for y in (1230, 1370, 1560, 1800): d.line([(0, y), (W, y)], (48, 52, 62), 3, cap=False)
        d.rect(270, 310, 810, 1130, fill=(16, 18, 26))
        # Foyer hinter Glas
        d.rect(300, 340, 780, 1130, fill=(150, 150, 142)); d.rect(300, 340, 780, 420, fill=(196, 196, 186))
        d.rect(340, 352, 740, 380, fill=(250, 250, 236))
        d.poly([(300, 1130), (380, 940), (700, 940), (780, 1130)], fill=(120, 118, 110))
        d.rect(380, 420, 700, 940, fill=(130, 132, 128))
        for mx in range(5):
            for my in range(3): d.rect(410 + mx * 54, 520 + my * 44, 456 + mx * 54, 556 + my * 44, fill=(96, 98, 100), outline=(60, 62, 66), width=2)
        d.rect(600, 690, 680, 940, fill=(84, 88, 96), outline=(50, 52, 58), width=3)
        d.poly([(200, 230), (880, 230), (930, 310), (150, 310)], fill=(24, 28, 40), outline=(10, 12, 18), width=5)
        d.rect(850, 480, 930, 560, fill=(220, 220, 214), outline=(10, 12, 18), width=4); d.text(890, 520, "12", font("title", 28), (20, 22, 30), anchor="mm")
        d.rect(846, 640, 906, 800, fill=(70, 74, 84), outline=(10, 12, 18), width=4)
        for i in range(5): d.rect(858, 656 + i * 28, 894, 672 + i * 28, fill=(150, 154, 160))
        d.rect(100, 960, 220, 1180, fill=(36, 40, 50), outline=(10, 12, 18), width=5, r=8); d.rect(90, 940, 230, 972, fill=(46, 50, 62), outline=(10, 12, 18), width=5, r=6)
        d.rect(960, 0, 990, 1130, fill=(30, 34, 44), outline=(10, 12, 18), width=3)
        d.rect(340, 1130, 740, 1200, fill=(30, 32, 38), outline=(10, 12, 18), width=4)
        d.soft(lambda q: q.poly([(300, 1130), (780, 1130), (940, 1700), (140, 1700)], fill=(255, 250, 220, 44)))
        s.bg = add(img, glow(540, 960, 270, 165, 240, (150, 150, 130), 1.6, .7))

    def raw(s, t):
        tt = min(t, s.FREEZE)
        img = s.bg.copy(); d = D(img, .5)
        op = ease(seg(tt, 1.5, 2.5))
        p = ease(seg(tt, 2.3, 5.5))
        fy = lerp(1050, 1450, p); k = lerp(.86, 1.36, p); fx = lerp(560, 524, p)
        ph = tt * 7.0

        def fig():
            d.soft(lambda q: q.ell(fx + 10, fy + 6, 90 * k, 22 * k, fill=(0, 0, 0, 90)))
            draw_figure(d.sub(fx, fy, k), "daniel_jacke", ph, 1 if tt > 2.3 else 0, "walk", look=.6 if tt > 4.6 else 0)

        def glass():
            ww = 240 * (1 - op * .92)
            d.soft(lambda q: (q.rect(300, 420, 300 + ww, 1130, fill=(150, 190, 215, 80), outline=(20, 24, 30, 255), width=7),
                              q.rect(780 - ww, 420, 780, 1130, fill=(150, 190, 215, 80), outline=(20, 24, 30, 255), width=7),
                              q.line([(316, 900), (300 + ww * .8, 560)], (255, 255, 255, 60), 8)))
        if fy < 1135: fig(); glass()
        else: glass(); fig()
        r = random.Random(int(t * 30))
        dd = ImageDraw.Draw(img, "RGBA")
        for _ in range(26):
            x, y = r.randint(0, 540), r.randint(0, 960); dd.line((x, y, x - 6, y + 34), fill=(230, 240, 250, 70), width=1)
        return img


class Cam2:
    """Kamera 02 – Aufzug. Daniel steht in hellem Kapuzenpullover in der Kabine."""
    FREEZE = 3.0

    def __init__(s):
        img = Image.new("RGB", (540, 960), (40, 44, 52)); d = D(img, .5)
        d.poly([(0, 60), (W, 60), (880, 270), (200, 270)], fill=(58, 64, 74))
        d.rect(0, 0, W, 60, fill=(30, 33, 40))
        d.poly([(360, 110), (720, 110), (770, 226), (310, 226)], fill=(244, 246, 240), outline=(120, 124, 130), width=4)
        d.rect(200, 270, 880, 1250, fill=(112, 120, 130))
        for x in (370, 540, 710): d.line([(x, 270), (x, 1250)], (86, 92, 102), 5, cap=False)
        d.rect(200, 270, 880, 330, fill=(92, 98, 108))
        d.rect(460, 280, 620, 360, fill=(12, 12, 14), outline=(40, 42, 48), width=4, r=6)
        d.rect(210, 920, 870, 944, fill=(190, 196, 204), outline=(60, 64, 70), width=3, r=10)
        d.poly([(0, 60), (200, 270), (200, 1250), (0, 1660)], fill=(80, 88, 98))
        d.poly([(W, 60), (880, 270), (880, 1250), (W, 1660)], fill=(72, 80, 90))
        d.poly([(940, 610), (1020, 560), (1020, 1010), (940, 980)], fill=(36, 38, 46), outline=(16, 18, 22), width=4)
        for i in range(5):
            for j in range(2):
                d.ell(962 + j * 34, 660 + i * 62 - j * 12, 11, fill=(250, 190, 80) if (i, j) == (4, 0) else (140, 144, 150), outline=(16, 18, 22), width=2)
        d.poly([(0, 1660), (200, 1250), (880, 1250), (W, 1660), (W, H), (0, H)], fill=(48, 52, 60))
        for i in range(-6, 7): d.line([(540 + i * 110, 1250), (540 + i * 300, H)], (40, 44, 52), 3, cap=False)
        for y in (1340, 1480, 1700): d.line([(0, y), (W, y)], (40, 44, 52), 3, cap=False)
        d.line([(200, 270), (200, 1250)], (30, 34, 40), 5, cap=False); d.line([(880, 270), (880, 1250)], (30, 34, 40), 5, cap=False)
        d.line([(0, 1660), (200, 1250), (880, 1250), (W, 1660)], (30, 34, 40), 6)
        s.bg = add(img, glow(540, 960, 270, 90, 300, (120, 124, 110), 1.6, .6))

    def raw(s, t):
        tt = min(t, s.FREEZE)
        img = s.bg.copy(); d = D(img, .5)
        fl = tt < 1.3
        d.text(540, 322, "4" if fl else "3", font("mono", 30), (255, 180, 60), anchor="mm")
        d.poly([(578, 312), (598, 312), (588, 330)], fill=(255, 180, 60))
        look = ease(seg(tt, 1.6, 2.3))
        sway = math.sin(tt * 1.8) * 5
        d.soft(lambda q: q.ell(540, 1508, 130, 30, fill=(0, 0, 0, 100)))
        draw_figure(d.sub(540, 1500, 1.46), "daniel_hoodie", 0, 0, "pockets", look=look, lean=sway)
        if 2.05 < tt < 2.2 or 2.3 < tt < 2.36:
            img = dim(img, .55)
        return img


def ts_box(txt, hot, size=96):
    return pill(txt, size, (8, 10, 16) if hot else (236, 244, 240), YEL if hot else (0, 0, 0, 150), "mono", 22, 8, r=8)


def brackets(d, box, col, w=6, ln=34):
    x0, y0, x1, y1 = box
    for (x, y, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        d.line((x, y, x + sx * ln, y), fill=col, width=w); d.line((x, y, x, y + sy * ln), fill=col, width=w)


class CamFull:
    """Szenen 6 und 7: Vollbild-Überwachungsaufnahme mit laufender Uhr und Standbild bei 23:47:00."""
    def __init__(s, cam, label, place, t_start_sec, dur, face, zoom_c):
        s.cam, s.label, s.place, s.t0, s.dur, s.face, s.zc = cam, label, place, t_start_sec, dur, face, zoom_c

    def frame(s, t):
        t = max(0, t)
        fz = s.cam.FREEZE
        raw = s.cam.raw(t)
        fr = t >= fz
        zk = ease(seg(t, fz + .15, fz + 1.6)) if fr else 0
        z = 1 + .34 * zk
        img = view(raw, lerp(270, s.zc[0], zk) * 2, lerp(480, s.zc[1], zk) * 2, z, k=.5, rs=Image.BICUBIC)
        img = cctv_grade(img, t)
        if fr and t - fz < .12:
            img = add(img, Image.new("RGB", (W, H), (int(190 * (1 - (t - fz) / .12)),) * 3))
        d = ImageDraw.Draw(img, "RGBA")
        if int(t * 2) % 2 == 0 or fr:
            d.ellipse((60, 196, 96, 232), fill=(235, 40, 40, 255))
        d.text((112, 188), "REC" if not fr else "STANDBILD", font=font("mono", 50), fill=(240, 246, 244, 255), stroke_width=2, stroke_fill=(0, 0, 0, 255))
        d.text((60, 250), f"{s.label} · {s.place}", font=font("mono", 50), fill=(240, 246, 244, 255), stroke_width=2, stroke_fill=(0, 0, 0, 255))
        sec = min(60, s.t0 + int(t + 1e-6 - (fz - (60 - s.t0))))
        sec = max(s.t0, sec)
        txt = "23:47:00" if sec >= 60 else f"23:46:{sec:02d}"
        hot = sec >= 60
        b = ts_box(txt, hot, 104)
        pul = 1 + .12 * max(0, 1 - (t - fz) / .3) if hot else 1
        put(img, b, 60 + b.width * pul / 2, 372, 1, pul)
        if fr:
            k = eout(seg(t, fz + .1, fz + .5))
            fx = (s.face[0] - lerp(270, s.zc[0], zk)) * 2 * z + 540; fy = (s.face[1] - lerp(480, s.zc[1], zk)) * 2 * z + 960
            hw = 120 * z * lerp(1.5, 1, k)
            brackets(d, (fx - hw, fy - hw * 1.1, fx + hw, fy + hw * 1.1), YEL + (int(255 * k),), 7, 40)
        return vig(img, .9)


# ================================================================== SZENE 5 – Ermittler am Überwachungsmonitor
class MonitorRoom:
    dur = 3.6
    MON = [(130, 300), (560, 300), (130, 680), (560, 680)]

    def __init__(s, cam1, cam2):
        s.c1, s.c2 = cam1, cam2
        img, d = layer()
        d.rect(0, 0, W, H, fill=(7, 11, 22))
        d.rect(0, 0, W, 1090, fill=(10, 16, 32))
        for x in range(0, W, 90): d.line([(x, 0), (x, 1090)], (8, 13, 27), 3, cap=False)
        d.rect(90, 250, 990, 1060, fill=(13, 18, 30), outline=(4, 6, 12), width=6, r=14)
        for x, y in s.MON:
            d.rect(x, y, x + 390, y + 340, fill=(26, 32, 46), outline=(4, 6, 12), width=6, r=12)
            d.rect(x + 14, y + 14, x + 376, y + 326, fill=(2, 4, 8))
            d.ell(x + 360, y + 333, 4, fill=(60, 230, 120))
        d.poly([(0, 1130), (W, 1130), (W, 1330), (0, 1330)], fill=(18, 24, 38), outline=(4, 6, 12), width=6)
        d.rect(0, 1320, W, H, fill=(5, 8, 16))
        d.rect(300, 1160, 720, 1230, fill=(30, 36, 50), outline=(4, 6, 12), width=5, r=8)
        for kx in range(316, 706, 26):
            for ky in (1172, 1194): d.rect(kx, ky, kx + 18, ky + 14, fill=(52, 60, 78))
        d.rect(800, 1140, 860, 1220, fill=(200, 204, 210), outline=(4, 6, 12), width=5, r=6); d.arc(866, 1180, 20, 22, -90, 90, (200, 204, 210), 7)
        d.rect(120, 1150, 240, 1230, fill=(24, 28, 40), outline=(4, 6, 12), width=5, r=6)
        s.room = fin(img).convert("RGB")
        s.glow = add(glow(W, H, 540, 660, 900, (30, 90, 110), 1.5, .55), glow(W, H, 540, 1230, 600, (20, 60, 80), 1.5, .5, ry=160))
        img, d = layer()
        draw_back(d.sub(310, 1420, 1.0), "hartmann")
        draw_back(d.sub(900, 1370, 1.02), "brandt")
        s.fg = fin(img)
        s.extra = [s._garage(), s._stairs()]

    def _garage(s):
        im = Image.new("RGB", (362, 312), (40, 44, 50)); d = D(im)
        d.poly([(0, 312), (0, 200), (362, 170), (362, 312)], fill=(58, 62, 68))
        for x in (40, 150, 260): d.rect(x, 20, x + 34, 215 - x * .08, fill=(90, 94, 100), outline=(20, 22, 26), width=3)
        d.rect(190, 170, 340, 230, fill=(24, 26, 32), r=14); d.rect(214, 140, 318, 180, fill=(24, 26, 32), r=12)
        d.ell(222, 232, 16, fill=(10, 10, 12)); d.ell(312, 228, 16, fill=(10, 10, 12))
        for x in range(0, 362, 60): d.line([(x, 290), (x + 30, 250)], (150, 150, 140), 3)
        return im

    def _stairs(s):
        im = Image.new("RGB", (362, 312), (50, 54, 60)); d = D(im)
        d.rect(0, 0, 362, 60, fill=(34, 36, 42))
        for i in range(7):
            d.rect(40 + i * 40, 250 - i * 28, 360, 280 - i * 28, fill=(86 - i * 4, 90 - i * 4, 96 - i * 4), outline=(24, 26, 30), width=2)
        d.line([(30, 210), (330, 0)], (150, 154, 160), 6); d.rect(250, 70, 330, 110, fill=(40, 150, 90)); d.rect(0, 280, 362, 312, fill=(40, 42, 48))
        return im

    def screens(s, img, t):
        c1 = s.c1.raw(2.6 + (t * .8) % 2.4).crop((40, 330, 500, 725)).resize((362, 312), Image.BILINEAR)
        c2 = s.c2.raw(.4 + t * .6).crop((40, 380, 500, 775)).resize((362, 312), Image.BILINEAR)
        for (x, y), src, nm in zip(s.MON, (c1, s.extra[0], s.extra[1], c2), ("CAM 01", "CAM 03", "CAM 04", "CAM 02")):
            g = cctv_grade(src, t + x * .01, noise=.16)
            ImageDraw.Draw(g).text((10, 6), nm, font=font("mono", 24), fill=(236, 244, 240))
            img.paste(g, (x + 14, y + 14))

    def frame(s, t):
        img = s.room.copy()
        s.screens(img, t)
        fk = .9 + .1 * math.sin(t * 40) * math.sin(t * 9)
        img = add(img, dim(s.glow, fk))
        hot = t > 1.75
        if hot:
            d = ImageDraw.Draw(img, "RGBA")
            on = (int((t - 1.75) * 8) % 2 == 0) or t > 2.5
            if on:
                for i in (0, 3):
                    x, y = s.MON[i]
                    d.rounded_rectangle((x - 8, y - 8, x + 398, y + 348), 16, outline=YEL + (255,), width=10)
        e = ease(t / s.dur); z = lerp(1.0, 1.32, e)
        img = view(img, 540, lerp(960, 780, e), z, rs=Image.BICUBIC)
        zf = 1 + (z - 1) * 1.6
        over(img, view(s.fg, 540, lerp(960, 900, e), zf))
        if hot and t < 2.0:
            img = add(img, Image.new("RGB", (W, H), (int(90 * (1 - (t - 1.75) / .25)),) * 3))
        return vig(img, .8)


# ================================================================== SZENE 8 – Split-Screen
class Split:
    dur = 9.5

    def __init__(s, cam1, cam2):
        s.r1 = cam1.raw(99); s.r2 = cam2.raw(99)
        s.tags = [pill(x, 54, (8, 10, 16), YEL) for x in ("DERSELBE MANN", "ZWEI ORTE", "DIESELBE UHRZEIT")]
        s.lab = [pill("DUNKLE JACKE", 50, YEL, (6, 10, 20), border=YEL), pill("HELLER HOODIE", 50, YEL, (6, 10, 20), border=YEL)]
        s.q = text_spr("?", "title", 150, YEL, stroke=6, glowc=(255, 160, 0), pad=30)
        s.bg = vgrad(W, H, [(0, (3, 6, 14)), (1, (6, 12, 26))])

    def panel(s, raw, t, zk, torso, seed):
        z = 1.3 + .65 * zk
        cx, cy = lerp(torso[0], torso[0], zk), lerp(575, torso[1], zk)
        im = view(raw, cx, cy, z, out=(524, 960), rs=Image.BICUBIC)
        return cctv_grade(im, t + seed, noise=.12), (cx, cy, z)

    def frame(s, t):
        img = s.bg.copy()
        ent = eout(seg(t, 0.0, .45))
        zk = ease(seg(t, 5.9, 7.0))
        p1, m1 = s.panel(s.r1, t, zk, (262, 548), 0)
        p2, m2 = s.panel(s.r2, t, zk, (270, 562), .37)
        x1 = 8 - (1 - ent) * 560; x2 = 548 + (1 - ent) * 560; y0 = 250
        img.paste(p1, (int(x1), y0)); img.paste(p2, (int(x2), y0))
        d = ImageDraw.Draw(img, "RGBA")
        for x in (x1, x2): d.rectangle((x, y0, x + 524, y0 + 960), outline=(120, 150, 150, 255), width=3)
        gl = (int(t * 30) % 37 == 0) * 6
        d.rectangle((536 + gl, y0 - 20, 544 + gl, y0 + 980), fill=YEL + (255,))
        f = font("mono", 40)
        d.text((x1 + 12, 186), "CAM 01 · HAUPTEINGANG", font=f, fill=(236, 244, 240, 255))
        d.text((x2 + 12, 186), "CAM 02 · AUFZUG", font=f, fill=(236, 244, 240, 255))
        pul = 1 + .16 * max(0, math.sin((t - 3.15) * 9)) * (1 if 3.15 < t < 4.6 else 0)
        b = ts_box("23:47:00", True, 84)
        put(img, b, x1 + 262, 1262, ent, pul); put(img, b, x2 + 262, 1262, ent, pul)

        def P(m, xo, wx, wy):       # Rohbild-Koordinate -> Bildschirm
            return xo + (wx - m[0]) * m[2] + 262, y0 + (wy - m[1]) * m[2] + 480
        ka = eout(seg(t, .35, .8)) * (1 - seg(t, 5.7, 6.0))
        if ka > 0:
            for m, xo, face in ((m1, x1, (262, 466)), (m2, x2, (270, 474))):
                fx, fy = P(m, xo, *face); hw = 62 * m[2] / 1.3 * lerp(1.6, 1, ka)
                brackets(d, (fx - hw, fy - hw * 1.15, fx + hw, fy + hw * 1.15), YEL + (int(255 * ka),), 6, 26)
            fa, fb = P(m1, x1, 262 + 50, 466), P(m2, x2, 270 - 50, 474)
            n = 14
            for i in range(n):
                if i % 2 == 0 and i / n < ka:
                    d.line((lerp(fa[0], fb[0], i / n), lerp(fa[1], fb[1], i / n), lerp(fa[0], fb[0], (i + 1) / n), lerp(fa[1], fb[1], (i + 1) / n)), fill=YEL + (255,), width=5)
        for i, (ta, tb) in enumerate(((.3, 5.7), (1.6, 5.7), (3.1, 5.7))):
            a = eout(seg(t, ta, ta + .25)) * (1 - seg(t, tb, tb + .3))
            put(img, s.tags[i], 540, 330 + i * 92, a, lerp(1.5, 1, eout(seg(t, ta, ta + .25))))
        kb = eout(seg(t, 6.6, 7.0))
        if kb > 0:
            for m, xo, box, lb in ((m1, x1, (200, 488, 324, 602), s.lab[0]), (m2, x2, (206, 500, 334, 628), s.lab[1])):
                a_, b_ = P(m, xo, box[0], box[1]), P(m, xo, box[2], box[3])
                brackets(d, (a_[0], a_[1], b_[0], b_[1]), YEL + (int(255 * kb),), 7, 40)
                put(img, lb, xo + 262, 1120 + (1 - kb) * 30, kb)
        qa = eout(seg(t, 4.9, 5.2)) * (1 - seg(t, 5.7, 6.0))
        put(img, s.q, 540, 620, qa, lerp(2.2, 1, eout(seg(t, 4.9, 5.2))))
        return vig(img, .55)


# ================================================================== SZENE 9 – zwei Monitore, Kamerafahrt
class Monitors:
    dur = 4.2

    def __init__(s, cam1, cam2):
        s.r = [cam1.raw(99).crop((65, 290, 475, 930)), cam2.raw(99).crop((65, 300, 475, 940))]
        img, d = layer()
        d.rect(0, 0, W, H, fill=(6, 10, 20)); d.rect(0, 0, W, 1140, fill=(9, 14, 28))
        for x in range(0, W, 90): d.line([(x, 0), (x, 1140)], (7, 12, 24), 3, cap=False)
        for x in (70, 560):
            d.rect(x + 190, 1050, x + 260, 1150, fill=(18, 22, 34), outline=(3, 5, 10), width=5)
            d.rect(x + 120, 1140, x + 330, 1166, fill=(22, 27, 40), outline=(3, 5, 10), width=5, r=8)
            d.rect(x, 370, x + 450, 1070, fill=(26, 32, 46), outline=(3, 5, 10), width=7, r=16)
            d.rect(x + 20, 390, x + 430, 1030, fill=(2, 4, 8)); d.ell(x + 420, 1050, 5, fill=(60, 230, 120))
        d.poly([(0, 1166), (W, 1166), (W, 1360), (0, 1360)], fill=(17, 23, 36), outline=(3, 5, 10), width=6)
        d.rect(0, 1350, W, H, fill=(4, 7, 14))
        d.line([(300, 1166), (340, 1260), (520, 1290)], (3, 5, 10), 8); d.line([(790, 1166), (760, 1250)], (3, 5, 10), 8)
        s.room = fin(img).convert("RGB")
        s.glow = add(glow(W, H, 295, 720, 620, (26, 84, 104), 1.5, .55), glow(W, H, 785, 720, 620, (26, 84, 104), 1.5, .55))
        img, d = layer()
        draw_back(d.sub(150, 1640, .95), "hartmann"); draw_back(d.sub(950, 1600, .98), "brandt")
        s.fg = fin(img)
        s.ts = ts_box("23:47:00", True, 60)

    def frame(s, t):
        img = s.room.copy()
        for i, x in enumerate((70, 560)):
            g = cctv_grade(s.r[i], t + i * .4, noise=.13)
            if random.Random(int(t * 30) + i * 7).random() < .06: g = ImageChops.offset(g, random.Random(int(t * 30)).randint(-30, 30), 0)
            img.paste(g, (x + 20, 390))
            put(img, s.ts, x + 225, 975)
            ImageDraw.Draw(img).text((x + 32, 398), f"CAM 0{i + 1}", font=font("mono", 34), fill=(236, 244, 240))
        fk = .88 + .12 * math.sin(t * 37) * math.sin(t * 8)
        img = add(img, dim(s.glow, fk))
        beat = max(0, 1 - ((t - .3) % 1.2) / .25) * .02
        e = ease(t / s.dur); z = lerp(1.0, 1.36, e) + beat
        img = view(img, 540, lerp(960, 760, e), z, rs=Image.BICUBIC)
        over(img, view(s.fg, 540, lerp(960, 1000, e), 1 + (z - 1) * .9))
        return vig(img, .85)


# ================================================================== SZENE 10 – Abstimmung A / B
def choice_card(letter, lines, col, icon, hot):
    cw, ch = 960, 330
    img, d = layer(cw, ch)
    if hot:
        d.rect(6, 6, cw - 6, ch - 6, fill=col + (70,), r=44)
    d.rect(20, 20, cw - 20, ch - 20, fill=(12, 20, 40, 244) if not hot else (20, 32, 60, 250), outline=col if hot else (70, 90, 130), width=8 if hot else 5, r=34)
    d.ell(150, ch / 2, 96, fill=col, outline=(4, 8, 16), width=6)
    d.text(150, ch / 2 - 6, letter, font("title", 150 * 2), (8, 12, 22), anchor="mm")
    d.text(280, 50, f"SPUR {letter}", font("mono", 36 * 2), col)
    size = 78
    while max(font("title", size).getlength(l) for l in lines) > 520: size -= 2
    for i, l in enumerate(lines):
        d.text(280, 100 + i * (size + 12), l, font("title", size * 2), (255, 255, 255))
    q = d.sub(850, ch / 2)
    if icon == "cam":
        q.rect(-56, -34, 20, 26, fill=col, outline=(4, 8, 16), width=5, r=8); q.poly([(20, -14), (58, -34), (58, 26), (20, 6)], fill=col, outline=(4, 8, 16), width=5)
        q.ell(-18, -4, 15, fill=(8, 12, 22)); q.line([(-18, 26), (-18, 56), (-50, 56)], col, 8); q.ell(34, -52, 6, fill=RED)
    else:
        q.rect(-44, -62, 30, 62, fill=col, outline=(4, 8, 16), width=5, r=4); q.ell(12, 4, 7, fill=(8, 12, 22))
        q.ell(38, 34, 24, outline=(255, 255, 255), width=8); q.line([(54, 52), (74, 74)], (255, 255, 255), 10)
    return fin(img, cw, ch)


class Choice:
    dur = 7.1

    def __init__(s, bgsrc):
        s.bg = dim(bgsrc.filter(ImageFilter.GaussianBlur(16)), .5)
        s.bg = add(s.bg, glow(W, H, 540, 700, 900, (16, 30, 70), 1.4, .8))
        s.h = [text_spr(x, "title", 92, (255, 255, 255), stroke=4, glowc=(0, 0, 0), pad=20) for x in ("WAS UNTERSUCHEN", "WIR ZUERST?")]
        A = ["ÜBERWACHUNGSKAMERAS", "UNTERSUCHEN"]; B = ["WOHNUNG", "DURCHSUCHEN"]
        s.a = [choice_card("A", A, YEL, "cam", h) for h in (0, 1)]
        s.b = [choice_card("B", B, TEAL, "door", h) for h in (0, 1)]
        s.cta = pill("KOMMENTIERE  A  ODER  B", 60, (8, 12, 22), (255, 255, 255), padx=34, pady=14, r=40)
        r = random.Random(9)
        s.dust = [(r.random(), r.random(), r.random()) for _ in range(40)]

    def frame(s, t):
        img = view(s.bg, 540, 960, 1.02 + .05 * t / s.dur)
        d = ImageDraw.Draw(img, "RGBA")
        for a, b, c in s.dust:
            x = (a * W + t * 20 * (c - .3)) % W; y = (b * H - t * 30 * (.4 + c)) % H
            d.ellipse((x, y, x + 3 + 3 * c, y + 3 + 3 * c), fill=(200, 220, 255, int(30 + 50 * c)))
        for i, sp in enumerate(s.h):
            a = eout(seg(t, i * .1, .35 + i * .1))
            put(img, sp, 540, 220 + i * 104 - (1 - a) * 30, a)
        ha = 1.0 if .25 < t < 2.0 else 0
        hb = 1.0 if 2.0 <= t < 4.6 else 0
        if t > 5.0: ha = hb = (math.sin((t - 5.0) * 5) > 0) * 1.0 if t < 6.2 else 1.0
        ea, eb = eback(seg(t, .2, .65)), eback(seg(t, .45, .9))
        pa = 1 + .035 * math.sin(t * 9) * ha; pb = 1 + .035 * math.sin(t * 9) * hb
        put(img, s.a[int(ha)], 540 - (1 - ea) * 1100, 590, 1, pa)
        put(img, s.b[int(hb)], 540 + (1 - eb) * 1100, 950, 1, pb)
        c = eback(seg(t, 4.95, 5.35))
        if c > 0: put(img, s.cta, 540, 1215, clamp(c), .6 + .4 * c + .02 * math.sin(t * 8))
        return vig(img, .7)


# ================================================================== Abschlussbild
class End:
    dur = 3.2

    def __init__(s, city):
        s.bg = dim(city.frame(3.9).filter(ImageFilter.GaussianBlur(10)), .42)
        s.l = [text_spr("DU ENTSCHEIDEST,", "title", 132, (255, 255, 255), stroke=5, glowc=(0, 0, 0), pad=30),
               text_spr("WIE ES", "title", 132, YEL, stroke=5, glowc=(0, 0, 0), pad=30),
               text_spr("WEITERGEHT.", "title", 132, YEL, stroke=5, glowc=(0, 0, 0), pad=30)]
        s.f2 = pill("FOLGE 2 FOLGT", 50, (255, 255, 255), (0, 0, 0, 150), "mono", 26, 12, border=(255, 255, 255))

    def frame(s, t):
        img = view(s.bg, 540, 960, 1.0 + .04 * t / s.dur)
        rain(img, t + 30, 150, 1)
        for i, sp in enumerate(s.l):
            t0 = .1 + i * .28
            k = eout(seg(t, t0, t0 + .22))
            put(img, sp, 540, 590 + i * 170, seg(t, t0, t0 + .1), lerp(1.9, 1, k))
        a = eout(seg(t, 1.2, 1.6))
        if a > 0:
            ImageDraw.Draw(img).rectangle((540 - 380 * a, 1058, 540 + 380 * a, 1068), fill=(255, 255, 255))
            put(img, s.f2, 540, 1150, a)
        return vig(img, .8)


# ================================================================== Zusammenbau
class Episode:
    def __init__(s, total):
        s.total = total
        city = City(); c1, c2 = Cam1(), Cam2()
        mons = Monitors(c1, c2)
        s.scenes = [city, Building(city), Portrait(), Apartment(), Lock(), MonitorRoom(c1, c2),
                    CamFull(c1, "CAM 01", "HAUPTEINGANG", 55, 7.8, (262, 466), (262, 560)),
                    CamFull(c2, "CAM 02", "AUFZUG", 57, 5.2, (270, 474), (270, 580)),
                    Split(c1, c2), mons, Choice(mons.frame(4.2)), End(city)]
        s.subs = Subtitles(SUBS)

    def frame(s, i):
        t = i / FPS
        k = max(j for j, c in enumerate(CUTS) if c <= t)
        lt = t - CUTS[k]
        img = s.scenes[k].frame(lt)
        tr = TRANS[k]
        if tr and lt < tr[1]:
            p = lt / tr[1]
            if tr[0] == "fade":
                img = Image.blend(s.scenes[k - 1].frame(t - CUTS[k - 1]), img, ease(p))
            elif tr[0] == "flash":
                img = add(img, Image.new("RGB", (W, H), (int(255 * (1 - p) ** 2),) * 3))
            elif tr[0] == "glitch":
                img = glitch(img, t, 1 - p, k)
        if k + 1 < len(CUTS) and TRANS[k + 1] and TRANS[k + 1][0] == "glitch" and CUTS[k + 1] - t < .12:
            img = glitch(img, t, .8, k)
        if t < .25: img = dim(img, t / .25)
        if s.total - t < .3: img = dim(img, max(0, (s.total - t) / .3) * .5 + .5)
        return s.subs.draw(img, t)
