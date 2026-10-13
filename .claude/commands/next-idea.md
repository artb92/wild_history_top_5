---
description: Add one new Top 5 video script to the publishing queue (used by the daily routine)
---

Add one new video to the queue in `videos/`. Do not render it: GitHub Actions renders and publishes
the oldest unpublished script every 2 days (`.github/workflows/render.yml`).

1. List `videos/` to see every theme already done or queued. Pick a new history Top 5 theme that is
   clearly different from all of them and likely to go viral on TikTok (dramatic, surprising, emotional:
   betrayals, last stands, cursed objects, deadliest mistakes, craziest escapes, weirdest deaths...).
2. Follow steps 1 and 2 of `.claude/commands/top5.md` to research it and write its script.json, in the
   folder `videos/<today as YYYY-MM-DD>-<short-slug>/script.json`. Double-check every number and date.
3. Validate it: `python3 -c "import json; s=json.load(open('<path>')); assert sorted(e['number'] for e in s['entries'])==[1,2,3,4,5]"`.
4. Commit only that new file to `main` with the message "Queue: <title>" and push it to `main`.
