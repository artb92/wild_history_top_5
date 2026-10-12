#!/usr/bin/env python3
"""Render a vertical Top 5 video from a script.json.

Usage: python3 make_video.py videos/<slug>/script.json
Needs: Pillow (pip install Pillow) and ffmpeg on PATH.
Output: videos/<slug>/<slug>.mp4 and videos/<slug>/credits.txt
"""
import json
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
W, H, FPS = 1080, 1920, 30
HOOK_SECONDS, ENTRY_SECONDS = 4, 13
GOLD, WHITE = (235, 185, 60), (255, 255, 255)
UA = {"User-Agent": "wild_history_top_5/0.1 (https://github.com/ArtB92/wild_history_top_5)"}
COMMONS_API = ("https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search"
               "&gsrnamespace=6&gsrlimit=5&prop=imageinfo&iiprop=url|extmetadata&iiurlwidth=1600&gsrsearch=")


def font(name, size, weight=None):
    f = ImageFont.truetype(str(ROOT / "fonts" / name), size)
    if weight:
        f.set_variation_by_name(weight)
    return f


def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read()


def commons_pick(data):
    """First search hit with a thumbnail, as (url, credit line)."""
    pages = sorted(data.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 0))
    for p in pages:
        info = (p.get("imageinfo") or [{}])[0]
        if info.get("thumburl"):
            meta = info.get("extmetadata", {})
            artist = meta.get("Artist", {}).get("value", "unknown")
            lic = meta.get("LicenseShortName", {}).get("value", "see page")
            return info["thumburl"], f"{p['title']} | {artist} | {lic} | {info.get('descriptionurl', '')}"
    return None


def get_image(query, prompt, dest):
    """Painting from Wikimedia Commons first, AI image from Pollinations as fallback. Cached in dest."""
    credit_file = dest.with_suffix(".txt")
    if dest.exists():
        return credit_file.read_text() if credit_file.exists() else "local file"
    sources = []
    if query:
        sources.append(lambda: commons_pick(json.loads(fetch(COMMONS_API + urllib.parse.quote(query + " filetype:bitmap")))))
    if prompt:
        sources.append(lambda: ("https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt)
                                + "?width=1080&height=1920&nologo=true", f"AI generated (Pollinations): {prompt}"))
    for source in sources:
        try:
            hit = source()
            if hit:
                dest.write_bytes(fetch(hit[0]))
                credit_file.write_text(hit[1])
                return hit[1]
        except Exception as e:  # try the next source
            print(f"  image source failed for {query or prompt!r}: {e}")
    sys.exit(f"No image found for {query!r}. Put a file at {dest} and rerun.")


