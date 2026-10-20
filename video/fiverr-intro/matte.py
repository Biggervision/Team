import torch, subprocess, numpy as np, sys
W,H=1920,1080
m=torch.jit.load(sys.argv[1]).eval(); torch.set_num_threads(4)
dec=subprocess.Popen(["ffmpeg","-v","error","-i",sys.argv[2],"-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","gray","-s",f"{W}x{H}","-r","30","-i","-","-c:v","libx264","-crf","12","-pix_fmt","yuv420p",sys.argv[3]],stdin=subprocess.PIPE)
rec=[None]*4; n=0
with torch.no_grad():
    while True:
        b=dec.stdout.read(W*H*3)
        if len(b)<W*H*3: break
        x=torch.from_numpy(np.frombuffer(b,np.uint8).reshape(H,W,3).copy()).permute(2,0,1)[None].float()/255
        fgr,pha,*rec=m(x,*rec,downsample_ratio=0.25)
        enc.stdin.write((pha[0,0].clamp(0,1)*255).byte().numpy().tobytes()); n+=1
        if n%200==0: print(n,flush=True)
enc.stdin.close(); enc.wait(); print("done",n)
