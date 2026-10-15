"""Prepare this folder for the card-set tool in one command, then open Claude Code or Codex here.

    python prepare.py            (macOS and Linux: python3 prepare.py)

Steps, each reported as OK or with what to fix:
1. Python 3.9 or newer.
2. A local environment, .venv, with the dependencies (Pillow). The skill runs the tool with its Python.
3. The Gemini API key: GEMINI_API_KEY from the environment, or from a .env file here. If there is none, it asks
   for the key (typing is hidden) and saves it to .env, which git ignores. The key is never printed.
4. A free check that the key works and that the two models the tool uses are available.
5. On request, a paid one-card test (about $0.10): one card generated, checked and framed in sets/smoke-test/.
6. Whether the Codex CLI is installed, for the optional ChatGPT route.

Uses only the Python standard library, so it runs before anything is installed. W028.
"""

from __future__ import annotations

import getpass
import os
import re
import shutil
import subprocess
import sys
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"
ENV_FILE = ROOT / ".env"
MODELS = ("gemini-nano-banana-2.1", "gemini-3.8-flash")  # generation; QA and measurements
EXAMPLE = "Make a card set for the Cinema collection: space adventure, bright and kind. 3 variants."


def venv_python() -> Path:
    return VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def step(n: int, text: str) -> None:
    print(f"\n[{n}/6] {text}")


def ok(text: str) -> None:
    print(f"      OK: {text}")


def stop(text: str) -> None:
    print(f"      NOT READY: {text}")
    sys.exit(1)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    print("Card-set tool: preparing this folder.")

    step(1, "Python")
    if sys.version_info < (3, 9):
        stop(f"Python {sys.version.split()[0]}; the tool needs 3.9 or newer (tested on 3.14).")
    ok(sys.version.split()[0])

    step(2, "Local environment with the dependencies (.venv)")
    py = venv_python()
    if not py.exists():
        print("      creating .venv ...")
        venv.EnvBuilder(with_pip=True).create(VENV)
    if subprocess.run([str(py), "-m", "pip", "install", "--disable-pip-version-check", "-q", "-r",
                       str(ROOT / "requirements.txt")]).returncode:
        stop("pip could not install the dependencies (see above). Check the internet connection and run again.")
    pil = subprocess.run([str(py), "-c", "import PIL; print(PIL.__version__)"], capture_output=True, text=True)
    if pil.returncode:
        stop("Pillow does not load in .venv.")
    ok(f"Pillow {pil.stdout.strip()} in .venv")

    step(3, "Gemini API key")
    sys.path.insert(0, str(ROOT / "pipeline"))
    from keys import read_key  # standard library only
    if read_key(("GEMINI_API_KEY", "GOOGLE_API_KEY")):
        ok("found (not shown)")
    else:
        print("      No GEMINI_API_KEY found. Create a key in Google AI Studio (https://aistudio.google.com/apikey)")
        print("      for a project with billing or prepaid credits; image generation has no free tier.")
        key = getpass.getpass("      Paste the key (hidden), or press Enter to stop: ").strip()
        if not key:
            stop("no key. Paste it here next time, or set the GEMINI_API_KEY environment variable.")
        ENV_FILE.write_text(f"GEMINI_API_KEY={key}\n", encoding="utf-8")
        try:
            os.chmod(ENV_FILE, 0o600)
        except OSError:
            pass
        ok("saved to .env in this folder; git ignores it, and deleting the file removes the key")

    step(4, "Free check of the key and the models")
    import gemini_image  # standard library only
    try:
        names = {m.get("name", "").removeprefix("models/") for m in gemini_image.list_models()}
    except gemini_image.GeminiError as err:
        stop(f"the API refused the key: {str(err)[:200]}")
    missing = [m for m in MODELS if m not in names]
    if missing:
        stop(f"the key works, but these models are not available to it: {', '.join(missing)}.")
    ok(f"key works; {', '.join(MODELS)} available")

    step(5, "Paid one-card test, about $0.10 (optional)")
    smoke = ROOT / "sets" / "smoke-test"
    if (smoke / "final" / "A01.png").exists():
        ok(f"already done earlier: {smoke / 'final' / 'A01.png'} (delete sets/smoke-test to run it again)")
    elif input("      Generate, check and frame one card now? [y/N] ").strip().lower() in ("y", "yes", "д", "да"):
        smoke.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / "sets" / "cosy-mystery" / "plan.json", smoke / "plan.json")
        plan = str(smoke / "plan.json")
        for args in (["cardgen.py", "run", plan, "--cards", "A01"], ["reframe.py", plan, "--route", "gemini", "--ids", "A01"]):
            if subprocess.run([str(py), "-I", str(ROOT / "pipeline" / args[0]), *args[1:]]).returncode:
                stop("the one-card test failed (see above).")
        line = next((l for l in (smoke / "summary.md").read_text(encoding="utf-8").splitlines() if l.startswith("Estimated cost")), "")
        amounts = re.findall(r"\$(\d+(?:\.\d+)?)", line)  # the total comes last when there is one
        ok(f"{smoke / 'final' / 'A01.png'}, about ${amounts[-1] if amounts else '?'}")
    else:
        print("      skipped")

    step(6, "ChatGPT route (optional)")
    if shutil.which("codex"):
        ok("Codex CLI found; the ChatGPT route also needs a ChatGPT subscription")
    else:
        print("      Codex CLI not found: fine, the main route is Gemini")

    print("\nReady. Open Claude Code or Codex in this folder and describe the set, for example (README.md has it in Russian):")
    print(f"  {EXAMPLE}")
    print("For a quicker look without planning, ask it to rerun an existing plan, for example Cosy Mystery, one variant.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
