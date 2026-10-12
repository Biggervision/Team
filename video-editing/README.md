# Video editing system: SK Mahbub personal brand

A reusable pipeline that reproduces the approved edit style on every new talking-head video.

- `MASTER_PROMPT.md`: the creative brief (the source of truth)
- `STYLE_GUIDE.md`: the locked technical values (fonts, sizes, colours, timings, grade, mix)
- `engine/`: the scripts that produced the approved edit
- `covers/`: the 9:16 text-only Reel cover generators

## Per-video workflow
Run everything from a working folder that contains `src/in.mp4` (the raw video).

```bash
pip install faster-whisper opencv-python-headless pillow numpy scipy
bash engine/fetch_fonts.sh                                   # -> fonts/
ffmpeg -i src/in.mp4 -ac 1 -ar 16000 src/audio16.wav
python3 engine/transcribe.py src/audio16.wav src/words.json  # word-level timestamps
python3 engine/cuts.py                                       # -> cut.json (pause trimming + remapped word times)
python3 engine/render_base.py                                # -> base2.mov (crop, grade, voice chain)
ffmpeg -i base2.mov -vn -c:a pcm_s16le -ac 1 base2_audio.wav
python3 engine/edit_master.py preview 1.0 5.0 20.0           # stills to check layout
python3 engine/edit_master.py                                # -> final4.mp4
```

## What to change for each new video (the content plan)
Edit only the **content plan** block near the top of `engine/edit_master.py`. Indexes are word positions printed by `cuts.py`.

| Variable | Purpose |
|---|---|
| `KW` | keyword word-indexes shown big/bold (style field: `pop`/`slide`/`highlight`/`shake` all render the same clean scale-in; `count` = animated number) |
| `COUNT` | start/end values + format for animated numbers |
| `ITAL` | words shown in the serif italic accent |
| `ZOOM` | word-indexes that get a punch-in, with strength |
| `COUNTER` + `counter()` | the topic-specific number scene (was $3,000–$4,000 ad spend; replace per topic) |
| `CARDS` | branded canvas scenes: `wave`, `list` (with items), `no` (statement) |
| `FIX` | transcript spelling fixes |

Also set per video:
- `render_base.py`: crop x-offset (`691` = face centre 995 − 304) for the new framing
- `edit_master.py`: `FACE` zoom centre if the framing differs

Content-specific graphics (counter, list items, card words) must be replaced to fit each topic. Do not reuse them on unrelated videos.
