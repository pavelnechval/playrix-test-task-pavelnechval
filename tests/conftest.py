"""Test configuration: every test runs offline.

- urllib.request.urlopen (the only network call, in gemini_image._call) raises, so no test can spend money by
  accident; the one test marked `paid` is skipped unless RUN_PAID_TESTS=1 and a Gemini key are set.
- Retry back-off sleeps are skipped, and cardgen's STOP flag is cleared around every test.
"""

from __future__ import annotations

import os
import sys
import urllib.request
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
for entry in (str(ROOT / "pipeline"), str(ROOT)):
    if entry not in sys.path:
        sys.path.insert(0, entry)

import cardgen  # noqa: E402
import gemini_image  # noqa: E402
import keys  # noqa: E402
from support import FakeGemini, make_plan, write_plan  # noqa: E402


class UnexpectedNetworkCall(AssertionError):
    """A test reached the network. Use FakeGemini, or mark the test `paid`."""


def _no_network(*args, **kwargs):
    raise UnexpectedNetworkCall("urllib.request.urlopen called from a test; the suite runs offline")


def pytest_collection_modifyitems(config, items):
    paid_on = os.environ.get("RUN_PAID_TESTS") == "1" and bool(keys.read_key(gemini_image.KEY_NAMES))
    skip = pytest.mark.skip(reason="paid test (about $0.10): set RUN_PAID_TESTS=1 and a Gemini key to run it")
    for item in items:
        if "paid" in item.keywords and not paid_on:
            item.add_marker(skip)


@pytest.fixture(autouse=True)
def offline(request, monkeypatch):
    cardgen.STOP.clear()
    if "paid" not in request.keywords:
        monkeypatch.setattr(urllib.request, "urlopen", _no_network)
        monkeypatch.setattr(gemini_image.time, "sleep", lambda seconds: None)
    yield
    cardgen.STOP.clear()


@pytest.fixture
def fake_gemini(monkeypatch) -> FakeGemini:
    return FakeGemini().install(monkeypatch)


@pytest.fixture
def plan() -> dict:
    return make_plan()


@pytest.fixture
def plan_path(tmp_path, plan) -> Path:
    """sets/test-set/plan.json inside the test's temporary folder (a sets/ level, so collection checks work)."""
    return write_plan(tmp_path / "sets" / "test-set", plan)


@pytest.fixture(scope="session")
def prompts() -> tuple[dict, dict]:
    return cardgen.load_sections(cardgen.PROMPT_FILE), cardgen.load_sections(cardgen.QA_FILE)


@pytest.fixture(scope="session")
def refs() -> cardgen.Refs:
    return cardgen.Refs()
