"""Catalyst Shorts engine v2 — one JSON script in, one finished vertical MP4 per account out.

usage:  python3 -I build.py <dir> make            # tts -> timeline -> audio -> (render -> mux -> qc) per variant
        python3 -I build.py <dir> stills 1.5,9.2  # preview PNGs at given seconds (after tts+timeline)
        python3 -I build.py <dir> render 3,5      # re-render only these scenes in every variant, then mux + qc
        python3 -I build.py <dir> variant youtube # full render + mux + qc of one variant only
<dir>/script.json (see RUNBOOK.md):
  {"voice": "am_michael", "speed": 1.05, "sources": "Sources: ...",
   "variants": {"youtube": "THE CAPTAIN", "instagram": "CATALYST TECH"},
   "segments": [{"say": "chunk one | chunk two => *shown* two | ...", "scene": {"type": "hook", ...}}, ...]}
Each variant becomes <dir>/final_<tag>.mp4 with that account name in the top bar and on the end card
(variants with the same name share one render). Without "variants": <dir>/final.mp4 named CATALYST TECH.
"""
import hashlib, html, json, os, re, shutil, subprocess, sys
import numpy as np, soundfile as sf
from scipy.signal import butter, lfilter

ENGINE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.environ.get("KOKORO_DIR", os.path.expanduser("~/models"))
CHROME = os.environ.get("CHROME", "/usr/bin/google-chrome")
W, H, FPS = 1080, 1920, 30
LEAD, GAP, TAIL = 0.15, 0.18, 1.6
SR = 48000
DEFAULT_BRAND = "CATALYST TECH"


def variants(spec):
    v = spec.get("variants") or {"": DEFAULT_BRAND}
    return [(t, v[t]) for t in v]


def sfx(tag):
    return f"_{tag}" if tag else ""


def clean_brand(b):
    b = re.sub(r"[^A-Za-z0-9 .&'!-]", "", str(b)).strip().upper()[:24]
    return html.escape(b or DEFAULT_BRAND)


def chunks_of(seg):
    out = []
    for part in seg["say"].split("|"):
        part = part.strip()
        if not part:
            continue
        say, show = ([x.strip() for x in part.split("=>", 1)] if "=>" in part else (part, part))
        out.append({"say": say.replace("*", ""), "show": show})
    return out


def spoken(seg):
    return " ".join(c["say"] for c in chunks_of(seg))


def weight(say):
    w = sum(ch.isalnum() for ch in say) + say.count(" ")
    tail = say.rstrip()[-1:]
    w += 5 if tail == "," else 8 if tail in ".?!:;" else 0
    return max(1.0, w)


def load(d):
    return json.load(open(f"{d}/script.json"))


def tts(d):
    spec = load(d)
    from kokoro_onnx import Kokoro
    k = Kokoro(f"{MODELS}/kokoro-v1.0.int8.onnx", f"{MODELS}/voices-v1.0.bin")
    voice, speed = spec.get("voice", "am_michael"), float(spec.get("speed", 1.05))
    res = []
    for i, seg in enumerate(spec["segments"]):
        text = spoken(seg)
        key = hashlib.sha1(f"{voice}|{speed}|{text}".encode()).hexdigest()[:16]
        wav, kf = f"{d}/seg{i:02d}.wav", f"{d}/seg{i:02d}.key"
        if not (os.path.exists(wav) and os.path.exists(kf) and open(kf).read() == key):
            s, sr = k.create(text, voice=voice, speed=speed, lang="en-us")
            thr = 0.01 * np.abs(s).max(); idx = np.where(np.abs(s) > thr)[0]
            s = s[max(0, idx[0] - int(.02 * sr)): min(len(s), idx[-1] + int(.06 * sr))]
            sf.write(wav, s, sr); open(kf, "w").write(key)
        x, sr = sf.read(wav)
        res.append({"i": i, "dur": round(len(x) / sr, 3)})
        print("tts", i, res[-1]["dur"], flush=True)
    json.dump({"segs": res}, open(f"{d}/tts.json", "w"))


def timeline(d):
    spec = load(d); tts_ = json.load(open(f"{d}/tts.json"))
    segs, t = [], LEAD
    for i, seg in enumerate(spec["segments"]):
        dur = tts_["segs"][i]["dur"]; cs = chunks_of(seg)
        ws = [weight(c["say"]) for c in cs]; tot = sum(ws); acc = 0; out = []
        for c, w in zip(cs, ws):
            out.append({"text": c["show"], "start": round(t + dur * acc / tot, 3)}); acc += w
        segs.append({"start": round(t, 3), "end": round(t + dur, 3), "chunks": out}); t += dur + GAP
    tl = {"total": round(segs[-1]["end"] + TAIL, 3), "fps": FPS, "segs": segs}
    json.dump(tl, open(f"{d}/timeline.json", "w"), indent=1)
    print("timeline total", tl["total"], "s", "(TOO LONG: trim the script)" if tl["total"] > 59.5 else "")
    return tl


