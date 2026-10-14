"""Skin-only lightening: mediapipe multiclass (face-skin + body-skin) mask -> LAB lift, warm-neutral, light smoothing."""
import sys, subprocess, numpy as np, cv2, mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
src, dst = sys.argv[1], sys.argv[2]
only = float(sys.argv[3]) if len(sys.argv) > 3 else None
LIFT = float(sys.argv[4]) if len(sys.argv) > 4 else 70.0
W, H = 1080, 1920
seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=BaseOptions(model_asset_path="seg.tflite"), output_confidence_masks=True))
prev = None
def process(fr):
    global prev
    small = cv2.resize(fr, (288, 512), interpolation=cv2.INTER_AREA)
    r = seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(small[..., ::-1])))
    cm = [np.squeeze(m.numpy_view()) for m in r.confidence_masks]
    m = np.clip(cm[2] + cm[3], 0, 1).astype(np.float32)
    m = cv2.resize(m, (288, 512))
    prev = m if prev is None else prev * 0.5 + m * 0.5
    mf = cv2.resize(prev, (W, H), interpolation=cv2.INTER_CUBIC)
    mf = cv2.ximgproc.guidedFilter(fr, mf, 10, 1e-3)
    mf = np.clip((mf - 0.25) / 0.5, 0, 1)[..., None]
    smooth = cv2.bilateralFilter(fr, 9, 40, 9)
    base = (fr * 0.45 + smooth * 0.55).astype(np.uint8)
    lab = cv2.cvtColor(base, cv2.COLOR_BGR2LAB).astype(np.float32)
    L = lab[..., 0]
    lab[..., 0] = L + LIFT * (1 - (L / 255) ** 2) * 1.0          # lift shadows/mids more than highlights
    lab[..., 1] = 128 + (lab[..., 1] - 128) * 0.82                # less red
    lab[..., 2] = 128 + (lab[..., 2] - 128) * 0.80                # less yellow
    lit = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR).astype(np.float32)
    return np.clip(fr * (1 - mf) + lit * mf, 0, 255).astype(np.uint8)
if only is not None:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(only), "-i", src, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(H, W, 3)
    for _ in range(3): out = process(fr)
    cv2.imwrite(dst, np.hstack([fr, out])); seg.close(); sys.exit()
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                        "-i", src, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", dst], stdin=subprocess.PIPE)
n = 0
while True:
    raw = dec.stdout.read(W * H * 3)
    if len(raw) < W * H * 3: break
    enc.stdin.write(process(np.frombuffer(raw, np.uint8).reshape(H, W, 3)).tobytes()); n += 1
enc.stdin.close(); enc.wait(); seg.close(); print("done", n)
