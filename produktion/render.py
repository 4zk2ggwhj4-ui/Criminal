"""Rendert die Folge: python3 render.py <mix.wav> <ausgabe.mp4> [startsek endsek]"""
import sys, math, subprocess, wave
from multiprocessing import Pool
EP = None

def init(total):
    global EP
    from folge_01 import Episode
    EP = Episode(total)

def work(i): return EP.frame(i).tobytes()

if __name__ == "__main__":
    wav, out = sys.argv[1], sys.argv[2]
    with wave.open(wav) as w: total = w.getnframes() / w.getframerate()
    n = math.ceil(total * 30)
    a, b = (int(float(sys.argv[3]) * 30), int(float(sys.argv[4]) * 30)) if len(sys.argv) > 4 else (0, n)
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920", "-r", "30", "-i", "-",
           "-ss", str(a / 30), "-t", str((b - a) / 30), "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-maxrate", "9M", "-bufsize", "18M", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(4, init, (total,)) as pool:
        for k, fr in enumerate(pool.imap(work, range(a, b), chunksize=4)):
            p.stdin.write(fr)
            if k % 300 == 0: print(k, "/", b - a, flush=True)
    p.stdin.close(); p.wait(); print("fertig", out, n, "frames")
