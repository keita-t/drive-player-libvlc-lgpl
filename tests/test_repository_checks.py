import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


docs = load_script("check_docs")
releases = load_script("check_releases")


class DocumentationChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        patch = "third-party/libvlc/patches/vlc/0001-example.patch"
        (self.root / patch).parent.mkdir(parents=True)
        (self.root / patch).write_text("patch")
        texts = {
            "README.md": "# Example\n\n```bash\nbuild\n```\n",
            "README.ja.md": "# 例\n\n```bash\nbuild\n```\n",
            "PATCHES.md": f"# Patches\n\n| [`vlc/0001`]({patch}) | Problem | Change |\n",
            "PATCHES.ja.md": f"# パッチ\n\n| [`vlc/0001`]({patch}) | 問題 | 変更 |\n",
        }
        for name, value in texts.items():
            (self.root / name).write_text(value, encoding="utf-8")
        self.assertEqual(docs.check(self.root, update=True), [])

    def test_translated_documents_pass(self):
        self.assertEqual(docs.check(self.root), [])

    def test_source_edit_requires_translation_acknowledgment(self):
        with (self.root / "README.md").open("a") as stream:
            stream.write("New information\n")
        self.assertTrue(any("translate the English changes" in e for e in docs.check(self.root)))

    def test_hash_refresh_does_not_hide_missing_patch_translation(self):
        (self.root / "PATCHES.ja.md").write_text("# パッチ\n", encoding="utf-8")
        self.assertTrue(any("patch entries differ" in e for e in docs.check(self.root, update=True)))

    def test_hash_refresh_does_not_hide_different_build_commands(self):
        path = self.root / "README.ja.md"
        path.write_text(path.read_text().replace("build", "wrong-command"))
        self.assertTrue(any("code blocks differ" in e for e in docs.check(self.root, update=True)))

    def test_undocumented_patch_is_detected(self):
        patch = self.root / "third-party/libvlc/patches/vlc/0002-new.patch"
        patch.write_text("patch")
        self.assertTrue(any("patch inventory differs" in e for e in docs.check(self.root)))

    def test_broken_translation_link_is_detected(self):
        with (self.root / "README.ja.md").open("a") as stream:
            stream.write("[link](missing.md)\n")
        self.assertTrue(any("missing link target" in e for e in docs.check(self.root)))

    def test_broken_section_link_is_detected(self):
        with (self.root / "README.ja.md").open("a") as stream:
            stream.write("[link](PATCHES.ja.md#missing-section)\n")
        self.assertTrue(any("missing link anchor" in e for e in docs.check(self.root)))


class ReleaseChecks(unittest.TestCase):
    def setUp(self):
        self.branches = {
            "main": "libvlc-lgpl-3.7.6-46",
            "ogg-libvlc": "libvlc-lgpl-3.7.6-37",
            "naked": "libvlc-lgpl-3.7.6-29-naked",
        }
        self.releases = [
            {
                "tag_name": tag,
                "target_commitish": branch,
                "draft": False,
                "prerelease": False,
                "assets": [{"name": f"{tag}.tar.xz", "state": "uploaded", "size": 1024}],
            }
            for branch, tag in self.branches.items()
        ]

    def test_independent_versions_with_legacy_ogg_tag_pass(self):
        self.assertEqual(releases.check(self.releases, self.branches), [])

    def test_every_branch_needs_a_release(self):
        errors = releases.check(self.releases[:2], self.branches)
        self.assertTrue(any("naked:" in e for e in errors))

    def test_draft_and_prerelease_do_not_count(self):
        for field in ("draft", "prerelease"):
            with self.subTest(field=field):
                data = copy.deepcopy(self.releases)
                data[1][field] = True
                self.assertTrue(releases.check(data, self.branches))

    def test_wrong_branch_is_detected(self):
        self.releases[2]["target_commitish"] = "variants"
        self.assertTrue(any("expected naked" in e for e in releases.check(self.releases, self.branches)))

    def test_missing_empty_and_unfinished_binary_do_not_count(self):
        for asset in ([], [{"name": "other.tar.xz", "state": "uploaded", "size": 1}],
                      [{"name": self.branches["main"] + ".tar.xz", "state": "uploaded", "size": 0}],
                      [{"name": self.branches["main"] + ".tar.xz", "state": "new", "size": 1}]):
            with self.subTest(asset=asset):
                data = copy.deepcopy(self.releases)
                data[0]["assets"] = asset
                self.assertTrue(releases.check(data, self.branches))


if __name__ == "__main__":
    unittest.main()
