"""Rendert den Film: Frames parallel mit Cairo, Ton synthetisch, Ausgabe via ffmpeg (H.264 + AAC)."""
import sys, subprocess, time, os
from multiprocessing import Pool
import numpy as np

W = int(os.environ.get('W', 3840)); H = W * 9 // 16
FPS = 24
OUT = sys.argv[1] if len(sys.argv) > 1 else 'wichtelbriefe_4k.mp4'
WAV = sys.argv[2] if len(sys.argv) > 2 else 'soundtrack.wav'


def work(i):
    import film
    return film.render_frame(i / FPS, W, H).tobytes()


if __name__ == '__main__':
    n = int(60 * FPS)
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
           '-i', '-', '-i', WAV, '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p',
           '-profile:v', 'high', '-tune', 'animation', '-movflags', '+faststart',
           '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-shortest', OUT]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    B = 8
    with Pool(int(os.environ.get('PROCS', 4))) as pool:
        for b0 in range(0, n, B):
            for buf in pool.map(work, range(b0, min(n, b0 + B)), chunksize=1):
                p.stdin.write(buf)
            if b0 % 48 == 0:
                print(f'{b0}/{n} {time.time() - t0:.0f}s', flush=True)
    p.stdin.close()
    p.wait()
    print('fertig', OUT, f'{time.time() - t0:.0f}s')
