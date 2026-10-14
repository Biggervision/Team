import json, subprocess
d = json.load(open("cut.json"))
GRADE = "colortemperature=temperature=7200:mix=0.7,colorbalance=rs=-0.02:bs=0.03:rm=-0.03:bm=0.02,eq=contrast=1.10:saturation=1.12:gamma=1.0,curves=all='0/0 0.25/0.22 0.5/0.5 0.75/0.78 1/0.97',vignette=PI/4.5"
VOICE = "highpass=f=80,equalizer=f=250:t=q:w=1:g=-2,equalizer=f=3500:t=q:w=1.2:g=2.5,acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=2"
f = []
for i, (_, s, e) in enumerate(d["src"]):
    f.append(f"[0:v]trim={s:.3f}:{e:.3f},setpts=PTS-STARTPTS,setsar=1[v{i}]")
    f.append(f"[1:a]atrim={s:.3f}:{e:.3f},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=mono,afade=t=in:d=0.015,afade=t=out:st={e-s-0.015:.3f}:d=0.015[a{i}]")
n = len(d["src"])
f.append("".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[cv][ca]")
f.append(f"[cv]{GRADE},format=yuv420p[ov]")
f.append(f"[ca]{VOICE},loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000[oa]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "prep.mov", "-i", "src/in.mp4", "-filter_complex", ";".join(f),
                "-map", "[ov]", "-map", "[oa]", "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-r", "30", "-c:a", "pcm_s16le", "base2.mov"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "base2.mov", "-vn", "-c:a", "pcm_s16le", "-ac", "1", "base2_audio.wav"], check=True)
print("base done")
