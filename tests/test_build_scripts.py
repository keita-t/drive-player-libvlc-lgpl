import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
IMAGE = "registry.videolan.org/vlc-debian-android@sha256:" + "0" * 64


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


settings = load_script("build_settings")
artifacts = load_script("verify_artifacts")


class BuildSettings(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "gradle").mkdir()
        (self.root / ".github").mkdir()

    def write(self, version, variant, image=IMAGE):
        (self.root / "gradle/libs.versions.toml").write_text(f'[versions]\nlibvlcLgpl = "{version}"\n')
        (self.root / ".github/libvlc-build.json").write_text(json.dumps({"variant": variant, "image": image}))

    def test_each_branch_builds_its_variant(self):
        for version, variant, branch in (
            ("3.7.6-49", "", "main"),
            ("3.7.6-49-ogg-libvlc", "ogg-libvlc", "ogg-libvlc"),
            ("3.7.6-naked-1", "naked", "naked"),
        ):
            self.write(version, variant)
            read = settings.read(self.root)
            self.assertEqual((read["version"], read["branch"], read["tag"]), (version, branch, f"libvlc-lgpl-{version}"))

    def test_a_version_must_name_its_variant(self):
        for version, variant in (("3.7.6-49", "naked"), ("3.7.6-naked-1", ""), ("3.7.6-49-naked", "naked")):
            self.write(version, variant)
            with self.assertRaises(settings.SettingsError):
                settings.read(self.root)

    def test_the_image_is_pinned_by_digest(self):
        self.write("3.7.6-49", "", image="registry.videolan.org/vlc-debian-android:latest")
        with self.assertRaises(settings.SettingsError):
            settings.read(self.root)

    def test_unknown_variant_is_refused(self):
        self.write("3.7.6-49", "other")
        with self.assertRaises(settings.SettingsError):
            settings.read(self.root)


class ArtifactVerification(unittest.TestCase):
    VERSION = "3.7.6-naked-1"

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.root, self.artifacts = base / "tag", base / "artifacts"
        files = {
            f"libvlc-lgpl-{self.VERSION}.tar.xz": b"release",
            "build-info.txt": b"info",
            "sources/vlc-66455a98-drive-player.tar.xz": b"vlc",
            "sources/contrib/ffmpeg-8.1.2.tar.xz": b"ffmpeg",
        }
        for name, data in files.items():
            (self.artifacts / name).parent.mkdir(parents=True, exist_ok=True)
            (self.artifacts / name).write_bytes(data)
        self.write_sums(self.artifacts, [n for n in files])
        for name, data in files.items():
            if name.startswith("sources/"):
                (self.root / name).parent.mkdir(parents=True, exist_ok=True)
                (self.root / name).write_bytes(data)
        self.write_sums(self.root / "sources", ["vlc-66455a98-drive-player.tar.xz", "contrib/ffmpeg-8.1.2.tar.xz"])
        (self.root / ".github").mkdir()
        (self.root / ".github/release-notes.md").write_text("Notes\n")

    @staticmethod
    def write_sums(directory, names):
        lines = [f"{hashlib.sha256((directory / n).read_bytes()).hexdigest()}  {n}\n" for n in names]
        (directory / "SHA256SUMS").write_text("".join(lines))

    def check(self):
        return artifacts.check(self.root, self.artifacts, self.VERSION)

    def test_the_tag_holding_the_runs_sources_passes(self):
        self.assertEqual(self.check(), [])

    def test_a_damaged_artifact_is_refused(self):
        (self.artifacts / "build-info.txt").write_bytes(b"other")
        self.assertTrue(any("does not match" in e for e in self.check()))

    def test_sources_other_than_the_runs_are_refused(self):
        (self.root / "sources/vlc-66455a98-drive-player.tar.xz").write_bytes(b"older build")
        self.write_sums(self.root / "sources", ["vlc-66455a98-drive-player.tar.xz", "contrib/ffmpeg-8.1.2.tar.xz"])
        self.assertTrue(any("is not the run's" in e for e in self.check()))

    def test_a_missing_or_extra_source_is_refused(self):
        (self.root / "sources/contrib/libvorbis-1.3.7.tar.xz").write_bytes(b"vorbis")
        self.assertTrue(any("differs from the run's" in e for e in self.check()))

    def test_stale_source_checksums_are_refused(self):
        (self.root / "sources/SHA256SUMS").write_text(f"{'0' * 64}  vlc-66455a98-drive-player.tar.xz\n")
        self.assertTrue(any("SHA256SUMS" in e for e in self.check()))

    def test_another_versions_archive_is_refused(self):
        self.assertTrue(any("hold no" in e for e in artifacts.check(self.root, self.artifacts, "3.7.6-naked-2")))

    def test_release_notes_are_required(self):
        (self.root / ".github/release-notes.md").unlink()
        self.assertTrue(any("release-notes" in e for e in self.check()))


if __name__ == "__main__":
    unittest.main()
