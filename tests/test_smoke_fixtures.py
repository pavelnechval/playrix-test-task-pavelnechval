"""The fixtures themselves: the plan factory validates clean, the fake refuses unscripted calls, the network is off."""

import urllib.request

import pytest

import cardgen
import colour_check
import gemini_image
from support import FAMILY_RGB, OBJECT_BOX, make_card, make_plan


def test_factory_plan_has_no_errors_or_warnings(plan_path):
    assert cardgen.validate(make_plan(), plan_path) == ([], [])


def test_synthetic_card_families_and_box():
    for family in FAMILY_RGB:
        image = make_card(family, "yellow" if family != "yellow" else "blue")
        assert colour_check.backdrop_family(image) == family
    image = make_card("purple", "yellow", OBJECT_BOX, (1000, 1000))
    assert image.getpixel((500, 500)) == FAMILY_RGB["yellow"]
    assert image.getpixel((299, 299)) == FAMILY_RGB["purple"]
    assert image.getpixel((300, 300)) == FAMILY_RGB["yellow"]
    assert image.getpixel((699, 699)) == FAMILY_RGB["yellow"]
    assert image.getpixel((700, 700)) == FAMILY_RGB["purple"]


def test_fake_gemini_refuses_unscripted_calls(fake_gemini):
    with pytest.raises(AssertionError, match="nothing queued"):
        gemini_image.generate_image("m", [])
    with pytest.raises(AssertionError, match="nothing queued"):
        gemini_image.generate_text("m", [])


def test_network_is_blocked(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "not-a-real-key")
    with pytest.raises(AssertionError, match="offline"):
        urllib.request.urlopen("https://example.invalid/")
    with pytest.raises(AssertionError, match="offline"):
        gemini_image._call("GET", "models")
