"""Helpers shared by the tests: a scripted Gemini stand-in, synthetic card images and a valid plan factory.

Nothing here touches the network. The pipeline modules are imported as top-level names (cardgen, gemini_image ...),
the way they import each other, so a monkeypatch on gemini_image reaches every caller.
"""

from __future__ import annotations

import copy
import io
import json
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw

import gemini_image

# Token counts of a typical generation and QA answer (sets/cosy-mystery/cards/A01/try1.*), for cost arithmetic
IMAGE_USAGE = {"total_input_tokens": 20_000, "total_output_tokens": 0}
TEXT_USAGE = {"total_input_tokens": 4_000, "total_output_tokens": 300, "total_thought_tokens": 400}


class FakeGemini:
    """Replaces gemini_image.generate_image, generate_text and list_models with scripted answers.

    Queue an image (PNG bytes, or a (bytes, mime type) pair) on `images`, a text answer (str) on `texts`, a model
    list on `models`; queue an exception instance to make the call raise it (GeminiError(503), BillingError).
    Every call is recorded in `calls` as (kind, model, parts, kwargs). An empty queue raises, so a test that
    expects no API call just queues nothing.
    """

    def __init__(self) -> None:
        self.images: deque = deque()
        self.texts: deque = deque()
        self.models: deque = deque()
        self.calls: list[tuple] = []

    def install(self, monkeypatch) -> "FakeGemini":
        monkeypatch.setattr(gemini_image, "generate_image", self.generate_image)
        monkeypatch.setattr(gemini_image, "generate_text", self.generate_text)
        monkeypatch.setattr(gemini_image, "list_models", self.list_models)
        return self

    def generate_image(self, model: str, parts: list[dict], **kwargs) -> dict:
        self.calls.append(("image", model, parts, kwargs))
        item = self._take(self.images, "generate_image")
        data, mime = item if isinstance(item, tuple) else (item, "image/png")
        return {"image_bytes": data, "mime_type": mime, "elapsed_s": 0.1, "attempts": 1, "images_in_response": 1,
                "image_source": "fake", "response": {"usage": dict(IMAGE_USAGE)}}

    def generate_text(self, model: str, parts: list[dict], **kwargs) -> dict:
        self.calls.append(("text", model, parts, kwargs))
        return {"text": self._take(self.texts, "generate_text"), "elapsed_s": 0.1, "attempts": 1,
                "response": {"usage": dict(TEXT_USAGE)}}

    def list_models(self) -> list[dict]:
        self.calls.append(("models", None, None, {}))
        return self._take(self.models, "list_models")

    @staticmethod
    def _take(queue: deque, name: str):
        if not queue:
            raise AssertionError(f"FakeGemini: unexpected {name} call, nothing queued")
        item = queue.popleft()
        if isinstance(item, BaseException):
            raise item
        return item

    def calls_of(self, kind: str) -> list[tuple]:
        return [c for c in self.calls if c[0] == kind]

    @staticmethod
    def text_of(call: tuple) -> str:
        """All text parts of one recorded call, joined."""
        return "\n".join(p["text"] for p in call[2] if p.get("type") == "text")


# ---------------------------------------------------------------- synthetic cards

FAMILY_RGB = {"red": (230, 30, 30), "orange": (240, 140, 30), "yellow": (240, 220, 40), "green": (60, 200, 80),
              "teal": (30, 200, 190), "blue": (50, 110, 230), "purple": (150, 60, 220), "pink": (240, 100, 180)}
OBJECT_BOX = [300, 300, 700, 700]  # y0, x0, y1, x1 on the 0-1000 scale: a centred square, 40% of the picture


def make_card(backdrop="purple", obj="yellow", box=OBJECT_BOX, size=(1024, 1024)) -> Image.Image:
    """A solid backdrop of a known colour family with one rectangular "object" of another family at `box`."""
    bg = FAMILY_RGB.get(backdrop, backdrop)
    fg = FAMILY_RGB.get(obj, obj)
    image = Image.new("RGB", size, bg)
    w, h = size
    y0, x0, y1, x1 = box
    ImageDraw.Draw(image).rectangle((round(x0 / 1000 * w), round(y0 / 1000 * h), round(x1 / 1000 * w) - 1,
                                     round(y1 / 1000 * h) - 1), fill=fg)
    return image


def png_bytes(image: Image.Image, fmt: str = "PNG") -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, fmt)
    return buffer.getvalue()


def card_png(backdrop="purple", obj="yellow", box=OBJECT_BOX, size=(1024, 1024)) -> bytes:
    return png_bytes(make_card(backdrop, obj, box, size))


