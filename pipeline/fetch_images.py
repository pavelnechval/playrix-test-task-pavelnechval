"""Download images listed in a JSON file into a folder and record their provenance.

Usage:
    python -I pipeline/fetch_images.py URLS_JSON OUT_DIR

URLS_JSON maps a local name to {"url": signed download URL, "widget": Miro item id}.
Existing files are skipped; only PNG/JPEG responses are kept. OUT_DIR/manifest.json
records the size, original file name and Miro item id of every image (never the
URLs, which are temporary signed links).
"""

from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

SIGNATURES = {b"\x89PNG\r\n\x1a\n": ".png", b"\xff\xd8\xff": ".jpg"}


def original_name(url: str) -> str:
    query = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    disposition = query.get("response-content-disposition", [""])[0]
    if 'filename="' in disposition:
        return disposition.split('filename="', 1)[1].split('"', 1)[0]
    return ""


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    entries = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    out = Path(argv[1])
    out.mkdir(parents=True, exist_ok=True)
    manifest_path = out / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    failures = 0
    for name, entry in entries.items():
        if any((out / f"{name}{ext}").exists() for ext in (".png", ".jpg")):
            print(f"skip {name}: exists")
            continue
        try:
            with urllib.request.urlopen(entry["url"], timeout=60) as response:
                data = response.read()
        except Exception as err:  # report network/HTTP errors and keep going
            print(f"FAILED {name}: {err}")
            failures += 1
            continue
        ext = next((e for signature, e in SIGNATURES.items() if data.startswith(signature)), None)
        if ext is None:
            print(f"FAILED {name}: not a PNG or JPEG ({len(data)} bytes)")
            failures += 1
            continue
        (out / f"{name}{ext}").write_bytes(data)
        manifest[name] = {
            "file": f"{name}{ext}",
            "bytes": len(data),
            "original_name": original_name(entry["url"]),
            "miro_widget": entry.get("widget", ""),
        }
        print(f"ok {name}: {len(data)} bytes ({manifest[name]['original_name']})")
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
