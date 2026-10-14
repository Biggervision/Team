"""One pass: light DSLR blur + darker moody background + skin-only lightening (mediapipe multiclass)."""
import sys, subprocess, numpy as np, cv2, mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
src, dst = sys.argv[1], sys.argv[2]
only = float(sys.argv[3]) if len(sys.argv) > 3 else None
BG_DARK = 0.62; LIFT = 40.0; R = 3
W, H = 1080, 1920
seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=BaseOptions(model_asset_path="seg.tflite"), output_confidence_masks=True))
disc = np.zeros((2 * R + 1, 2 * R + 1), np.float32); cv2.circle(disc, (R, R), R, 1, -1); disc /= disc.sum()
pv = {}
def smooth(k, m):
    pv[k] = m if k not in pv else pv[k] * 0.5 + m * 0.5
    return pv[k]
def process(fr):
    small = cv2.resize(fr, (288, 512), interpolation=cv2.INTER_AREA)
    r = seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(small[..., ::-1])))
    cm = [cv2.resize(np.squeeze(m.numpy_view()).astype(np.float32), (288, 512)) for m in r.confidence_masks]
    person = smooth("p", 1 - cm[0]); skin = smooth("s", np.clip(cm[2] + cm[3], 0, 1))
    pm = cv2.ximgproc.guidedFilter(fr, cv2.resize(person, (W, H), interpolation=cv2.INTER_CUBIC), 8, 1e-3)
    pm = np.clip((pm - 0.3) / 0.45, 0, 1)
    sm = cv2.ximgproc.guidedFilter(fr, cv2.resize(skin, (W, H), interpolation=cv2.INTER_CUBIC), 10, 1e-3)
    sm = np.clip((sm - 0.25) / 0.5, 0, 1)[..., None]
    # background: light bokeh + darken (moody)
    hs = cv2.resize(fr, (W // 2, H // 2), interpolation=cv2.INTER_AREA).astype(np.float32)
    bm = cv2.resize(1 - pm, (W // 2, H // 2))
    bg = cv2.filter2D(hs * bm[..., None], -1, disc) / (cv2.filter2D(bm, -1, disc)[..., None] + 1e-4)
    bg = cv2.resize(bg, (W, H), interpolation=cv2.INTER_CUBIC) * BG_DARK
    a = pm[..., None]
    out = fr.astype(np.float32) * a + bg * (1 - a)
    # skin
    o8 = np.clip(out, 0, 255).astype(np.uint8)
    smoothd = cv2.bilateralFilter(o8, 9, 40, 9)
    base = (o8 * 0.45 + smoothd * 0.55).astype(np.uint8)
    lab = cv2.cvtColor(base, cv2.COLOR_BGR2LAB).astype(np.float32)
    L = lab[..., 0]
    lab[..., 0] = L + LIFT * (1 - (L / 255) ** 2)
    lab[..., 1] = 128 + (lab[..., 1] - 128) * 0.92
    lab[..., 2] = 128 + (lab[..., 2] - 128) * 0.90
    lit = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR).astype(np.float32)
    return np.clip(out * (1 - sm) + lit * sm, 0, 255).astype(np.uint8)
if only is not None:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(only), "-i", src, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(H, W, 3)
    for _ in range(3): o = process(fr)
    cv2.imwrite(dst, np.hstack([fr, o])); seg.close(); sys.exit()
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                        "-i", src, "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-crf", "12", "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", dst], stdin=subprocess.PIPE)
n = 0
while True:
    raw = dec.stdout.read(W * H * 3)
    if len(raw) < W * H * 3: break
    enc.stdin.write(process(np.frombuffer(raw, np.uint8).reshape(H, W, 3)).tobytes()); n += 1
enc.stdin.close(); enc.wait(); seg.close(); print("done", n)