def background(src, dest):
    """Blurred, darkened full-screen fill with the whole picture fitted on top, at 2x for a smooth zoom."""
    img = Image.open(src).convert("RGB")
    s = 2
    fill = cover(img, W * s, H * s).filter(ImageFilter.GaussianBlur(40)).point(lambda v: v * 0.45)
    fit = img.resize((W * s, round(img.height * W * s / img.width)))
    if fit.height > H * s:
        fit = cover(img, W * s, H * s)
    fill.paste(fit, (0, (H * s - fit.height) // 2))
    fill.save(dest)


def cover(img, w, h):
    scale = max(w / img.width, h / img.height)
    r = img.resize((round(img.width * scale), round(img.height * scale)))
    return r.crop(((r.width - w) // 2, (r.height - h) // 2, (r.width - w) // 2 + w, (r.height - h) // 2 + h))


def wrap(draw, text, f, width):
    lines, line = [], ""
    for word in text.split():
        test = f"{line} {word}".strip()
        if draw.textlength(test, font=f) <= width or not line:
            line = test
        else:
            lines.append(line)
            line = word
    return lines + [line] if line else lines


def text_block(draw, text, f, y, fill, gap=12, anchor_bottom=False):
    """Centered wrapped text with a black outline. Returns the y below the block (or above, if anchor_bottom)."""
    lines = wrap(draw, text, f, W - 120)
    height = sum(f.size + gap for _ in lines)
    if anchor_bottom:
        y -= height
    top = y
    for line in lines:
        draw.text((W // 2, y), line, font=f, fill=fill, anchor="ma", stroke_width=4, stroke_fill="black")
        y += f.size + gap
    return top if anchor_bottom else y


def gradient(height, top):
    """Black band fading out toward the middle of the screen."""
    g = Image.new("L", (1, height))
    for i in range(height):
        g.putpixel((0, i), int(220 * (1 - i / height) if top else 220 * i / height))
    return Image.merge("RGBA", [Image.new("L", (W, height))] * 3 + [g.resize((W, height))])


def overlays(head, sub, body, body_font, out_head, out_body):
    """Two transparent layers: the heading (number, title, year) and the explanation that fades in later."""
    layer = Image.new("RGBA", (W, H))
    layer.alpha_composite(gradient(650, True), (0, 0))
    d = ImageDraw.Draw(layer)
    y = 110
    for text, f, color in head:
        y = text_block(d, text, f, y, color) + 10
    if sub:
        text_block(d, sub, font("Oswald.ttf", 52, b"SemiBold"), y, GOLD)
    layer.save(out_head)

    layer = Image.new("RGBA", (W, H))
    layer.alpha_composite(gradient(720, False), (0, H - 720))
    text_block(ImageDraw.Draw(layer), body, body_font, H - 140, WHITE, anchor_bottom=True)
    layer.save(out_body)


def render_segment(bg, head, body, seconds, body_at, out):
    frames = seconds * FPS
    loop = ["-loop", "1", "-framerate", str(FPS), "-t", str(seconds), "-i"]
    graph = (f"[0]zoompan=z='1+0.08*on/{frames}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={W}x{H}:fps={FPS}[bg];"
             f"[1]format=rgba,fade=in:st=0.1:d=0.4:alpha=1[h];"
             f"[2]format=rgba,fade=in:st={body_at}:d=0.8:alpha=1[b];"
             f"[bg][h]overlay[a];[a][b]overlay,fade=in:d=0.3,fade=out:st={seconds - 0.3}:d=0.3,format=yuv420p")
    run(["ffmpeg", "-y", *loop, str(bg), *loop, str(head), *loop, str(body), "-filter_complex", graph,
         "-t", str(seconds), "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", str(out)])


def run(cmd):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", *cmd[1:]], check=True)


def find_music(script):
    if script.get("music"):
        return ROOT / script["music"]
    mp3s = sorted(p for p in ROOT.rglob("*.mp3") if "build" not in p.parts)
    if not mp3s:
        sys.exit("No .mp3 found in the repo. Add one or set \"music\" in script.json.")
    return mp3s[0]


def main(script_path):
    script_path = Path(script_path).resolve()
    script = json.loads(script_path.read_text())
    entries = sorted(script["entries"], key=lambda e: -e["number"])
    assert [e["number"] for e in entries] == [5, 4, 3, 2, 1], "script.json needs entries numbered 5 to 1"
    folder = script_path.parent
    build = folder / "build"
    build.mkdir(exist_ok=True)

    segments = [dict(name="hook", query=script.get("hook_image_query"), prompt=script.get("hook_prompt"),
                     head=[(script["title"].upper(), font("Anton-Regular.ttf", 130), WHITE)], sub=None,
                     body=script["hook"], body_font=font("Anton-Regular.ttf", 90), seconds=HOOK_SECONDS, body_at=1)]
    for e in entries:
        segments.append(dict(name=f"n{e['number']}", query=e.get("image_query"), prompt=e.get("prompt"),
                             head=[(f"#{e['number']}", font("Anton-Regular.ttf", 200), GOLD),
                                   (e["title"].upper(), font("Anton-Regular.ttf", 88), WHITE)],
                             sub=e.get("year"), body=e["text"], body_font=font("Oswald.ttf", 46, b"Medium"), seconds=ENTRY_SECONDS, body_at=2))

    credits = []
    for s in segments:
        print(f"Rendering {s['name']}...")
        p = build / s["name"]
        credits.append(f"{s['name']}: {get_image(s['query'], s['prompt'], p.with_suffix('.img'))}")
        background(p.with_suffix(".img"), p.with_name(s["name"] + "_bg.png"))
        overlays(s["head"], s["sub"], s["body"], s["body_font"], p.with_name(s["name"] + "_head.png"), p.with_name(s["name"] + "_body.png"))
        render_segment(p.with_name(s["name"] + "_bg.png"), p.with_name(s["name"] + "_head.png"),
                       p.with_name(s["name"] + "_body.png"), s["seconds"], s["body_at"], p.with_suffix(".mp4"))

    total = sum(s["seconds"] for s in segments)
    (build / "list.txt").write_text("".join(f"file '{s['name']}.mp4'\n" for s in segments))
    out = folder / f"{folder.name}.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(build / "list.txt"),
         "-stream_loop", "-1", "-i", str(find_music(script)), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
         "-af", f"afade=t=out:st={total - 2}:d=2", "-c:a", "aac", "-b:a", "192k", "-t", str(total), str(out)])
    (folder / "credits.txt").write_text("\n".join(credits) + "\n")
    print(f"Done: {out} ({total}s). Image credits: {folder / 'credits.txt'}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
