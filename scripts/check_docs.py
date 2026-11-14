#!/usr/bin/env python3
"""Check Japanese translations against their English source and patch inventory."""

import argparse
import hashlib
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MARKER = re.compile(r"<!-- source-sha256: ([0-9a-f]{64}) -->")


def anchors(text):
    result = set(re.findall(r'<a id="([^"]+)"></a>', text))
    for heading in re.findall(r"^#+ (.+)$", text, re.M):
        result.add(re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-"))
    return result


def check(root=ROOT, update=False):
    errors = []
    for name in ("README", "PATCHES"):
        source_path = root / f"{name}.md"
        translation_path = root / f"{name}.ja.md"
        source = source_path.read_text(encoding="utf-8")
        translation = translation_path.read_text(encoding="utf-8")
        digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
        marker = f"<!-- source-sha256: {digest} -->"
        if update:
            translation = MARKER.sub("", translation).lstrip("\n")
            translation = marker + "\n\n" + translation
            translation_path.write_text(translation, encoding="utf-8")
        if MARKER.findall(translation) != [digest]:
            errors.append(f"{translation_path.name}: translate the English changes, then run --update")
        # Every patch entry must have a translation, in the same order.
        rows = r"^\| (\[`[^`]+`\]\([^)]+\)) \|"
        if re.findall(rows, source, re.M) != re.findall(rows, translation, re.M):
            errors.append(f"{translation_path.name}: patch entries differ from English")
        # Build commands must work identically in either language.
        blocks = r"^```[^\n]*\n(.*?)^```"
        if re.findall(blocks, source, re.M | re.S) != re.findall(blocks, translation, re.M | re.S):
            errors.append(f"{translation_path.name}: code blocks differ from English")
        for path, contents in ((source_path, source), (translation_path, translation)):
            for target in re.findall(r"\]\(([^)]+)\)", contents):
                if "://" in target:
                    continue
                filename, separator, anchor = target.partition("#")
                destination = root / filename if filename else path
                if not destination.exists():
                    errors.append(f"{path.name}: missing link target {target}")
                elif separator and anchor not in anchors(destination.read_text(encoding="utf-8")):
                    errors.append(f"{path.name}: missing link anchor {target}")
    # Descriptions must cover exactly the patches shipped on this branch.
    patch_source = (root / "PATCHES.md").read_text(encoding="utf-8")
    documented = set(re.findall(r"\]\((third-party/libvlc/patches/[^)]+)\)", patch_source))
    shipped = {str(p.relative_to(root)) for p in (root / "third-party/libvlc/patches").glob("*/*.patch")}
    if documented != shipped:
        errors.append(f"PATCHES.md: patch inventory differs (missing={sorted(shipped - documented)}, extra={sorted(documented - shipped)})")
    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--update", action="store_true", help="record source hashes AFTER translating both documents")
    args = parser.parse_args()
    problems = check(update=args.update)
    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        sys.exit(1)
    print("English/Japanese documentation is in sync.")
