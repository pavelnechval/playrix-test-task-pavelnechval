"""cardgen.validate: the plan rules of rulebook.md section 6 and set_guidelines.md section 5."""

import json

import pytest

import cardgen
from support import make_plan, write_plan


def errors_of(plan, plan_path=None):
    return cardgen.validate(plan, plan_path)[0]


def warnings_of(plan, plan_path=None):
    return cardgen.validate(plan, plan_path)[1]


def card(plan, index, variant=0):
    return plan["variants"][variant]["cards"][index]


def test_valid_fixture_passes(plan, plan_path):
    assert cardgen.validate(plan, plan_path) == ([], [])


# ---------------------------------------------------------------- errors

@pytest.mark.parametrize("category", [0, 5, "1", None, 2.0, True])
def test_category_must_be_an_integer_1_to_4(plan, category):
    """W036: 2.0 and true used to pass (2.0 == 2 in Python), and generation then crashed on CATEGORY_2.0."""
    card(plan, 0)["category"] = category
    errors = errors_of(plan)
    assert any(e.startswith(f"A01: category {category!r} is not 1-4") for e in errors), errors


def test_category_5_is_rejected_even_when_the_counts_still_hold(plan):
    """W023: category 5 (gold character cards) passed as long as categories 1-4 were still present."""
    card(plan, 2)["category"] = 5  # two category 1 cards remain
    assert [e for e in errors_of(plan) if "category 5" in e] == ["A03: category 5 is not 1-4"]


def test_category_counts_must_be_1_to_4(plan):
    for i in (1, 5):
        card(plan, i)["category"] = 1  # five category 1 cards, no category 2
    errors = errors_of(plan)
    assert "variant A: category 1 appears 5 times (allowed 1-4)" in errors
    assert "variant A: category 2 appears 0 times (allowed 1-4)" in errors


def test_wrong_star_layout(plan):
    card(plan, 0)["stars"], card(plan, 9)["stars"] = 5, 1
    assert any(e.startswith("variant A: stars in card order must be [1, 1, 2, 2, 3, 3, 4, 4, 5, 5]") for e in errors_of(plan))


def test_cards_not_in_star_order(plan):
    cards = plan["variants"][0]["cards"]
    cards.insert(0, cards.pop())  # the climax moved to the front
    errors = errors_of(plan)
    assert any("stars in card order must be" in e and "found [5, 1, 1, 2, 2, 3, 3, 4, 4, 5]" in e for e in errors)


def test_fewer_than_4_roles(plan):
    for c in plan["variants"][0]["cards"][:6]:
        c["role"] = "carry"
    for c in plan["variants"][0]["cards"][6:]:
        c["role"] = "place"
    errors = errors_of(plan)
    assert "variant A: 2 object roles (need at least 4)" in errors
    assert "variant A: 6 cards with role 'carry' (max 4)" in errors


def test_more_than_4_cards_per_role(plan):
    card(plan, 1)["role"] = "gear"  # five gear cards; still four roles
    errors = errors_of(plan)
    assert errors == ["variant A: 5 cards with role 'gear' (max 4)"]


def test_unknown_role(plan):
    card(plan, 0)["role"] = "prop"
    assert any("role missing or not one of" in e and "['A01']" in e for e in errors_of(plan))


@pytest.mark.parametrize("field, value, text", [
    ("bg_color", "teal", "A01: bg_color 'teal' not in"),
    ("bg_color", "", "A01: bg_color '' not in"),
])
def test_bad_background_colour(plan, field, value, text):
    card(plan, 0)[field] = value
    assert any(e.startswith(text) for e in errors_of(plan))


def test_bad_window_and_lead_colour(plan):
    plan["variants"][0]["window_color"] = "teal"
    plan["variants"][1]["lead_color"] = "teal"
    plan["variants"][2]["window_color"] = "purple"  # the template is called violet
    errors = errors_of(plan)
    assert "variant A: window_color 'teal' not in ['blue', 'orange', 'pink', 'violet']" in errors
    assert "variant B: lead_color 'teal' not in ['blue', 'green', 'orange', 'pink', 'purple', 'red', 'yellow']" in errors
    assert "variant C: window_color 'purple' not in ['blue', 'orange', 'pink', 'violet']" in errors


def test_three_same_colour_neighbours_in_the_window(plan):
    for i in (1, 4):  # purple on cards 1, 2, 4, 5 and 6: pairs 1-2 and 4-5 (left-right) and 1-6 (above-below) match
        card(plan, i)["bg_color"] = "purple"
    errors = errors_of(plan)
    assert "variant A: 3 same-colour neighbours in the 5x2 window (max 2): A01-A02, A04-A05, A01-A06" in errors


def test_window_pairs_are_the_5x2_neighbours():
    assert cardgen.WINDOW_PAIRS == [(0, 1), (1, 2), (2, 3), (3, 4), (5, 6), (6, 7), (7, 8), (8, 9),
                                   (0, 5), (1, 6), (2, 7), (3, 8), (4, 9)]


