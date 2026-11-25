import sys, time, numpy as np
from PIL import Image
import film2 as film
ts = [float(x) for x in sys.argv[2].split(',')]
W = int(sys.argv[3]) if len(sys.argv) > 3 else 960
H = W * 9 // 16
imgs = []
for t in ts:
    t0 = time.time()
    a = film.render_frame(t, W, H)
    print(t, round(time.time() - t0, 2), flush=True)
    imgs.append(Image.fromarray(a))
cols = 3
rows = (len(imgs) + cols - 1) // cols
sheet = Image.new('RGB', (cols * W, rows * H), 'white')
for i, im in enumerate(imgs):
    sheet.paste(im, ((i % cols) * W, (i // cols) * H))
sheet.save(sys.argv[1])
