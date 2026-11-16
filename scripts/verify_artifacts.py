#!/usr/bin/env python3
"""Check a build run's artifacts against the tag a Release publishes them under.

publish.yml runs this in a checkout of the tag, with the artifacts of the build.yml run it publishes
downloaded beside it. A Release attaches the archive the run built, so the tag must hold that build's
complete corresponding source: the run's artifacts must be whole (their SHA256SUMS), the tag's
`sources/` must be exactly the patched libvlcjni and VLC trees and the contribs' archives the run
built from, with checksums that match, and the tag must carry the Release's notes.
"""

import argparse
import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
NOTES = ".github/release-notes.md"


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_sums(path):
    """{relative path: SHA-256} from a sha256sum listing."""
    sums = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            digest, name = line.split(maxsplit=1)
            sums[name.lstrip("*")] = digest
    return sums


def files_under(directory):
    return {str(p.relative_to(directory)) for p in directory.rglob("*") if p.is_file()}


def check(root, artifacts, version):
    errors = []
    listing = artifacts / "SHA256SUMS"
    if not listing.is_file():
        return ["the artifacts have no SHA256SUMS"]
    listed = read_sums(listing)
    for name, digest in listed.items():
        path = artifacts / name
        if not path.is_file() or sha256(path) != digest:
            errors.append(f"artifact {name} does not match its SHA-256")
    unlisted = files_under(artifacts) - set(listed) - {"SHA256SUMS"}
    if unlisted:
        errors.append(f"artifacts not in SHA256SUMS: {sorted(unlisted)}")
    archive = f"libvlc-lgpl-{version}.tar.xz"
    if archive not in listed:
        errors.append(f"the artifacts hold no {archive}")

    # The corresponding source: the tag's sources/ is the run's, file for file.
    built = artifacts / "sources"
    published = root / "sources"
    built_files = files_under(built) if built.is_dir() else set()
    published_files = (files_under(published) if published.is_dir() else set()) - {"SHA256SUMS"}
    if not built_files:
        errors.append("the artifacts hold no sources")
    if built_files != published_files:
        errors.append(
            "sources/ differs from the run's: "
            f"missing={sorted(built_files - published_files)}, extra={sorted(published_files - built_files)}"
        )
    for name in sorted(built_files & published_files):
        if sha256(built / name) != sha256(published / name):
            errors.append(f"sources/{name} is not the run's")
    if (published / "SHA256SUMS").is_file():
        sums = read_sums(published / "SHA256SUMS")
        if set(sums) != published_files:
            errors.append("sources/SHA256SUMS does not list exactly the files in sources/")
        for name in sorted(set(sums) & published_files):
            if sha256(published / name) != sums[name]:
                errors.append(f"sources/SHA256SUMS records another SHA-256 for {name}")
    else:
        errors.append("sources/SHA256SUMS is missing")

    notes = root / NOTES
    if not notes.is_file() or not notes.read_text(encoding="utf-8").strip():
        errors.append(f"{NOTES} is missing or empty")
    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifacts", type=Path, help="the downloaded artifact of the build run")
    parser.add_argument("version", help="the version the tag publishes")
    args = parser.parse_args()
    problems = check(ROOT, args.artifacts, args.version)
    for problem in problems:
        print(problem, file=sys.stderr)
    sys.exit(bool(problems))
