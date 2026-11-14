# Repository maintenance

- Keep `main`, `ogg-libvlc`, and `naked` as independent source histories. Start variant
  changes from that variant's branch. Keep historical tags and release assets unchanged.
- English (`README.md`, `PATCHES.md`) is the default documentation. Translate substantive
  changes into `README.ja.md` / `PATCHES.ja.md` in the same change, preserving patch links
  and commands. Only after translating, run `python3 scripts/check_docs.py --update`.
  This records the reviewed English revision; it does not translate or review meaning.
- When changing patches, update the corresponding English and Japanese table rows.
- Keep at least the latest stable binary release for every maintained branch public.
  Record the latest tags in `.github/release-branches.json` on all three branches.
  Only `main` should hold GitHub's repository-wide Latest designation.
- Run `python3 scripts/check_docs.py`, `python3 -m unittest discover -s tests`,
  and `bash -n third-party/libvlc/build-native.sh` before publishing changes.
