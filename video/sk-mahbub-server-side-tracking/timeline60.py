"""60-second cut: same original voice at natural speed/pitch; trimmed at natural pauses.
Each scene = list of kept (in, out) segments in clip time."""
import json
from timeline import CUES, SFX, FPS

SEGS = {  # id: (segments, gap_before)
    "01": ([(0.45, 2.42), (2.74, 7.02)], 0.35),            # hook (pause tightened)
    "02": ([(2.50, 6.82), (7.06, 11.40), (11.90, 12.62)], 0.22),            # from "iOS privacy updates..."
    "03": ([(6.10, 11.22)], 0.22),                          # "That means inaccurate reporting..."
    "04": ([(0.42, 3.00)], 0.40),                           # server-side tracking
    "05": ([(0.00, 2.38), (2.60, 7.82)], 0.22),             # how it works
    "06": ([(1.82, 3.38), (3.60, 5.04), (5.26, 7.50)], 0.25),  # three benefits
    "07": ([(0.25, 6.30)], 0.30),                           # intro + title
    "08": ([(0.74, 4.70), (5.24, 8.68)], 0.30),             # "When your tracking is wrong..."
    "09": ([(0.76, 2.42), (5.40, 9.02)], 0.30),             # "Before you scale your campaigns, fix your tracking..."
}
HIDE = {"09": ["make", "working"]}   # visual beats whose words were cut
END_HOLD = 2.5


def mapper(segs):
    def f(v, kind):
        acc = 0.0
        for i, (a, b) in enumerate(segs):
            if v < a:
                if i == 0:
                    return v - a if (kind == "sfx" and v < 0) else (0.0 if kind == "cue" else None)
                return acc if kind == "cue" else None   # inside a removed gap
            if v <= b:
                return acc + v - a
            acc += b - a
        return acc + (v - segs[-1][1])   # after last segment: extrapolate
    return f


def build():
    t, scenes = 0.0, []
    for cid, (segs, gap) in SEGS.items():
        t += gap
        start = t
        dur = sum(b - a for a, b in segs)
        m = mapper(segs)
        cues = {}
        for k, v in CUES[cid].items():
            cues[k] = 1e6 if k in HIDE.get(cid, []) else round(start + m(v, "cue"), 3)
        if cid == "02":
            cues["often"] = -1
            cues["lost"] = round(start + m(12.0, "cue"), 3)  # true onset of "lost"
        if cid == "07":  # "We build..." sentence cut: bring the infra strip in after the title
            cues["build"] = round(cues["conv"] + .45, 3)
            cues["server"] = round(cues["build"] + .5, 3)
            cues["reliable"] = cues["infra"] = cues["dependable"] = 1e6  # line cut in this version
        sfx = []
        for v, ty, g in SFX[cid]:
            r = m(v, "sfx")
            if r is not None:
                sfx.append((round(start + r, 3), ty, g))
        scenes.append(dict(id=cid, start=round(start, 3), trim_in=segs[0][0], trim_out=segs[-1][1],
                           segs=segs, dur=round(dur, 3), cues=cues, sfx=sfx))
        t += dur
    total = t + END_HOLD
    for i, s in enumerate(scenes):
        s["vs"] = 0.0 if i == 0 else round(s["start"] - .3, 3)
        s["ve"] = round(scenes[i + 1]["start"] - .3, 3) if i + 1 < len(scenes) else round(total, 3)
    return dict(fps=FPS, total=round(total, 3), cut=60, scenes=scenes)


if __name__ == "__main__":
    tl = build()
    json.dump(tl, open("timeline.json", "w"), indent=1)
    for s in tl["scenes"]:
        print(s["id"], s["start"], s["dur"], {k: round(v - s["start"], 2) for k, v in s["cues"].items() if v < 1e5})
    print("total", tl["total"])
