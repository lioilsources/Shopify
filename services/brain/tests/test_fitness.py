import pytest

from brain.fitness import grade_image, load_profiles

PROFILES = {p.id: p for p in load_profiles()}


def g(w, h, pid):
    return grade_image(w, h, PROFILES[pid])


def test_seed_loads_and_is_consistent():
    assert len(PROFILES) >= 15
    for p in PROFILES.values():
        assert p.short_cm <= p.long_cm and p.max_long_cm >= p.long_cm
        assert p.aspect in {"free", "fixed", "panorama"}


def test_small_native_print_is_ok():
    # phone case is 2:1, 18 cm at 300 dpi = 2126 px on the long side
    assert g(1536, 768, "phone-case").grade == "upscale"
    assert g(2400, 1200, "phone-case").grade == "ok"
    assert g(1536, 1024, "phone-case").grade == "caveat"  # 25 % crop


def test_shirt_needs_upscale_within_cap():
    f = g(1024, 1536, "tshirt-dtg")
    assert f.grade == "upscale" and "orientačně" in f.note
    assert f.max_long_cm == 46  # capped by the largest print area


def test_poster_max_size_follows_cap():
    f = g(1536, 1024, "poster")
    assert f.grade == "upscale"
    # 3:2 cropped to A-ratio keeps 1448 px; x4 at 150 dpi = 98 cm, below A0
    assert f.max_long_cm == pytest.approx(98.1, abs=0.2)
    assert f.crop == pytest.approx(0.057, abs=0.01)


def test_square_image_on_mug_is_cropped_too_much():
    f = g(1024, 1024, "mug")
    assert f.grade == "no" and f.max_long_cm is None


def test_panorama_outpaints_with_caveat():
    f = g(1536, 1024, "kitchen-glass")
    assert f.grade == "caveat" and "panorama" in f.note
    assert f.max_short_cm <= 60


def test_beyond_cap_is_caveat():
    f = g(1024, 1024, "wallpaper-mural")
    assert f.grade == "caveat" and "nad strop" in f.note


def test_moderate_crop_is_caveat():
    # 16:9 image on a 2:3 puzzle -> ~16 % crop
    f = g(1820, 1024, "puzzle")
    assert f.grade == "caveat" and "ořez" in f.note
