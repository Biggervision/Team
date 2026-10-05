"""Audio pipeline: enhance the real voice-over (no voice change), synthesize
original SFX + an original minimal tech score, duck music under voice, master."""
import json, subprocess, sys, os
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000
RAW = sys.argv[1] if len(sys.argv) > 1 else "voiceover"
OUT = "build"
os.makedirs(OUT, exist_ok=True)
tl = json.load(open("timeline.json"))
TOTAL = tl["total"]
N = int(TOTAL * SR)
rng = np.random.default_rng(7)


def sh(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr); raise SystemExit(1)
    return r.stderr


def read(path):
    sr, x = wavfile.read(path)
    x = x.astype(np.float32)
    if x.dtype != np.float32 or np.abs(x).max() > 2:
        x /= 32768.0
    return x if x.ndim == 1 else x.mean(1)


# ---------------------------------------------------------------- VOICE
# Clean-up only: high-pass, light denoise, gentle EQ, de-ess, compression,
# loudness match. No pitch/formant/timbre processing -> voice identity intact.
VOICE_CHAIN = ("highpass=f=75,afftdn=nr=8:nf=-55,"
               "equalizer=f=220:t=q:w=1.1:g=-2,equalizer=f=3300:t=q:w=1.2:g=1.8,"
               "highshelf=f=9500:g=1.2,deesser=i=0.35,"
               "acompressor=threshold=0.09:ratio=2.8:attack=8:release=140:makeup=1.6")
vo = np.zeros(N, np.float32)
for s in tl["scenes"]:
    src = f"{RAW}/raw_{s['id']}.wav"
    tmp = f"{OUT}/vo_{s['id']}_a.wav"
    # clean the whole clip once, then keep only the chosen segments (natural speed & pitch)
    full = f"{OUT}/vo_{s['id']}_full.wav"
    sh(f"ffmpeg -v error -y -i {src} -af \"{VOICE_CHAIN}\" -ar {SR} -ac 1 -c:a pcm_f32le {full}")
    xf = read(full)
    segs = s.get("segs") or [(s["trim_in"], s["trim_out"])]
    parts = []
    for a, b in segs:
        p = xf[int(a * SR):int(b * SR)].copy()
        fi, fo = int(.015 * SR), int(.03 * SR)
        p[:fi] *= np.linspace(0, 1, fi); p[-fo:] *= np.linspace(1, 0, fo)
        parts.append(p)
    wavfile.write(tmp, SR, np.concatenate(parts).astype(np.float32))
    m = json.loads(sh(f"ffmpeg -i {tmp} -af loudnorm=I=-16:TP=-2:LRA=9:print_format=json -f null - ")
                   .split("[Parsed_loudnorm")[-1].split("\n", 1)[1])
    fin = f"{OUT}/vo_{s['id']}.wav"
    sh(f"ffmpeg -v error -y -i {tmp} -af loudnorm=I=-16:TP=-2:LRA=9:measured_I={m['input_i']}:"
       f"measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
       f"offset={m['target_offset']}:linear=true -ar {SR} -ac 1 {fin}")
    x = read(fin)
    i0 = int(s["start"] * SR)
    vo[i0:i0 + len(x)] += x[: N - i0]

# ---------------------------------------------------------------- helpers
def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], "band", fs=SR, output="sos"), x)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, "low", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, "high", fs=SR, output="sos"), x)


def sine_glide(n, f0, f1, curve=3.0):
    t = np.arange(n) / SR
    k = np.linspace(0, 1, n) ** (1 / curve)
    f = f0 + (f1 - f0) * k
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def noise(n):
    return rng.standard_normal(n).astype(np.float32)


def norm(x, peak=1.0):
    return x / (np.abs(x).max() + 1e-9) * peak


