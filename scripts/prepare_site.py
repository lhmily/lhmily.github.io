"""Prepare the static portfolio for deployment and optional analytics."""

from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).parents[1]
DEFAULT_OUTPUT = ROOT / "_site"
PLACEHOLDER = "  <!-- CLOUDFLARE_WEB_ANALYTICS -->"
BEACON_URL = "https://static.cloudflareinsights.com/beacon.min.js"
EXCLUDED = {".git", ".github", ".gitignore", ".idea", "scripts", "_site", "pyproject.toml"}


def analytics_markup(token: str) -> str:
    settings = json.dumps({"token": token}, separators=(",", ":"))
    return f'  <script defer src="{BEACON_URL}" data-cf-beacon=\'{settings}\'></script>'


def prepare(output: Path, token: str = "") -> None:
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    for source in ROOT.iterdir():
        if source.name in EXCLUDED:
            continue
        destination = output / source.name
        if source.is_dir():
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)

    page = output / "index.html"
    text = page.read_text()
    if text.count(PLACEHOLDER) != 1:
        raise ValueError("index.html must contain one analytics placeholder")
    page.write_text(text.replace(PLACEHOLDER, analytics_markup(token) if token else ""))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    prepare(args.output.resolve(), os.getenv("CLOUDFLARE_WEB_ANALYTICS_TOKEN", "").strip())
    print(f"prepared portfolio in {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