def test_two_same_colour_neighbours_are_allowed(plan):
    card(plan, 6)["bg_color"] = "purple"  # pairs 1-6 and 6-7 now match
    assert errors_of(plan) == []


def test_three_non_day_cards(plan):
    card(plan, 0)["light"], card(plan, 1)["light"] = "night", "sunset"
    assert "variant A: 3 sunset or night cards (max 2)" in errors_of(plan)


def test_unknown_light(plan):
    card(plan, 0)["light"] = "dawn"
    assert "variant A: light must be one of ['day', 'night', 'sunset']" in errors_of(plan)


def test_missing_set_bible_fields(plan):
    variant = plan["variants"][0]
    del variant["moment"]
    variant["motif"] = ""
    errors, warnings = cardgen.validate(plan)
    assert "variant A: missing set-bible field 'moment'" in errors
    assert "variant A: missing set-bible field 'motif'" in warnings


def test_lead_colour_outside_2_to_6_is_an_error(plan):
    plan["variants"][0]["lead_color"] = "yellow"  # on no card
    assert "variant A: lead colour yellow on 0 cards (reference sets: 2-6, aim 3-5)" in errors_of(plan)


@pytest.mark.parametrize("count", [2, 6])
def test_lead_colour_on_2_or_6_cards_is_a_warning(plan, count):
    colours = (["purple", "green", "purple", "blue", "purple", "pink", "purple", "green", "purple", "purple"] if count == 6
               else ["pink", "green", "blue", "purple", "pink", "purple", "red", "green", "blue", "orange"])
    for c, colour in zip(plan["variants"][0]["cards"], colours):
        c["bg_color"] = colour
    errors, warnings = cardgen.validate(plan)
    assert errors == []
    assert f"variant A: lead colour purple on {count} cards (aim 3-5)" in warnings


def test_eleven_cards_two_variants_duplicates_and_missing_fields(plan):
    variant = plan["variants"][0]
    variant["cards"].append({**variant["cards"][0]})  # the same id and name again
    plan["variants"] = plan["variants"][:2]
    del card(plan, 1)["subject"]
    card(plan, 2)["background"] = ""
    errors = errors_of(plan)
    assert "need 3-5 variants, found 2" in errors
    assert "variant A: needs exactly 10 cards, found 11" in errors
    assert "variant A: duplicate card names" in errors
    assert "duplicate card id A01" in errors
    assert "A02: missing subject" in errors and "A03: missing background" in errors


# ---------------------------------------------------------------- warnings

def test_object_and_backdrop_in_one_colour_family_warns(plan):
    card(plan, 0)["main_colors"] = "deep violet enamel with a lilac rim"  # on a purple background
    card(plan, 1)["main_colors"] = "mint leaves and cream"  # mint is green, on a green background
    errors, warnings = cardgen.validate(plan)
    assert errors == []
    assert "A01: the object (purple) and its background share one colour family" in warnings
    assert "A02: the object (green) and its background share one colour family" in warnings


@pytest.mark.parametrize("text, family", [
    ("polished brass-gold rim, warm chestnut-brown handle", "yellow"),  # the first colour word decides
    ("deep navy hull with red trim", "blue"),
    ("Cherry red with golden trim", "red"),
    ("cream and white", None),
    ("", None),
])
def test_main_colour_family(text, family):
    assert cardgen.main_colour_family(text) == family


def test_long_names_warn(plan):
    card(plan, 0)["name"] = "The Great Big Brass Lantern"
    card(plan, 1)["name"] = "Extraordinary Teapot"  # one word too long
    errors, warnings = cardgen.validate(plan)
    assert errors == []
    assert "A01: name 'The Great Big Brass Lantern' is long (keep 1-2 words, up to 16 characters)" in warnings
    assert "A02: name 'Extraordinary Teapot' is long (keep 1-2 words, up to 16 characters)" in warnings
    assert len("Extraordinary Teapot") > 16


def test_no_scene_among_the_top_cards_warns(plan):
    for i, category in ((7, 2), (8, 3), (9, 1)):  # the three scenes become props; the only scene is now a common
        card(plan, i)["category"] = category
    card(plan, 0)["category"] = 4
    errors, warnings = cardgen.validate(plan)
    assert errors == []
    assert "variant A: no category 4 scene among the 4-5 star cards (big places usually close a set)" in warnings


