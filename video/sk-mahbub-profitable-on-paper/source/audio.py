import numpy as np, scipy.io.wavfile as wf
from scipy.signal import butter, sosfilt
SR=48000; O2=31.552; O3=87.168; END=O3+38.635+3.4
N=int(END*SR)+SR
rng=np.random.default_rng(7)
def env(n,a,d):  # attack seconds, exp decay tau
    t=np.arange(n)/SR; e=np.exp(-t/d); at=np.clip(t/max(a,1e-4),0,1); return e*at
def lp(x,f,o=2): return sosfilt(butter(o,f,'low',fs=SR,output='sos'),x)
def hp(x,f,o=2): return sosfilt(butter(o,f,'high',fs=SR,output='sos'),x)
def bp(x,f1,f2): return sosfilt(butter(2,[f1,f2],'band',fs=SR,output='sos'),x)
def sine(f,n,ph=0): t=np.arange(n)/SR; return np.sin(2*np.pi*f*t+ph)
# ---- SFX palette ----
def click(g=1):
    n=int(.05*SR); x=bp(rng.standard_normal(n),2500,7000)*env(n,.0005,.006); x+=sine(1800,n)*env(n,.0005,.01)*.4; return x*.35*g
def pop(f=880,g=1):
    n=int(.18*SR); t=np.arange(n)/SR; fr=f*(1+.35*np.exp(-t/.015)); ph=2*np.pi*np.cumsum(fr)/SR
    return (np.sin(ph)*env(n,.002,.045)+.25*np.sin(2*ph)*env(n,.001,.02))*.32*g
def confirm(f=1046.5,g=1):
    n=int(.5*SR); a=sine(f,n)*env(n,.003,.12); b=np.zeros(n); k=int(.07*SR); b[k:]=sine(f*1.5,n-k)*env(n-k,.003,.16)
    return (a+b*.8)*.17*g
def swoosh(g=1,d=.45):
    n=int(d*SR); x=rng.standard_normal(n); t=np.arange(n)/SR
    e=np.sin(np.pi*np.clip(t/d,0,1))**2; x=bp(x,600,3500)*e; return x*.06*g
def thud(g=1):
    n=int(.6*SR); t=np.arange(n)/SR; fr=50+60*np.exp(-t/.04); ph=2*np.pi*np.cumsum(fr)/SR
    return np.sin(ph)*env(n,.003,.18)*.45*g
def impact(g=1):
    x=thud(1.1); c=np.zeros_like(x); m=confirm(784,1.0); c[:len(m)]+=m; n=len(x)
    sh=lp(rng.standard_normal(n),5000)*env(n,.001,.25)*.02
    return (x*.8+c*1.1+sh)*g
def tick(g=1): return pop(1500,.45*g)
sfx=np.zeros((N,))
def at(t,x):
    i=int(t*SR); sfx[i:i+len(x)]+=x[:max(0,N-i)]
S1=[(0.1,swoosh()),(0.15,pop(660,.8))]+[(0.45+i*.14,click()) for i in range(4)]+[(1.6,pop(990,.8)),(4.38,pop(520,1.0)),(4.4,swoosh(.6))]
S1+=[(x,pop(1175,.9)) for x in (15.12,16.02,16.82,17.56)]
S1+=[(19.65,swoosh(1.1,.7)),(20.9,pop(740)),(21.1,click(.7)),(22.5,pop(620,.8)),(26.9,tick(1.0)),(28.5,pop(880,.6)),(29.3,pop(660,.7))]
S2=[(0.5,swoosh(1,.6)),(0.6,pop(700,.8)),(1.0,pop(800,.8)),(4.9,click()),(5.1,click(.6)),(9.7,click()),(9.9,click(.6)),(14.2,pop(1046,.9)),(16.8,thud(.9))]
S2+=[(19.5+i*.05,click(.25)) for i in range(20)]+[(22.1,confirm(1046.5,.9)),(22.23,confirm(1318.5,.6))]
S2+=[(25.3,pop(780,.8)),(26.2,confirm(880,1))]+[(31.2+i*.05,click(.25)) for i in range(20)]
S2+=[(34.6+i*.13,confirm(1046.5+i*60,.55)) for i in range(6)]+[(39.2,pop(780,.8)),(41.94,impact(.8)),(42.0,confirm(1318.5,.7))]
S2+=[(43.3,swoosh(1,.7)),(44.0,pop(700,.8)),(44.45,pop(820,.8)),(47.7,thud(.8)),(47.72,confirm(988,.6)),(50.6,pop(1100,.5)),(53.3,pop(1200,.5))]
S3=[(0.4,swoosh(1,.7)),(0.95,pop(700,.8)),(4.1,tick())]+[(x,pop(620+i*90,.8)) for i,x in enumerate((5.3,6.5,7.7,8.55,10.8))]
S3+=[(10.8,confirm(1046.5,.7)),(9.4,click(.6)),(10.9,click(.6)),(11.9,swoosh(1,.6)),(12.2,pop(700,.8)),(13.6,pop(820,.8))]+[(13.9+i*.16,click(.5)) for i in range(5)]
S3+=[(14.4,confirm(1046.5,.7)),(15.3,confirm(1174.7,.7)),(16.5,confirm(1318.5,.8)),(16.9,click(.7)),(18.5,swoosh(.6,.8)),(21.4,swoosh(1,.6)),(21.95,pop(600,1.0))]
S3+=[(24.9,swoosh(1,.8)),(26.05,impact(1.0)),(29.1,tick()),(30.7,tick()),(31.9,tick()),(32.9,pop(900,.7)),(34.4,swoosh(1,.7)),(34.85,pop(660,.6)),(36.7,confirm(784,.8)),(36.82,confirm(1174.7,.6))]
for o,lst in ((0,S1),(O2,S2),(O3,S3)):
    for t,x in lst: at(o+t,x)
