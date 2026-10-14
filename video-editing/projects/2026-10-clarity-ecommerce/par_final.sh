set -e
cd "$(dirname "$0")"
N=4; F=1380; C=$(( (F + N - 1) / N ))
rm -f sk_part_*.mov skin_part_*.mov clip_p2_*.mp4 mix_p2.wav
# 1) split graded base into 4 frame-exact chunks
for i in $(seq 0 $((N-1))); do
  a=$((i*C)); b=$(( (i+1)*C )); [ $b -gt $F ] && b=$F
  ffmpeg -v error -y -i base2.mov -vf "trim=start_frame=$a:end_frame=$b,setpts=PTS-STARTPTS" -af "atrim=start=$(python3 -c "print($a/30)"):end=$(python3 -c "print($b/30)"),asetpts=PTS-STARTPTS" -c:v libx264 -crf 10 -preset ultrafast -c:a pcm_s16le sk_part_$i.mov
done
# 2) skin pass in parallel
for i in $(seq 0 $((N-1))); do python3 -I ../skin.py sk_part_$i.mov skin_part_$i.mov > sk_log_$i.txt 2>&1 & done; wait
grep -h "^done" sk_log_*.txt
for i in $(seq 0 $((N-1))); do echo "file 'skin_part_$i.mov'"; done > sk_list.txt
ffmpeg -v error -y -f concat -safe 0 -i sk_list.txt -an -c:v libx264 -crf 14 -preset fast -pix_fmt yuv420p base2_skin_v.mov
mv base2.mov base2_noskin2.mov; mv base2_skin_v.mov base2.mov
echo "skin done: $(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 base2.mov) frames"
# 3) audio mix once, then 4 render workers
python3 -I -c "import sys; sys.argv=['edit_p2.py']; sys.path.insert(0,'.'); import edit_p2 as E; E.build_audio(); print('mix ok', E.TOTAL)"
TOT=$(python3 -I -c "import sys; sys.argv=['edit_p2.py']; sys.path.insert(0,'.'); import edit_p2 as E; print(int(round(E.TOTAL*30)))")
RC=$(( (TOT + N - 1) / N ))
for i in $(seq 0 $((N-1))); do
  a=$((i*RC)); b=$(( (i+1)*RC )); [ $b -gt $TOT ] && b=$TOT
  python3 -I edit_p2.py clip $(python3 -c "print(f'{$a/30:.6f}')") $(python3 -c "print(f'{$b/30:.6f}')") > rd_log_$i.txt 2>&1 &
done; wait
ls clip_p2_*.mp4 | sort -t_ -k3 -n | sed "s/.*/file '&'/" > rd_list.txt; cat rd_list.txt
ffmpeg -v error -y -f concat -safe 0 -i rd_list.txt -i mix_p2.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart final_p2.mp4
ffprobe -v error -show_entries format=duration,size -of compact final_p2.mp4
ffmpeg -v error -y -i final_p2.mp4 -c:v libx264 -b:v 4200k -preset medium -pass 1 -an -f null /dev/null
ffmpeg -v error -y -i final_p2.mp4 -c:v libx264 -b:v 4200k -preset medium -pass 2 -c:a aac -b:a 160k -movflags +faststart Clarity_Final.mp4
ls -la Clarity_Final.mp4; echo FINAL_READY
