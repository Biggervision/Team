"""DSLR-style background blur: person mask (mediapipe multiclass) + disc-kernel bokeh, temporally smoothed."""
import sys, subprocess, numpy as np, cv2, mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
src, dst = sys.argv[1], sys.argv[2]
only = float(sys.argv[3]) if len(sys.argv) > 3 else None   # preview: single timestamp -> png
W, H = 1080, 1920
seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=BaseOptions(model_asset_path="seg.tflite"), output_confidence_masks=True,
    running_mode=vision.RunningMode.IMAGE))
R = 5
disc = np.zeros((2 * R + 1, 2 * R + 1), np.float32); cv2.circle(disc, (R, R), R, 1, -1); disc /= disc.sum()
prev = None
def process(fr):
    global prev
    small = cv2.resize(fr, (288, 512), interpolation=cv2.INTER_AREA)
    r = seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(small[..., ::-1])))
    m = 1 - np.squeeze(r.confidence_masks[0].numpy_view()).astype(np.float32)
    m = cv2.resize(m, (288, 512))
    prev = m if prev is None else prev * 0.55 + m * 0.45          # temporal smoothing
    mf = cv2.resize(prev, (W, H), interpolation=cv2.INTER_CUBIC)
    mf = cv2.ximgproc.guidedFilter(fr, mf, 8, 1e-3)
    mf = np.clip((mf - 0.3) / 0.45, 0, 1)
    # bokeh on background only (normalised so the subject does not bleed into the blur)
    hs = cv2.resize(fr, (W // 2, H // 2), interpolation=cv2.INTER_AREA).astype(np.float32)
    bm = cv2.resize(1 - mf, (W // 2, H // 2))[..., None]
    num = cv2.filter2D(hs * bm, -1, disc); den = cv2.filter2D(bm[..., 0], -1, disc)[..., None] + 1e-4
    bg = num / den
    # small highlight bloom for lens character
    pass
    bg = cv2.resize(bg, (W, H), interpolation=cv2.INTER_CUBIC)
    a = mf[..., None]
    return np.clip(fr * a + bg * (1 - a), 0, 255).astype(np.uint8)
if only is not None:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(only), "-i", src, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(H, W, 3)
    for _ in range(3): out = process(fr)
    cv2.imwrite(dst, np.hstack([fr, out])); sys.exit()
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                        "-i", src, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "12", "-preset", "fast", "-c:a", "copy", "-shortest", dst], stdin=subprocess.PIPE)
n = 0
while True:
    raw = dec.stdout.read(W * H * 3)
    if len(raw) < W * H * 3: break
    enc.stdin.write(process(np.frombuffer(raw, np.uint8).reshape(H, W, 3)).tobytes()); n += 1
    if n % 300 == 0: print(n, flush=True)
enc.stdin.close(); enc.wait(); seg.close(); print("done", n)
