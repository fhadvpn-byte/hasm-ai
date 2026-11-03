import base64
import io

from PIL import Image, ImageDraw, ImageFont

from accident_kroky.paths import arabic_font
from accident_kroky.tables import normalize_items

_COLORS = (
    "#0f766e",
    "#0369a1",
    "#b45309",
    "#7c3aed",
    "#be123c",
    "#047857",
    "#1d4ed8",
    "#a16207",
    "#4338ca",
    "#9f1239",
)


def _font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype(str(arabic_font()), size)
    except (OSError, FileNotFoundError):
        return ImageFont.load_default()


def _decode_snapshot(snapshot: str) -> bytes:
    if not isinstance(snapshot, str) or "," not in snapshot or not snapshot.startswith("data:image"):
        return b""
    try:
        return base64.b64decode(snapshot.split(",", 1)[1])
    except (ValueError, TypeError):
        return b""


def render_sketch(items: list[dict], width: int = 1200, height: int = 640) -> bytes:
    image = Image.new("RGB", (width, height), "#f6f1e6")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, int(height * 0.28), width, int(height * 0.72)), fill="#e7dcc4")
    draw.rectangle((0, int(height * 0.34), width, int(height * 0.66)), fill="#3f4854")
    draw.line((0, int(height * 0.36), width, int(height * 0.36)), fill="#f8fafc", width=4)
    draw.line((0, int(height * 0.64), width, int(height * 0.64)), fill="#f8fafc", width=4)
    center = int(height * 0.5)
    x = 0
    while x < width:
        draw.line((x, center, min(width, x + 28), center), fill="#f5d90a", width=4)
        x += 48
    compass = (width - 68, 24, width - 24, 68)
    draw.ellipse(compass, fill="#0f2744")
    north = _font(22)
    draw.text((width - 46, 46), "ش", fill="#f8fafc", font=north, anchor="mm")

    number_font = _font(22)
    hole_font = _font(16)
    for item in normalize_items(items):
        px = int(item["x"] * width)
        py = int(item["y"] * height)
        kind = item["kind"]
        if kind == "tree":
            draw.rectangle((px - 4, py - 2, px + 4, py + 22), fill="#7c4a21")
            draw.ellipse((px - 16, py - 30, px + 16, py - 2), fill="#15803d")
            draw.ellipse((px - 26, py - 20, px - 4, py + 2), fill="#15803d")
            draw.ellipse((px + 4, py - 20, px + 26, py + 2), fill="#15803d")
        elif kind == "pole":
            draw.line((px, py - 34, px, py + 20), fill="#374151", width=6)
            draw.line((px, py - 2, px, py + 8), fill="#f5d90a", width=6)
            draw.rectangle((px - 10, py - 40, px + 10, py - 32), fill="#e5e7eb")
        elif kind == "hole":
            draw.ellipse((px - 22, py - 14, px + 22, py + 14), fill="#6b3f24", outline="#3f2414", width=2)
            draw.text((px, py), "حفرة", fill="#f8f1e6", font=hole_font, anchor="mm")
        else:
            color = _COLORS[(item["n"] - 1) % len(_COLORS)]
            draw.ellipse((px - 18, py - 18, px + 18, py + 18), fill=color, outline="#ffffff", width=3)
            draw.text((px, py), str(item["n"]), fill="#ffffff", font=number_font, anchor="mm")

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def sketch_bytes(items: list[dict], snapshot: str) -> bytes:
    raw = _decode_snapshot(snapshot)
    if raw:
        try:
            Image.open(io.BytesIO(raw)).verify()
            return raw
        except (OSError, ValueError):
            pass
    return render_sketch(items)
