# Catalyst Tech — Daily Shorts Runbook (v2 · 2026-11-13)

## Mission
Every day: pick ONE fresh tech story, make ONE ~50 s vertical explainer video in English, publish it to YouTube Shorts +
Instagram Reels (via Buffer) and TikTok (via Metricool, Monday–Thursday only), then send Mate a short report in Turkish.
Mate (Gökhan Kondakcı) decided: fully automatic, no approval step, Claude decides topic, tone and everything else.
Never publish a video that failed QC. Never publish twice on the same day (§0.5).

### Accounts: each video shows the name of the account it goes to (Mate's rule, 13 Nov 2026)
| Platform | Account | `variants` tag → name on screen | Follow line for the post text |
|---|---|---|---|
| YouTube Shorts | "The Captain" — Buffer channel `6af7279362b70b94b01bea38` | `youtube` → `THE CAPTAIN` | Follow The Captain for daily tech in 60 seconds. |
| Instagram Reels | "catalysttech01" — Buffer channel `6af7275962b70b94b01be5c5` | `instagram` → `CATALYST TECH` | Follow @catalysttech01 for daily tech in 60 seconds. |
| TikTok (Mon–Thu) | "Bubu" — Metricool blogId/brandId `8085653` | `tiktok` → `BUBU` | Follow for daily tech in 60 seconds. |

Buffer organization: `6af720fc2d3df5092c7c2051` ("My organization"). Timezone everywhere: Europe/Istanbul (+03:00).
If Mate renames or reconnects an account, IDs and names can change: re-list (Buffer `list_channels`, Metricool `getBrandSettings`),
pick the channel by service, use its current name on screen and in the follow line, and mention the change in the report.
The narration never says a channel name, because the same audio goes to every account.

### Voice: alternates every day (Mate's rule, 13 Nov 2026)
Even number of days since 2026-11-13 → `am_michael` (male). Odd → `af_heart` (female). Today's voice:
```
python3 -c "import datetime as d,zoneinfo as z;t=d.datetime.now(z.ZoneInfo('Europe/Istanbul')).date();print(t,'am_michael' if (t-d.date(2026,11,13)).days%2==0 else 'af_heart')"
```

## 0. Preconditions: check first
1. Buffer connector tools exist (ToolSearch "buffer").
2. Metricool connector tools exist (ToolSearch "metricool").
3. GitHub repo `gokhankondakci200516-hue/catalyst-shorts` can be attached with push access
   (mcp__claude-code-remote__add_repo owner=gokhankondakci200516-hue repo=catalyst-shorts access=push).
- Repo missing → no way to host the video → do not produce; report what is missing (§9) and stop.
- Buffer missing → still do TikTok (if Mon–Thu). Metricool missing → still do YouTube + Instagram.
- Both Buffer and Metricool missing → report what is missing (§9) and stop.

## 0.5 Already published today? Never post twice
Today = the Europe/Istanbul date. Call Buffer `list_posts` with
`{"organizationId": "6af720fc2d3df5092c7c2051", "channelIds": ["6af7279362b70b94b01bea38", "6af7275962b70b94b01be5c5"],
"createdAt": {"start": "<today>T00:00:00+03:00"}, "status": ["scheduled", "sending", "sent", "error"]}`.
- A YouTube post created today exists (any status) → do NOT make a new video. Go to §8 and report what is out today
  (status per platform, error text if any, links from `get_post` → `externalLink`). If one platform is missing and today's
  file for it is online (§6 URL answers 200), post just that one (§7) before reporting.
- No YouTube post today → continue with §1.

## 1. Environment (≈1 min)
```
pip install --break-system-packages -q kokoro-onnx soundfile
mkdir -p ~/models && cd ~/models
curl -sSLO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx
curl -sSLO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
```
Engine = `page.html` + `build.py` (+ this file) in `~/engine/`. Get them from the artifact named in the task prompt
(read_file with `paths`) or from the repo's `engine/` folder. ffmpeg, Google Chrome (/usr/bin/google-chrome) and Python
Playwright are normally preinstalled. If Playwright is missing: `pip install --break-system-packages playwright && playwright install chromium`
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
- No repeats: read the last 14 days of YouTube posts (Buffer `list_posts`, YouTube channel, status sent) — no same story,
  not the same company two days in a row.