# ---------------------------------------------------------------- SFX
def sfx(kind):
    if kind == "tick":
        n = int(0.06 * SR)
        x = bp(noise(n), 2500, 7000) * env(n, 0.0005, 0.006) + 0.5 * np.sin(2 * np.pi * 2100 * np.arange(n) / SR) * env(n, 0.0005, 0.012)
    elif kind == "blip":
        n = int(0.16 * SR)
        x = sine_glide(n, 1150, 1650, 1) * env(n, 0.002, 0.04) + 0.3 * sine_glide(n, 2300, 3300, 1) * env(n, 0.002, 0.02)
    elif kind == "confirm":
        n = int(0.7 * SR); t = np.arange(n) / SR
        x = np.sin(2 * np.pi * 880 * t) * env(n, 0.003, 0.12)
        k = int(0.075 * SR)
        x[k:] += 0.9 * np.sin(2 * np.pi * 1318.5 * t[: n - k]) * env(n - k, 0.003, 0.22)
        x += 0.15 * np.sin(2 * np.pi * 2637 * t) * env(n, 0.003, 0.05)
    elif kind == "error":
        n = int(0.32 * SR); t = np.arange(n) / SR
        x = np.sin(2 * np.pi * 330 * t) * env(n, 0.004, 0.06)
        k = int(0.11 * SR)
        x[k:] += np.sin(2 * np.pi * 247 * t[: n - k]) * env(n - k, 0.004, 0.09)
        x = lp(x + 0.1 * np.sign(x) * np.abs(x) ** 0.5, 2500)
    elif kind == "dropout":
        n = int(0.45 * SR)
        x = sine_glide(n, 900, 180, 0.6) * env(n, 0.003, 0.14)
        x = np.round(x * 12) / 12  # light bitcrush
        x = lp(x, 3000)
    elif kind == "glitch":
        n = int(0.28 * SR)
        x = bp(noise(n), 800, 6000) * (rng.random(n // 400 + 1).repeat(400)[:n] > 0.55) * env(n, 0.001, 0.12)
        x += 0.4 * np.sign(np.sin(2 * np.pi * 120 * np.arange(n) / SR)) * env(n, 0.001, 0.05)
        x = lp(x, 5000)
    elif kind in ("whoosh", "whoosh_soft"):
        n = int(0.75 * SR)
        e = np.sin(np.linspace(0, np.pi, n)) ** 2
        nz = noise(n)
        lo = bp(nz, 300, 1500); hi = bp(nz, 1500, 6000)
        mix = np.linspace(0, 1, n)
        x = (lo * (1 - mix) + hi * mix * 0.6) * e
        if kind == "whoosh_soft":
            x = lp(x, 2500)
    elif kind == "riser":
        n = int(0.9 * SR)
        e = np.linspace(0, 1, n) ** 2.5
        x = hp(noise(n), 1500) * e * 0.5 + 0.5 * sine_glide(n, 200, 800, 0.5) * e
        x = lp(x, 7000)
        x[-int(0.02 * SR):] *= np.linspace(1, 0, int(0.02 * SR))
    elif kind in ("impact_soft", "impact_deep"):
        deep = kind == "impact_deep"
        n = int((2.4 if deep else 1.2) * SR)
        x = sine_glide(n, 120 if deep else 160, 42 if deep else 60, 0.25) * env(n, 0.002, 0.45 if deep else 0.22)
        x += 0.35 * lp(noise(n), 900) * env(n, 0.001, 0.05)
        x += (0.25 if deep else 0.12) * bp(noise(n), 200, 2000) * env(n, 0.01, 0.6 if deep else 0.3)
    elif kind == "pulse":
        n = int(1.0 * SR); t = np.arange(n) / SR
        x = np.sin(2 * np.pi * 110 * t) * env(n, 0.01, 0.25) * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * t))
        x += 0.3 * np.sin(2 * np.pi * 220 * t) * env(n, 0.01, 0.15)
    elif kind == "process":
        n = int(1.2 * SR); t = np.arange(n) / SR
        gate = (np.sin(2 * np.pi * 14 * t) > 0.3).astype(np.float32)
        x = np.sin(2 * np.pi * (1400 + 300 * np.sin(2 * np.pi * 3 * t)) * t) * gate * env(n, 0.05, 0.5) * 0.4
        x = lp(x, 4000)
    else:
        raise ValueError(kind)
    return norm(x.astype(np.float32))


sfx_tr = np.zeros(N, np.float32)
for s in tl["scenes"]:
    for t0, kind, g in s["sfx"]:
        x = sfx(kind) * 10 ** (g / 20)
        i0 = int(t0 * SR)
        if kind == "riser":  # riser ends on its cue
            i0 -= len(x) - int(0.6 * SR)
        i0 = max(0, i0)
        sfx_tr[i0:i0 + len(x)] += x[: N - i0]

