"""cardgen: turn a set plan into finished card illustrations (generate -> QA -> retry -> sheets).

    python -I pipeline/cardgen.py validate sets/<slug>/plan.json
    python -I pipeline/cardgen.py run sets/<slug>/plan.json [--variants A,B] [--cards A01,A02] [--workers 4] [--retries 2] [--no-qa]
    python -I pipeline/cardgen.py regen sets/<slug>/plan.json A05 --fix "make the bow pink"   # then reframes A05
    python -I pipeline/cardgen.py choose sets/<slug>/plan.json A05 try2   # undo: an earlier attempt becomes final
    python -I pipeline/cardgen.py sheets sets/<slug>/plan.json
    python -I pipeline/cardgen.py setcheck sets/<slug>/plan.json   # measured set checklist -> setcheck.md

Everything is written next to the plan:
- cards/<id>/try<n>.*: each attempt, with its request, response and QA records
- final/<id>.png: the accepted image, cropped to the card shape (430x480)
- sheets/: contact sheets
- summary.json and summary.md: verdicts, attempts, tokens and estimated cost
- costs.jsonl: every paid call of every script (costs.py); summary.md totals it

Finished cards are skipped on re-run, so an interrupted run can simply be started again. If the Gemini balance
runs out (HTTP 402), the command stops with a message saying so; top it up and run the same command again.
Needs GEMINI_API_KEY (see keys.py); the key is never printed or stored.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import io
import json
import re
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from PIL import Image  # noqa: E402

import colour_check  # noqa: E402
import costs  # noqa: E402
import gemini_image  # noqa: E402
from sheets import build_sheet, to_card  # noqa: E402

GEN_MODEL = "gemini-nano-banana-2.1"
QA_MODEL = "gemini-3.8-flash"
PROMPT_FILE = HERE / "prompts" / "card_v7.md"
QA_FILE = HERE / "prompts" / "qa_v4.md"
REFS_FILE = HERE / "refs_production.json"
CARDS_DIR = ROOT / "references" / "miro_v1" / "cards"
# USD, see costs.py (the QA rates are an unverified assumption; tokens are logged either way)
GEN_INPUT_PER_M, GEN_IMAGE_1K = costs.GEN_INPUT_PER_M, costs.GEN_IMAGE_1K
QA_INPUT_PER_M, QA_OUTPUT_PER_M = costs.TEXT_INPUT_PER_M, costs.TEXT_OUTPUT_PER_M
BG_COLORS = {"red", "orange", "yellow", "green", "blue", "purple", "pink"}
# Whole words only (W018: "brand" used to block "branding iron"). IP and text, then weapons, alcohol and tobacco.
BANNED = ["oscar", "academy award", "hollywood", "disney", "pixar", "marvel", "star wars", "harry potter",
          "titanic", "barbie", "coca", "pepsi", "nike", "mickey", "minnie", "indiana jones", "james bond",
          "logo", "brand", "trademark", "lettering", "writing that says", "sign that says",
          "gun", "guns", "rifle", "pistol", "revolver", "holster", "bullet", "bullets", "ammunition", "shotgun",
          "cannon", "sword", "dagger", "bomb", "dynamite", "grenade",
          "whiskey", "whisky", "beer", "wine", "liquor", "alcohol", "vodka", "rum", "champagne", "cocktail",
          "cigar", "cigarette", "tobacco"]
PEOPLE = ["man", "woman", "girl", "boy", "person", "people", "prince", "princess", "king", "queen",
          "character", "couple", "bride", "groom", "witch", "fairy"]
COLOUR_WORDS = {"red": "red", "crimson": "red", "scarlet": "red", "cherry": "red", "ruby": "red", "pink": "pink",
                "orange": "orange", "copper": "orange", "brown": "orange", "gold": "yellow", "brass": "yellow",
                "yellow": "yellow", "green": "green", "mint": "green", "blue": "blue", "navy": "blue",
                "purple": "purple", "violet": "purple", "lilac": "purple", "lavender": "purple"}
# Set bible (plan schema 2), from set_guidelines.md: the checklist items a plan can be checked against.
ROLES = {"carry": "a thing you carry or wear", "food": "food or drink", "gear": "a gadget, furniture or gear",
         "vehicle": "a vehicle", "place": "a place, building or landmark",
         "nature": "a natural thing: a plant, animal, rock, shell or celestial body"}  # W030: rocks and planets had no role
LIGHTS = {"day", "sunset", "night"}
WINDOW_COLORS = {"orange", "pink", "violet", "blue"}  # the 4 empty set templates on the brief's board
STARS = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5]  # rarity layout of the final reference windows and the templates
WINDOW_PAIRS = [(i, i + 1) for i in range(9) if i != 4] + [(i, i + 5) for i in range(5)]  # neighbours in the 5x2 window
CATEGORY_SHORT = {
    1: "category 1: floating object, simple background",
    2: "category 2: object on a plain surface, simple background",
    3: "category 3: object on a realistic surface, simple back wall",
    4: "category 4: object inside a realistic environment, low angle",
}
LOCK = threading.Lock()
STOP = threading.Event()  # set when the Gemini balance is empty: no new calls anywhere in this process (W023)


def load_sections(path: Path) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    name = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            name = line[3:].strip()
            sections[name] = []
        elif name:
            sections[name].append(line)
    return {key: "\n".join(lines).strip() for key, lines in sections.items()}


# ---------------------------------------------------------------- plan validation

def main_colour_family(text: str) -> str | None:
    """Colour family of the first colour word in a card's main_colors, if any."""
    hits = [(m.start(), family) for word, family in COLOUR_WORDS.items() for m in re.finditer(rf"\b{word}", text.lower())]
    return min(hits)[1] if hits else None


