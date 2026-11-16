"""Public previews: at most 1024 px, JPEG, tiled watermark (plan 02 §5).

Originals stay private; only these previews are ever served without a token.
"""

import io
import math

from PIL import Image, ImageDraw, ImageFont

from brain.storage import LocalStorage

PREVIEW_MAX = 1024
WATERMARK = "SlopMarket · AI"


def _font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default(size=size)


def make_preview(original: bytes, max_side: int = PREVIEW_MAX) -> bytes:
    with Image.open(io.BytesIO(original)) as src:
        img = src.convert("RGB")
    img.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)

    w, h = img.size
    size = max(14, w // 28)
    font = _font(size)
    tile = Image.new("RGBA", (w * 2, h * 2), (0, 0, 0, 0))
    draw = ImageDraw.Draw(tile)
    step_x, step_y = size * 12, size * 5
    for row, y in enumerate(range(0, h * 2, step_y)):
        offset = (row % 2) * step_x // 2
        for x in range(-step_x, w * 2, step_x):
            draw.text((x + offset, y), WATERMARK, font=font, fill=(255, 255, 255, 70))
    tile = tile.rotate(math.degrees(math.atan2(h, w)) * 0.5, resample=Image.Resampling.BICUBIC)
    left, top = (tile.width - w) // 2, (tile.height - h) // 2
    overlay = tile.crop((left, top, left + w, top + h))
    out = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

    buf = io.BytesIO()
    out.save(buf, "JPEG", quality=82, optimize=True, progressive=True)
    return buf.getvalue()


def ensure_preview(storage: LocalStorage, sha256: str) -> bytes:
    """Return the stored preview, building it from the original on first use."""
    path = storage.root / "public" / sha256[:2] / f"{sha256}.jpg"
    if path.is_file():
        return path.read_bytes()
    data = make_preview(storage.get(sha256))
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_bytes(data)
    tmp.replace(path)
    return data


def preview_url(sha256: str) -> str:
    return f"/media/preview/{sha256}.jpg"
