# The Phone Call Black Hole — explainer video

Code-rendered motion graphics locked to the recorded voiceover. Storyboard: `../docs/video/call-tracking-explainer-storyboard.md`.

## Outputs (`out/`)
- `call-tracking-explainer_16x9.mp4`: 1920×1080, 30 fps, 71.5 s (YouTube, LinkedIn, Facebook, website)
- `call-tracking-explainer_9x16.mp4`: 1080×1920, 30 fps, 71.5 s, captions burned in (Reels, Shorts, TikTok)
- Audio: voiceover + synthesized sound design + music bed, mastered to about −14.7 LUFS and −1.3 dBTP

## Rebuild
```bash
export NODE_PATH=$(npm root -g)          # needs playwright + ffmpeg
node render.cjs video h out/_h_silent.mp4
node render.cjs video v out/_v_silent.mp4 --caps
python3 audio/build_audio.py assets/voiceover.m4a out/mix_raw.wav   # needs numpy + scipy
ffmpeg -i out/mix_raw.wav -af "volume=7.3dB,alimiter=limit=0.78:attack=2:release=60:level=disabled" out/mix.wav
ffmpeg -i out/_h_silent.mp4 -i out/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest out/call-tracking-explainer_16x9.mp4
```
Preview single frames: `node render.cjs stills h <dir> 12.5 30 --caps`.

## Changing things
- Brand colors: `src/palette.js` (provisional values; swap in the official hex codes and re-render).
- Timing and captions: `src/timeline.js`. The voiceover starts at 0.50 s.
- Scenes: `src/scenes.js`, one function per storyboard scene.
