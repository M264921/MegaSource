#!/usr/bin/env python3
"""Build the production MegaSource.json file from the curated source list."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

SOURCE_URLS = [
    "https://ipa.cypwn.xyz/cypwn.json",
    "https://bit.ly/Quantumsource",
    "https://bit.ly/Quantumsource-plus",
    "https://bit.ly/wuxuslibraryplus",
    "https://bit.ly/Altstore-complete",
    "https://altstore.oatmealdome.me/",
    "https://flyinghead.github.io/flycast-builds/altstore.json",
    "https://burritosoftware.github.io/altstore/channels/burritosource.json",
    "https://alts.lao.sb",
    "https://floridaman7588.me/altjb/altsource.json",
    "https://pokemmo.com/altstore/",
    "https://alt.getutm.app",
    "https://theodyssey.dev/altstore/odysseysource.json",
    "https://taurine.app/altstore/taurinestore.json",
    "https://altstore.9ani.app",
    "https://randomblock1.com/altstore/apps.json",
    "https://provenance-emu.com/apps.json",
    "https://bit.ly/40Isul6",
    "https://ish.app/altstore.json",
    "https://community-apps.sidestore.io/sidecommunity.json",
    "https://repo.starfiles.co/public?gbox",
    "https://repo.apptesters.org",
]


def build_payload() -> dict[str, object]:
    """Return the MegaSource payload expected by AltStore."""
    sources = []
    seen = set()
    for url in SOURCE_URLS:
        normalized = url.strip()
        if not normalized:
            continue
        if normalized in seen:
            raise ValueError(f"Duplicated source URL: {normalized}")
        seen.add(normalized)
        sources.append({"url": normalized})

    return {
        "name": "MegaSource",
        "identifier": "megasource.toninomontana",
        "apps": [],
        "sources": sources,
    }


def write_json(path: Path, data: dict[str, object]) -> None:
    payload = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    path.write_text(payload, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate MegaSource.json pointing to the curated AltStore sources."
    )
    parser.add_argument(
        "-o",
        "--output",
        default="MegaSource.json",
        help="Path to the output JSON file (defaults to MegaSource.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the generated JSON to stdout without writing to disk",
    )
    args = parser.parse_args()

    data = build_payload()
    if args.dry_run:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    output_path = Path(args.output)
    write_json(output_path, data)
    print(f"Wrote MegaSource payload to {output_path.resolve()}")


if __name__ == "__main__":
    main()
