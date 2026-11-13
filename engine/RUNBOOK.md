# Catalyst Tech — Daily Shorts Runbook (v1 · 2026-11-13)

## Mission
Every day: pick ONE fresh tech story, make ONE ~50 s vertical explainer video in English with a male AI voice,
publish it to YouTube Shorts + Instagram Reels (via Buffer) and TikTok (via Metricool, Monday–Thursday only),
then send Mate a short report in Turkish. Mate (Gökhan Kondakcı, owner of the "Catalyst Tech" channel) decided:
fully automatic, no approval step, Claude decides topic, tone and everything else. Never publish a video that failed QC.

## 0. Preconditions — check first
1. Buffer connector tools exist (ToolSearch "buffer"); its channels include YouTube and Instagram.
2. Metricool connector tools exist (ToolSearch "metricool"); TikTok is connected in Metricool.
3. GitHub repo `gokhankondakci200516-hue/catalyst-shorts` can be attached with push access
   (mcp__claude-code-remote__add_repo owner=gokhankondakci200516-hue repo=catalyst-shorts access=push).
- Repo missing → no way to host the video → do not produce; report what is missing (§9) and stop.
- Buffer missing → still do TikTok (if Mon–Thu). Metricool missing → still do YouTube + Instagram.
- Both Buffer and Metricool missing → report what is missing (§9) and stop.

## 1. Environment (≈1 min)
```
pip install --break-system-packages -q kokoro-onnx soundfile
mkdir -p ~/models && cd ~/models
curl -sSLO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx
curl -sSLO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
```
Engine = `page.html` + `build.py` (+ this file) in `~/engine/`. Get them from the repo's `engine/` folder,
or from the artifact named in the task prompt (read_file with `paths`). ffmpeg, Google Chrome (/usr/bin/google-chrome)
and Python Playwright are normally preinstalled. If Playwright is missing: `pip install --break-system-packages playwright && playwright install chromium`
and set `CHROME` to that browser's path.

## 2. Pick the topic (≤10 searches)
- Use today's date (Europe/Istanbul). Look for tech news from the last 48 h (e.g. "tech news today", "AI news today",
  "smartphone launch", "Android news", "Apple news", "Google news", "Samsung news", "Nvidia news", "gadget launch", "space launch").
