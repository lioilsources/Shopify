from brain.gallery_import import _ratio, attributes_for, name_for
from brain.gate import evaluate, licence_ok


def test_licence_allowlist():
    assert licence_ok("FLUX.1-schnell")
    assert licence_ok("qwen_image_fp8_e4m3fn.safetensors")
    assert licence_ok("flux-2-klein-4b")
    assert licence_ok("Z-Image-Turbo")
    assert not licence_ok("flux1-dev-fp8")
    assert not licence_ok("FLUX.2-klein-9B")
    assert not licence_ok("FLUX.1 Kontext dev")
    assert not licence_ok("sdxl_base_1.0")  # conditional licence: owner decides, not the gate
    assert not licence_ok(None)


def test_evaluate_blocking_and_review():
    ok = evaluate({"params": {"model": "qwen-image"}, "tags": ["dog", "grass"]})
    assert ok == []
    bad = evaluate({"params": {"model": "flux1-dev"}, "tags": ["signature", "text"], "revoked": True})
    codes = {r["code"]: r for r in bad}
    assert codes["revoked"]["blocking"] and codes["licence"]["blocking"]
    assert not codes["review"]["blocking"]
    assert "podpis" in codes["review"]["detail"] and "nápis" in codes["review"]["detail"]


def test_attributes_keep_model_and_prompt_private():
    item = {"width": 1536, "height": 1024, "style": "akvarel", "subject": "liška",
            "prompt": "a fox", "params": {"model": "qwen-image"}}
    attrs = attributes_for(item)
    assert attrs == {"styl": "akvarel", "namet": "liška", "orientace": "na šířku",
                     "pomer_stran": "3:2", "megapixely": 1.6}


def test_ratio_snaps_to_print_formats():
    assert _ratio(1024, 1024) == "1:1"
    assert _ratio(1344, 768) == "16:9"
    assert _ratio(1000, 1300) == "3:4"
    assert _ratio(1000, 1700) == "1000:1700"


def test_name_from_caption():
    assert name_for({"imageId": "x", "caption": "akvarelová liška v lese. Druhá věta."}, "Zvířata") == "Akvarelová liška v lese"
    assert name_for({"imageId": "abcdef123456"}, "Zvířata") == "Zvířata abcdef12"
