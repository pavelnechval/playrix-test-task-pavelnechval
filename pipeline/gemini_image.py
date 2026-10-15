"""Minimal Gemini image-generation client (Python standard library only).

The API key is read at runtime from GEMINI_API_KEY (or GOOGLE_API_KEY): first
from the process environment, then, on Windows, from the user environment in
the registry, so a variable created after the terminal or app started still
works. The key is never printed, logged or written to disk.

Usage:
    python -I pipeline/gemini_image.py check    # verify the key and list image models (free call)
"""

from __future__ import annotations

import base64
import http.client
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # sibling modules when run as a script with -I
from keys import read_key  # noqa: E402

API_ROOT = "https://generativelanguage.googleapis.com/v1beta"
KEY_NAMES = ("GEMINI_API_KEY", "GOOGLE_API_KEY")
NETWORK = -1  # pseudo status for dropped connections and timeouts
RETRYABLE = (NETWORK, 429, 500, 502, 503, 504)
LONG_STRING = 2000  # longer strings (base64 images, signatures) are replaced in logged responses


class GeminiError(RuntimeError):
    """Missing key, HTTP or network error, or a response without an image."""

    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.status = status


BILLING_HELP = ("The Gemini API balance is empty (HTTP 402: the prepaid credits are used up). Top it up in AI Studio "
                "(https://ai.studio/projects, Billing), then run the same command again; finished work is kept and skipped.")


class BillingError(GeminiError):
    """HTTP 402: the account can't pay for more calls. Retrying won't help, so every script stops on it (W023)."""


def api_key() -> str:
    key = read_key(KEY_NAMES)
    if key:
        return key
    raise GeminiError(
        "No Gemini API key found. Create the user environment variable GEMINI_API_KEY "
        "(Windows: Start > 'Edit environment variables for your account') and retry."
    )


def _call(method: str, path: str, body: dict | None = None, timeout: int = 300) -> dict:
    request = urllib.request.Request(
        f"{API_ROOT}/{path}",
        data=None if body is None else json.dumps(body).encode("utf-8"),
        method=method,
        headers={"x-goog-api-key": api_key(), "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", errors="replace")[:3000]
        if err.code == 402:
            raise BillingError(BILLING_HELP, 402) from None
        raise GeminiError(f"HTTP {err.code} for {method} {path}: {detail}", err.code) from None
    except urllib.error.URLError as err:
        raise GeminiError(f"Network error for {method} {path}: {err.reason}", NETWORK) from None
    except (http.client.HTTPException, ConnectionError, TimeoutError) as err:  # dropped or stalled connections
        raise GeminiError(f"Network error for {method} {path}: {err!r}", NETWORK) from None


def text_part(text: str) -> dict:
    return {"type": "text", "text": text}


def image_part(data: bytes, mime_type: str = "image/png") -> dict:
    return {"type": "image", "mime_type": mime_type, "data": base64.b64encode(data).decode("ascii")}


def generate_image(
    model: str,
    parts: list[dict],
    *,
    aspect_ratio: str = "1:1",
    image_size: str = "1K",
    thinking_level: str | None = None,
    retries: int = 2,
) -> dict:
    """Send one Interactions API request; return the final image and run metadata."""
    body = {
        "model": model,
        "input": parts,
        "response_format": {"type": "image", "aspect_ratio": aspect_ratio, "image_size": image_size},
    }
    if thinking_level:
        body["generation_config"] = {"thinking_level": thinking_level}
    for attempt in range(1, retries + 2):
        started = time.perf_counter()
        try:
            response = _call("POST", "interactions", body)
            break
        except GeminiError as err:
            if err.status in RETRYABLE and attempt <= retries:
                time.sleep(5 * attempt)
                continue
            raise
    elapsed = time.perf_counter() - started
    images, source = _final_images(response)
    if not images:
        raise GeminiError("No image in response: " + json.dumps(redact(response))[:3000])
    final = images[-1]
    return {
        "image_bytes": base64.b64decode(final["data"]),
        "mime_type": final.get("mime_type") or final.get("mimeType") or "image/png",
        "elapsed_s": round(elapsed, 1),
        "attempts": attempt,
        "images_in_response": len(images),
        "image_source": source,
        "response": redact(response),
    }


def generate_text(model: str, parts: list[dict], *, retries: int = 2) -> dict:
    """Send one Interactions API request expecting a text answer (e.g. a vision review)."""
    body = {"model": model, "input": parts}
    for attempt in range(1, retries + 2):
        started = time.perf_counter()
        try:
            response = _call("POST", "interactions", body, timeout=180)
            break
        except GeminiError as err:
            if err.status in RETRYABLE and attempt <= retries:
                time.sleep(5 * attempt)
                continue
            raise
    steps = [s for s in response.get("steps", []) if isinstance(s, dict) and s.get("type") == "model_output"]
    texts = [block.get("text", "") for step in steps for block in step.get("content", [])
             if isinstance(block, dict) and block.get("type") == "text"]
    if not texts:
        raise GeminiError("No text in response: " + json.dumps(redact(response))[:3000])
    return {
        "text": "\n".join(texts),
        "elapsed_s": round(time.perf_counter() - started, 1),
        "attempts": attempt,
        "response": redact(response),
    }


def _final_images(response: dict) -> tuple[list[dict], str]:
    """Images of the final answer, preferring documented fields over a blind search."""
    output = response.get("output_image")
    if isinstance(output, dict) and output.get("data"):
        return [output], "output_image"
    steps = [s for s in response.get("steps", []) if isinstance(s, dict) and s.get("type") == "model_output"]
    if steps and (found := _collect_images(steps)):
        return found, "steps.model_output"
    if "candidates" in response and (found := _collect_images(response["candidates"])):
        return found, "candidates"
    return _collect_images(response), "anywhere"


def _collect_images(node, found: list[dict] | None = None) -> list[dict]:
    if found is None:
        found = []
    if isinstance(node, dict):
        inline = node.get("inlineData") or node.get("inline_data")
        if isinstance(inline, dict) and inline.get("data"):
            found.append(inline)
        elif node.get("type") == "image" and isinstance(node.get("data"), str):
            found.append(node)
        for value in node.values():
            if isinstance(value, (dict, list)) and value is not inline:
                _collect_images(value, found)
    elif isinstance(node, list):
        for item in node:
            _collect_images(item, found)
    return found


def redact(node):
    """Copy of an API response that is safe and small enough to keep in the run log."""
    if isinstance(node, dict):
        return {key: redact(value) for key, value in node.items()}
    if isinstance(node, list):
        return [redact(value) for value in node]
    if isinstance(node, str) and len(node) > LONG_STRING:
        return f"<{len(node)} chars omitted>"
    return node


def list_models() -> list[dict]:
    models, token = [], None
    while True:
        page = _call("GET", "models?pageSize=200" + (f"&pageToken={token}" if token else ""), timeout=60)
        models.extend(page.get("models", []))
        token = page.get("nextPageToken")
        if not token:
            return models


def main(argv: list[str]) -> int:
    if argv[:1] != ["check"]:
        print(__doc__)
        return 2
    try:
        models = list_models()
    except GeminiError as err:
        print(f"FAILED: {err}")
        return 1
    print(f"Key OK. {len(models)} models visible. The balance is not checked here: the first paid call reports an "
          "empty one. Image-related models:")
    for model in models:
        name = model.get("name", "")
        if "image" in name or "banana" in name:
            print(f"  {name}  ({model.get('displayName', '')})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
