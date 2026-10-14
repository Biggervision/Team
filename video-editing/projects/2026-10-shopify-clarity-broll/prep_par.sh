set -e
cd "$(dirname "$0")"
F=$(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 src/in.mp4); N=4; C=$(( (F + N - 1) / N ))
for i in $(seq 0 $((N-1))); do a=$((i*C)); b=$(( (i+1)*C )); [ $b -gt $F ] && b=$F
  ffmpeg -v error -y -i src/in.mp4 -vf "trim=start_frame=$a:end_frame=$b,setpts=PTS-STARTPTS" -an -c:v libx264 -crf 10 -preset ultrafast pp_in_$i.mov; done
for i in $(seq 0 $((N-1))); do python3 -I prep4.py pp_in_$i.mov pp_out_$i.mov > pp_log_$i.txt 2>&1 & done; wait
grep -h "^done" pp_log_*.txt
for i in $(seq 0 $((N-1))); do echo "file 'pp_out_$i.mov'"; done > pp_list.txt
ffmpeg -v error -y -f concat -safe 0 -i pp_list.txt -c:v libx264 -crf 12 -preset fast -pix_fmt yuv420p prep.mov
python3 -I base_p4.py
echo PREP_BASE_DONE