def check_set_bible(variant: dict, errors: list[str], warnings: list[str]) -> None:
    """Plan schema 2: the items of the set checklist (set_guidelines.md §5) that a plan can be checked against."""
    vid, cards = variant.get("id", "?"), variant.get("cards", [])
    for field in ("moment", "mood", "lead_color", "window_color", "motif"):
        if not variant.get(field):
            (warnings if field == "motif" else errors).append(f"variant {vid}: missing set-bible field '{field}'")
    lead = variant.get("lead_color")
    if lead and lead not in BG_COLORS:
        errors.append(f"variant {vid}: lead_color '{lead}' not in {sorted(BG_COLORS)}")
    if variant.get("window_color") and variant["window_color"] not in WINDOW_COLORS:
        errors.append(f"variant {vid}: window_color '{variant['window_color']}' not in {sorted(WINDOW_COLORS)}")
    roles = [c.get("role") for c in cards]  # checklist 3: the kit of the experience
    bad = [c.get("id") for c in cards if c.get("role") not in ROLES]
    if bad:
        errors.append(f"variant {vid}: role missing or not one of {sorted(ROLES)}: {bad}")
    used = {r for r in roles if r in ROLES}
    if len(used) < 4:
        errors.append(f"variant {vid}: {len(used)} object roles (need at least 4)")
    errors += [f"variant {vid}: {roles.count(r)} cards with role '{r}' (max 4)" for r in sorted(used) if roles.count(r) > 4]
    stars = [c.get("stars") for c in cards]  # checklist 5: the crescendo
    if stars != STARS[:len(cards)]:
        errors.append(f"variant {vid}: stars in card order must be {STARS}, found {stars}")
    elif not any(c.get("category") == 4 for c in cards[6:]):
        warnings.append(f"variant {vid}: no category 4 scene among the 4-5 star cards (big places usually close a set)")
    colors = [c.get("bg_color") for c in cards]  # checklist 6: colour
    if lead in BG_COLORS:
        n = colors.count(lead)
        if not 2 <= n <= 6:
            errors.append(f"variant {vid}: lead colour {lead} on {n} cards (reference sets: 2-6, aim 3-5)")
        elif not 3 <= n <= 5:
            warnings.append(f"variant {vid}: lead colour {lead} on {n} cards (aim 3-5)")
        warnings += [f"variant {vid}: {colors.count(c)} {c} cards; only the lead colour should exceed 3"
                     for c in sorted(set(colors) - {lead}) if c and colors.count(c) > 3]
    families = len(set(colors))
    if not 4 <= families <= 7:
        warnings.append(f"variant {vid}: {families} colour families (reference sets: 4-7, aim 5-6)")
    same = [f"{cards[a].get('id')}-{cards[b].get('id')}" for a, b in WINDOW_PAIRS if b < len(colors) and colors[a] == colors[b]]
    if len(same) > 2:
        errors.append(f"variant {vid}: {len(same)} same-colour neighbours in the 5x2 window (max 2): {', '.join(same)}")
    lights = [c.get("light", "day") for c in cards]  # checklist 7: light
    if any(light not in LIGHTS for light in lights):
        errors.append(f"variant {vid}: light must be one of {sorted(LIGHTS)}")
    if sum(light != "day" for light in lights) > 2:
        errors.append(f"variant {vid}: {sum(light != 'day' for light in lights)} sunset or night cards (max 2)")
    warnings += [f"{c.get('id')}: name '{c.get('name')}' is long (keep 1-2 words, up to 16 characters)"  # checklist 9
                 for c in cards if len(str(c.get("name", "")).split()) > 2 or len(str(c.get("name", ""))) > 16]


NOT_OBJECTS = {"time", "spot", "day", "night", "party", "fun", "life", "trail", "hunt", "dream", "show", "magic"}


