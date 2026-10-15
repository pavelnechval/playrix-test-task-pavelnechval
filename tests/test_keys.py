"""keys.read_key: environment first, then the .env file; nothing is ever printed."""

import sys

import pytest

import keys

NAMES = ("GEMINI_API_KEY", "GOOGLE_API_KEY")


class NoRegistry:
    """Stands in for winreg: the user environment holds no key during these tests."""

    HKEY_CURRENT_USER = None

    @staticmethod
    def OpenKey(*args):
        raise OSError("no registry in tests")


@pytest.fixture
def isolated(monkeypatch, tmp_path):
    for name in NAMES:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setitem(sys.modules, "winreg", NoRegistry)
    env_file = tmp_path / ".env"
    monkeypatch.setattr(keys, "ENV_FILE", env_file)
    return env_file


def test_no_key_anywhere(isolated):
    assert keys.read_key(NAMES) is None


def test_environment_wins_in_name_order(isolated, monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "google-key-test")
    assert keys.read_key(NAMES) == "google-key-test"
    monkeypatch.setenv("GEMINI_API_KEY", "  gemini-key-test \n")
    assert keys.read_key(NAMES) == "gemini-key-test"  # the first name wins, and it is stripped


def test_environment_before_the_env_file(isolated, monkeypatch):
    isolated.write_text("GEMINI_API_KEY=file-key-test\n", encoding="utf-8")
    assert keys.read_key(NAMES) == "file-key-test"
    monkeypatch.setenv("GEMINI_API_KEY", "env-key-test")
    assert keys.read_key(NAMES) == "env-key-test"
    monkeypatch.setenv("GEMINI_API_KEY", "   ")  # an empty variable does not hide the file
    assert keys.read_key(NAMES) == "file-key-test"


@pytest.mark.parametrize("content, expected", [
    ("GEMINI_API_KEY=plain-test\n", "plain-test"),
    ('export GEMINI_API_KEY="quoted-test"\n', "quoted-test"),
    ("GEMINI_API_KEY='single-test'\n", "single-test"),
    ("  GEMINI_API_KEY = spaced-test  \n", "spaced-test"),
    ("# GEMINI_API_KEY=commented\nOTHER=1\nGOOGLE_API_KEY=google-test\n", "google-test"),
    ("GEMINI_API_KEY=\nGOOGLE_API_KEY=second-test\n", "second-test"),  # an empty value is skipped
    ("GOOGLE_API_KEY=first-in-file\nGEMINI_API_KEY=second-in-file\n", "first-in-file"),  # file order, not name order
    ("GEMINI_API_KEY\n", None),  # no '=' at all
    ("", None),
])
def test_env_file_parsing(isolated, content, expected):
    isolated.write_text(content, encoding="utf-8")
    assert keys.read_key(NAMES) == expected


def test_only_the_named_variables_count(isolated):
    isolated.write_text("OPENAI_API_KEY=other-test\n", encoding="utf-8")
    assert keys.read_key(NAMES) is None
    assert keys.read_key(("OPENAI_API_KEY",)) == "other-test"
