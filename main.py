#!/usr/bin/env python3
"""One-Liner Marathon entry.

Writes one original funny line (<=280 chars) to /output/entry.txt,
deterministically: same bytes on every run.
"""
import hashlib
import os
import sys

LINE = "I told the GPS I knew a shortcut. It has been silent for forty minutes, out of respect."

OUTPUT_PATH = "/output/entry.txt"

MIN_LEN = 1
MAX_LEN = 280


def check_length(line):
    """Gate 1: the sealed scorer only accepts 1-280 characters."""
    if not MIN_LEN <= len(line) <= MAX_LEN:
        raise ValueError(
            f"line is {len(line)} chars, gate needs {MIN_LEN}-{MAX_LEN}"
        )


def check_single_line(line):
    """Gate 2: one line, no newline characters, not only whitespace."""
    if not line.strip():
        raise ValueError("line must not be only whitespace")
    if "\n" in line or "\r" in line:
        raise ValueError("entry must be a single line")


def validate(line):
    """Check the line against the sealed scorer's gate, without asserts.

    Asserts vanish under python -O, so the gate is enforced with explicit
    checks that always run, and failures name the broken rule.
    """
    check_length(line)
    check_single_line(line)


def ensure_output_dir(path):
    """Create the output directory when it does not exist yet."""
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)


def read_back(path):
    """Read the bytes that landed on disk, for byte-for-byte proof."""
    with open(path, "rb") as f:
        return f.read()


def verify(raw):
    """Prove the file on disk is exactly the line the judge will read."""
    if raw != LINE.encode("utf-8"):
        print("entry.txt on disk differs from LINE", file=sys.stderr)
        raise SystemExit(1)
    if raw.count(b"\n") != 0:
        print("entry.txt must hold exactly one line", file=sys.stderr)
        raise SystemExit(1)


def report(raw):
    """Fingerprint the bytes that landed, so a later run can prove the
    output is byte-identical: same sha256, same length, same line."""
    digest = hashlib.sha256(raw).hexdigest()
    print(f"entry.txt: {len(raw)} bytes, sha256 {digest}")


def main():
    try:
        validate(LINE)
    except ValueError as exc:
        print(f"invalid entry: {exc}", file=sys.stderr)
        raise SystemExit(1)
    # Deterministic by construction: fixed constant, no randomness, no
    # timestamps, explicit UTF-8 encoding, no trailing newline added.
    ensure_output_dir(OUTPUT_PATH)
    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="") as f:
        f.write(LINE)
    raw = read_back(OUTPUT_PATH)
    verify(raw)
    report(raw)


if __name__ == "__main__":
    main()
