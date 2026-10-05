"""Master timeline for the SK Mahbub server-side tracking video.

All cue times are in ORIGINAL clip time (seconds into SCENE_xx.m4a) and were
measured from word timestamps + silence detection on the real voice-over.
The voice-over is the source of truth: scene placement is derived from it.
"""
import json

FPS = 30

# id, trim_in, trim_out, gap_before (silence before this clip starts)
CLIPS = [
    ("01", 0.45, 7.15, 0.70),
    ("02", 0.05, 11.70, 0.40),
    ("03", 0.00, 11.30, 0.35),
    ("04", 0.40, 3.05, 0.85),   # breath before the solution
    ("05", 0.00, 7.90, 0.35),
    ("06", 0.20, 7.55, 0.35),
    ("07", 0.25, 16.55, 0.60),
    ("08", 0.20, 8.70, 0.55),
    ("09", 0.40, 9.10, 0.60),
]
END_HOLD = 4.2  # end card after last word

# visual cues (clip time)
CUES = {
    "01": dict(running=0.60, google=1.58, sure=2.83, lead=4.26, purchase=5.02, actually=5.82, tracked=6.6),
    "02": dict(often=0.46, ios=2.64, adblock=4.37, browser=5.43, issues=7.17, valuable=9.26, lost=11.25),
    "03": dict(platforms=1.26, data=3.0, campaign=3.81, optimize=4.86, means=6.23, inaccurate=6.55,
               weaker=7.72, wasted=9.70),
    "04": dict(this=0.54, server=1.15, comes=2.0),
    "05": dict(conversion=0.32, processed=1.38, server=2.9, sent=4.1, google=5.3, meta=6.1, tiktok=6.95),
    "06": dict(result=0.33, reliable=1.97, less=3.75, better=5.42),
    "07": dict(hi=0.36, name=0.98, paid=2.56, web=3.30, conv=4.75, consultant=5.55, build=7.25,
               server=8.45, reliable=11.65, infra=13.6, dependable=15.6),
    "08": dict(tracking=1.30, wrong=2.04, missing=3.55, pause=4.49, losing=5.62, wasting=6.70),
    "09": dict(before=0.86, scale=1.24, make=2.62, working=4.40, fix=5.57, costing=6.11),
}

# SFX (clip time, type, gain dB)
SFX = {
    "01": [(-0.55, "whoosh_soft", -10), (0.95, "blip", -14), (1.55, "blip", -14), (2.15, "blip", -14),
           (2.83, "tick", -12), (4.30, "glitch", -15), (5.06, "dropout", -13), (5.82, "impact_soft", -9)],
    "02": [(0.46, "impact_soft", -11), (1.27, "blip", -13), (1.85, "whoosh", -14), (2.64, "error", -16), (4.37, "error", -16),
           (5.43, "error", -16), (7.17, "error", -16), (8.0, "dropout", -16), (9.6, "dropout", -15),
           (11.25, "glitch", -12)],
    "03": [(-0.2, "whoosh", -14), (1.3, "dropout", -17), (3.81, "tick", -13), (6.55, "tick", -10),
           (7.72, "tick", -10), (9.70, "impact_soft", -10)],
    "04": [(-0.6, "riser", -12), (1.15, "impact_deep", -5), (1.6, "pulse", -14)],
    "05": [(0.32, "blip", -16), (1.4, "process", -16), (2.9, "pulse", -13), (4.1, "whoosh", -15),
           (5.3, "confirm", -15), (6.1, "confirm", -15), (6.95, "confirm", -15)],
    "06": [(0.33, "whoosh_soft", -13), (1.97, "confirm", -11), (3.75, "confirm", -11), (5.42, "confirm", -11)],
    "07": [(-0.3, "whoosh_soft", -12), (0.98, "impact_soft", -12), (2.56, "tick", -16), (3.30, "tick", -16),
           (4.75, "tick", -16), (7.25, "whoosh_soft", -16), (8.45, "pulse", -17)],
    "08": [(-0.3, "whoosh", -14), (2.04, "glitch", -12), (3.55, "dropout", -13), (5.62, "impact_deep", -5),
           (6.70, "impact_soft", -9)],
    "09": [(-0.3, "whoosh_soft", -13), (0.86, "tick", -14), (2.62, "tick", -14), (5.57, "impact_soft", -9),
           (9.25, "confirm", -15)],
}


def build():
    t = 0.0
    scenes = []
    for cid, tin, tout, gap in CLIPS:
        t += gap
        start = t  # timeline time where clip trim_in plays
        dur = tout - tin
        scenes.append(dict(id=cid, start=round(start, 3), trim_in=tin, trim_out=tout, dur=round(dur, 3),
                           cues={k: round(start + v - tin, 3) for k, v in CUES[cid].items()},
                           sfx=[(round(start + v - tin, 3), ty, g) for v, ty, g in SFX[cid]]))
        t += dur
    total = t + END_HOLD
    # visual windows: each scene owns [start - lead, next.start - lead]
    lead = 0.30
    for i, s in enumerate(scenes):
        s["vs"] = 0.0 if i == 0 else round(s["start"] - lead, 3)
        s["ve"] = round(scenes[i + 1]["start"] - lead, 3) if i + 1 < len(scenes) else round(total, 3)
    return dict(fps=FPS, total=round(total, 3), scenes=scenes)


if __name__ == "__main__":
    tl = build()
    json.dump(tl, open("timeline.json", "w"), indent=1)
    for s in tl["scenes"]:
        print(s["id"], s["vs"], s["start"], s["ve"])
    print("total", tl["total"])