def audio(d):
    tl = json.load(open(f"{d}/timeline.json")); total = tl["total"]; N = int(total * SR)
    voice = np.zeros(N)
    for i, s in enumerate(tl["segs"]):
        x, sr = sf.read(f"{d}/seg{i:02d}.wav")
        n = int(len(x) * SR / sr); y = np.interp(np.arange(n) / SR, np.arange(len(x)) / sr, x)
        p = int(s["start"] * SR); voice[p:p + n] += y[:max(0, N - p)]
    rng = np.random.default_rng(7); tt = np.arange(N) / SR
    beat = 60 / 100; bar = 4 * beat
    chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
    mtof = lambda m: 440 * 2 ** ((m - 69) / 12)
    pad = np.zeros(N); bass = np.zeros(N)
    for k in range(int(total / bar) + 1):
        a = int(k * bar * SR); b = min(N, int(((k + 1) * bar + .5) * SR))
        if a >= N: break
        st = np.arange(b - a) / SR; env = np.minimum(1, st / .7) * np.clip((bar + .5 - st) / .7, 0, 1)
        for m in chords[k % 4]:
            for det in (-.06, .06):
                f = mtof(m) * 2 ** (det / 12)
                pad[a:b] += .045 * env * sum((.55 ** h) * np.sin(2 * np.pi * f * (h + 1) * st + h) for h in range(5))
        bass[a:b] += .11 * env * np.sin(2 * np.pi * mtof(chords[k % 4][0] - 24) * st)
    pad = lfilter(*butter(2, 2200 / (SR / 2)), pad)
    kick = np.zeros(N); kt = np.arange(int(.3 * SR)) / SR
    kw = np.sin(2 * np.pi * np.cumsum(42 + 90 * np.exp(-kt * 28)) / SR) * np.exp(-kt * 14)
    hats = np.zeros(N); ht = np.arange(int(.06 * SR)) / SR
    hn = lfilter(*butter(2, 7000 / (SR / 2), 'high'), rng.standard_normal(len(ht))) * np.exp(-ht * 70)
    for bi in range(int(total / beat)):
        tb = bi * beat
        if tb < 2.4 or tb > total - 1.2: continue
        p = int(tb * SR); kick[p:p + len(kw)] += .16 * kw[:max(0, N - p)]
        p2 = int((tb + beat / 2) * SR); hats[p2:p2 + len(hn)] += .035 * hn[:max(0, N - p2)]
    music = pad + bass + kick + hats
    wh = np.zeros(N); wl = int(.6 * SR); wt = np.arange(wl) / SR; noise = rng.standard_normal(wl)
    dark = lfilter(*butter(2, 600 / (SR / 2)), noise); bright = lfilter(*butter(2, 5000 / (SR / 2)), noise)
    mixw = np.clip(wt / .45, 0, 1); wav = ((1 - mixw) * dark * 2.2 + mixw * bright) * np.sin(np.pi * np.clip(wt / .6, 0, 1)) ** 2
    for s in tl["segs"][1:]:
        p = int((s["start"] - .38) * SR); wh[p:p + wl] += .05 * wav[:max(0, N - p)]
    env = np.convolve(np.abs(voice), np.ones(int(.08 * SR)) / int(.08 * SR), mode="same")
    duck = np.convolve(1 - .6 * np.clip(env / .04, 0, 1), np.ones(int(.15 * SR)) / int(.15 * SR), mode="same")
    fade = np.clip((total - tt) / 1.2, 0, 1) * np.clip(tt / .3, 0, 1)
    out = voice + (music * duck * .55 + wh) * fade
    out = out / max(1e-6, np.abs(out).max()) * .9
    sf.write(f"{d}/mix.wav", np.stack([out, out], 1).astype(np.float32), SR)
    print("audio", round(N / SR, 2), "s")


def browser():
    from playwright.sync_api import sync_playwright
    p = sync_playwright().start()
    b = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox", "--force-color-profile=srgb"])
    return p, b


def page(d, b, brand=DEFAULT_BRAND):
    spec = load(d); tl = json.load(open(f"{d}/timeline.json"))
    doc = open(f"{ENGINE}/page.html").read()
    doc = (doc.replace("__TIMELINE__", json.dumps(tl)).replace("__SCENES__", json.dumps([s["scene"] for s in spec["segments"]]))
           .replace("__META__", json.dumps({"sources": spec.get("sources", "")})).replace("__BRAND__", clean_brand(brand)))
    pg = b.new_page(viewport={"width": W, "height": H}); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
    pg.set_content(doc); pg.evaluate("window.READY"); pg.wait_for_timeout(250)
    return pg, tl, errs


