#!/usr/bin/env python3
"""The World in One Image — Thursday, 19 November 2026.

Entry for make.fun competition news-image-20261119, "Sum up 19
November's world news in one image" ($250 shared by the top 50; entries
close Saturday 21 November 2026, 00:00 UTC = 07:00 WIB; bounty page
https://make.fun/bounty/news-image-20261119).

Running this file writes the newspaper poster that ships in this repo
(world_news_19_nov_2026.png) to /output/entry.png. The poster itself
was drawn at build time by render_poster.py with Pillow; this file does
nothing but copy its bytes, using the standard library alone. That
matters because the grader runs `python3 -P -s`, where no third-party
package exists, and because the program runs twice and must write the
same bytes both times — fixed bytes in, fixed bytes out.

The gate, checked here on every run with a small stdlib PNG reader: a
whole PNG of at most 1 MiB and 1024x1024 px. This poster is 1024x1024
and well under the byte cap.

    python3 main.py                  -> /output/entry.png
    python3 main.py out.png          -> the given path
    MAKEFUN_OUTPUT_DIR=/tmp/out python3 main.py

When /output cannot be created or written, ./output/entry.png is used.

Author: Januar (@januar). Payout wallet (reference only, unused here):
FM6M2TMzjhzj7QztEV91bAwV4N2bApYd2AZpZLcHyeKm
"""

import hashlib
import os
import struct
import sys
from pathlib import Path

POSTER_FILE = "world_news_19_nov_2026.png"
OUTPUT_FILE = "entry.png"
BYTE_CAP = 1024 * 1024
SIDE_CAP = 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class PosterError(Exception):
    """The poster file is missing, broken, or over the gate."""


def load_poster():
    """Read the poster PNG that ships next to this file."""
    path = Path(__file__).resolve().parent / POSTER_FILE
    try:
        return path.read_bytes()
    except OSError as exc:
        raise PosterError(f"cannot read {POSTER_FILE}: {exc}") from exc


def inspect_png(blob):
    """Return (width, height) from the IHDR chunk, or raise PosterError."""
    if blob[:8] != PNG_SIGNATURE or len(blob) < 33:
        raise PosterError("not a valid PNG file")
    size, kind = struct.unpack(">I4s", blob[8:16])
    if kind != b"IHDR" or size != 13:
        raise PosterError("PNG has no IHDR chunk first")
    return struct.unpack(">II", blob[16:24])


def enforce_gate(blob):
    """Return (width, height) or raise PosterError when over the gate."""
    width, height = inspect_png(blob)
    if len(blob) > BYTE_CAP:
        raise PosterError(f"poster is {len(blob)} bytes, over the 1 MiB cap")
    if width > SIDE_CAP or height > SIDE_CAP:
        raise PosterError(
            f"poster is {width}x{height}, over the 1024x1024 cap")
    return width, height


def choose_destination(argv):
    """Pick the output path: argv, then MAKEFUN_OUTPUT_DIR, then /output."""
    if len(argv) > 1:
        return Path(argv[1])
    directory = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    try:
        os.makedirs(directory, exist_ok=True)
        probe = Path(directory) / ".makefun_write_test"
        probe.touch()
        probe.unlink()
    except OSError:
        directory = Path.cwd() / "output"
        os.makedirs(directory, exist_ok=True)
    return Path(directory) / OUTPUT_FILE


def emit(argv):
    """Copy the poster to the output path and report what was written."""
    blob = load_poster()
    width, height = enforce_gate(blob)
    target = choose_destination(argv)
    target.write_bytes(blob)
    short_hash = hashlib.sha256(blob).hexdigest()[:16]
    print(f"wrote {target} — PNG {width}x{height}, {len(blob):,} bytes, "
          f"sha256={short_hash}...")
    return 0


def main(argv):
    try:
        return emit(argv)
    except PosterError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
