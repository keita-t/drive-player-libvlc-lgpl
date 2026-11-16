# libVLC for DrivePlayer — corresponding source

English | [日本語](README.ja.md)

This branch (`naked`) holds the complete corresponding source of the comparison build
`com.example.driveplayer.thirdparty:libvlc-lgpl` 3.7.6-29-naked, for arm64-v8a under the GNU LGPL 2.1
or more permissive licenses. The app does not ship this build: it applies only the two VLC patches the
app cannot run without, plus all four Java binding patches. The app's build is tracked on `main`.

Each published build of the library has a tag named after its version (`libvlc-lgpl-<version>`), holding exactly the
sources, patches and build scripts that produced that build. Each maintained branch keeps its latest
published build available as a GitHub Release. Releases are kept as they are published from 3.7.6-49 on; the
releases of earlier builds, other than the ones listed here, were withdrawn, and their tags remain:

| Library version | Tag | Branch | What it is |
|---|---|---|---|
| 3.7.6-49 | [`libvlc-lgpl-3.7.6-49`](https://github.com/keita-t/drive-player-libvlc-lgpl/releases/tag/libvlc-lgpl-3.7.6-49) | [`main`](https://github.com/keita-t/drive-player-libvlc-lgpl/tree/main) | The build the app ships, with the patches listed in [main/PATCHES.md](https://github.com/keita-t/drive-player-libvlc-lgpl/blob/main/PATCHES.md). The built library is attached to the GitHub release of its tag |
| 3.7.6-37 | [`libvlc-lgpl-3.7.6-37`](https://github.com/keita-t/drive-player-libvlc-lgpl/releases/tag/libvlc-lgpl-3.7.6-37) | [`ogg-libvlc`](https://github.com/keita-t/drive-player-libvlc-lgpl/tree/ogg-libvlc) | The latest published build using libVLC's own Ogg demuxer and libvorbis; originally published as a regular app build |
| 3.7.6-29-naked | [`libvlc-lgpl-3.7.6-29-naked`](https://github.com/keita-t/drive-player-libvlc-lgpl/releases/tag/libvlc-lgpl-3.7.6-29-naked) | [`naked`](https://github.com/keita-t/drive-player-libvlc-lgpl/tree/naked) | A comparison build with only the VLC patches the app cannot run without, plus the Java binding patches |

The branches track different recipes and versions independently; their latest releases do not have to share a
version number. `ogg-libvlc` starts from the existing 3.7.6-37 tag and `naked` from 3.7.6-29-naked. The old
`variants` branch is retained as historical source; new comparison builds belong on their named branch.
Existing tags and binary assets retain their original names and contents.

## Contents

| Path | What it is |
|---|---|
| `sources/libvlcjni-ddde54ff-drive-player.tar.xz` | libvlcjni at commit `ddde54fff93ab40c529a46eae80fe357ae0af97e`, with DrivePlayer's patches applied |
| `sources/vlc-66455a98-drive-player-naked.tar.xz` | VLC media player 3.0 at commit `66455a98c8c515796b4a192acaa125c5d68c76c8`, with libvlcjni's patches and only DrivePlayer's VLC patches 0001 and 0002 applied. It includes VLC's contrib build system (`contrib/src`), with the patches it applies to the third-party components |
| `sources/contrib/` | The source archives of the 27 third-party components linked into `libvlc.so`, as published by each project |
| `sources/SHA256SUMS` | Checksums of the archives above |
| `third-party/libvlc/build-native.sh` | The script that builds `libvlc.so`, `libvlcjni.so` and `libc++_shared.so` |
| `third-party/libvlc/patches/` | DrivePlayer's modifications to libvlcjni and VLC, as `git am` patches |
| `PATCHES.md` | What each patch solved and what it changes |
| `third-party/libvlc/aar/` | The Gradle build that packages the libraries and the Java bindings as an Android library (AAR) |
| `gradle/`, `gradlew` | The Gradle wrapper (Gradle 8.7) and the version entries the AAR build reads |

The layout of `third-party/libvlc/` and `gradle/` matches the DrivePlayer source tree, where the same
files are used unchanged.

## What was changed, and why

This build differs from the libVLC VideoLAN publishes on Maven Central (`org.videolan.android:libvlc-all`) in three
ways: it contains no component under the GNU General Public License, it leaves out what the app does not use, and
it carries source patches for behaviour the app relies on.

### Left out

| What | How the build ensures it |
|---|---|
| Third-party components under the GPL | Components are chosen from an explicit list (`contrib_packages` in `build-native.sh`), and VLC's contrib system runs with its GPL and GPLv3 guards on. FFmpeg's configuration is checked to have its GPL, version 3 and non-free parts disabled. |
| VLC modules under the GPL | They are not linked (`module_blacklist`), and the build stops if any linked module declares the GPL. |
| GPL sources inside LGPL code | The renderer discoverer of the Java bindings and the yadif deinterlacing algorithm are removed (the [License patches](PATCHES.md#license)). |
| Features the app does not use | Stream output (transcoding, recording, casting), network access and streaming protocols, disc playback, Lua scripts, tag reading, service discovery, fontconfig, and the modules listed in `module_blacklist`. |

### Patches

`patches/libvlcjni/` (4 patches) is applied to libvlcjni, and `patches/vlc/` (2 patches) to VLC after the patches
libvlcjni itself carries, all with `git am`. [PATCHES.md](PATCHES.md) lists each with the problem it solved and the
change it makes:

| What they concern | Patches |
|---|---|
| [License](PATCHES.md#license) | 2 |
| [Reading media through the app](PATCHES.md#reading-media-through-the-app) | 2 |
| [Bindings](PATCHES.md#bindings) | 2 |

## Build

The native libraries are built inside VideoLAN's Android build image, which provides NDK r29 and the
tools VLC's build expects. The image is pinned by digest:

```
registry.videolan.org/vlc-debian-android@sha256:5f041ff50465aea803b93855d463f4b98f1d9f3be6628e304af2bf3fded6f98e
```

```bash
mkdir -p work
docker run --rm --init \
    --user "$(id -u):$(id -g)" \
    --volume "$PWD/work:/work" \
    --volume "$PWD/third-party/libvlc:/recipe:ro" \
    --env LIBVLC_VARIANT=naked \
    registry.videolan.org/vlc-debian-android@sha256:5f041ff50465aea803b93855d463f4b98f1d9f3be6628e304af2bf3fded6f98e \
    bash /recipe/build-native.sh
```

The libraries, the Java bindings and a record of the build (`build-info.txt`: revisions, component
versions, linked modules) are left in `work/out/`. The AAR is then packaged with JDK 21 and an Android SDK
with platform 36 (`ANDROID_HOME` set):

```bash
./gradlew -p third-party/libvlc/aar publish \
    -Plibvlc.nativeOutput="$PWD/work/out" \
    -Plibvlc.repository="$PWD/repository" \
    -Plibvlc.variant=naked
```

Use `LIBVLC_VARIANT=naked` for this branch's native build and `-Plibvlc.variant=naked` when packaging
the AAR, as in the commands above. This retains the 3.7.6-29-naked recipe: only VLC patches 0001 and 0002
and all four Java binding patches apply. Unlike current main's naked option, this historical build opens
Ogg with libVLC's own demuxer and includes libvorbis. The VLC archive already contains just these patches.

`build-native.sh` fetches the pinned libvlcjni and VLC commits and the component archives from their
upstream locations. To build from this repository's copies instead:

- Extract `sources/libvlcjni-*.tar.xz` to `work/src/libvlcjni` and `sources/vlc-*.tar.xz` to
  `work/src/libvlcjni/vlc`. These are the trees `build-native.sh` produces in its `fetch_sources` step,
  patches applied; run the remaining steps of `main` against them.
- Copy `sources/contrib/*` to `work/tarballs/`. VLC's contrib build uses the archives it finds there and
  verifies each against the SHA-512 it records in `contrib/src/<component>/SHA512SUMS`.

## Maintaining the branches, documentation and releases

Make recipe and patch changes on the branch for that build. This branch (`naked`) retains its historical recipe;
the `ogg-libvlc` and `naked` READMEs describe their own versions and build options. Changes shared by all
branches, such as documentation checks, should be applied to all three without merging their source archives.

English is the default. Update `README.md` together with `README.ja.md`, and `PATCHES.md` together with
`PATCHES.ja.md`, in the same change. After reviewing the translations, run:

```bash
python3 scripts/check_docs.py --update
python3 scripts/check_docs.py
python3 -m unittest discover -s tests
```

The check records the English source's SHA-256 in each Japanese document, detects untranslated source
updates, and checks patch coverage, links and build commands. It does not assess translation quality;
review both languages before refreshing the hashes. GitHub Actions runs the checks for all three branches.

Builds run on GitHub Actions. `build.yml` builds a branch's recipe in VideoLAN's image whenever a
`build/<version>` branch is pushed, or when it is run by hand. `scripts/build_settings.py` reads what it builds:
the version from `gradle/libs.versions.toml`, and the variant and the image's digest from
`.github/libvlc-build.json`. The run keeps, as its artifact `libvlc-lgpl-<version>` for 90 days, the archive a
Release attaches (`libvlc-lgpl-<version>.tar.xz`), the build's corresponding source (`sources/`: the patched
libvlcjni and VLC trees and the contribs' archives) and `build-info.txt`. DrivePlayer's
`libvlc_build.sh ci-build` pushes the build branch from its recipe, waits for the run and installs the
artifact for testing.

A tested build is published from the same run. On the build's branch, commit the recipe the run built, the
run's `sources/` with `sources/SHA256SUMS`, both README release tables, the branch's entry in
`.github/release-branches.json`, and the Release notes in `.github/release-notes.md` (the branch, source tag,
build options, archive contents and SHA-256). Tag that commit `libvlc-lgpl-<version>`, push the tag, and
publish:

```bash
gh workflow run publish.yml -f tag='libvlc-lgpl-<version>' -f run='<build.yml run ID>'
```

`publish.yml` checks that the run succeeded on the tag's recipe and that the tag's `sources/` are the run's,
then creates the Release with the run's archive, titled `libvlc-lgpl <version> (<branch>)`; a release of
`main` becomes the repository-wide Latest. Then push the branch, and record the tag in
`.github/release-branches.json` on the other two branches. Keep at least the newest stable release and its
binary asset public for each branch; do not delete older releases as part of this maintenance. The daily and
manual release checks verify publication, assets, branch ancestry and that the repository-wide Latest
release belongs to `main`.

## Licenses

libVLC, libvlcjni and this build are distributed under the GNU Lesser General Public License, version 2.1
or later ([LICENSE](LICENSE)). DrivePlayer's build scripts and patches in this repository are provided
under the same license. Each third-party component in `sources/contrib/` is distributed under its own
license, found in its archive:

| License | Components |
|---|---|
| GNU LGPL 2.1 or later | FFmpeg, libdvbpsi, libebml, libmatroska, GNU FriBidi, GNU libiconv, libplacebo, libsoxr, mpg123 |
| BSD 2-Clause | dav1d, OpenJPEG |
| BSD 3-Clause | libogg, libvorbis, libtheora, libvpx, libFLAC, Opus, Speex |
| MIT | HarfBuzz ("Old MIT"), libxml2 |
| ISC | libass |
| FreeType Project License | FreeType |
| Independent JPEG Group License | libjpeg |
| PNG Reference Library License version 2 | libpng |
| zlib License | zlib |
| Boost Software License 1.0 | UTF8-CPP |
| GSM license (permissive) | libgsm |

The Android app links libVLC only as these shared libraries (`libvlc.so`, `libvlcjni.so`) through the
libvlcjni Java API, so a modified build made from these sources can take their place.
