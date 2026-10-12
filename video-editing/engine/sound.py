"""Synthesised SFX library + background music bed (48 kHz stereo float32)."""
import numpy as np
from scipy import signal

SR = 48000
rng = np.random.default_rng(7)


def _t(d):
    return np.arange(int(d * SR)) / SR


def _env(n, a, r, curve=4.0):
    """attack seconds a, then exponential-ish release to end"""
    t = np.arange(n) / SR
    na = max(1, int(a * SR))
    e = np.ones(n)
    e[:na] = np.linspace(0, 1, na) ** 2
    rel = t[na:] - t[na]
    e[na:] = np.exp(-curve * rel / max(r, 1e-3))
    return e


def _sos(kind, f, order=2):
    return signal.butter(order, f, kind, fs=SR, output="sos")


def _stereo(x, pan=0.0):
    l = np.cos((pan + 1) * np.pi / 4)
    r = np.sin((pan + 1) * np.pi / 4)
    return np.stack([x * l, x * r], 1) * 1.414


def _reverb(x, dur=0.9, mix=0.18):
    n = int(dur * SR)
    ir = rng.standard_normal(n) * np.exp(-6 * np.arange(n) / n)
    ir = signal.sosfilt(_sos("lowpass", 5000), ir)
    ir /= np.abs(ir).sum() ** 0.5 * 12
    wet = signal.fftconvolve(x, ir)
    out = np.zeros(len(wet))
    out[: len(x)] += x * (1 - mix)
    out += wet * mix * 6
    return out


def _sweep_filter(x, f0, f1, kind="bandpass", q=1.2, chunk=256):
    """time-varying filter by processing in chunks"""
    out = np.zeros_like(x)
    n = len(x)
    zi = None
    for i in range(0, n, chunk):
        p = i / n
        f = f0 * (f1 / f0) ** p
        if kind == "bandpass":
            sos = signal.butter(2, [f / (1 + 0.5 / q), min(SR / 2 - 100, f * (1 + 0.5 / q))], "bandpass", fs=SR, output="sos")
        else:
            sos = signal.butter(2, min(SR / 2 - 100, f), kind, fs=SR, output="sos")
        if zi is None or zi.shape[0] != sos.shape[0]:
            zi = signal.sosfilt_zi(sos) * 0
        out[i:i + chunk], zi = signal.sosfilt(sos, x[i:i + chunk], zi=zi)
    return out


def norm(x, peak=1.0):
    m = np.abs(x).max()
    return x / m * peak if m > 0 else x


# ---------------- SFX ----------------
def whoosh(d=0.55, f0=300, f1=4000, pan0=-0.6, pan1=0.6):
    n = int(d * SR)
    x = rng.standard_normal(n)
    x = _sweep_filter(x, f0, f1, "bandpass", q=0.9)
    t = np.linspace(0, 1, n)
    env = np.sin(np.pi * t ** 0.7) ** 2
    x = norm(x * env)
    pan = np.linspace(pan0, pan1, n)
    l = np.cos((pan + 1) * np.pi / 4)
    r = np.sin((pan + 1) * np.pi / 4)
    st = np.stack([x * l, x * r], 1) * 1.2
    return np.stack([_reverb(st[:, 0], 0.5, 0.15), _reverb(st[:, 1], 0.5, 0.15)], 1)


def swish(d=0.22):
    return whoosh(d, 1500, 7000, 0.3, -0.3)


def impact(d=1.1, f0=95, f1=42, heavy=False):
    t = _t(d)
    ph = 2 * np.pi * np.cumsum(f1 + (f0 - f1) * np.exp(-t * 18)) / SR
    body = np.sin(ph) * np.exp(-t * (3.2 if heavy else 5.5))
    click = signal.sosfilt(_sos("lowpass", 2500), rng.standard_normal(len(t))) * np.exp(-t * 90)
    x = body + click * (0.8 if heavy else 0.5)
    x = np.tanh(x * 1.5)
    return _stereo(norm(_reverb(x, 1.0, 0.22)))


def pop(f0=900, f1=260, d=0.09):
    t = _t(d)
    ph = 2 * np.pi * np.cumsum(f1 + (f0 - f1) * np.exp(-t * 60)) / SR
    x = np.sin(ph) * np.exp(-t * 45)
    x += signal.sosfilt(_sos("highpass", 3000), rng.standard_normal(len(t))) * np.exp(-t * 400) * 0.3
    return _stereo(norm(_reverb(x, 0.3, 0.12)))


def click(f=2400):
    t = _t(0.04)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t * 180)
    x += signal.sosfilt(_sos("highpass", 4000), rng.standard_normal(len(t))) * np.exp(-t * 900) * 0.6
    return _stereo(norm(x))


def tick():
    t = _t(0.018)
    x = signal.sosfilt(_sos("bandpass", [3000, 9000]), rng.standard_normal(len(t))) * np.exp(-t * 600)
    x += np.sin(2 * np.pi * 5200 * t) * np.exp(-t * 500) * 0.5
    return _stereo(norm(x))


