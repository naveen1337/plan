from app.modules.openrouter import openrouter_utils


def test_build_payload_drops_none_values() -> None:
    payload = openrouter_utils.build_payload({"prompt": "x", "seed": None, "n": 1})
    assert payload == {"prompt": "x", "n": 1}


def test_build_payload_does_not_mutate_input() -> None:
    source = {"prompt": "x", "seed": None}
    openrouter_utils.build_payload(source)
    assert source == {"prompt": "x", "seed": None}


def test_media_type_for_each_format() -> None:
    assert openrouter_utils.media_type_for("png") == "image/png"
    assert openrouter_utils.media_type_for("jpeg") == "image/jpeg"
    assert openrouter_utils.media_type_for("webp") == "image/webp"
