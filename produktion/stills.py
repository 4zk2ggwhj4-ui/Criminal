"""Kontrollbilder: python3 stills.py <ausgabeordner> t1 t2 ..."""
import sys, time
from folge_01 import *
out = sys.argv[1]; ep = Episode(61.649)
for a in sys.argv[2:]:
    t0 = time.time(); im = ep.frame(int(float(a) * FPS)); im.save(f"{out}/s_{float(a):05.2f}.jpg", quality=85)
    print(a, round(time.time() - t0, 2))
