import json,subprocess
k=json.load(open("cut.json"))["keep"]
GRADE="colortemperature=temperature=5300:mix=1,colorbalance=rs=0.02:bs=-0.06:rm=0.03:bm=-0.06:rh=0.02:bh=-0.04,eq=contrast=1.12:saturation=1.10:gamma=0.95,curves=all='0/0 0.12/0.07 0.5/0.5 0.9/0.86 1/0.94',vignette=PI/4.2"
f=[]
for i,(s,e) in enumerate(k):
    z=1.0
    w=round(608/z/2)*2;h=round(1080/z/2)*2;x=995-w//2;y=int((1080-h)*0.3)
    f.append(f"[0:v]trim={s:.3f}:{e:.3f},setpts=PTS-STARTPTS,crop={w}:{h}:{x}:{y},scale=1080:1920:flags=lanczos,setsar=1[v{i}]")
    f.append(f"[0:a]atrim={s:.3f}:{e:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={e-s-0.015:.3f}:d=0.015[a{i}]")
n=len(k)
f.append("".join(f"[v{i}][a{i}]" for i in range(n))+f"concat=n={n}:v=1:a=1[cv][ca]")
f.append(f"[cv]{GRADE},format=yuv420p[ov]")
f.append("[ca]highpass=f=80,equalizer=f=250:t=q:w=1:g=-2,equalizer=f=3500:t=q:w=1.2:g=2.5,acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=2,loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000[oa]")
subprocess.run(["ffmpeg","-v","error","-y","-i","src/in.mp4","-filter_complex",";".join(f),"-map","[ov]","-map","[oa]","-c:v","libx264","-crf","14","-preset","fast","-r","30","-c:a","pcm_s16le","base2.mov"],check=True)
