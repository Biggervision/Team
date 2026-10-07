"""Builds the soundtrack: voiceover + synthesized UI sound design + music bed.

Usage: python3 build_audio.py <voiceover> <out.wav>
Every cue time is master time (voiceover placed at 0.50 s).
"""
import subprocess
import sys

import numpy as np
from scipy.signal import butter, sosfilt

SR = 48000
DUR = 71.5
VO_OFFSET = 0.5
VO_TRIM = 65.6  # drop the trailing silence of the recording
BPM = 96
BEAT = 60 / BPM
rng = np.random.default_rng(7)


def n(sec):
    return int(round(sec * SR))


def tl(sec):
    return np.arange(n(sec)) / SR


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, 'low', fs=SR, output='sos'), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, 'high', fs=SR, output='sos'), x)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], 'band', fs=SR, output='sos'), x)


def adsr(length, a=0.005, r=None):
    e = np.ones(length)
    na = max(1, n(a))
    e[:na] = np.linspace(0, 1, na)
    if r:
        nr = min(length, n(r))
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


# ---------------- sound effects ----------------
def pluck(f, dur=0.35, decay=8.0, bright=0.4):
    t = tl(dur)
    x = np.sin(2 * np.pi * f * t) + bright * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t)
    return x * np.exp(-decay * t) * adsr(len(t), 0.004)


def tick(f=1600, dur=0.05):
    t = tl(dur)
    return np.sin(2 * np.pi * f * t) * np.exp(-90 * t) + 0.3 * rng.standard_normal(len(t)) * np.exp(-400 * t)


def pop():
    t = tl(0.07)
    f = np.linspace(900, 380, len(t))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-45 * t)


def sweep(f0, f1, dur, decay=3.0):
    t = tl(dur)
    f = np.geomspace(f0, f1, len(t))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-decay * t) * adsr(len(t), 0.03, 0.1)


def noise(dur):
    return rng.standard_normal(n(dur))


def whoosh(dur=0.8, lo=300, hi=2500):
    t = tl(dur)
    env = np.sin(np.pi * t / dur) ** 2
    return bp(noise(dur), lo, hi) * env * 0.6


def whoom_down():
    return sweep(480, 110, 0.65, 3.5) * 0.8 + lp(noise(0.65), 400) * np.exp(-5 * tl(0.65)) * 0.25


def layer(*xs):
    out = np.zeros(max(len(x) for x in xs))
    for x in xs:
        out[:len(x)] += x
    return out


def click():
    return layer(tick(2200, 0.03) * 0.8, sweep(160, 90, 0.06, 40) * 0.6)


def thump():
    return sweep(140, 55, 0.18, 18)


def chime(notes, gap=0.035, dur=1.4, decay=3.2):
    out = np.zeros(n(dur + gap * len(notes)))
    for i, m in enumerate(notes):
        p = pluck(mtof(m), dur, decay, 0.15)
        out[n(i * gap):n(i * gap) + len(p)] += p / len(notes) * 1.6
    return out


def ring():
    out = np.zeros(n(1.3))
    pat = [76, 71, 76, 71, 76, 71]
    for i, m in enumerate(pat):
        p = pluck(mtof(m), 0.3, 11, 0.25)
        out[n(i * 0.11):n(i * 0.11) + len(p)] += p
    return out * 0.7


def haptic():
    t = tl(0.45)
    return np.sin(2 * np.pi * 160 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 28 * t)) * adsr(len(t), 0.01, 0.08) * 0.35


def drag(dur=0.46):
    return bp(noise(dur), 900, 3000) * adsr(n(dur), 0.04, 0.12) * 0.25


def crackle(dur=0.7):
    out = np.zeros(n(dur))
    for _ in range(14):
        i = rng.integers(0, len(out) - 200)
        out[i:i + 120] += rng.standard_normal(120) * np.exp(-np.arange(120) / 20)
    return hp(out, 2500) * 0.4


def shimmer(dur=1.4, f0=1800, f1=3600, count=10):
    out = np.zeros(n(dur + 0.3))
    for i in range(count):
        f = f0 * (f1 / f0) ** (i / count)
        p = pluck(f, 0.25, 18, 0.1)
        s = n(i * dur / count)
        out[s:s + len(p)] += p
    return out * 0.35


# ---------------- placement ----------------
L = np.zeros(n(DUR) + SR)
R = np.zeros_like(L)


def put(x, at, gain=1.0, pan=0.0):
    s = n(at)
    e = min(len(L), s + len(x))
    x = x[:e - s] * gain
    L[s:e] += x * np.sqrt((1 - pan) / 2) * 1.414
    R[s:e] += x * np.sqrt((1 + pan) / 2) * 1.414


SFX_GAIN = 0.16
G = SFX_GAIN