# ---- music: minimal, 100 BPM ----
bpm=100; beat=60/bpm; bar=4*beat
mus=np.zeros(N); drums=np.zeros(N)
def mtof(m): return 440*2**((m-69)/12)
chords=[[57,60,64,67,71],[53,57,60,64,67],[48,52,55,59,64],[55,59,62,64,69]]  # Am9 Fmaj7 Cmaj7 G6/9
nb=int(END/bar)+2
for b in range(nb):
    ch=chords[(b//2)%4]; t0=b*bar
    if b%2==0:  # pad over two bars
        n=int(2*bar*SR); tt=np.arange(n)/SR
        e=np.clip(tt/1.2,0,1)*np.clip((2*bar-tt)/1.0,0,1)
        p=sum(np.sin(2*np.pi*mtof(m)*tt)+.5*np.sin(2*np.pi*mtof(m)*1.003*tt) for m in ch[:4])
        p=lp(p*e,1800)*.022
        i=int(t0*SR); mus[i:i+n]+=p[:max(0,N-i)]
        bn=sine(mtof(ch[0]-12),n)*e*.05; mus[i:i+n]+=lp(bn,400)[:max(0,N-i)]
    # arpeggio 8ths
    for k in range(8):
        m=ch[[0,2,4,1,3,2,4,3][k]]+12; n=int(.5*SR); tt=np.arange(n)/SR
        tone=(np.sin(2*np.pi*mtof(m)*tt)+.3*np.sin(4*np.pi*mtof(m)*tt))*env(n,.004,.16)*.035
        i=int((t0+k*beat/2)*SR); mus[i:i+n]+=tone[:max(0,N-i)]
    for k in range(4):  # soft kick 1&3, rim tick 2&4, hats 8ths
        i=int((t0+k*beat)*SR)
        if k%2==0:
            n=int(.3*SR); tt=np.arange(n)/SR; ph=2*np.pi*np.cumsum(45+70*np.exp(-tt/.03))/SR
            x=np.sin(ph)*env(n,.002,.09)*.16; drums[i:i+n]+=x[:max(0,N-i)]
        else:
            n=int(.08*SR); x=bp(rng.standard_normal(n),1500,4000)*env(n,.001,.02)*.05; drums[i:i+n]+=x[:max(0,N-i)]
        for h in (0,1):
            j=int((t0+k*beat+h*beat/2)*SR); n=int(.05*SR)
            x=hp(rng.standard_normal(n),7000)*env(n,.0005,.012)*(.022 if h else .014); drums[j:j+n]+=x[:max(0,N-j)]
tt=np.arange(N)/SR
def gate(ranges):
    g=np.ones(N)
    for a,b in ranges:
        g*=1-np.clip((tt-a)/.3,0,1)*np.clip((b+.3-tt)/.3,0,1)
    return np.clip(g,0,1)
# drums: enter softly in hook after 6s; drop out for "But here's the problem" pause and the final CTA
dg=np.clip((tt-6)/3,0,1)*.6+np.clip((tt-O2)/2,0,1)*.4
dg*=gate([(O2+16.6,O2+18.6),(O3+21.8,O3+25.0),(O3+34.6,END+5)])
mus=mus+drums*dg
fade=np.clip(tt/2.0,0,1)*np.clip((END-tt)/3.0,0,1)
mus*=fade
st=np.stack([mus,mus],1)
# slight stereo width on sfx
sf=np.stack([sfx,np.roll(sfx,int(.0004*SR))],1)
wf.write('music.wav',SR,(st/np.max(np.abs(st))*.5).astype(np.float32))
wf.write('sfx.wav',SR,(sf/np.max(np.abs(sf))*.5).astype(np.float32))
print('END',END)
