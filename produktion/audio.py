"""Musik + Soundeffekte (vollständig synthetisch erzeugt) und Mischung mit der Sprecherstimme.
Aufruf: python3 audio.py <sprecher.mp3|wav> <ausgabe.wav>"""
import sys, subprocess, wave
import numpy as np
SR = 44100
rng = np.random.default_rng(42)


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def filt(x, lo=None, hi=None, order=4):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); g = np.ones_like(f)
    if hi: g *= 1 / np.sqrt(1 + (f / hi) ** (2 * order))
    if lo: g *= 1 - 1 / np.sqrt(1 + (f / lo) ** (2 * order))
    return np.fft.irfft(X * g, len(x))


def tt(d): return np.arange(int(d * SR)) / SR
def noise(d): return rng.standard_normal(int(d * SR))


class Bus:
    def __init__(s, n): s.b = np.zeros((n, 2))
    def add(s, sig, t, gain=1.0, pan=0.0):
        i = int(t * SR)
        if i >= len(s.b): return
        sig = sig[: len(s.b) - i]
        s.b[i:i + len(sig), 0] += sig * gain * (1 - max(0, pan)); s.b[i:i + len(sig), 1] += sig * gain * (1 + min(0, pan))


def reverb(x, wet=.25, decay=1.1, length=2.6):
    out = x.copy()
    for ch in range(2):
        ir = filt(noise(length) * np.exp(-tt(length) / decay), lo=200, hi=5000)
        n = len(x) + len(ir)
        y = np.fft.irfft(np.fft.rfft(x[:, ch], n) * np.fft.rfft(ir, n), n)[: len(x)]
        out[:, ch] += wet * y / 40
    return out


def impact(d=1.6, f0=95, f1=34):
    t = tt(d); f = f1 + (f0 - f1) * np.exp(-t * 9)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2)
    return s + filt(noise(d), hi=1800) * np.exp(-t * 28) * .6


def whoosh(d=.6, up=True):
    n = noise(d); t = tt(d); k = t / d if up else 1 - t / d
    out = np.zeros_like(n)
    for i in range(8):
        a, b = int(i * len(n) / 8), int((i + 1) * len(n) / 8)
        fc = 300 + 3500 * ((i + .5) / 8 if up else 1 - (i + .5) / 8)
        out[a:b] = filt(n, lo=fc * .6, hi=fc * 1.6)[a:b]
    return out * np.sin(np.pi * t / d) ** 2


def blip(f, d=.09, a=40):
    t = tt(d); return np.sin(2 * np.pi * f * t) * np.exp(-t * a) * np.minimum(1, t * 800)


def bell(f, d=1.2):
    t = tt(d); return (np.sin(2 * np.pi * f * t) + .5 * np.sin(2 * np.pi * f * 2.01 * t) + .25 * np.sin(2 * np.pi * f * 3.02 * t)) * np.exp(-t * 4.5)


