#!/usr/bin/env python3
"""Delete *.memo files whose weighted length (ASCII counts as 0.5) falls outside 65-80."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


ASCII_THRESHOLD = 128
MIN_LENGTH = 60.0
MAX_LENGTH = 85.0


def weighted_length(text: str) -> float:
    """Return weighted length ignoring newlines; ASCII characters count as 0.5."""
    total = 0.0
    for ch in text:
        if ch in ("\n", "\r"):
            continue
        total += 0.5 if ord(ch) < ASCII_THRESHOLD else 1.0
    return total


def iter_memo_files(root: Path):
    for path in root.rglob("*.memo"):
        if path.is_file():
            yield path


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check *.memo files and delete those whose weighted length is not between 65 and 80."
        ),
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Directory to scan (default: current directory).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List files that would be removed without deleting them.",
    )

    args = parser.parse_args()
    root = Path(args.root).resolve()

    if not root.is_dir():
        parser.error(f"Directory does not exist: {root}")

    removal_candidates = []

    for memo_path in iter_memo_files(root):
        try:
            content = memo_path.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"Failed to read: {memo_path} ({exc})", file=sys.stderr)
            continue

        length = weighted_length(content)
        if MIN_LENGTH <= length <= MAX_LENGTH:
            continue

        removal_candidates.append((memo_path, length))

    if not removal_candidates:
        print("No files exceeded the allowed range.")
        return 0

    for memo_path, length in removal_candidates:
        action = "Would delete" if args.dry_run else "Deleting"
        print(f"{action}: {memo_path} (length: {length:.1f})")
        if not args.dry_run:
            try:
                memo_path.unlink()
            except OSError as exc:
                print(f"Failed to delete: {memo_path} ({exc})", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
