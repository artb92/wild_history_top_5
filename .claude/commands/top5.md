---
description: Research a Top 5 history theme, write its script.json, and render the video
argument-hint: <theme, e.g. "biggest betrayals in history">
---

Make a Top 5 video about: $ARGUMENTS

1. Research the theme and pick the 5 strongest entries: big consequences, a story that lands in 10 seconds,
   and well documented facts. Rank them so #1 is the payoff. Double-check every number and date you use.
2. Pick a short slug (e.g. `betrayals`) and write `videos/<slug>/script.json` in the same shape as
   `videos/betrayals/script.json`:
   - `title`: on-screen title of the hook, e.g. "The 5 Biggest Betrayals in History".
   - `hook`: one punchy line teasing #1 (under 8 words).
   - `hook_image_query` / `hook_prompt`: picture for the hook.
   - `entries`: exactly 5, numbered 5 to 1, each with `title` (under 6 words), `year`,
     `text` (2 or 3 sentences, at most 50 words), `image_query` and `prompt`.
   - `image_query` is a Wikimedia Commons search for a famous public-domain painting or photo of the event
     (name the painter or the painting when you know it). `prompt` is the AI image fallback
     ("dramatic oil painting" style). Avoid queries likely to return Nazi symbols or gore.
3. Show the user the 5 entries and hooks, then run `python3 make_video.py videos/<slug>/script.json`.
4. Look at a few frames (`ffmpeg -ss <t> -i videos/<slug>/<slug>.mp4 -frames:v 1 frame.png`). If an image is wrong,
   delete `videos/<slug>/build/<n>.img`, fix its `image_query`, and rerun (other images stay cached).
5. Tell the user where the video is, and paste `videos/<slug>/credits.txt` for the TikTok description.
