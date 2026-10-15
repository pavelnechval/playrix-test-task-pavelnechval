"""prepare.py with every outside step faked: the exit codes, and the key never reaching stdout."""

import subprocess
import sys
from pathlib import Path

import pytest

import gemini_image
import keys
import prepare

KEY = "AIza-test-key-not-real-0123456789"


class Done:
    returncode = 0
    stdout = "12.3.0\n"


@pytest.fixture
def faked(monkeypatch, tmp_path):
    """No venv is created, pip is not run, no key is written to the repository and nothing prompts."""
    monkeypatch.setattr(prepare, "venv_python", lambda: Path(sys.executable))
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: Done())
    monkeypatch.setattr(prepare, "ENV_FILE", tmp_path / ".env")
    monkeypatch.setattr(prepare, "ROOT", tmp_path)
    monkeypatch.setattr(prepare.shutil, "which", lambda name: None)
    monkeypatch.setattr("builtins.input", lambda prompt="": pytest.fail("prepare.py asked a question"))
    monkeypatch.setattr(prepare.getpass, "getpass", lambda prompt="": pytest.fail("prepare.py asked for the key"))
    monkeypatch.setattr(keys, "read_key", lambda names: KEY)
    monkeypatch.setattr(gemini_image, "list_models", lambda: [{"name": f"models/{m}"} for m in prepare.MODELS])


def test_ready_when_everything_is_in_place(faked, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda prompt="": "n")
    assert prepare.main() == 0
    out = capsys.readouterr().out
    assert "[1/6] Python" in out and "Pillow 12.3.0 in .venv" in out and "found (not shown)" in out
    assert "key works; gemini-nano-banana-2.1, gemini-3.8-flash available" in out
    assert "skipped" in out and "Codex CLI not found" in out and "Ready." in out
    assert KEY not in out and "AIza" not in out


def test_missing_model_exits_1(faked, monkeypatch, capsys):
    monkeypatch.setattr(gemini_image, "list_models", lambda: [{"name": "models/gemini-3.8-flash"}, {"name": "models/other"}])
    with pytest.raises(SystemExit) as stop:
        prepare.main()
    assert stop.value.code == 1
    out = capsys.readouterr().out
    assert "NOT READY: the key works, but these models are not available to it: gemini-nano-banana-2.1." in out
    assert KEY not in out


def test_refused_key_exits_1(faked, monkeypatch, capsys):
    def fail():
        raise gemini_image.GeminiError("HTTP 400 for GET models?pageSize=200: API key not valid", 400)
    monkeypatch.setattr(gemini_image, "list_models", fail)
    with pytest.raises(SystemExit) as stop:
        prepare.main()
    assert stop.value.code == 1
    out = capsys.readouterr().out
    assert "NOT READY: the API refused the key: HTTP 400" in out
    assert KEY not in out


def test_empty_key_exits_1_without_writing_env(faked, monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(keys, "read_key", lambda names: None)
    monkeypatch.setattr(prepare.getpass, "getpass", lambda prompt="": "   ")
    with pytest.raises(SystemExit) as stop:
        prepare.main()
    assert stop.value.code == 1
    assert "NOT READY: no key." in capsys.readouterr().out
    assert not (tmp_path / ".env").exists()


def test_pasted_key_is_saved_to_env_and_never_printed(faked, monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(keys, "read_key", lambda names: None)
    monkeypatch.setattr(prepare.getpass, "getpass", lambda prompt="": f" {KEY} ")
    monkeypatch.setattr("builtins.input", lambda prompt="": "n")
    assert prepare.main() == 0
    assert (tmp_path / ".env").read_text(encoding="utf-8") == f"GEMINI_API_KEY={KEY}\n"
    out = capsys.readouterr().out
    assert "saved to .env in this folder" in out and KEY not in out


def test_pip_failure_exits_1(faked, monkeypatch, capsys):
    class Failed:
        returncode = 1
        stdout = ""
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: Failed())
    with pytest.raises(SystemExit) as stop:
        prepare.main()
    assert stop.value.code == 1
    assert "pip could not install the dependencies" in capsys.readouterr().out


def test_smoke_test_already_done_is_reported(faked, monkeypatch, capsys, tmp_path):
    done = tmp_path / "sets" / "smoke-test" / "final"
    done.mkdir(parents=True)
    (done / "A01.png").write_bytes(b"png")
    assert prepare.main() == 0
    assert "already done earlier" in capsys.readouterr().out