# Scene 1 — hook
put(ring(), 0.0, G * 1.4)
put(haptic(), 0.02, G)
for at, f, pan in [(1.88, 1200, 0.2), (3.12, 1350, 0.35), (3.86, 1520, 0.35), (4.32, 1700, 0.2)]:
    put(tick(f, 0.06), at, G * 0.9, pan)
for i in range(6):
    put(pop(), 5.9 + i * 0.09, G * 0.7, -0.3)
put(shimmer(0.9, 2400, 4200, 8), 7.92, G * 0.5, -0.2)

# Scene 2 — black hole (mirrors the call spawner in scenes.js)
for i in range(34):
    ts = 8.3 + i * 0.16
    lost = ts > 10.6 and i % 3 != 0
    if lost:
        at = ts + 1.75 * 0.5
        if 9.3 < at < 13.6 and i % 2 == 0:
            put(whoom_down(), at, G * 0.55)
    else:
        at = ts + 1.75
        if 9.3 < at < 13.6:
            put(tick(2000, 0.04), at, G * 0.35, 0.5)

# Scene 3 — 30 vs 10
for i in range(14):
    put(tick(1500 + i * 40, 0.03), 14.85 + i * 0.045, G * 0.45)
for i in range(7):
    put(tick(1300, 0.03), 17.35 + i * 0.1, G * 0.4)
put(click(), 18.02, G * 1.1)
put(sweep(320, 260, 0.12, 25), 18.05, G * 0.8)

# Scene 4 — underperforming
put(tick(1100, 0.04), 21.36, G * 0.7)
put(tick(900, 0.04), 21.5, G * 0.7)

# Scene 5 — cut, pause, lose
put(drag(), 23.94, G * 1.0)
put(click(), 24.54, G * 1.3)
put(thump(), 24.56, G * 0.9)
for i, at in enumerate([27.0, 27.6, 28.2, 28.8, 29.58]):
    put(sweep(mtof(76 - i * 2), mtof(70 - i * 2), 0.5, 5), at, G * (0.45 - i * 0.05), 0.4)

# Scene 6 — reveal
put(whoosh(1.1, 200, 1800), 30.9, G * 0.9)
put(chime([84, 88], 0.04, 1.0, 4), 32.26, G * 0.6)
put(crackle(), 34.0, G * 0.5)

# Scene 7 — the guide
put(pop(), 37.96, G * 0.8, 0.3)
put(tick(2400, 0.04), 38.0, G * 0.6, 0.3)

# Scene 8 — the plan
for at in (39.76, 41.5, 44.78):
    put(click(), at, G * 0.8)
    put(thump(), at, G * 0.5)
put(sweep(800, 1600, 0.5, 2) * 0.4, 42.4, G * 0.5)
put(shimmer(1.4, 1500, 3800, 12), 45.04, G * 0.7, 0.2)
put(chime([79, 84], 0.05, 0.9, 5), 47.46, G * 0.6)

# Scene 9 — success
for i in range(16):
    put(tick(1500 + i * 50, 0.03), 49.08 + i * 0.05, G * 0.4)
put(chime([84, 88, 91], 0.05, 1.2, 4), 49.9, G * 0.55)
put(chime([72, 76, 79, 84], 0.07, 2.0, 2.2), 57.9, G * 0.9)

# Scene 10 — stakes
put(click(), 60.44, G * 0.6)
for k, pan in enumerate(np.linspace(-0.2, 0.8, 4)):
    put(ring()[n(k * 0.3):n(k * 0.3 + 0.3)], 63.76 + k * 0.3, G * (0.7 - k * 0.15), pan)

# Scene 11 — final card
put(chime([72, 79, 84], 0.06, 1.6, 2.5), 66.0, G * 0.6)

sfx = np.stack([L, R])[:, :n(DUR)]


# ---------------- music bed ----------------
CH = {
    'Am9': [45, 52, 55, 59, 60], 'Fmaj7': [41, 48, 52, 57], 'Em7': [40, 47, 50, 55], 'Dm9': [38, 45, 48, 53, 64],
    'Esus': [40, 47, 52, 57], 'Cadd9': [48, 55, 62, 64], 'G6': [43, 50, 59, 64], 'Am7': [45, 52, 55, 60],
}
# (start, end, chords per bar, pad gain, pluck density 0..2, drums)
SECTIONS = [
    (0.0, 9.3, ['Am9', 'Fmaj7', 'Am9', 'Fmaj7'], 0.9, 1, 0),
    (9.3, 22.9, ['Am9', 'Fmaj7', 'Am9', 'Em7'], 1.0, 1, 1),
    (22.9, 31.0, ['Fmaj7', 'Dm9', 'Am9', 'Em7'], 0.8, 0, 0),
    (31.0, 36.6, ['Dm9', 'Esus', 'Esus'], 0.85, 0, 0),
    (37.9, 48.3, ['Cadd9', 'G6', 'Am7', 'Fmaj7'], 1.0, 2, 2),
    (48.3, 58.7, ['Cadd9', 'G6', 'Am7', 'Fmaj7'], 1.15, 2, 3),
    (58.7, 65.8, ['Am7', 'Fmaj7', 'Cadd9', 'G6'], 0.85, 1, 0),
    (65.8, 71.5, ['Cadd9'], 1.0, 0, 0),
]
BAR = BEAT * 4