def collection_overlaps(plan: dict, plan_path: Path) -> list[str]:
    """Cards whose name ends in the same object word as a card of a finished set of the collection, that is a set
    with final_set/sources.json (W030: the QA judge sees one card at a time, so it passed a scooter that repeated
    Love in the City's Vintage Scooter)."""
    def head(name: str) -> str:
        word = re.sub(r"[^a-z]", "", (name.lower().split() or [""])[-1])
        return word[:-1] if word.endswith("s") and not word.endswith("ss") and len(word) > 3 else word
    others: dict[str, str] = {}
    for sources in sorted(plan_path.resolve().parent.parent.glob("*/final_set/sources.json")):
        if sources.parent.parent == plan_path.resolve().parent:
            continue
        try:
            data = json.loads(sources.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for card in data.get("cards", {}).values():
            others.setdefault(head(card.get("name", "")), f"{card.get('name')} ({data.get('set', sources.parent.parent.name)})")
    return [f"{c.get('id')}: '{c.get('name')}' repeats the object of {others[key]} in the collection"
            for v in plan.get("variants", []) for c in v.get("cards", [])
            if (key := head(c.get("name", ""))) in others and key not in NOT_OBJECTS]


def validate(plan: dict, plan_path: Path | None = None) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    if plan_path is not None:
        warnings += collection_overlaps(plan, plan_path)
    schema = plan.get("schema", 1)
    if schema < 2:
        warnings.append("plan schema 1: no set bible, so set_guidelines.md is not checked (new plans use \"schema\": 2)")
    variants = plan.get("variants", [])
    if not 3 <= len(variants) <= 5:
        errors.append(f"need 3-5 variants, found {len(variants)}")
    seen_ids = set()
    for variant in variants:
        vid, cards = variant.get("id", "?"), variant.get("cards", [])
        vschema = variant.get("schema", schema)  # a single variant may opt in (chosen variants of schema-1 plans)
        if len(cards) != 10:
            errors.append(f"variant {vid}: needs exactly 10 cards, found {len(cards)}")
        names = [c.get("name", "").strip().lower() for c in cards]
        if len(set(names)) != len(names):
            errors.append(f"variant {vid}: duplicate card names")
        counts = {k: sum(1 for c in cards if c.get("category") == k) for k in (1, 2, 3, 4)}
        for k, n in counts.items():
            if not 1 <= n <= 4:
                errors.append(f"variant {vid}: category {k} appears {n} times (allowed 1-4)")
        colors = [c.get("bg_color", "") for c in cards]
        for i, color in enumerate(colors):
            if color not in BG_COLORS:
                errors.append(f"{cards[i].get('id')}: bg_color '{color}' not in {sorted(BG_COLORS)}")
            if vschema < 2 and i and color == colors[i - 1]:  # schema 1 rule; schema 2 checks the 5x2 window instead
                errors.append(f"{cards[i].get('id')}: same background colour as its neighbour ({color})")
        if vschema < 2:
            errors += [f"variant {vid}: {colors.count(c)} cards with a {c} background (max 4)" for c in set(colors) if colors.count(c) > 4]
        else:
            check_set_bible(variant, errors, warnings)
        for card in cards:
            cid = card.get("id", "?")
            if cid in seen_ids:
                errors.append(f"duplicate card id {cid}")
            seen_ids.add(cid)
            for field in ("id", "name", "category", "subject", "unique_detail", "main_colors", "background", "bg_color"):
                if card.get(field) in (None, ""):
                    errors.append(f"{cid}: missing {field}")
            if card.get("category") not in (1, 2, 3, 4):  # no gold character cards (category 5), and no typos (W023)
                errors.append(f"{cid}: category {card.get('category')!r} is not 1-4")
            text = " ".join(str(card.get(f, "")) for f in ("name", "subject", "unique_detail", "background", "context_cue")).lower()
            errors += [f"{cid}: banned term '{term}'" for term in BANNED if re.search(rf"\b{re.escape(term)}\b", text)]
            warnings += [f"{cid}: mentions '{term}' (no people or characters allowed)" for term in PEOPLE
                         if re.search(rf"\b{term}\b", text)]
            family = main_colour_family(str(card.get("main_colors", "")))
            if family and family == card.get("bg_color"):  # W016: 3 of 7 such cards passed with Pavel (72% overall)
                warnings.append(f"{cid}: the object ({family}) and its background share one colour family")
    return errors, warnings


# ---------------------------------------------------------------- generation and QA

class Refs:
    def __init__(self) -> None:
        spec = json.loads(REFS_FILE.read_text(encoding="utf-8"))
        self.refs = spec["refs"]
        self.png: dict[str, bytes] = {}
        for ref in self.refs:
            buffer = io.BytesIO()
            Image.open(CARDS_DIR / f"{ref['cell']}.png").convert("RGB").save(buffer, "PNG")
            self.png[ref["id"]] = buffer.getvalue()
        self.record = [{**r, "sha256": hashlib.sha256(self.png[r["id"]]).hexdigest()} for r in self.refs]

    def of_category(self, category: int) -> list[dict]:
        return [r for r in self.refs if r["category"] == category]


def generation_parts(card: dict, template: dict, refs: Refs, fix: str) -> tuple[list[dict], list[str]]:
    parts = [gemini_image.text_part(template["INTRO"].format(n_refs=len(refs.refs)))]
    texts = [parts[0]["text"]]
    for ref in refs.refs:
        label = template["REFERENCE_LABEL"].format(ref_id=ref["id"], category_short=CATEGORY_SHORT[ref["category"]])
        parts += [gemini_image.text_part(label), gemini_image.image_part(refs.png[ref["id"]])]
        texts.append(label)
    task = template["TASK"].format(
        name=card["name"], subject=card["subject"], unique_detail=card["unique_detail"],
        main_colors=card["main_colors"], background=card["background"],
        context_cue=card.get("context_cue") or "none", category=card["category"],
        category_rules=template[f"CATEGORY_{card['category']}"],
        fix=f"- Correction from the art review of the previous attempt: {fix}" if fix else "",
    ).rstrip()
    parts.append(gemini_image.text_part(task))
    texts.append(task)
    return parts, texts


def review(card: dict, image: bytes, mime: str, template: dict, qa_template: dict, refs: Refs) -> dict:
    prompt = qa_template["PROMPT"].format(
        name=card["name"], subject=card["subject"], unique_detail=card["unique_detail"], background=card["background"],
        context_cue=card.get("context_cue") or "none",  # W023: without it the judge failed planned cues as extra props
        category=card["category"], category_rule=template[f"CATEGORY_{card['category']}"])
    parts = [gemini_image.text_part(prompt), gemini_image.image_part(image, mime)]
    parts += [gemini_image.image_part(refs.png[r["id"]]) for r in refs.of_category(card["category"])[:2]]
    result = gemini_image.generate_text(QA_MODEL, parts)
    raw = result["text"]
    try:
        verdict = json.loads(raw[raw.index("{"): raw.rindex("}") + 1])
    except ValueError:  # W025: this used to count as a pass
        verdict = {"pass": None, "qa_error": "unparseable QA answer", "raw": raw[:2000]}
    if not isinstance(verdict, dict):
        verdict = {"pass": None, "qa_error": "QA answer is not a JSON object", "raw": raw[:2000]}
    elif not isinstance(verdict.get("pass"), bool):
        verdict.update({"pass": None, "qa_error": "QA answer has no true/false verdict"})
    usage = result["response"].get("usage", {})
    verdict["usage"] = usage
    verdict["est_cost_usd"] = costs.text_cost(usage)
    verdict["elapsed_s"] = result["elapsed_s"]
    return verdict


def judge(card: dict, image: bytes, mime: str, out: Path, template: dict, qa_template: dict, refs: Refs) -> dict:
    """The QA verdict on one image: the vision judge, asked once more if its answer has no verdict, then the pixel
    colour check. "pass" is True, False or None (no verdict: the call failed or the answer was unreadable)."""
    verdict: dict = {"pass": None}
    for _ in range(2):
        try:
            verdict = review(card, image, mime, template, qa_template, refs)
            costs.log(out, "qa", card["id"], verdict["est_cost_usd"])
        except gemini_image.GeminiError as err:  # unreviewed is "unchecked", never "passed" (W023)
            verdict = {"pass": None, "qa_error": str(err)[:300]}
            if isinstance(err, gemini_image.BillingError):
                STOP.set()
            break
        if verdict.get("pass") is not None:
            break
    colour = colour_check.check(to_card(Image.open(io.BytesIO(image)).convert("RGB"), 480), card)
    if colour:  # the pixel check overrules the vision judge on the background colour
        verdict.setdefault("checks", {})["bg_colour"] = colour
        if not colour["pass"]:
            verdict["pass"] = False
            verdict["fix"] = f"Make the background {card['bg_color']}: {card['background']}. {verdict.get('fix', '')}".strip()
    return verdict


def record_verdict(attempt: dict, verdict: dict, stem: Path) -> None:
    Path(f"{stem}.qa.json").write_text(json.dumps(verdict, indent=2), encoding="utf-8")
    attempt.update(qa_pass=qa_pass(verdict), qa_cost=verdict.get("est_cost_usd", 0),
                   failed=[k for k, v in verdict.get("checks", {}).items() if isinstance(v, dict) and not v.get("pass")],
                   fix=verdict.get("fix", ""), checks_passed=passed_checks(verdict))


def passed_checks(verdict: dict) -> int:
    return sum(1 for check in verdict.get("checks", {}).values() if isinstance(check, dict) and check.get("pass"))


def produce_card(card: dict, out: Path, template: dict, qa_template: dict, refs: Refs,
                 retries: int, use_qa: bool, first_fix: str = "") -> dict:
    card_dir = out / "cards" / card["id"]
    card_dir.mkdir(parents=True, exist_ok=True)
    attempts, fix, reviewer_fix = [], first_fix, ""
    existing = sorted(card_dir.glob("try*.request.json"))
    start = len(existing) + 1
    rounds = retries + 1
    # W025: an earlier attempt with an image but no verdict (its QA call failed or was cut off) is reviewed before
    # anything new is drawn, so an interrupted run resumes without paying for the image again
    waiting = next((a for a in reversed(collect_card(card, out)["attempts"]) if a.get("file") and a.get("qa_pass") is None),
                   None) if use_qa else None
    if waiting and not STOP.is_set():
        image = (card_dir / waiting["file"]).read_bytes()
        verdict = judge(card, image, "image/jpeg" if waiting["file"].endswith(".jpg") else "image/png", out, template,
                        qa_template, refs)
        attempt = {k: waiting[k] for k in ("try", "file", "gen_cost", "gen_s") if k in waiting}
        record_verdict(attempt, verdict, card_dir / f"try{waiting['try']}")
        attempts.append(attempt)
        if attempt["qa_pass"] is not False:  # passed, or still no verdict: draw nothing new
            rounds = 0
        else:
            reviewer_fix = attempt["fix"]
            fix = " ".join(p for p in (first_fix, reviewer_fix) if p)
            rounds = retries  # the reviewed attempt counts as one of the attempts
    for n in range(start, start + rounds):
        if STOP.is_set():
            break
        parts, texts = generation_parts(card, template, refs, fix)
        stem = card_dir / f"try{n}"
        request = {"card": card, "model": GEN_MODEL, "prompt_file": PROMPT_FILE.name, "refs": refs.record,
                   "text_parts": texts, "fix": fix, "sent_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        Path(f"{stem}.request.json").write_text(json.dumps(request, indent=2), encoding="utf-8")
        try:
            result = gemini_image.generate_image(GEN_MODEL, parts, aspect_ratio="1:1", image_size="1K")
        except gemini_image.GeminiError as err:
            Path(f"{stem}.error.txt").write_text(str(err), encoding="utf-8")
            attempts.append({"try": n, "error": str(err)[:300]})
            if isinstance(err, gemini_image.BillingError):
                STOP.set()
                break
            continue
        ext = ".jpg" if "jpeg" in result["mime_type"] else ".png"
        image = result.pop("image_bytes")
        Path(f"{stem}{ext}").write_bytes(image)
        usage = result["response"].get("usage", {})
        result["est_cost_usd"] = costs.image_cost(usage)
        costs.log(out, "generate", card["id"], result["est_cost_usd"])
        Path(f"{stem}.response.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        attempt = {"try": n, "file": f"try{n}{ext}", "gen_cost": result["est_cost_usd"], "gen_s": result["elapsed_s"]}
        if use_qa:
            record_verdict(attempt, judge(card, image, result["mime_type"], out, template, qa_template, refs), stem)
        else:
            attempt.update(qa_pass=None, checks_passed=None)
        attempts.append(attempt)
        if not use_qa or attempt["qa_pass"] is not False:  # passed, or no verdict to retry against
            break
        reviewer_fix = attempt["fix"] or reviewer_fix
        fix = " ".join(p for p in (first_fix, reviewer_fix) if p)  # a reviewer's note adds to the producer's, never replaces it
    errors = [a["error"] for a in attempts if "error" in a]
    note = f"; {len(errors)} call(s) failed, the last: {errors[-1][:90]}" if errors else ""
    good = [a for a in attempts if "file" in a]
    if STOP.is_set() and not any(a.get("qa_pass") for a in good):
        # W025: the balance ran out before a verdict; the earlier final image and choice stay, and the new attempt
        # waits in cards/<id>/ to be reviewed on the next run
        with LOCK:
            print(f"{card['id']} {card['name']}: stopped, final image unchanged{note}", flush=True)
        return {"id": card["id"], "status": "interrupted", "attempts": attempts}
    if not good:
        with LOCK:
            print(f"{card['id']} {card['name']}: no image{note}", flush=True)
        return {"id": card["id"], "status": "failed", "attempts": attempts}
    best = next((a for a in good if a.get("qa_pass")), None) or max(good, key=lambda a: a.get("checks_passed") or 0)
    final = out / "final" / f"{card['id']}.png"
    final.parent.mkdir(exist_ok=True)
    to_card(Image.open(card_dir / best["file"]).convert("RGB"), 480).save(final)
    status = attempt_status(best, use_qa)
    (card_dir / "chosen.json").write_text(json.dumps({"file": best["file"], "status": status}), encoding="utf-8")
    with LOCK:
        print(f"{card['id']} {card['name']}: {status} after {len(attempts)} attempt(s){note}", flush=True)
    return {"id": card["id"], "name": card["name"], "status": status, "chosen": best["file"], "attempts": attempts}


def qa_pass(verdict: dict) -> bool | None:
    """True or False from the judge; None when there is no verdict (the QA call failed)."""
    return None if verdict.get("pass") is None else bool(verdict["pass"])


def attempt_status(attempt: dict, use_qa: bool = True) -> str:
    if attempt.get("qa_pass"):
        return "passed"
    return "unchecked" if not use_qa or attempt.get("qa_pass") is None else "accepted_with_issues"


def selected_cards(plan: dict, variants: str | None, cards: str | None) -> list[dict]:
    wanted_v = set(variants.split(",")) if variants else None
    wanted_c = set(cards.split(",")) if cards else None
    return [c for v in plan["variants"] if not wanted_v or v["id"] in wanted_v
            for c in v["cards"] if not wanted_c or c["id"] in wanted_c]


def run(plan_path: Path, args: argparse.Namespace) -> None:
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    errors, warnings = validate(plan)
    for w in warnings:
        print("warning:", w)
    if errors:
        raise SystemExit("Plan invalid:\n  " + "\n  ".join(errors))
    out = plan_path.parent
    template, qa_template, refs = load_sections(PROMPT_FILE), load_sections(QA_FILE), Refs()
    def needs_work(card: dict) -> bool:
        if not (out / "final" / f"{card['id']}.png").exists():
            return True
        chosen = out / "cards" / card["id"] / "chosen.json"  # W025: a card left without a verdict gets reviewed
        return not args.no_qa and chosen.exists() and json.loads(chosen.read_text(encoding="utf-8")).get("status") == "unchecked"
    todo = [c for c in selected_cards(plan, args.variants, args.cards) if needs_work(c)]
    print(f"{len(todo)} card(s) to make with {GEN_MODEL}; QA {'on (' + QA_MODEL + ')' if not args.no_qa else 'off'}; "
          f"up to {1 + args.retries} attempt(s) each; ~${0.055 * len(todo):.2f} per attempt round")
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(produce_card, c, out, template, qa_template, refs, args.retries, not args.no_qa) for c in todo]
        for future, card in zip(futures, todo):
            try:
                future.result()
            except Exception as err:  # one card's failure must never stop the rest of the set
                with LOCK:
                    print(f"{card['id']} {card['name']}: crashed ({err!r}); re-run to retry it", flush=True)
    write_summary(plan, out)
    sheets(plan_path)
    if STOP.is_set():
        raise SystemExit(gemini_image.BILLING_HELP)


def regen(plan_path: Path, card_id: str, fix: str, use_qa: bool, frame: bool = True) -> None:
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    card = next(c for v in plan["variants"] for c in v["cards"] if c["id"] == card_id)
    out = plan_path.parent
    result = {}
    try:  # final/<id>.png is replaced only once a new image exists; every earlier attempt stays in cards/<id>/
        result = produce_card(card, out, load_sections(PROMPT_FILE), load_sections(QA_FILE), Refs(), 1, use_qa, fix)
    finally:
        write_summary(plan, out)
    if STOP.is_set():
        sheets(plan_path)
        raise SystemExit(gemini_image.BILLING_HELP)
    print(f"{card_id}: compare it with the earlier attempts in cards/{card_id}/; "
          f"'cardgen.py choose <plan> {card_id} try<n>' brings an earlier one back")
    finish_card(plan_path, card_id, frame and result.get("status") != "failed")


def finish_card(plan_path: Path, card_id: str, frame: bool) -> None:
    """After regen or choose: frame the new final image like the rest of the set (W023), then rebuild the sheets."""
    if frame and (plan_path.parent / "reframe_log.json").exists():  # only once the set has been framed
        import reframe  # here, not at the top: reframe imports cardgen
        code = reframe.main([str(plan_path), "--route", "gemini", "--ids", card_id])
        if code:
            raise SystemExit(code)
    else:
        sheets(plan_path)


def choose(plan_path: Path, card_id: str, attempt: str, frame: bool = True) -> None:
    """Make an earlier attempt the card's final image, for example to undo a regen (W023)."""
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    card = next(c for v in plan["variants"] for c in v["cards"] if c["id"] == card_id)
    out = plan_path.parent
    n = int(attempt.lower().removeprefix("try"))
    record = next((a for a in collect_card(card, out)["attempts"] if a["try"] == n and a.get("file")), None)
    if not record:
        raise SystemExit(f"{card_id}: try{n} has no image in cards/{card_id}/")
    status = attempt_status(record, "qa_pass" in record)
    card_dir = out / "cards" / card_id
    (card_dir / "chosen.json").write_text(json.dumps({"file": record["file"], "status": status, "by": "choose"}),
                                          encoding="utf-8")
    to_card(Image.open(card_dir / record["file"]).convert("RGB"), 480).save(out / "final" / f"{card_id}.png")
    write_summary(plan, out)
    print(f"{card_id} {card['name']}: try{n} is now the final image ({status})")
    finish_card(plan_path, card_id, frame)


def collect_card(card: dict, out: Path) -> dict:
    """Rebuild a card's record from the files on disk, so summaries survive crashes and re-runs."""
    card_dir = out / "cards" / card["id"]
    attempts = []
    tries = sorted(card_dir.glob("try*.request.json"), key=lambda p: int(p.name[3:].split(".")[0]))
    for request in tries:
        n = int(request.name[3:].split(".")[0])
        stem = card_dir / f"try{n}"
        attempt: dict = {"try": n}
        response, error, qa = Path(f"{stem}.response.json"), Path(f"{stem}.error.txt"), Path(f"{stem}.qa.json")
        if response.exists():
            r = json.loads(response.read_text(encoding="utf-8"))
            image = next((p.name for p in card_dir.glob(f"try{n}.*") if p.suffix in (".jpg", ".png")), None)
            attempt.update(file=image, gen_cost=r.get("est_cost_usd", 0), gen_s=r.get("elapsed_s"))
        elif error.exists():
            attempt["error"] = error.read_text(encoding="utf-8")[:300]
        else:
            attempt["error"] = "no response recorded (run interrupted)"
        if qa.exists():
            q = json.loads(qa.read_text(encoding="utf-8"))
            attempt.update(qa_pass=qa_pass(q), qa_cost=q.get("est_cost_usd", 0), fix=q.get("fix", ""),
                           failed=[k for k, v in q.get("checks", {}).items() if isinstance(v, dict) and not v.get("pass")],
                           checks_passed=passed_checks(q))
        attempts.append(attempt)
    chosen_path, final = card_dir / "chosen.json", out / "final" / f"{card['id']}.png"
    if chosen_path.exists():
        chosen = json.loads(chosen_path.read_text(encoding="utf-8"))
    elif final.exists():  # cards finished before chosen.json existed: same rule as produce_card
        good = [a for a in attempts if a.get("file")]
        best = next((a for a in good if a.get("qa_pass")), None) or max(good, key=lambda a: a.get("checks_passed") or 0)
        chosen = {"file": best["file"], "status": attempt_status(best)}
    else:
        chosen = {"file": None, "status": "failed" if attempts else "not_started"}
    return {"id": card["id"], "name": card["name"], "status": chosen["status"], "chosen": chosen["file"], "attempts": attempts}


def write_summary(plan: dict, out: Path) -> None:
    cards = [collect_card(c, out) for v in plan["variants"] for c in v["cards"]]
    attempts = [a for c in cards for a in c["attempts"]]
    statuses = ("passed", "accepted_with_issues", "unchecked", "failed", "not_started")
    summary = {
        "set": plan["set"], "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "images_generated": sum(1 for a in attempts if a.get("file")),
        "qa_reviews": sum(1 for a in attempts if "qa_pass" in a),
        "first_try_pass": sum(1 for c in cards if c["attempts"] and c["attempts"][0].get("qa_pass")),
        "est_cost_usd": round(sum((a.get("gen_cost") or 0) + (a.get("qa_cost") or 0) for a in attempts), 2),
        "status_counts": {s: sum(1 for c in cards if c["status"] == s) for s in statuses},
        "cards": {c["id"]: c for c in cards},
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    lines = [f"# {plan['set']}: run summary", "",
             f"Images generated: {summary['images_generated']}; QA reviews: {summary['qa_reviews']}; "
             f"passed on the first try: {summary['first_try_pass']} of {len(cards)}.", "",
             cost_line(out, summary["est_cost_usd"]), "",
             f"Status: {summary['status_counts']}", "",
             "| card | name | status | attempts | QA fails on the chosen attempt | open reviewer's fix |", "|---|---|---|---|---|---|"]
    for c in cards:
        chosen = next((a for a in c["attempts"] if a.get("file") == c["chosen"]), {})
        # The reviewer's fix for the chosen image, only while still open (W018); W023: it used to come from the last attempt.
        open_fix = "" if c["status"] == "passed" else (chosen.get("fix") or "")
        lines.append(f"| {c['id']} | {c['name']} | {c['status']} | {len(c['attempts'])} | "
                     f"{', '.join(chosen.get('failed', [])) or '-'} | {open_fix[:120]} |")
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def cost_line(out: Path, gen_qa: float) -> str:
    """Generation and QA come from the attempt files; everything else from costs.jsonl, so nothing is counted twice."""
    other = {k: v for k, v in costs.totals(out).items() if k not in ("generate", "qa", "total")}
    text = f"Estimated cost: ${gen_qa:.2f} for generation and QA (from the attempt files)"
    if other:
        extra = sum(other.values())
        parts = ", ".join(f"{k} ${v:.3f}" for k, v in other.items())
        text += f" + ${extra:.3f} for {parts} (costs.jsonl) = ${gen_qa + extra:.2f}"
    if older_than_log(out):  # only sets begun before the log existed (W030: the remark confused a new set's report)
        text += (". This set began before costs.jsonl existed (W023), so earlier background extension and vision calls "
                 "are missing")
    return text + ". Text-model rates unverified."


def older_than_log(out: Path) -> bool:
    """True if the set's first generation request is older than its first costs.jsonl entry."""
    log = out / "costs.jsonl"
    first_logged = log.read_text(encoding="utf-8").split("\n", 1)[0] if log.exists() else ""
    sent = [json.loads(p.read_text(encoding="utf-8")).get("sent_at", "") for p in out.glob("cards/*/try1.request.json")]
    if not sent:
        return False
    if not first_logged:
        return True
    # a request is stamped when sent and its log line written when it returns, so allow a margin
    first_sent = datetime.fromisoformat(min(s for s in sent if s))
    return (datetime.fromisoformat(json.loads(first_logged)["at"]) - first_sent).total_seconds() > 600


# ---------------------------------------------------------------- sheets

def sheets(plan_path: Path) -> None:
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    out = plan_path.parent
    final = out / "final"
    rows_overview = []
    for variant in plan["variants"]:
        cards = [c for c in variant["cards"] if (final / f"{c['id']}.png").exists()]
        if not cards:
            continue
        items = [(f"{c['id']} {c['name']} C{c['category']} {'*' * c.get('stars', 0)}".rstrip(), final / f"{c['id']}.png") for c in cards]
        build_sheet([(f"{variant['id']} 1-5", items[:5]), (f"{variant['id']} 6-10", items[5:])],
                    out / "sheets" / f"variant_{variant['id']}.png", 240, f"{plan['set']}: variant {variant['id']}, {variant.get('concept', '')}")
        rows_overview.append((f"Variant {variant['id']}", [(c["id"], final / f"{c['id']}.png") for c in cards]))
    if rows_overview:
        build_sheet(rows_overview, out / "sheets" / "overview.png", 150, f"{plan['set']}: all variants")
        build_sheet(rows_overview, out / "sheets" / "overview_card_size.png", 66, f"{plan['set']} at card size")
        print(f"Sheets: {out / 'sheets'}")


# ---------------------------------------------------------------- set check (measured)

SHORT = {"red": "R", "orange": "O", "yellow": "Y", "green": "G", "teal": "T", "blue": "B", "purple": "P", "pink": "K",
         "grey/dark": "-"}


def setcheck(plan_path: Path, final_dir: str = "final") -> str:
    """Measure each finished variant against the set checklist (set_guidelines.md §5); write setcheck.md."""
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    out = plan_path.parent
    errors, warnings = validate(plan)
    lines = [f"# {plan['set']}: set check ({final_dir}/)", "",
             "Planned values come from plan.json. Measured values come from the final images: the backdrop colour family "
             "of each card, by pixels, as in colour_check.py. Reference ranges are from the 15 object sets of the reference "
             "collection (analysis/set_palette_profile.md): 4-7 colour families (mean 5.5), the leading family on 2-6 cards "
             "(mean 3.8), and 1.7 of 13 same-colour neighbour pairs on average.", "",
             f"Plan check: {len(errors)} error(s), {len(warnings)} warning(s).", ""]
    lines += [f"- ERROR: {e}" for e in errors] + [f"- warning: {w}" for w in warnings] + [""]
    head = ["Variant", "Moment / mood", "Roles", "Stars", "Lead colour: planned / measured cards",
            "Backdrops measured (cards 1-5 / 6-10)", "Families", "Same-colour neighbours", "Sunset / night",
            "Backdrop differs from plan"]
    lines += ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for variant in plan["variants"]:
        cards = variant["cards"]
        paths = [out / final_dir / f"{c['id']}.png" for c in cards]
        if not all(p.exists() for p in paths):
            lines.append(f"| {variant['id']} | (not all cards finished) |" + " |" * (len(head) - 2))
            continue
        measured = [colour_check.backdrop_family(Image.open(p)) for p in paths]
        lead = variant.get("lead_color", "")
        planned = [c.get("bg_color") for c in cards]
        roles = [c.get("role") for c in cards if c.get("role")]
        same = sum(measured[a] == measured[b] for a, b in WINDOW_PAIRS)
        differs = [f"{c['id']} ({c['bg_color']} -> {m})" for c, m in zip(cards, measured) if m != c["bg_color"]]
        row = [variant["id"], f"{variant.get('moment', '-')} / {variant.get('mood', '-')}",
               f"{len(set(roles))}: " + ", ".join(f"{r} {roles.count(r)}" for r in sorted(set(roles))) if roles else "-",
               "ok" if [c.get("stars") for c in cards] == STARS else "not 1,1,2,2,3,3,4,4,5,5",
               f"{lead or '-'}: {planned.count(lead)} / {measured.count(lead)}" if lead else "-",
               " ".join(SHORT[m] for m in measured[:5]) + " / " + " ".join(SHORT[m] for m in measured[5:]),
               str(len(set(measured))), f"{same}/13", str(sum(c.get("light", "day") != "day" for c in cards)),
               ", ".join(differs) or "-"]
        lines.append("| " + " | ".join(row) + " |")
    lines += ["", "The visual items (name test, one world, mood, motif, overlap with other sets) are judged by the agent "
              "and the designer on the variant sheets; see SKILL.md."]
    text = "\n".join(lines) + "\n"
    (out / ("setcheck.md" if final_dir == "final" else f"setcheck_{final_dir.replace('/', '_')}.md")).write_text(text, encoding="utf-8")
    return text


def main(argv: list[str]) -> int:
    sys.stdout.reconfigure(errors="replace")  # a cp1251 console must never crash a run on a non-ASCII character (W018)
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["validate", "run", "regen", "choose", "sheets", "summary", "setcheck"])
    parser.add_argument("plan", type=Path)
    parser.add_argument("card", nargs="?", help="card id for regen and choose")
    parser.add_argument("attempt", nargs="?", help="choose: the attempt to make final, e.g. try2")
    parser.add_argument("--variants")
    parser.add_argument("--cards")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--no-qa", action="store_true")
    parser.add_argument("--fix", default="")
    parser.add_argument("--no-reframe", action="store_true", help="regen, choose: leave the new final image unframed")
    parser.add_argument("--final-dir", default="final", help="setcheck: folder of finished images, relative to the plan")
    args = parser.parse_args(argv)
    if args.command == "validate":
        errors, warnings = validate(json.loads(args.plan.read_text(encoding="utf-8")), args.plan)
        for w in warnings:
            print("warning:", w)
        print("\n".join(f"ERROR: {e}" for e in errors) or "Plan OK")
        return 1 if errors else 0
    if args.command == "run":
        run(args.plan, args)
    elif args.command == "regen":
        if not args.card:
            raise SystemExit("regen needs a card id")
        regen(args.plan, args.card, args.fix, not args.no_qa, not args.no_reframe)
    elif args.command == "choose":
        if not (args.card and args.attempt):
            raise SystemExit("choose needs a card id and an attempt, e.g. A05 try2")
        choose(args.plan, args.card, args.attempt, not args.no_reframe)
    elif args.command == "summary":
        write_summary(json.loads(args.plan.read_text(encoding="utf-8")), args.plan.parent)
        sheets(args.plan)
    elif args.command == "setcheck":
        print(setcheck(args.plan, args.final_dir))
    else:
        sheets(args.plan)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