# ---------------------------------------------------------------- MUSIC
BPM = 100
BEAT = 60 / BPM
BAR = BEAT * 4
mid = lambda m: 440 * 2 ** ((m - 69) / 12)
CHORDS = [  # D minor, airy voicings
    [50, 57, 60, 64, 69],   # Dm9 (no 3rd -> open)
    [46, 53, 57, 60, 65],   # Bbmaj7(add9)
    [43, 50, 53, 57, 62],   # Gm9
    [45, 52, 57, 59, 64],   # Asus2/add4
]
FINAL = [50, 57, 62, 64, 69]  # resolve

S = {s["id"]: s for s in tl["scenes"]}
cue = lambda sid, k: S[sid]["cues"][k]

# energy keyframes (time, energy 0..1)
E_KEYS = [(0, 0.0), (0.4, 0.35), (S["02"]["start"], 0.45), (S["03"]["start"], 0.52),
          (S["04"]["start"] - 0.9, 0.5), (S["04"]["start"] - 0.5, 0.18), (cue("04", "server"), 0.75),
          (S["05"]["start"], 0.75), (S["06"]["start"], 0.85), (S["07"]["start"] - 0.2, 0.85),
          (S["07"]["start"] + 0.8, 0.55), (S["08"]["start"], 0.65), (cue("08", "pause") - 0.1, 0.65),
          (cue("08", "pause") + 0.25, 0.10), (cue("08", "losing") - 0.02, 0.10), (cue("08", "losing") + 0.05, 0.95),
          (S["09"]["start"] - 0.1, 0.8), (S["09"]["start"] + 0.8, 0.42), (TOTAL - 3.0, 0.4), (TOTAL, 0.0)]
tt = np.arange(N) / SR
energy = np.interp(tt, [k[0] for k in E_KEYS], [k[1] for k in E_KEYS]).astype(np.float32)
groove_on = ((tt >= cue("04", "server")) & (tt < S["07"]["start"])) | \
            ((tt >= cue("08", "losing")) & (tt < S["09"]["start"] + 0.2))
groove = lp(groove_on.astype(np.float32), 3).astype(np.float32)

pad = np.zeros(N, np.float32)
bass = np.zeros(N, np.float32)
arp = np.zeros(N, np.float32)
nbars = int(np.ceil(TOTAL / BAR))
final_bar_t = (nbars - 2) * BAR
for b in range(nbars):
    ch = FINAL if b * BAR >= final_bar_t else CHORDS[b % 4]
    i0 = int(b * BAR * SR); i1 = min(N, int((b + 1) * BAR * SR) + int(0.4 * SR))
    if b * BAR >= final_bar_t:
        i1 = N
    n = i1 - i0
    t = np.arange(n) / SR
    fade = np.minimum(1, t / 0.35) * np.minimum(1, (n - np.arange(n)) / SR / 0.4)
    seg = np.zeros(n, np.float32)
    for m in ch:
        for det in (-0.06, 0.0, 0.07):
            f = mid(m + det)
            for h in range(1, 6):
                seg += np.sin(2 * np.pi * f * h * t + rng.random() * 6.28) / (h ** 1.4)
    pad[i0:i1] += seg * fade * 0.03
    fb = mid(ch[0] - 12)
    bass[i0:i1] += (np.sin(2 * np.pi * fb * t) + 0.25 * np.sin(4 * np.pi * fb * t)) * fade * 0.25
    # 8th-note pluck arpeggio
    tones = [ch[1] + 12, ch[2] + 12, ch[3] + 12, ch[4] + 12, ch[3] + 12, ch[2] + 12, ch[4] + 12, ch[1] + 24]
    for k in range(8):
        j0 = i0 + int(k * BEAT / 2 * SR)
        nn = int(0.6 * SR)
        if j0 >= N:
            break
        nn = min(nn, N - j0)
        tk = np.arange(nn) / SR
        f = mid(tones[k])
        p = (np.sin(2 * np.pi * f * tk) + 0.35 * np.sin(4 * np.pi * f * tk) + 0.1 * np.sin(6 * np.pi * f * tk))
        arp[j0:j0 + nn] += p * np.exp(-tk / 0.16) * np.minimum(1, tk / 0.003) * (0.9 if k % 2 == 0 else 0.6) * 0.09