def saw(f, t):
    return 2 * ((f * t) % 1) - 1


def pad_note(m, dur):
    t = tl(dur)
    f = mtof(m)
    x = sum(saw(f * 2 ** (d / 1200), t + ph) for d, ph in ((-7, 0), (0, 0.31), (7, 0.67)))
    x = lp(x / 3, 900 + 300 * (m > 55), 2)
    return x * adsr(len(t), 0.9, 1.2)


mus = np.zeros(n(DUR) + SR * 3)
for start, end, chords, gain, plk, drums in SECTIONS:
    t0 = start
    bi = 0
    while t0 < end - 0.05:
        ch = chords[bi % len(chords)]
        dur = min(BAR, end - t0) + 1.2
        for m in CH[ch]:
            p = pad_note(m, dur) * 0.05 * gain
            mus[n(t0):n(t0) + len(p)] += p
        # plucked arpeggio
        if plk:
            notes = [m + 12 for m in CH[ch][1:]] + [CH[ch][-1] + 24]
            steps = 8 if plk == 2 else 4
            for s in range(steps):
                at = t0 + s * BAR / steps
                if at >= end:
                    break
                m = notes[(s * 2 + bi) % len(notes)]
                p = pluck(mtof(m), 0.5, 7, 0.25) * (0.05 if plk == 2 else 0.04)
                mus[n(at):n(at) + len(p)] += p
        # light percussion
        if drums:
            for b in range(4):
                at = t0 + b * BEAT
                if at >= end:
                    break
                if drums >= 2 or b % 2 == 0:
                    k = sweep(110, 45, 0.25, 14) * (0.10 if drums >= 2 else 0.06)
                    mus[n(at):n(at) + len(k)] += k
                if drums >= 2:
                    h = hp(noise(0.05), 6000) * np.exp(-60 * tl(0.05)) * 0.02
                    mus[n(at + BEAT / 2):n(at + BEAT / 2) + len(h)] += h
                if drums >= 3:
                    h = hp(noise(0.04), 7000) * np.exp(-80 * tl(0.04)) * 0.012
                    for q in (0.25, 0.75):
                        mus[n(at + BEAT * q):n(at + BEAT * q) + len(h)] += h
        t0 += BAR
        bi += 1
mus = mus[:n(DUR)]
# breath before "Here's the fix"
tt = np.arange(len(mus)) / SR
gate = np.ones_like(mus)
gate[(tt > 36.2) & (tt < 37.9)] = np.interp(tt[(tt > 36.2) & (tt < 37.9)], [36.2, 36.9, 37.9], [1, 0.12, 0.12])
mus *= gate
mus *= np.clip((DUR - tt) / 2.5, 0, 1)  # tail fade


# ---------------- voiceover ----------------
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', sys.argv[1], '-t', str(VO_TRIM), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                     capture_output=True, check=True).stdout
vo = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
vo = hp(vo, 70)
vo *= adsr(len(vo), 0.01, 0.25)
voice = np.zeros(n(DUR))
voice[n(VO_OFFSET):n(VO_OFFSET) + len(vo)] = vo[:n(DUR) - n(VO_OFFSET)]

# duck music under the voice
win = n(0.05)
env = np.sqrt(np.convolve(voice ** 2, np.ones(win) / win, mode='same'))
active = (env > 0.02).astype(float)
active = np.convolve(active, np.ones(n(0.4)) / n(0.4), mode='same')
duck = 1 - 0.45 * np.clip(active, 0, 1)

vo_rms = np.sqrt(np.mean(vo[np.abs(vo) > 0.02] ** 2))
mus_rms = np.sqrt(np.mean(mus ** 2)) + 1e-9
mus *= (vo_rms * 0.30 / mus_rms)
music = mus * duck

mix = np.stack([voice + music * 0.98 + sfx[0] * vo_rms * 2.2, voice + music * 1.02 + sfx[1] * vo_rms * 2.2])
peak = np.max(np.abs(mix))
mix = mix / peak * 0.89
pcm = (mix.T * 32767).astype(np.int16)

with open(sys.argv[2], 'wb') as f:
    import wave
    w = wave.open(f, 'wb')
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
    w.close()
print('wrote', sys.argv[2], 'vo_rms', round(vo_rms, 3), 'peak', round(peak, 3))
