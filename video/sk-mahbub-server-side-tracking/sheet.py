import sys,glob
from PIL import Image, ImageDraw
fs=sorted(glob.glob(sys.argv[1]+'/*.jpg'),key=lambda f:float(f.split('_')[-1][:-4]))
cols=int(sys.argv[3]) if len(sys.argv)>3 else 4; w,h=360,640
rows=(len(fs)+cols-1)//cols
sh=Image.new('RGB',(cols*w,rows*(h+24)),(40,40,40));d=ImageDraw.Draw(sh)
for i,f in enumerate(fs):
    im=Image.open(f).resize((w,h));x,y=(i%cols)*w,(i//cols)*(h+24)
    sh.paste(im,(x,y+24));d.text((x+6,y+5),f.split('_')[-1][:-4],fill=(255,255,0))
sh.save(sys.argv[2],quality=88)