# pad filter brightness follows energy (two-band crossfade)
pad_dark = lp(pad, 700); pad_bright = lp(pad, 3200)
pad_f = pad_dark * (1 - energy) + pad_bright * energy
# simple stereo-ish ping delay on arp (mono out)
d = int(BEAT * 0.75 * SR)
arp_d = arp.copy()
for rep in range(1, 4):
    arp_d[d * rep:] += arp[:-d * rep] * (0.35 ** rep)
arp_d = lp(arp_d, 5000)

# drums (soft)
kick = np.zeros(N, np.float32); hat = np.zeros(N, np.float32)
kn = int(0.4 * SR)
ks = sine_glide(kn, 140, 45, 0.15) * env(kn, 0.001, 0.12)
hn = int(0.08 * SR)
hs = hp(noise(hn), 7000) * env(hn, 0.0005, 0.018)
nb = int(TOTAL / BEAT)
for b in range(nb):
    i0 = int(b * BEAT * SR)
    if i0 + kn < N: kick[i0:i0 + kn] += ks
    j0 = int((b + 0.5) * BEAT * SR)
    if j0 + hn < N: hat[j0:j0 + hn] += hs
music = (pad_f * (0.55 + 0.45 * energy) + bass * lp(energy, 2) * 0.9 + arp_d * np.clip(energy * 1.3 - 0.15, 0, 1)
         + (kick * 0.55 + hat * 0.12) * groove * energy)
# global music level follows energy softly
music *= (0.35 + 0.65 * energy)
music = norm(music, 0.5)
# subtle reverb via ffmpeg
wavfile.write(f"{OUT}/music_dry.wav", SR, music.astype(np.float32))
sh(f"ffmpeg -v error -y -i {OUT}/music_dry.wav -af \"aecho=0.85:0.6:73|131|211:0.28|0.2|0.12\" {OUT}/music_wet.wav")
music = read(f"{OUT}/music_wet.wav")[:N]
music = np.pad(music, (0, N - len(music)))
music *= np.minimum(1, np.minimum(tt / 0.4, (TOTAL - tt) / 2.0))  # fades
music = music / (np.sqrt(np.mean(music ** 2)) + 1e-9) * 10 ** (-20 / 20)  # RMS -20 dBFS
music = np.clip(music, -0.98, 0.98)

# ---------------------------------------------------------------- DUCK + MIX
a = np.abs(vo)
k = int(0.02 * SR)
venv = np.convolve(a, np.ones(k) / k, "same")
speaking = (venv > 0.01).astype(np.float32)
# smooth attack 60ms / release 350ms
duck = np.zeros(N, np.float32); g = 0.0
att, rel = np.exp(-1 / (0.06 * SR)), np.exp(-1 / (0.35 * SR))
sp = speaking
for i in range(0, N, 48):  # control rate 1 kHz
    target = sp[i]
    c = att ** 48 if target > g else rel ** 48
    g = target + (g - target) * c
    duck[i:i + 48] = g
music_gain = 10 ** (-9 / 20) * (1 - 0.55 * duck)   # music bed ~-29 dBFS RMS, ducks a further ~7 dB under voice
mix = vo * 1.0 + sfx_tr * 0.9 + music * music_gain
wavfile.write(f"{OUT}/vo.wav", SR, vo)
wavfile.write(f"{OUT}/sfx.wav", SR, sfx_tr)
wavfile.write(f"{OUT}/music.wav", SR, (music * music_gain).astype(np.float32))
wavfile.write(f"{OUT}/mix_pre.wav", SR, mix.astype(np.float32))
# master: social-ready loudness
m = json.loads(sh(f"ffmpeg -i {OUT}/mix_pre.wav -af loudnorm=I=-14:TP=-1.2:LRA=9:print_format=json -f null -")
               .split("[Parsed_loudnorm")[-1].split("\n", 1)[1])
sh(f"ffmpeg -v error -y -i {OUT}/mix_pre.wav -af \"loudnorm=I=-14:TP=-1.2:LRA=9:measured_I={m['input_i']}:"
   f"measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
   f"offset={m['target_offset']}:linear=true,alimiter=limit=0.89:level=false\" -ar 48000 -ac 2 {OUT}/final_mix.wav")
print("audio done", TOTAL)
