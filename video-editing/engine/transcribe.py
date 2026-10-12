import json,sys
from faster_whisper import WhisperModel
m=WhisperModel("medium",device="cpu",compute_type="int8",cpu_threads=4)
import numpy as np,wave
w_=wave.open(sys.argv[1]);a=np.frombuffer(w_.readframes(w_.getnframes()),np.int16).astype(np.float32)/32768
segs,info=m.transcribe(a,word_timestamps=True,vad_filter=True)
out=[]
for s in segs:
    out.append({"start":s.start,"end":s.end,"text":s.text,"words":[{"w":w.word,"s":w.start,"e":w.end} for w in s.words]})
    print(f"[{s.start:6.2f}-{s.end:6.2f}]{s.text}",flush=True)
json.dump({"lang":info.language,"segs":out},open(sys.argv[2],"w"))
print("LANG",info.language)