- Choose ONE story with a clear "what's new", global appeal (consumer tech, phones, AI tools, gadgets, game hardware, EVs,
  space, big platform changes, security warnings with a clear action) and ≥2 independent reliable sources
  (official announcement, Reuters, AP, Bloomberg, The Verge, Engadget, TechCrunch, Ars Technica, 9to5Google/9to5Mac,
  Android Authority, Tom's Hardware, Electrek …). Prefer stories with concrete numbers (price, date, specs) and a catch.
- Avoid: politics/elections, war, crime/violence, personal scandals, deaths, health/medical claims, investment or crypto-price talk,
  single-source rumors/leaks, adult content, stories mainly about Anthropic or Claude (conflict of interest), anything you would have to guess.
- No repeats: look at the last 14 days of posts (Buffer sent/queued list) — no same story, not the same company two days in a row.

## 3. Script (English)
- 120–150 spoken words → 45–56 s. Hard limit: `build.py` prints the timeline total; it must be ≤ 59 s.
- 6–8 segments, one sentence-ish each = one scene. Arc: hook (≤12 words, concrete, surprising) → what it is (name, price/date)
  → how it works / why it matters → the catch / limits → context (history, rival, numbers) → last segment: a question to the
  viewer + "follow for daily tech in sixty seconds."
- Tone: confident, curious, plain words. No hype words ("insane", "game-changer"), no promise the video doesn't keep.
  Every claim must be in your sources; attribute estimates and opinions ("Ring's founder says …").
- TTS spelling in `say`: numbers, money, years and units as words ("two hundred and fifty dollars", "twenty twenty-six"),
  dotted acronyms when letters should be spelled ("A.I.", "U.S."), no symbols (& % $ /).
- Captions: split each segment with `|` into 2–5-word chunks. Mark one key word per segment with *asterisks*.
  If the screen should show something different from what is spoken, write `spoken text => shown text`,
  e.g. `for about two hundred and fifty dollars. => for about *$250*.`
- Scene `cue` numbers point at chunk positions inside that segment (0-based).

## 4. Scenes — `script.json`
```
{"voice": "am_michael", "speed": 1.05,
 "sources": "Sources: Outlet A · Outlet B · Outlet C",
 "meta": {"title": "...", "description": "...", "caption": "..."},
 "segments": [{"say": "...", "scene": {"type": "hook", ...}}, ...]}
```
Scene types (`*` = optional). Keep text short — titles are auto-shrunk to fit but must stay readable.
- `hook`: label, line1 (white, ≤14 chars, CAPS), line2 (gradient, ≤12 chars, CAPS), art*
- `title`: label, title (`*word*` = gradient), art*, number* {value, prefix, suffix, decimals, cue}, sub*, sub_cue*
- `versus`: label, title*, left {value, label}, right {value, label}, cue, art*
- `steps`: label, title, steps [{text ≤26 chars, cue}] (2–4), art*
- `compare`: label, title*, bars [{label, value, display, color "amber"|"cyan"}] (2–3), cue, note*, art*
- `cards`: label (e.g. "BUT…"), title, cards [{icon, title ≤16 chars, sub ≤48 chars, cue}] (≤3)
- `timeline`: label, title, from {year, name, sub}, to {year, name, sub}, cue, art*, art_cue*
- `stat`: label, value, prefix*, suffix*, decimals*, caption, cue, art*
- `quote`: label, quote (real and sourced, ≤25 words), by
- `visual`: label, title, art, sub*, sub_cue*
- `question`: label, question (`*part*` gradient), options [2], cue — ALWAYS last; it also shows the sources line and the end card.
Icons: clock card pin chip battery shield money globe warning check rocket phone cloud eye lock bolt calendar chart users robot wifi camera car gamepad download spark.
Art: built-in `drone` `phone` `chip` `cloud` `laptop` `car` `robot` `globe` `server` `rocket` (or `{"asset": "phone", "w": 360}`),
or your own inline `<svg …>` string: simple line art, colors #45E3FF (cyan), #FFC24A (amber), #4A5670 (lines), #121722 (fills).
No logos, brand marks, real people or copied product photos. Animation classes for your SVG (timing via `animation-delay`,
counted from the scene's first word): a-bob a-float a-spin a-rot a-pulse a-dash a-up a-down a-pop a-fade a-blink, and a-draw
(add `style="stroke-dasharray:L;stroke-dashoffset:L"` with L ≥ the path length).
Vary the scene mix from day to day; labels are short CAPS eyebrows (THE IDEA, HOW IT WORKS, THE CATCH, THE NUMBERS, WHY IT MATTERS).
Dates on screen as "Nov 10, 2026". Only facts from your sources go on screen.
Meta:
- `title`: YouTube title ≤ 70 chars with the product/company name; no clickbait.
- `description`: 1–2 sentences + "Sources: …" + "Narrated with an AI voice." + 3 hashtags including #Shorts.
- `caption`: 2–3 short lines for Instagram/TikTok + 4–6 hashtags incl. #tech, then "Narrated with an AI voice." and "Sources: …".

## 5. Build and QC (≈7 min)
```
D=~/work/out/$(TZ=Europe/Istanbul date +%F); mkdir -p $D   # write $D/script.json
KOKORO_DIR=~/models python3 -I ~/engine/build.py $D make
```
Then Read `$D/qc/sheet.png` (one frame per scene + end card) and check: nothing cut off or overlapping, nothing outside the
frame, numbers and names correct, captions readable, end card present. The QC line must show duration ≤ 59 s and loudness ≈ -14 LUFS.
Fix problems in script.json and rebuild (`build.py $D stills 3.5,9.1` for quick looks, `build.py $D render 2,4` to redo scenes).
Never publish a video that failed QC.

## 6. Host the file
Attach the repo (add_repo, push) and clone it as add_repo says. Keep `engine/` in the repo (copy the current engine files there if
missing). In `v/` keep only the last 3 days, add `v/YYYY-MM-DD.mp4`, then rewrite history so old videos don't pile up:
`git checkout --orphan tmp && git add -A && git commit -m "video YYYY-MM-DD" && git branch -D main && git branch -m main && git push -f origin main`
Public URL (GitHub Pages): `https://gokhankondakci200516-hue.github.io/catalyst-shorts/v/YYYY-MM-DD.mp4` — wait (up to 5 min)
until `curl -sI` gives 200 and the right content-length. Fallback: `https://raw.githubusercontent.com/gokhankondakci200516-hue/catalyst-shorts/main/v/YYYY-MM-DD.mp4`.

## 7. Publish — directly, no approval step
- Read each tool's schema first; never invent parameters.
- Buffer → YouTube: video URL, title = meta.title, description = meta.description, public, not made for kids, AI flag on if offered.
- Buffer → Instagram: Reel, caption = meta.caption, AI-generated flag ON.
- Metricool → TikTok, Monday–Thursday only (free plan: 20 published posts/month): video URL, caption = meta.caption,
  AI-generated content ON if offered.
- Publish now (or the nearest slot within the next hour). On failure retry once; if it still fails, report it.
  Never post the same video twice — check queued/sent lists before re-posting.
- Also look up yesterday's posts (status and any views/likes the tools return).

## 8. Report to Mate — Turkish, short, plain words, no jargon
Send with SendUserMessage AND repeat it as your final message:
```
Bugünün videosu: <konu, 1 cümle Türkçe> (<süre> sn)
YouTube Shorts ✅ · Instagram Reels ✅ · TikTok ✅ (veya: bugün TikTok günü değil)
Dün: <durum / izlenme, varsa>
<Sadece bir sorun ya da ondan bir şey gerekiyorsa tek cümle. Yoksa: "Senin yapman gereken bir şey yok.">
```

## 9. Setup steps to quote when something is missing (Turkish)
1. Instagram → Ayarlar ve hareketler → Hesap türü ve araçları → Profesyonel hesaba geç → İçerik üreticisi.
2. buffer.com → ücretsiz hesap → kanal bağla: YouTube kanalı + Instagram.
3. metricool.com → ücretsiz hesap → TikTok'u bağla.
4. GitHub → yeni depo `catalyst-shorts`, Public, "Add a README" işaretli → Create; sonra Settings → Pages → Branch: main → Save.
5. Claude bağlayıcıları: Metricool'u ekle; Buffer'ı özel bağlayıcı olarak ekle: https://mcp.buffer.com/mcp

## 10. Standing rules
- The core news needs ≥2 reliable sources; every other claim ≥1.
- No copyrighted images, logos or music; no likeness of real people; no impersonation.
- "AI VOICE" stays on screen (the engine draws it); AI disclosure in every caption; platform AI flags wherever offered.
- If unsure about posting (tool errors, policy questions), don't guess — skip and report.
- Don't change engine files except to fix a real bug; mention any change in the report.
