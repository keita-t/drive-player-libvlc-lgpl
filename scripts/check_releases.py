#!/usr/bin/env python3
"""Verify that each maintained branch has its recorded public binary release."""

import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def check(releases, branches):
    errors = []
    for branch, tag in branches.items():
        release = next((r for r in releases if r["tag_name"] == tag), None)
        if release is None or release["draft"] or release["prerelease"]:
            errors.append(f"{branch}: {tag} must be a published stable release")
            continue
        if release["target_commitish"] != branch:
            errors.append(f"{branch}: {tag} targets {release['target_commitish']}, expected {branch}")
        if not any(a["name"] == f"{tag}.tar.xz" and a["state"] == "uploaded" and a["size"] > 0 for a in release["assets"]):
            errors.append(f"{branch}: {tag} has no uploaded binary archive")
    return errors


if __name__ == "__main__":
    repository = os.environ.get("GITHUB_REPOSITORY", "keita-t/drive-player-libvlc-lgpl")
    branches = json.loads((ROOT / ".github/release-branches.json").read_text())
    pages = json.loads(subprocess.check_output([
        "gh", "api", "--paginate", "--slurp", f"repos/{repository}/releases?per_page=100",
    ], text=True))
    releases = [release for page in pages for release in page]
    errors = check(releases, branches)
    latest = json.loads(subprocess.check_output(["gh", "api", f"repos/{repository}/releases/latest"], text=True))
    if latest["tag_name"] != branches["main"]:
        errors.append("The repository's Latest release must be main's recorded release")
    for branch, tag in branches.items():
        if subprocess.run(["git", "merge-base", "--is-ancestor", tag, f"origin/{branch}"], cwd=ROOT).returncode:
            errors.append(f"{branch}: {tag} is not in the branch history")
    for error in errors:
        print(error, file=sys.stderr)
    sys.exit(bool(errors))
