# wild_history_top_5

Makes ~70 second vertical (1080x1920) "Top 5" history videos for TikTok: a hook, then #5 to #1,
each with a painting, a title and a short explanation, over dramatic music.

## Setup (macOS)

```sh
brew install ffmpeg
pip3 install -r requirements.txt
```

## Make a video

With Claude Code in this folder:

```
/top5 biggest betrayals in history
```

Claude researches the theme, writes `videos/<slug>/script.json` and renders it. To render a script yourself:

```sh
python3 make_video.py videos/betrayals/script.json
```

The video lands in `videos/<slug>/<slug>.mp4` and the image credits in `videos/<slug>/credits.txt`
(put them in the TikTok description; some Commons images require attribution).

- Images: public-domain paintings from Wikimedia Commons, with an AI image from Pollinations.ai as fallback.
  They are cached in `videos/<slug>/build/`. To swap one, drop your own picture at `build/<n5|n4|...|hook>.img`.
- Music: `"music"` in script.json, otherwise the first `.mp3` in the repo. It loops if too short and fades out at the end.
- Timing: hook 4 s, each entry 13 s (`HOOK_SECONDS`, `ENTRY_SECONDS` in `make_video.py`).
- Fonts: Anton and Oswald (SIL Open Font License, see `fonts/`).
