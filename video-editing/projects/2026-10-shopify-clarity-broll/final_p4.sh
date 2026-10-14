set -e
cd "$(dirname "$0")"
rm -f clip_p4_*.mp4 mix_p4.wav
python3 -I edit_p4.py audio
TOT=$(python3 -I -c "import sys; sys.argv=['x','audio']; sys.path.insert(0,'.'); import edit_p4 as E; print(int(round(E.TOTAL*30)))" 2>/dev/null | tail -1)
N=4; RC=$(( (TOT + N - 1) / N ))
for i in $(seq 0 $((N-1))); do a=$((i*RC)); b=$(( (i+1)*RC )); [ $b -gt $TOT ] && b=$TOT
  python3 -I edit_p4.py clip $(python3 -c "print(f'{$a/30:.6f}')") $(python3 -c "print(f'{$b/30:.6f}')") > rd_$i.txt 2>&1 & done; wait
ls clip_p4_*.mp4 | sort -t_ -k3 -n | sed "s/.*/file '&'/" > rd_list.txt
ffmpeg -v error -y -f concat -safe 0 -i rd_list.txt -i mix_p4.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart final_p4.mp4
ffmpeg -v error -y -i final_p4.mp4 -c:v libx264 -crf 21 -maxrate 4.4M -bufsize 9M -preset medium -c:a aac -b:a 160k -movflags +faststart Shopify_Clarity_Final.mp4
ffprobe -v error -show_entries format=duration,size -of compact Shopify_Clarity_Final.mp4
echo FINAL_READY
