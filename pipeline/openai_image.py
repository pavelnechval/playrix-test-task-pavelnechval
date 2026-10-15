"""Minimal OpenAI GPT Image client (Python standard library only).

Uses the Images API edit endpoint, which accepts up to 16 reference images
(multipart `image[]`). The key is read at runtime from OPENAI_API_KEY (see
keys.py) and is never printed, logged or written to disk.

Usage:
    python -I pipeline/openai_image.py check    # verify the key and list image models (free call)
"""

from __future__ import annotations

import base64
import json
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # sibling modules when run as a script with -I
from keys import read_key  # noqa: E402

API_ROOT = "https://api.openai.com/v1"
KEY_NAMES = ("OPENAI_API_KEY",)
RETRYABLE = (429, 500, 502, 503, 504)


class OpenAIError(RuntimeError):
    """Missing key, HTTP or network error, or a response without an image."""

    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.status = status


def api_key() -> str:
    key = read_key(KEY_NAMES)
    if key:
        return key
    raise OpenAIError(
        "No OpenAI API key found. Create the user environment variable OPENAI_API_KEY "
        "(Windows: Start > 'Edit environment variables for your account') and retry."
    )


def _send(request: urllib.request.Request, timeout: int) -> dict:
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", errors="replace")[:3000]
        raise OpenAIError(f"HTTP {err.code} for {request.full_url}: {detail}", err.code) from None
    except urllib.error.URLError as err:
        raise OpenAIError(f"Network error for {request.full_url}: {err.reason}") from None


def _multipart(fields: dict[str, str], images: list[Path]) -> tuple[bytes, str]:
    boundary = uuid.uuid4().hex
    chunks = []
    for name, value in fields.items():
        chunks.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode("utf-8"))
    for path in images:
        mime = "image/jpeg" if path.suffix.lower() in (".jpg", ".jpeg") else "image/png"
        header = (f'--{boundary}\r\nContent-Disposition: form-data; name="image[]"; filename="{path.name}"\r\n'
                  f"Content-Type: {mime}\r\n\r\n")
        chunks.append(header.encode("utf-8") + path.read_bytes() + b"\r\n")
    chunks.append(f"--{boundary}--\r\n".encode("utf-8"))
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


def edit_image(
    model: str,
    prompt: str,
    images: list[Path],
    *,
    size: str = "1024x1024",
    quality: str = "high",
    retries: int = 2,
) -> dict:
    """One Images API edit call with reference images; return the image and run metadata."""
    fields = {"model": model, "prompt": prompt, "size": size, "quality": quality, "n": "1", "output_format": "png"}
    body, content_type = _multipart(fields, images)
    for attempt in range(1, retries + 2):
        request = urllib.request.Request(
            f"{API_ROOT}/images/edits",
            data=body,
            method="POST",
            headers={"Authorization": f"Bearer {api_key()}", "Content-Type": content_type},
        )
        started = time.perf_counter()
        try:
            response = _send(request, timeout=600)
            break
        except OpenAIError as err:
            if err.status in RETRYABLE and attempt <= retries:
                time.sleep(5 * attempt)
                continue
            raise
    elapsed = time.perf_counter() - started
    items = response.get("data") or []
    if not items or not items[0].get("b64_json"):
        raise OpenAIError("No image in response: " + json.dumps({k: v for k, v in response.items() if k != "data"})[:3000])
    logged = {k: v for k, v in response.items() if k != "data"}
    logged["revised_prompt"] = items[0].get("revised_prompt")
    return {
        "image_bytes": base64.b64decode(items[0]["b64_json"]),
        "mime_type": "image/png",
        "elapsed_s": round(elapsed, 1),
        "attempts": attempt,
        "response": logged,
    }


def list_models() -> list[dict]:
    request = urllib.request.Request(f"{API_ROOT}/models", headers={"Authorization": f"Bearer {api_key()}"})
    return _send(request, timeout=60).get("data", [])


def main(argv: list[str]) -> int:
    if argv[:1] != ["check"]:
        print(__doc__)
        return 2
    try:
        models = list_models()
    except OpenAIError as err:
        print(f"FAILED: {err}")
        return 1
    print(f"Key OK. {len(models)} models visible. Image models:")
    for model in sorted(m.get("id", "") for m in models):
        if "image" in model:
            print(f"  {model}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