## 3. Script (English)
- 120–150 spoken words → 45–56 s. Hard limit: `build.py` prints the timeline total; it must be ≤ 59 s.
- 6–8 segments, one sentence-ish each = one scene. Arc: hook (≤12 words, concrete, surprising) → what it is (name, price/date)
  → how it works / why it matters → the catch / limits → context (history, rival, numbers) → last segment: a question to the
  viewer + "follow for daily tech in sixty seconds." Never a channel name in the narration.
- Tone: confident, curious, plain words. No hype words ("insane", "game-changer"), no promise the video doesn't keep.
  Every claim must be in your sources; attribute estimates and opinions ("Ring's founder says …").
- TTS spelling in `say`: numbers, money, years and units as words ("two hundred and fifty dollars", "twenty twenty-six"),
  dotted acronyms when letters should be spelled ("A.I.", "U.S."), no symbols (& % $ /).
- Captions: split each segment with `|` into 2–5-word chunks. Mark one key word per segment with *asterisks*.
  If the screen should show something different from what is spoken, write `spoken text => shown text`,
  e.g. `for about two hundred and fifty dollars. => for about *$250*.`
- Scene `cue` numbers point at chunk positions inside that segment (0-based).

## 4. Scenes: `script.json`
```
{"voice": "<today's voice>", "speed": 1.05,
 "sources": "Sources: Outlet A · Outlet B · Outlet C",
 "variants": {"youtube": "THE CAPTAIN", "instagram": "CATALYST TECH", "tiktok": "BUBU"},
 "meta": {"title": "...", "description": "...", "caption": "..."},
 "segments": [{"say": "...", "scene": {"type": "hook", ...}}, ...]}
```
`variants`: one finished video per account, each with that account's name in the top bar and on the end card
(names from the table above). Leave out `tiktok` on Friday, Saturday and Sunday.
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
- `description` (YouTube): 1–2 sentences + the viewer question + "Narrated with an AI voice." + "Sources: …" +
  "Follow The Captain for daily tech in 60 seconds." + 5–7 hashtags including #Shorts and #tech.
- `caption` (Instagram and TikTok): a hook line + 1–2 short lines + the viewer question + "Narrated with an AI voice." +
  "Sources: …" + a line `{FOLLOW}` + 5–8 hashtags including #tech. When posting, replace `{FOLLOW}` with that platform's
  follow line from the table.

## 5. Build and QC (≈5 min per variant: 10–15 min)
```
D=~/work/out/$(TZ=Europe/Istanbul date +%F); mkdir -p $D   # write $D/script.json
KOKORO_DIR=~/models python3 -I ~/engine/build.py $D make
```
Output: `$D/final_youtube.mp4`, `$D/final_instagram.mp4` (+ `$D/final_tiktok.mp4`). Read every `$D/qc_<tag>/sheet.png`
(one frame per scene + end card) and check: nothing cut off or overlapping, nothing outside the frame, numbers and names
correct, captions readable, the right account name in the top bar and on the end card. Each QC line must show
duration ≤ 59 s and loudness ≈ -14 LUFS. Fix problems in script.json and rebuild (`build.py $D stills 3.5,9.1` for quick
looks, `build.py $D render 2,4` to redo scenes in every variant, `build.py $D variant tiktok` for one variant).
Never publish a video that failed QC.

