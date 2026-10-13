"""Quick self-checks: python3 test_make_video.py"""
from PIL import Image, ImageDraw

from make_video import commons_pick, font, wrap

# Commons search results come back unordered; the lowest "index" is the best match.
data = {"query": {"pages": {
    "2": {"index": 2, "title": "File:B.jpg", "imageinfo": [{"thumburl": "https://x/B.jpg"}]},
    "1": {"index": 1, "title": "File:A.jpg", "imageinfo": [{"thumburl": "https://x/A.jpg", "descriptionurl": "https://c/A",
          "extmetadata": {"Artist": {"value": "Giotto"}, "LicenseShortName": {"value": "Public domain"}}}]},
}}}
url, credit = commons_pick(data)
assert url == "https://x/A.jpg" and "Giotto" in credit and "Public domain" in credit, credit
assert commons_pick({}) is None

d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
lines = wrap(d, "one two three four five six seven eight nine ten " * 5, font("Oswald.ttf", 46), 960)
assert len(lines) > 1 and all(d.textlength(l, font=font("Oswald.ttf", 46)) <= 960 for l in lines)
print("ok")