def qa_answer(passed: bool = True, fix: str = "", failing: tuple[str, ...] = ()) -> str:
    """A judge answer in the shape prompts/qa_v4.md asks for."""
    checks = {k: {"pass": k not in failing, "why": "test"}
              for k in ("subject", "category", "clean", "framing", "colour", "detail", "style")}
    return json.dumps({"checks": checks, "pass": passed, "fix": fix})


# ---------------------------------------------------------------- plan factory (schema 2, rulebook.md section 6)

# (category, role, stars, light, bg_color, main_colors) in card order: 3 x C1, 2 x C2, 2 x C3, 3 x C4; four roles,
# at most four cards per role; stars 1,1,2,2,3,3,4,4,5,5; one sunset; lead colour purple on three cards; one
# same-colour neighbour pair in the 5x2 window (cards 1 and 6); the object's first colour word never matches bg_color.
CARD_SPECS = [
    (1, "gear", 1, "day", "purple", "gold and cream"),
    (2, "carry", 1, "day", "green", "red and white"),
    (1, "carry", 2, "day", "blue", "orange and cream"),
    (3, "carry", 2, "day", "purple", "gold and cream"),
    (1, "gear", 3, "day", "pink", "green and gold"),
    (2, "gear", 3, "day", "purple", "gold and cream"),
    (3, "gear", 4, "day", "red", "blue and white"),
    (4, "vehicle", 4, "day", "green", "red and white"),
    (4, "place", 5, "day", "blue", "orange and cream"),
    (4, "place", 5, "sunset", "orange", "blue and cream"),
]
NAMES = {
    "A": ["Brass Lantern", "Tin Kettle", "Paper Map", "Oak Chest", "Copper Bell", "Clay Jug", "Velvet Chair",
          "Steam Cart", "Stone Mill", "Clock Tower"],
    "B": ["Glass Lens", "Wool Scarf", "Wax Letter", "Pine Desk", "Bronze Key", "Fruit Pie", "Leather Bag",
          "Red Tram", "Stone Bridge", "Old Lighthouse"],
    "C": ["Silk Ribbon", "Tea Tin", "Sealed Note", "Ink Pot", "Pocket Watch", "Honey Jar", "Wing Chair",
          "River Boat", "Market Hall", "Lamp Tower"],
}
WINDOW_OF = {"A": "violet", "B": "blue", "C": "pink"}


def background_text(category: int, bg: str, light: str) -> str:
    if category == 4:
        sky = "a glowing orange sunset sky" if light == "sunset" else f"a bright {bg} sky with a few soft clouds"
        return f"A wide band of ground across the bottom under {sky}."
    if category == 3:
        return f"A polished wooden tabletop in front of a smooth {bg} wall with a soft gradient; bright daylight."
    if category == 2:
        return f"A plain {bg} flat surface and a smooth {bg} wall gradient, the surface lighter than the wall."
    return f"A plain {bg} background with a smooth gradient and soft rays centred behind the object; bright daylight."


def make_card_spec(variant_id: str, index: int) -> dict:
    category, role, stars, light, bg, main = CARD_SPECS[index]
    name = NAMES[variant_id][index]
    return {
        "id": f"{variant_id}{index + 1:02d}", "name": name, "category": category, "role": role, "stars": stars,
        "light": light, "subject": f"A {name.lower()}, drawn big and chunky with a clear silhouette.",
        "unique_detail": "one painted star on its side", "main_colors": main,
        "background": background_text(category, bg, light), "bg_color": bg, "context_cue": "",
        "why": "an iconic prop of the theme",
    }


def make_plan(variants: tuple[str, ...] = ("A", "B", "C")) -> dict:
    """A plan that cardgen.validate accepts with no errors and no warnings."""
    return {
        "schema": 2, "collection": "Cinema", "set": "Test Set", "genre": "test genre", "wishes": "warm and cosy",
        "variants": [{
            "id": vid, "concept": f"Variant {vid}: the props of the theme",
            "moment": "A bright morning when the story begins.", "mood": "cheerful", "lead_color": "purple",
            "window_color": WINDOW_OF[vid], "motif": "stars",
            "cards": [make_card_spec(vid, i) for i in range(10)],
        } for vid in variants],
    }


def write_plan(folder: Path, plan: dict) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "plan.json"
    path.write_text(json.dumps(copy.deepcopy(plan), indent=1), encoding="utf-8")
    return path


def find_card(plan: dict, card_id: str) -> dict:
    return next(c for v in plan["variants"] for c in v["cards"] if c["id"] == card_id)
