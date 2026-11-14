# libVLC for DrivePlayer — corresponding source

English | [日本語](README.ja.md)

This repository holds the complete corresponding source of the libVLC library that the DrivePlayer
Android app ships: `com.example.driveplayer.thirdparty:libvlc-lgpl`, a build of libVLC and its Java
bindings (libvlcjni) made from sources under the GNU Lesser General Public License 2.1 or more
permissive licenses only, for arm64-v8a.

Each published build of the library has a tag named after its version (`libvlc-lgpl-<version>`), holding exactly the
sources, patches and build scripts that produced that build. Each maintained branch keeps its latest
published build available as a GitHub Release; older releases remain available too:

| Library version | Tag | Branch | What it is |
|---|---|---|---|
| 3.7.6-46 | [`libvlc-lgpl-3.7.6-46`](https://github.com/keita-t/drive-player-libvlc-lgpl/releases/tag/libvlc-lgpl-3.7.6-46) | [`main`](https://github.com/keita-t/drive-player-libvlc-lgpl/tree/main) | The build the app ships, with the patches listed in [main/PATCHES.md](https://github.com/keita-t/drive-player-libvlc-lgpl/blob/main/PATCHES.md). The built library is attached to the GitHub release of its tag |
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
| `sources/vlc-66455a98-drive-player.tar.xz` | VLC media player 3.0 at commit `66455a98c8c515796b4a192acaa125c5d68c76c8`, with libvlcjni's patches and DrivePlayer's patches applied. It includes VLC's contrib build system (`contrib/src`), with the patches it applies to the third-party components |
| `sources/contrib/` | The source archives of the 28 third-party components linked into `libvlc.so`, as published by each project |
| `sources/SHA256SUMS` | Checksums of the archives above |
| `third-party/libvlc/build-native.sh` | The script that builds `libvlc.so`, `libvlcjni.so` and `libc++_shared.so` |
| `third-party/libvlc/patches/` | DrivePlayer's modifications to libvlcjni and VLC, as `git am` patches |
| `PATCHES.md` | What each patch solved and what it changes |
| `third-party/libvlc/aar/` | The Gradle build that packages the libraries and the Java bindings as an Android library (AAR) |
| `gradle/`, `gradlew` | The Gradle wrapper (Gradle 8.13) and the version entries the AAR build reads |

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
| libVLC's own Ogg demuxer and libvorbis | FFmpeg's demuxer opens Ogg and FFmpeg decodes Vorbis. The Ogg demuxer is not linked (`module_blacklist`), and libvorbis is not built. |
| Features the app does not use | Stream output (transcoding, recording, casting), network access and streaming protocols, disc playback, Lua scripts, tag reading, service discovery, fontconfig, and the modules listed in `module_blacklist`. |

### Patches

`patches/libvlcjni/` (5 patches) is applied to libvlcjni, and `patches/vlc/` (124 patches) to VLC after the patches
libvlcjni itself carries, all with `git am`. [PATCHES.md](PATCHES.md) lists each with the problem it solved and the
change it makes:

| What they concern | Patches |
|---|---|
| [License](PATCHES.md#license) | 2 |
| [Reading media through the app](PATCHES.md#reading-media-through-the-app) | 3 |
| [Opening and reading streams](PATCHES.md#opening-and-reading-streams) | 15 |
| [Video tracks and the app's window](PATCHES.md#video-tracks-and-the-apps-window) | 6 |
| [Audio](PATCHES.md#audio) | 13 |
| [Pause](PATCHES.md#pause) | 2 |
| [Seeking](PATCHES.md#seeking) | 17 |
| [Times and lengths](PATCHES.md#times-and-lengths) | 17 |
| [Elementary video streams](PATCHES.md#elementary-video-streams) | 9 |
| [Video size and pixel aspect](PATCHES.md#video-size-and-pixel-aspect) | 11 |
| [Video output](PATCHES.md#video-output) | 5 |
| [Hardware decoders](PATCHES.md#hardware-decoders) | 5 |
| [FFmpeg's decoders](PATCHES.md#ffmpegs-decoders) | 11 |
| [Ogg, with libVLC's own demuxer](PATCHES.md#ogg-with-libvlcs-own-demuxer) (`ogg-libvlc` variant only, but for 0032) | 6 |
| [MIDI and game music](PATCHES.md#midi-and-game-music) | 7 |

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
    registry.videolan.org/vlc-debian-android@sha256:5f041ff50465aea803b93855d463f4b98f1d9f3be6628e304af2bf3fded6f98e \
    bash /recipe/build-native.sh
```

The libraries, the Java bindings and a record of the build (`build-info.txt`: revisions, component
versions, linked modules) are left in `work/out/`. The AAR is then packaged with JDK 21 and an Android SDK
with platform 36 (`ANDROID_HOME` set):

```bash
./gradlew -p third-party/libvlc/aar publish \
    -Plibvlc.nativeOutput="$PWD/work/out" \
    -Plibvlc.repository="$PWD/repository"
```

The recipe also builds two variants for comparison, from the same sources; the app ships the default build.
With `--env LIBVLC_VARIANT=ogg-libvlc`, libVLC's own demuxer opens Ogg instead of FFmpeg's, and libvorbis and
VLC's Vorbis decoder are built, as the default build did up to 3.7.6-37. With `--env LIBVLC_VARIANT=naked`, only
the VLC patches the app cannot run without (0001 and 0002) are applied, as 3.7.6-29-naked was built; Ogg is opened
as in the default build, where 3.7.6-29-naked opened it with libVLC's own demuxer.

`build-native.sh` fetches the pinned libvlcjni and VLC commits and the component archives from their
upstream locations. To build from this repository's copies instead:

- Extract `sources/libvlcjni-*.tar.xz` to `work/src/libvlcjni` and `sources/vlc-*.tar.xz` to
  `work/src/libvlcjni/vlc`. These are the trees `build-native.sh` produces in its `fetch_sources` step,
  patches applied; run the remaining steps of `main` against them.
- Copy `sources/contrib/*` to `work/tarballs/`. VLC's contrib build uses the archives it finds there and
  verifies each against the SHA-512 it records in `contrib/src/<component>/SHA512SUMS`.

## Maintaining the branches, documentation and releases

Make recipe and patch changes on the branch for that build. This branch (`main`) uses the default recipe;
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

For a new release, first commit its complete corresponding source on the appropriate branch and tag that
commit as `libvlc-lgpl-<version>`. Build and verify the binary archive using that tag's recipe and retain the
archive layout described by the existing release. Publish the archive with that branch as the target:

```bash
branch=ogg-libvlc # main, ogg-libvlc or naked
tag='libvlc-lgpl-<version>'
gh release create "$tag" "$tag.tar.xz" --verify-tag --target "$branch" \
    --title "${tag#libvlc-lgpl-} ($branch)" --notes-file release-notes.md --latest=false
```

Replace `<version>` with the actual version (including any variant suffix) before running the command.
Release notes should identify the branch, source tag, build options, archive contents and SHA-256.
For `main`, use `--latest=true`; comparison releases use `--latest=false`. Update the branch's entry in
`.github/release-branches.json` on all three branches, along with both README release tables. Keep at least
the newest stable release and its binary asset public for each branch; do not delete older releases as part
of this maintenance. The daily and manual release checks verify publication, assets, branch ancestry and
that the repository-wide Latest release belongs to `main`.

## Licenses

libVLC, libvlcjni and this build are distributed under the GNU Lesser General Public License, version 2.1
or later ([LICENSE](LICENSE)). DrivePlayer's build scripts and patches in this repository are provided
under the same license. Each third-party component in `sources/contrib/` is distributed under its own
license, found in its archive:

| License | Components |
|---|---|
| GNU LGPL 2.1 or later | FFmpeg, libdvbpsi, libebml, libmatroska, GNU FriBidi, GNU libiconv, libplacebo, libsoxr, mpg123, FluidLite, Game_Music_Emu (built with its LGPL Nuked YM2612 emulator; the GPL MAME emulator in its archive is not built) |
| BSD 2-Clause | dav1d, OpenJPEG |
| BSD 3-Clause | libogg, libtheora, libvpx, libFLAC, Opus, Speex |
| MIT | HarfBuzz ("Old MIT"), libxml2 |
| ISC | libass |
| FreeType Project License | FreeType |
| Independent JPEG Group License | libjpeg |
| PNG Reference Library License version 2 | libpng |
| zlib License | zlib |
| Boost Software License 1.0 | UTF8-CPP |
| GSM license (permissive) | libgsm |
| Public domain or MIT | stb_vorbis, inside FluidLite's archive |

The Android app links libVLC only as these shared libraries (`libvlc.so`, `libvlcjni.so`) through the
libvlcjni Java API, so a modified build made from these sources can take their place.