## 6. Host the files
Attach the repo (add_repo, push) and clone it as add_repo says. Copy the current `~/engine/` files into the repo's
`engine/` folder (build.py as `engine/build.py`). In `v/` keep only yesterday's and today's files; add today's as
`v/YYYY-MM-DD-<tag>.mp4` (one per variant). Then rewrite history so old videos don't pile up:
`git checkout --orphan tmp && git add -A && git commit -m "video YYYY-MM-DD" && git branch -D main && git branch -m main && git push -f origin main`
Public URL (GitHub Pages): `https://gokhankondakci200516-hue.github.io/catalyst-shorts/v/YYYY-MM-DD-<tag>.mp4` — wait
(up to 5 min) until `curl -sI` gives 200, `content-type: video/mp4` and the right content-length for every file.
Fallback: `https://raw.githubusercontent.com/gokhankondakci200516-hue/catalyst-shorts/main/v/YYYY-MM-DD-<tag>.mp4`.

## 7. Publish: directly, no approval step
Load each tool's schema (ToolSearch) first; never invent parameters. Each platform gets its own variant's URL.
- YouTube — Buffer `create_post`:
  `{"channelId": "6af7279362b70b94b01bea38", "schedulingType": "automatic", "mode": "shareNow",
  "assets": [{"video": {"url": "<…-youtube.mp4>"}}], "text": "<meta.description>",
  "metadata": {"youtube": {"title": "<meta.title>", "categoryId": "28", "privacy": "public", "madeForKids": false, "isAiGenerated": true}}}`
- Instagram — Buffer `create_post`:
  `{"channelId": "6af7275962b70b94b01be5c5", "schedulingType": "automatic", "mode": "shareNow",
  "assets": [{"video": {"url": "<…-instagram.mp4>"}}], "text": "<meta.caption with the Instagram follow line>",
  "metadata": {"instagram": {"type": "reel", "shouldShareToFeed": true, "isAiGenerated": true}}}`
- TikTok, Monday–Thursday only (Metricool free plan: 20 published posts/month) — Metricool `createScheduledPost` with
  `blogId "8085653"`, `date` = now + 10 min as `YYYY-MM-DDTHH:MM:SS+03:00`, and `info` = this JSON as a string:
  `{"autoPublish": true, "draft": false, "descendants": [], "firstCommentText": "", "hasNotReadNotes": false,
  "media": ["<…-tiktok.mp4>"], "mediaAltText": [], "providers": [{"network": "tiktok"}],
  "publicationDate": {"dateTime": "<same time, YYYY-MM-DDTHH:MM:SS>", "timezone": "Europe/Istanbul"},
  "shortener": false, "smartLinkData": {"ids": []}, "text": "<meta.caption with the TikTok follow line>",
  "tiktokData": {"privacyOption": "PUBLIC_TO_EVERYONE", "isAigc": true, "disableComment": false, "disableDuet": false,
  "disableStitch": false, "commercialContentThirdParty": false, "commercialContentOwnBrand": false, "autoAddMusic": false,
  "photoCoverIndex": 0, "title": "<meta.title>"}}`
- About 3 minutes later, `get_post` each Buffer post: expect status `sent` and an `externalLink` (Instagram can stay
  `sending` for a few minutes). On failure retry once; if it still fails, report it. Never re-post without checking §0.5 first.
  A sent YouTube post may come back with `isAiGenerated: false` (seen on 13 Nov 2026); that is not a failure and is no reason
  to re-post: the on-screen "AI VOICE" pill and the "Narrated with an AI voice." line stay the disclosure.
- Also look up yesterday's posts (status, and views/likes if the tools return them).

## 8. Report to Mate: Turkish, short, plain words, no jargon
Send with SendUserMessage AND repeat it as your final message:
```
Bugünün videosu: <konu, 1 cümle Türkçe> (<süre> sn, <erkek/kadın> sesi)
YouTube (The Captain) ✅ · Instagram (catalysttech01) ✅ · TikTok (Bubu) ✅ (veya: bugün TikTok günü değil)
<YouTube ve Instagram linkleri>
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
- Each account's video shows that account's name; the narration names no channel.
- If unsure about posting (tool errors, policy questions), don't guess — skip and report.
- Don't change engine files except to fix a real bug; mention any change in the report.
