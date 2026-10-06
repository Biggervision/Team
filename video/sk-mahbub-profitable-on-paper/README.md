# Profitable on Paper — SK Mahbub

An animated educational video in the style of a SaaS analytics product video. It is built on the recorded voiceover (Scene 01–03), which is the master timeline: nothing in it was cut, reordered or rewritten.

| File | Format | Use |
|---|---|---|
| `SK-Mahbub_Profitable-on-Paper_16x9_1920x1080.mp4` | 1920×1080, H.264/AAC, 30 fps, 2:09 | YouTube, LinkedIn, Facebook, website embeds |
| `SK-Mahbub_Profitable-on-Paper_9x16_1080x1920.mp4` | 1080×1920, H.264/AAC, 30 fps, 2:09 | Reels, Shorts, TikTok |

**Ownership:** the "SK Mahbub — Web Analytics & Conversion Tracking Consultant" signature stays on screen for the whole video and closes it as the end card. The name is also written into the MP4 metadata (artist, copyright and comment fields).

## Source (`source/`)
- `render.js`: a deterministic canvas renderer. Both layouts share one timeline, keyed to word timestamps.
- `capture.js`: drives headless Chromium and pipes the frames to ffmpeg.
- `audio.py`: synthesizes the UI sound effects and the minimal 100 BPM music bed.
- `words.json`: Whisper word timestamps for the voiceover.

To rebuild, put the Inter variable font in `source/fonts/InterVariable.ttf` and the voiceover as `s1.m4a`, `s2.m4a` and `s3.m4a`. Then run `node capture.js l|v video <start> <end> out.mp4` and mux the result with the mix.
