# SK Mahbub — Server-Side Tracking (9:16 social video)

**Final render:** `SK_Mahbub_Server_Side_Tracking_9x16.mp4` (1080×1920, 30 fps, H.264 + AAC, 90 s, −14 LUFS)

## Inputs
- `voiceover/raw_01..09.wav`: SK Mahbub's original voice-over (SCENE_01–09). This is the source of truth for timing.
- `assets/portrait.jpg`: original portrait, shown uncropped-aspect and unaltered (only framed and masked).
- Brand palette sampled from the website screenshot: base `#04090B`, teal accent `#19C3B1`.

## Pipeline
1. `timeline.py`: scene placement, word-level visual cues, SFX cues (measured from the voice-over) → `timeline.json`
2. `audio.py`: voice clean-up only (HPF, light denoise, EQ, de-ess, compression, loudness match; **no pitch/formant/voice change**), original synthesized SFX and score, music ducked under the voice, master → `build/final_mix.wav`
3. `engine.js` + `index.html`: deterministic canvas motion-graphics renderer (`renderFrame(t)`)
4. `render.js`: headless Chromium → PNG frames → x264

```bash
pip install numpy scipy pillow
python3 timeline.py && python3 audio.py
for i in 0 1 2 3; do node render.js video $((i*675)) $(((i+1)*675)) build/seg/s$i.mp4 & done; wait
printf "file 'seg/s%d.mp4'\n" 0 1 2 3 > build/list.txt
ffmpeg -f concat -safe 0 -i build/list.txt -c copy build/video_only.mp4
ffmpeg -i build/video_only.mp4 -i build/final_mix.wav -map 0:v -map 1:a -c:v copy -af volume=1.3dB -c:a aac -b:a 256k -movflags +faststart -shortest out.mp4
```
Preview stills: `node render.js stills out_dir 5 20 33`
