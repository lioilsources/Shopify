import io

from PIL import Image

from brain.previews import PREVIEW_MAX, make_preview


def _png(w, h, color=(30, 120, 60)):
    buf = io.BytesIO()
    Image.new("RGB", (w, h), color).save(buf, "PNG")
    return buf.getvalue()


def test_preview_is_small_jpeg_with_watermark():
    data = make_preview(_png(1536, 1024))
    img = Image.open(io.BytesIO(data))
    assert img.format == "JPEG"
    assert max(img.size) == PREVIEW_MAX and img.size == (1024, 683)
    # A flat source image is no longer flat: the watermark is drawn on it.
    assert len(set(img.convert("L").getdata())) > 3


def test_small_image_is_not_upscaled():
    img = Image.open(io.BytesIO(make_preview(_png(600, 400))))
    assert img.size == (600, 400)
