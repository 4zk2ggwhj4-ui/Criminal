"""TikTok-Cover Folge 1: python3 cover.py <ausgabe.png>"""
import sys
from folge_01 import *

city = City()
bg = Building(city).frame(0.3).filter(ImageFilter.GaussianBlur(7))
img = dim(bg, .5)
img = add(img, glow(W, H, 540, 1150, 900, (20, 40, 90), 1.5, .9))

def bust(outfit):
    im, d = layer(W, 900, bg=(0, 0, 0, 0))
    draw_daniel_bust(d.sub(540, 330, 1.85), outfit)
    return fin(im, W, 900)

a, b = bust("daniel_jacke"), bust("daniel_hoodie")
Y0 = 760
shadow = Image.new("RGBA", (W, 900), (0, 0, 0, 0)); shadow.putalpha(a.getchannel("A").filter(ImageFilter.GaussianBlur(30)).point(lambda v: int(v * .8)))
over(img, shadow, (0, Y0 + 10))
right = Image.new("RGB", (W, 900), (20, 30, 40)); right.paste(b, (0, 0), b)
right = cctv_grade(right, 0.3, noise=.12).convert("RGBA"); right.putalpha(b.getchannel("A"))
m = Image.new("L", (W, 900), 0); md = ImageDraw.Draw(m)
zig = [(540 + (26 if i % 2 else -26), i * 60) for i in range(16)]
md.polygon(zig + [(W, 900), (W, 0)], fill=255)
over(img, a, (0, Y0))
img.paste(right, (0, Y0), ImageChops.multiply(right.getchannel("A"), m))
d = ImageDraw.Draw(img, "RGBA")
d.line([(x, y + Y0) for x, y in zig], fill=YEL + (255,), width=9, joint="curve")
rain(img, 1.3, 170, 1)
img = vig(img, .8)
d = ImageDraw.Draw(img, "RGBA")
d.rectangle((0, 0, W, 760), fill=(4, 8, 20, 110))
put(img, pill("INTERAKTIVER KRIMI · FOLGE 1", 46, (8, 12, 22), YEL, padx=28, pady=10), 540, 170)
for i, (txt, col) in enumerate((("DER MANN,", (255, 255, 255)), ("DER ZWEIMAL", YEL), ("EXISTIERTE", (255, 255, 255)))):
    put(img, text_spr(txt, "title", 178, col, stroke=6, glowc=(0, 0, 0), pad=36), 540, 318 + i * 186)
for x, nm in ((270, "CAM 01"), (810, "CAM 02")):
    put(img, ts_box("23:47:00", True, 76), x, 1640)
    put(img, text_spr(nm, "mono", 44, (236, 244, 240), stroke=2), x, 1570)
put(img, pill("DU ENTSCHEIDEST, WIE ES WEITERGEHT", 50, (255, 255, 255), (0, 0, 0, 170), padx=28, pady=12, border=(255, 255, 255)), 540, 1770)
img.save(sys.argv[1])