def ding(f=1568):
    t = _t(1.6)
    x = np.zeros_like(t)
    for ratio, amp, dec in ((1, 1, 3.0), (2.0, 0.5, 4.5), (2.76, 0.35, 6), (5.4, 0.15, 9)):
        x += amp * np.sin(2 * np.pi * f * ratio * t) * np.exp(-t * dec)
    t2 = t - 0.09
    m = t2 > 0
    for ratio, amp, dec in ((1, 0.9, 3.0), (2.0, 0.4, 4.5), (2.76, 0.3, 6)):
        x[m] += amp * np.sin(2 * np.pi * f * 1.26 * ratio * t2[m]) * np.exp(-t2[m] * dec)
    x *= np.minimum(1, t / 0.003)
    return _stereo(norm(_reverb(x, 1.2, 0.25)))


def riser(d=1.0):
    n = int(d * SR)
    t = np.linspace(0, 1, n)
    x = _sweep_filter(rng.standard_normal(n), 400, 8000, "bandpass", q=1.5)
    tone = np.sin(2 * np.pi * np.cumsum(200 + 900 * t ** 2) / SR) * 0.25
    x = norm(x) * 0.8 + tone
    x *= t ** 2.2
    return _stereo(norm(x))


def glitch(d=0.2):
    n = int(d * SR)
    x = np.sign(np.sin(2 * np.pi * np.cumsum(rng.choice([180, 360, 720, 90], n // 800 + 1).repeat(800)[:n]) / SR))
    x = signal.sosfilt(_sos("bandpass", [300, 5000]), x) * (rng.random(n // 400 + 1).repeat(400)[:n] > 0.35)
    x *= np.linspace(1, 0.2, n)
    return _stereo(norm(x))


def bubble():
    return pop(1400, 700, 0.06)


# ---------------- music bed ----------------
def _note(freq, d, amp=1.0):
    t = _t(d)
    x = np.zeros_like(t)
    for det in (-0.12, 0, 0.12):  # detuned voices (cents-ish in Hz ratio)
        f = freq * (1 + det / 100)
        for h in range(1, 9):
            x += np.sin(2 * np.pi * f * h * t + rng.random() * 6.28) / h ** 1.6
    env = np.minimum(1, t / 0.35) * np.minimum(1, (d - t) / 0.6).clip(0, 1)
    return x * env * amp


def music(dur, bpm=88):
    beat = 60 / bpm
    bar = beat * 4
    n = int(dur * SR) + SR
    L = np.zeros(n)
    R = np.zeros(n)
    A = 440.0
    def hz(semi):
        return A * 2 ** (semi / 12)
    # Am9, Fmaj7, Cmaj7, G6 voicings (semitones from A4)
    chords = [[-12, -9, -5, -2, 2], [-16, -12, -9, -5, -1], [-9, -5, -2, 2, 7], [-14, -10, -7, -3, 2]]
    roots = [-24, -28, -33, -26]
    t0 = 0.0
    k = 0
    while t0 < dur:
        ch = chords[k % 4]
        for j, s in enumerate(ch):
            x = _note(hz(s), bar + 0.6, 0.06)
            pan = (j / (len(ch) - 1) - 0.5) * 0.8
            i = int(t0 * SR)
            seg = x[: n - i]
            L[i:i + len(seg)] += seg * np.cos((pan + 1) * np.pi / 4)
            R[i:i + len(seg)] += seg * np.sin((pan + 1) * np.pi / 4)
        # sub bass
        tb = _t(bar)
        b = np.sin(2 * np.pi * hz(roots[k % 4]) * tb) * np.minimum(1, tb / 0.05) * np.exp(-tb * 0.6) * 0.16
        i = int(t0 * SR)
        L[i:i + len(b)] += b[: n - i]
        R[i:i + len(b)] += b[: n - i]
        # soft kick on 1 & 3, hat on 8ths, gentle pluck arpeggio
        for q in range(8):
            tq = t0 + q * beat / 2
            i = int(tq * SR)
            if i >= n - SR:
                break
            if q in (0, 4):
                tk = _t(0.35)
                kk = np.sin(2 * np.pi * np.cumsum(45 + 70 * np.exp(-tk * 30)) / SR) * np.exp(-tk * 9) * 0.22
                L[i:i + len(kk)] += kk
                R[i:i + len(kk)] += kk
            th = _t(0.05)
            hh = signal.sosfilt(_sos("highpass", 8000), rng.standard_normal(len(th))) * np.exp(-th * 120) * (0.035 if q % 2 else 0.02)
            L[i:i + len(hh)] += hh * 0.8
            R[i:i + len(hh)] += hh
            note = ch[(q * 3) % len(ch)] + 12
            tp = _t(0.5)
            pl = np.sin(2 * np.pi * hz(note) * tp) * np.exp(-tp * 7) * 0.03
            pan = 0.35 if q % 2 else -0.35
            L[i:i + len(pl)] += pl * np.cos((pan + 1) * np.pi / 4)
            R[i:i + len(pl)] += pl * np.sin((pan + 1) * np.pi / 4)
        t0 += bar
        k += 1
    m = np.stack([L, R], 1)[: int(dur * SR)]
    m = signal.sosfilt(_sos("lowpass", 7000), m, axis=0)
    return norm(m, 0.5)