def static(d=.32):
    n = noise(d); g = (rng.random(int(d * 40) + 1) > .3).repeat(SR // 40 + 1)[: len(n)]
    return filt(n, lo=900) * g * np.exp(-tt(d) * 3)


def pad(freqs, d, att=1.2, rel=1.5):
    t = tt(d); s = np.zeros_like(t)
    for f in freqs:
        for det in (-.004, 0, .005):
            ph = rng.random() * 6.28
            s += np.sin(2 * np.pi * f * (1 + det) * t + ph) + .3 * np.sin(2 * np.pi * 2 * f * (1 + det) * t + ph * 2)
    env = np.minimum(1, t / att) * np.minimum(1, (d - t) / rel)
    return s / len(freqs) / 3 * env * (1 + .15 * np.sin(2 * np.pi * .23 * t))


def note(n): return 440 * 2 ** ((n - 69) / 12)


def build(voice):
    n = len(voice); D = n / SR
    mus, sfx = Bus(n), Bus(n)
    # Regen
    for ch, pan in ((0, -1), (1, 1)):
        r = filt(noise(D), lo=700, hi=7500, order=2)
        t = np.arange(n) / SR
        lvl = np.interp(t, [0, 8.6, 9.4, 13.8, 14.3, 24.6, 25, 32.4, 32.8, 58.4, 58.9, D], [1, 1, .4, .4, .3, .3, .7, .7, .25, .25, 1, 1])
        mus.add(r * lvl, 0, .05, pan)
    # Drone
    t = np.arange(n) / SR
    dr = sum(np.sin(2 * np.pi * f * t + .7 * np.sin(2 * np.pi * f * 2 * t)) for f in (36.71, 36.9, 73.42))
    mus.add(filt(dr, hi=240) * (.75 + .25 * np.sin(2 * np.pi * .11 * t)) * np.minimum(1, t / 2), 0, .085)
    # Akkordflächen
    prog = [(0, 14.4, [50, 53, 57, 62]), (13.6, 25.2, [46, 50, 53, 62]), (24.4, 38.2, [43, 46, 50, 58]), (37.4, 47.8, [45, 49, 52, 58]),
            (47.0, 59.0, [50, 53, 57, 64]), (58.4, D, [38, 50, 57, 65])]
    for a, b, ch in prog:
        mus.add(filt(pad([note(x) for x in ch], b - a), hi=1800), a, .11)
    mus.add(pad([note(81)], 5.4, 2, 2) * .5, 9.0, .03, .3); mus.add(pad([note(82)], 9.5, 2, 2) * .5, 37.8, .035, -.3)
    # Ticken
    tk = 21.2; i = 0
    while tk < 58.5:
        step = .6 if tk < 37.8 else .3
        s = filt(noise(.03), lo=2500 if i % 2 else 3800) * np.exp(-tt(.03) * 200)
        mus.add(s, tk, .11 if tk < 37.8 else .08, .25 if i % 2 else -.25); tk += step; i += 1
    # Herzschlag
    hb = 37.8
    while hb < 51.4:
        for off, g in ((0, 1), (.27, .7)):
            mus.add(impact(.35, 62, 38), hb + off, .34 * g)
        hb += 1.2
    # treibender Bass (Abstimmung)
    b = 51.5; i = 0
    while b < 58.5:
        f = note([38, 38, 41, 38, 38, 38, 36, 38][i % 8]); t_ = tt(.28)
        s = filt(np.sign(np.sin(2 * np.pi * f * t_)) * np.exp(-t_ * 9), hi=420)
        mus.add(s, b, .13); b += .3; i += 1
    rs = whoosh(3.4, True) * np.linspace(0, 1, int(3.4 * SR)) ** 2
    mus.add(rs, 55.2, .16)
    # Soundeffekte
    th = filt(noise(3.6), hi=130) * np.exp(-tt(3.6) * 1.1) * (1 + .6 * np.sin(2 * np.pi * 3.1 * tt(3.6)))
    sfx.add(th, .2, .9); sfx.add(filt(noise(.25), lo=1500) * np.exp(-tt(.25) * 14), .18, .1)
    for tc in (4.0, 14.0, 17.2, 21.2, 47.3, 51.5): sfx.add(whoosh(.7, True), tc - .35, .09, .3)
    sfx.add(whoosh(.5, False), 9.0, .1)
    sfx.add(impact(), 11.64, .75); sfx.add(blip(180, .2, 20), 11.64, .3)
    sfx.add(blip(2400, .03, 150), 14.35, .1)                                    # Türschloss
    tcr = tt(.8); cr = np.sin(2 * np.pi * np.cumsum(330 + 90 * np.sin(2 * np.pi * 2.3 * tcr) + 40 * tcr) / SR) * np.sin(np.pi * tcr / .8) ** 2
    sfx.add(filt(cr * (.6 + .4 * np.sign(np.sin(2 * np.pi * 47 * tcr))), lo=250, hi=2500), 14.4, .035, .4)
    sfx.add(blip(3000, .02, 200), 15.18, .12)                                   # Taschenlampe
    sfx.add(bell(1318), 17.75, .05); sfx.add(bell(1568), 19.45, .05)
    sfx.add(bell(880), 22.95, .1); sfx.add(bell(1320), 23.08, .08); sfx.add(impact(.8, 70, 40), 22.95, .3)
    for tc in (24.8, 32.6, 37.8): sfx.add(static(), tc - .1, .13)
    for tc in (30.0, 35.6):
        sfx.add(blip(1250, .08, 25), tc, .09); sfx.add(blip(1660, .12, 20), tc + .09, .09); sfx.add(impact(1.0, 80, 36), tc, .45)
    for tc, f in ((38.1, 520), (39.4, 620), (40.95, 740), (44.45, 620), (44.45, 930)): sfx.add(blip(f, .12, 30), tc, .1)
    sfx.add(impact(1.2, 70, 34), 42.7, .4)
    for tc, f in ((51.72, 660), (51.97, 880), (53.5, 990), (56.48, 1320)): sfx.add(blip(f, .14, 26), tc, .1)
    sfx.add(impact(2.6, 110, 30), 58.6, .9); sfx.add(filt(noise(1.5), lo=2000) * np.exp(-tt(1.5) * 5), 58.6, .08)
    # Ducking + Mischung
    env = np.sqrt(np.convolve(voice ** 2, np.ones(2205) / 2205, "same"))
    env = np.convolve(np.clip(env / (np.percentile(env, 95) + 1e-9), 0, 1), np.ones(6000) / 6000, "same")
    v = voice / np.max(np.abs(voice)) * .9
    m = reverb(mus.b, .3) * (1 - .5 * env)[:, None]
    s = reverb(sfx.b, .35) * (1 - .3 * env)[:, None] * .6
    vr = np.sqrt(np.mean(v[np.abs(v) > .02] ** 2)); mr = np.sqrt(np.mean(m ** 2)) + 1e-9
    m *= vr * 10 ** (-15 / 20) / mr
    mix = v[:, None] + m + s * .8
    fade = np.minimum(1, (n - np.arange(n)) / (SR * .5)); mix[:, :] *= np.ones(n)[:, None]
    mix = v[:, None] + (m + s * .8) * fade[:, None]
    mix = np.tanh(mix * 1.05) / np.tanh(1.05) * .97
    print("voice rms %.3f music rms %.3f sfx peak %.3f mix peak %.3f" % (vr, np.sqrt(np.mean(m ** 2)), np.max(np.abs(s)), np.max(np.abs(mix))))
    return mix


if __name__ == "__main__":
    mix = build(load(sys.argv[1]))
    with wave.open(sys.argv[2], "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype("<i2").tobytes())
    print("dauer", len(mix) / SR)
