"""Command line: ``yt-transcript-apify <video> [--format text|srt|vtt|json] [--lang en]``."""

from __future__ import annotations

import argparse
import json
import sys

from .client import ApifyTranscriptClient, TranscriptError


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="yt-transcript-apify",
        description="Print the transcript of YouTube videos (works from cloud servers). Needs APIFY_TOKEN.",
    )
    p.add_argument("videos", nargs="+", help="YouTube links or 11-character video IDs")
    p.add_argument("--format", choices=["text", "srt", "vtt", "json"], default="text")
    p.add_argument("--lang", action="append", help="preferred language code, repeatable (default: original)")
    p.add_argument("--translate", help="translate to this language code")
    p.add_argument("--token", help="Apify API token (default: $APIFY_TOKEN)")
    a = p.parse_args(argv)

    fmt = {"text": ["text"], "srt": ["srt"], "vtt": ["vtt"], "json": ["segments", "text"]}[a.format]
    client = ApifyTranscriptClient(token=a.token)
    try:
        rows = client.fetch_many(a.videos, languages=a.lang, formats=fmt, translate_to=a.translate)
    except TranscriptError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    code = 0
    for row in rows:
        if row.get("status") != "success":
            print(f"# {row.get('input')}: {row.get('message') or row.get('status')}", file=sys.stderr)
            code = 1
            continue
        if a.format == "json":
            print(json.dumps(row, ensure_ascii=False))
        else:
            print(row.get(a.format) or "")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
