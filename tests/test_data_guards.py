"""Guards on the shipped data and docs: plans, final sets, the reference pack, prompt placeholders, cost-line wording."""

import json
import re
import string
from pathlib import Path

import pytest
from PIL import Image

import cardgen
import codex_images
import gemini_image

ROOT = Path(cardgen.ROOT)
PLANS = sorted(ROOT.glob("sets/*/plan.json"))
FINAL_SETS = sorted(ROOT.glob("sets/*/final_set"))
SKILL = ROOT / ".claude" / "skills" / "card-set" / "SKILL.md"
PIPELINE_README = ROOT / "pipeline" / "README.md"
RULEBOOK = ROOT / "pipeline" / "rulebook.md"
PROMPTS = ROOT / "pipeline" / "prompts"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def ids(path):
    return path.parent.name


@pytest.mark.parametrize("plan_path", PLANS, ids=ids)
def test_every_shipped_plan_validates_with_zero_errors(plan_path):
    errors, warnings = cardgen.validate(load(plan_path), plan_path)
    assert errors == []


def test_there_are_shipped_plans_and_final_sets():
    assert len(PLANS) >= 7 and len(FINAL_SETS) >= 4


@pytest.mark.parametrize("final_set", FINAL_SETS, ids=ids)
def test_final_set_has_10_cards_in_star_order_with_all_categories(final_set):
    sources = load(final_set / "sources.json")
    plan = load(final_set.parent / "plan.json")
    variant = next(v for v in plan["variants"] if v["id"] == sources["variant"])
    cards = variant["cards"]
    assert list(sources["cards"]) == [c["id"] for c in cards]  # the deliverable follows plan order
    assert [c["stars"] for c in cards] == cardgen.STARS
    assert [s["stars"] for s in sources["cards"].values()] == cardgen.STARS
    pngs = sorted(p.name for p in final_set.glob("*.png"))
    assert pngs == sorted(f"{c['id']}.png" for c in cards) and len(pngs) == 10
    for c in cards:
        assert Image.open(final_set / f"{c['id']}.png").size == (430, 480)
    categories = [c["category"] for c in cards]
    assert set(categories) == {1, 2, 3, 4}
    assert all(1 <= categories.count(k) <= 4 for k in (1, 2, 3, 4))
    for source in sources["cards"].values():
        assert source["from"]  # every card says where it came from


def test_reference_pack_has_12_refs_3_per_category_all_present(refs):
    spec = load(cardgen.REFS_FILE)
    assert len(spec["refs"]) == 12
    for category in (1, 2, 3, 4):
        assert len(refs.of_category(category)) == 3
    for ref in spec["refs"]:
        assert (cardgen.CARDS_DIR / f"{ref['cell']}.png").exists()
    assert len(refs.png) == 12 and all(data.startswith(b"\x89PNG") for data in refs.png.values())
    assert {r["id"] for r in refs.record} == {f"R{i}" for i in range(1, 13)}
    assert all(len(r["sha256"]) == 64 for r in refs.record)


def test_cost_line_wording_matches_the_docs(tmp_path):
    line = cardgen.cost_line(tmp_path, 1.23)
    prefix = line.split(":")[0]
    assert prefix == "Estimated cost"
    assert line.startswith("Estimated cost: $1.23 for generation and QA (from the attempt files)")
    for doc in (SKILL, PIPELINE_README):
        assert f'"{prefix}"' in doc.read_text(encoding="utf-8"), f"{doc.name} should name the {prefix!r} line of summary.md"
    prepare_src = (ROOT / "prepare.py").read_text(encoding="utf-8")
    assert f'startswith("{prefix}")' in prepare_src  # prepare.py reads the same line from summary.md


def test_every_prompt_file_named_in_the_docs_exists():
    named = set()
    for doc in (SKILL, PIPELINE_README, RULEBOOK, ROOT / "README.md"):
        named |= set(re.findall(r"prompts/([\w.-]+\.md)", doc.read_text(encoding="utf-8")))
    assert {"card_v7.md", "qa_v4.md"} <= named
    missing = sorted(name for name in named if not (PROMPTS / name).exists())
    assert missing == []
    assert cardgen.PROMPT_FILE.exists() and cardgen.QA_FILE.exists()


