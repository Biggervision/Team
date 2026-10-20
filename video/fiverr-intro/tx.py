import json,sys
from faster_whisper import WhisperModel
m=WhisperModel("small.en",device="cpu",compute_type="int8")
import numpy as np
segs,_=m.transcribe(np.fromfile(sys.argv[1],dtype=np.float32),word_timestamps=True,beam_size=5)
out=[]
for s in segs:
    print(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text}")
    for w in s.words: out.append([round(w.start,2),round(w.end,2),w.word])
json.dump(out,open(sys.argv[2],"w"))