def stills(d, times):
    p, b = browser(); pg, tl, errs = page(d, b, variants(load(d))[0][1]); os.makedirs(f"{d}/stills", exist_ok=True)
    for t in times:
        pg.evaluate(f"render({t})"); pg.screenshot(path=f"{d}/stills/t{t:05.2f}.png")
    print("page errors:", errs[:5] or "none"); b.close(); p.stop()


def render(d, only=None, tag="", brand=DEFAULT_BRAND):
    p, b = browser(); pg, tl, errs = page(d, b, brand)
    if errs: raise SystemExit(f"page errors: {errs[:5]}")
    segs = tl["segs"]; bounds = [0] + [s["start"] - .09 for s in segs[1:]] + [tl["total"]]
    sd = f"{d}/scenes{sfx(tag)}"; os.makedirs(sd, exist_ok=True); files = []
    for i in range(len(segs)):
        out = f"{sd}/s{i:02d}.mp4"; files.append(out)
        if only is not None and i not in only and os.path.exists(out): continue
        f0, f1 = round(bounds[i] * FPS), round(bounds[i + 1] * FPS); tmp = f"{sd}/s{i:02d}.tmp.mp4"
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-i", "-", "-c:v", "libx264",
                               "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p", "-r", str(FPS), tmp], stdin=subprocess.PIPE)
        for f in range(f0, f1):
            pg.evaluate(f"render({f / FPS})"); ff.stdin.write(pg.screenshot(type="jpeg", quality=92))
        ff.stdin.close()
        if ff.wait() != 0: raise SystemExit(f"ffmpeg failed on scene {i}")
        os.replace(tmp, out); print("scene", i, f1 - f0, "frames", tag, flush=True)
    if errs: print("page errors:", errs[:5])
    b.close(); p.stop()
    with open(f"{sd}/list.txt", "w") as fh:
        for f in files: fh.write(f"file '{os.path.abspath(f)}'\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{sd}/list.txt", "-c", "copy", f"{d}/video{sfx(tag)}.mp4"], check=True)


def mux(d, tag=""):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{d}/video{sfx(tag)}.mp4", "-i", f"{d}/mix.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart",
                    f"{d}/final{sfx(tag)}.mp4"], check=True)


def build(d, only=None, tags=None):
    done = {}
    for tag, brand in variants(load(d)):
        if tags and tag not in tags: continue
        key = clean_brand(brand)
        if key in done:
            shutil.copyfile(f"{d}/final{sfx(done[key])}.mp4", f"{d}/final{sfx(tag)}.mp4")
            print("variant", tag, "= copy of", done[key]); continue
        render(d, only, tag, brand); mux(d, tag); qc(d, tag); done[key] = tag


def qc(d, tag=""):
    from PIL import Image
    tl = json.load(open(f"{d}/timeline.json")); qd = f"{d}/qc{sfx(tag)}"; final = f"{d}/final{sfx(tag)}.mp4"; os.makedirs(qd, exist_ok=True)
    times = [s["start"] + .72 * (s["end"] - s["start"]) for s in tl["segs"]] + [tl["total"] - .3]
    ims = []
    for k, t in enumerate(times):
        f = f"{qd}/f{k:02d}.png"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{t:.2f}", "-i", final, "-frames:v", "1", f], check=True)
        ims.append(Image.open(f).convert("RGB").resize((360, 640)))
    cols = 5; rows = (len(ims) + cols - 1) // cols; sheet = Image.new("RGB", (360 * cols, 640 * rows), (40, 40, 40))
    for k, im in enumerate(ims): sheet.paste(im, ((k % cols) * 360, (k // cols) * 640))
    sheet.save(f"{qd}/sheet.png")
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size", "-of", "json", final], capture_output=True, text=True)
    fmt = json.loads(probe.stdout)["format"]
    loud = subprocess.run(["ffmpeg", "-hide_banner", "-i", final, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    lufs = [l.strip() for l in loud.splitlines() if l.strip().startswith("I:")][-1:]
    print(f"QC {tag or 'final'} duration={float(fmt['duration']):.2f}s size={int(fmt['size']) / 1e6:.1f}MB loudness={lufs} sheet={qd}/sheet.png")


if __name__ == "__main__":
    d, cmd = sys.argv[1], sys.argv[2]
    arg = sys.argv[3] if len(sys.argv) > 3 else None
    if cmd == "make":
        tts(d); timeline(d); audio(d); build(d)
    elif cmd == "tts": tts(d)
    elif cmd == "timeline": timeline(d)
    elif cmd == "audio": audio(d)
    elif cmd == "stills": stills(d, [float(x) for x in arg.split(",")])
    elif cmd == "render": build(d, [int(x) for x in arg.split(",")] if arg else None)
    elif cmd == "variant": build(d, None, [arg])
    elif cmd == "mux": [mux(d, t) for t, _ in variants(load(d))]
    elif cmd == "qc": [qc(d, t) for t, _ in variants(load(d))]