def placeholders(text):
    return {name for _, name, _, _ in string.Formatter().parse(text) if name}


@pytest.fixture
def cheap_images(monkeypatch):
    """Reference images as a small stub, so 200 cards' prompts build in a moment."""
    monkeypatch.setattr(gemini_image, "image_part", lambda data, mime_type="image/png": {"type": "image", "mime_type": mime_type, "data": ""})


def every_card():
    return [(plan_path.parent.name, card) for plan_path in PLANS for v in load(plan_path)["variants"] for card in v["cards"]]


def test_prompt_placeholders_are_all_filled_for_every_shipped_card(prompts, refs, fake_gemini, cheap_images):
    template, qa_template = prompts
    gen_names = set().union(*(placeholders(template[k]) for k in template))
    qa_names = placeholders(qa_template["PROMPT"])
    assert gen_names == {"n_refs", "ref_id", "category_short", "name", "subject", "unique_detail", "main_colors", "background",
                         "context_cue", "category", "category_rules", "fix"}
    assert qa_names == {"name", "subject", "unique_detail", "context_cue", "background", "category", "category_rule"}
    cards = every_card()
    assert len(cards) >= 200
    for set_name, card in cards:
        parts, texts = cardgen.generation_parts(card, template, refs, "")
        text = "\n".join(texts)
        for name in gen_names:
            assert "{" + name + "}" not in text, f"{set_name} {card['id']}: {{{name}}} left in the generation prompt"
        assert card["name"] in text and card["subject"] in text and card["background"] in text
        assert len(parts) == 1 + 2 * 12 + 1 and len(texts) == 1 + 12 + 1
        assert ("Context cue: " + (card.get("context_cue") or "none")) in text
        fake_gemini.texts.append('{"pass": true, "fix": ""}')
        cardgen.review(card, b"\x89PNG", "image/png", template, qa_template, refs)
        prompt = fake_gemini.text_of(fake_gemini.calls[-1])
        for name in qa_names:
            assert "{" + name + "}" not in prompt, f"{set_name} {card['id']}: {{{name}}} left in the QA prompt"
        assert card["name"] in prompt and template[f"CATEGORY_{card['category']}"] in prompt
        assert '"pass": true' in prompt  # the doubled braces of the answer shape survive str.format
        fake_gemini.calls.clear()


def test_codex_route_uses_the_same_card_text(prompts, refs, tmp_path, monkeypatch, cheap_images):
    template, _ = prompts
    plan_path = tmp_path / "plan.json"
    plan_path.write_bytes(PLANS[0].read_bytes())
    monkeypatch.setattr(codex_images, "rel", lambda path: path.as_posix())  # the temp plan is outside the repository
    plan = load(plan_path)
    variant = plan["variants"][0]
    codex_images.prepare(plan_path, [variant["id"]], "gpt")
    for card in variant["cards"]:
        prompt_file = (tmp_path / "gpt" / "prompts" / f"{card['id']}.md").read_text(encoding="utf-8")
        task = cardgen.generation_parts(card, template, refs, "")[1][-1]
        assert task in prompt_file, f"{card['id']}: the ChatGPT route's card text differs from the Gemini route's"
        assert prompt_file.count("Reference images, attach in this order:") == 1
        assert len(re.findall(r"^\d\. .+\.png$", prompt_file, re.M)) == 4  # 3 references of the category and the sheet
    task_file = tmp_path / "gpt" / f"codex_task_{variant['id']}.md"
    assert task_file.exists() and "Work only inside" in task_file.read_text(encoding="utf-8")


def test_skill_names_the_commands_that_exist():
    text = SKILL.read_text(encoding="utf-8")
    for script in re.findall(r"python -I pipeline/(\w+\.py)", text):
        assert (ROOT / "pipeline" / script).exists(), script
    for command in re.findall(r"cardgen\.py (\w+) ", text):
        assert command in ("validate", "run", "regen", "choose", "sheets", "summary", "setcheck"), command