def test_collection_overlap_uses_finished_sets_of_the_collection(plan, plan_path):
    other = plan_path.parent.parent / "other-set" / "final_set"
    other.mkdir(parents=True)
    (other / "sources.json").write_text(json.dumps({"set": "Love in the City", "variant": "B", "cards": {
        "B03": {"name": "Vintage Scooter", "stars": 2, "from": "x"},
        "B07": {"name": "Date Night", "stars": 4, "from": "x"}}}), encoding="utf-8")
    card(plan, 0)["name"] = "Red Scooters"  # the plural still matches
    card(plan, 1)["name"] = "Movie Night"  # "night" is not an object
    errors, warnings = cardgen.validate(plan, plan_path)
    assert errors == []
    assert warnings == ["A01: 'Red Scooters' repeats the object of Vintage Scooter (Love in the City) in the collection"]
    assert cardgen.validate(plan) == ([], [])  # without the plan's path there is no collection to compare with
    (other / "sources.json").write_text("{not json", encoding="utf-8")
    assert warnings_of(plan, plan_path) == []  # an unreadable sources file is skipped


def test_the_set_itself_is_not_compared_with_itself(plan, plan_path):
    mine = plan_path.parent / "final_set"
    mine.mkdir()
    (mine / "sources.json").write_text(json.dumps({"set": "Test Set", "cards": {"A01": {"name": "Brass Lantern"}}}), encoding="utf-8")
    assert warnings_of(plan, plan_path) == []


# ---------------------------------------------------------------- banned and people words, whole words only

@pytest.mark.parametrize("text, banned", [
    ("a branding iron hanging on a hook", []),
    ("a brand logo on the side", ["brand", "logo"]),
    ("the race had begun", []),
    ("a toy gun", ["gun"]),
    ("a rumble of thunder", []),
    ("a bottle of rum", ["rum"]),
    ("a star wars poster", ["star wars"]),
    ("a winery", []),
    ("a glass of wine", ["wine"]),
])
def test_banned_terms_match_whole_words_only(plan, text, banned):
    card(plan, 0)["subject"] = text
    assert sorted(e for e in errors_of(plan) if "banned term" in e) == sorted(f"A01: banned term '{t}'" for t in banned)


@pytest.mark.parametrize("text, people", [
    ("a manual coffee grinder", []),
    ("a man in a hat", ["man"]),
    ("a kingfisher on a branch", []),
    ("the king's crown", ["king"]),
    ("a princely sum", []),
    ("a prince and a princess", ["prince", "princess"]),
    ("fairy lights on a string", ["fairy"]),
])
def test_people_words_match_whole_words_only(plan, text, people):
    card(plan, 0)["unique_detail"] = text
    assert [w for w in warnings_of(plan) if "no people" in w] == [f"A01: mentions '{t}' (no people or characters allowed)" for t in people]


def test_banned_terms_are_checked_in_the_fields_the_model_sees(plan):
    card(plan, 0)["why"] = "a famous disney prop"  # not sent to the model, not checked
    card(plan, 0)["context_cue"] = "a disney sign that says hello"
    errors = errors_of(plan)
    assert errors == ["A01: banned term 'disney'", "A01: banned term 'sign that says'"]


# ---------------------------------------------------------------- schema 1

def test_schema_1_plan_warns_but_passes(plan):
    del plan["schema"]
    for variant in plan["variants"]:
        for field in ("moment", "mood", "lead_color", "window_color", "motif"):
            del variant[field]
        for c in variant["cards"]:
            for field in ("role", "stars", "light"):
                del c[field]
    errors, warnings = cardgen.validate(plan)
    assert errors == []
    assert warnings == ['plan schema 1: no set bible, so set_guidelines.md is not checked (new plans use "schema": 2)']


def test_schema_1_rules_neighbours_and_four_per_colour(plan):
    del plan["schema"]
    card(plan, 1)["bg_color"] = "purple"  # same as its neighbour A01
    for i in (2, 4):
        card(plan, i)["bg_color"] = "green"  # five green... no: A02 purple now; make it five of one colour
    for i in (6, 8):
        card(plan, i)["bg_color"] = "green"
    errors = errors_of(plan)
    assert "A02: same background colour as its neighbour (purple)" in errors
    assert "variant A: 5 cards with a green background (max 4)" in errors


def test_a_single_variant_may_opt_into_schema_2(plan):
    del plan["schema"]
    plan["variants"][0]["schema"] = 2
    card(plan, 1)["bg_color"] = "purple"  # a same-colour neighbour: allowed by the window rule, not by schema 1
    plan["variants"][1]["cards"][1]["bg_color"] = "purple"
    errors = errors_of(plan)
    assert errors == ["B02: same background colour as its neighbour (purple)"]


# ---------------------------------------------------------------- the command

def test_validate_command(plan_path, plan, capsys):
    assert cardgen.main(["validate", str(plan_path)]) == 0
    assert capsys.readouterr().out.strip() == "Plan OK"
    plan["variants"][0]["cards"][0]["category"] = 5
    plan["variants"][0]["cards"][1]["name"] = "A Very Long Name Indeed"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    assert cardgen.main(["validate", str(plan_path)]) == 1
    out = capsys.readouterr().out
    assert "warning: A02: name 'A Very Long Name Indeed' is long" in out
    assert "ERROR: A01: category 5 is not 1-4" in out
