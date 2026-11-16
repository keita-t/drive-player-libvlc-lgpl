#!/usr/bin/env python3
"""Print what this branch's recipe builds, for the build and publish workflows.

The version is the catalog's `libvlcLgpl` (gradle/libs.versions.toml): the AAR is published under it,
and its Release is tagged `libvlc-lgpl-<version>`. The variant (build-native.sh's LIBVLC_VARIANT)
and VideoLAN's Android build image, pinned by digest, are in .github/libvlc-build.json. Each
maintained branch builds one variant: `main` the recipe's own build, `ogg-libvlc` and `naked` their
namesakes, and a version names its variant the way DrivePlayer's libvlc_build.sh does.
"""

import json
from pathlib import Path
import re
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
# The branch each variant is maintained on.
BRANCHES = {"": "main", "ogg-libvlc": "ogg-libvlc", "naked": "naked"}
# The versions each variant is published under: the recipe's revision, the same suffixed with
# ogg-libvlc, and the naked variant's revisions of its own.
VERSIONS = {
    "": re.compile(r"[0-9]+\.[0-9]+\.[0-9]+-[0-9]+"),
    "ogg-libvlc": re.compile(r"[0-9]+\.[0-9]+\.[0-9]+-[0-9]+-ogg-libvlc"),
    "naked": re.compile(r"[0-9]+\.[0-9]+\.[0-9]+-naked-[0-9]+"),
}
IMAGE = re.compile(r"[a-z0-9.\-]+(/[a-z0-9.\-_]+)+@sha256:[0-9a-f]{64}")


class SettingsError(Exception):
    pass


def read(root=ROOT):
    """The build this checkout's recipe makes: version, variant, image, branch and tag."""
    try:
        catalog = tomllib.loads((root / "gradle/libs.versions.toml").read_text(encoding="utf-8"))
        version = catalog["versions"]["libvlcLgpl"]
        build = json.loads((root / ".github/libvlc-build.json").read_text(encoding="utf-8"))
        variant, image = build["variant"], build["image"]
    except (OSError, KeyError, ValueError) as error:
        raise SettingsError(f"cannot read the build settings: {error}") from error
    if variant not in BRANCHES:
        raise SettingsError(f"unknown variant {variant!r}; expected one of {sorted(BRANCHES)}")
    if not VERSIONS[variant].fullmatch(version):
        raise SettingsError(f"version {version!r} is not one the {variant or 'default'} build is published under")
    if not IMAGE.fullmatch(image):
        raise SettingsError(f"image {image!r} is not pinned by digest")
    return {
        "version": version,
        "variant": variant,
        "image": image,
        "branch": BRANCHES[variant],
        "tag": f"libvlc-lgpl-{version}",
    }


if __name__ == "__main__":
    try:
        settings = read()
    except SettingsError as error:
        print(error, file=sys.stderr)
        sys.exit(1)
    for key, value in settings.items():
        print(f"{key}={value}")
