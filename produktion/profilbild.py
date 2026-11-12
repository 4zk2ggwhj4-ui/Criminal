"""Profilbild (quadratisch, für runden Zuschnitt): python3 profilbild.py <ausgabe.png>"""
import sys
from engine import *

S = 1080
img = vgrad(S, S, [(0, (4, 8, 22)), (.6, (16, 32, 66)), (1, (8, 16, 36))])
img = add(img, glow(S, S, 540, 470, 620, (255, 180, 70), 2.0, .45))

def bust(outfit):
    im, d = layer(S, S)
    draw_daniel_bust(d.sub(540, 500, 1.75), outfit)
    return fin(im, S, S)

a, b = bust("daniel_jacke"), bust("daniel_hoodie")
right = Image.new("RGB", (S, S), (20, 30, 40)); right.paste(b, (0, 0), b)
right = cctv_grade(right, 0.3, noise=.12).convert("RGBA"); right.putalpha(b.getchannel("A"))
zig = [(540 + (24 if i % 2 else -24), i * 60) for i in range(19)]
m = Image.new("L", (S, S), 0); ImageDraw.Draw(m).polygon(zig + [(S, S), (S, 0)], fill=255)
over(img, a)
img.paste(right, (0, 0), ImageChops.multiply(right.getchannel("A"), m))
d = ImageDraw.Draw(img, "RGBA")
d.line(zig, fill=YEL + (255,), width=10, joint="curve")
r = random.Random(2)
for _ in range(90):
    x, y, l = r.randint(0, S), r.randint(0, S), r.randint(40, 100)
    d.line((x, y, x - l * .16, y + l), fill=(170, 205, 255, r.randint(30, 90)), width=2)
img = ImageChops.multiply(img, vignette(.7, S, S))
put(img, pill("23:47", 120, (8, 10, 16), YEL, "mono", 22, 8, r=8), 540, 905)
img.save(sys.argv[1])
