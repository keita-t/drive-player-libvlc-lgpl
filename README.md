# libVLC for Drive Player — corresponding source

This repository holds the complete corresponding source of the libVLC library that the Drive Player
Android app ships: `com.example.driveplayer.thirdparty:libvlc-lgpl`, a build of libVLC and its Java
bindings (libvlcjni) made from sources under the GNU Lesser General Public License 2.1 or more
permissive licenses only, for arm64-v8a.

Each published build of the library has a tag named after its version (`libvlc-lgpl-<version>`), holding exactly the
sources, patches and build scripts that produced that build. Two builds matter:

| Library version | Tag | Branch | What it is |
|---|---|---|---|
| 3.7.6-35 | `libvlc-lgpl-3.7.6-35` | `main` | The build the app ships, with the patches listed in [PATCHES.md](PATCHES.md). The built library is attached to the GitHub release of its tag |
| 3.7.6-29-naked | `libvlc-lgpl-3.7.6-29-naked` | `variants` | A build for comparison, which the app does not ship: libVLC as upstream makes it, in this build's LGPL-only configuration, with only the patches the app cannot run without. The built library is attached to the GitHub release of its tag |

## Contents

| Path | What it is |
|---|---|
| `sources/libvlcjni-ddde54ff-drive-player.tar.xz` | libvlcjni at commit `ddde54fff93ab40c529a46eae80fe357ae0af97e`, with Drive Player's patches applied |
| `sources/vlc-66455a98-drive-player.tar.xz` | VLC media player 3.0 at commit `66455a98c8c515796b4a192acaa125c5d68c76c8`, with libvlcjni's patches and Drive Player's patches applied. It includes VLC's contrib build system (`contrib/src`), with the patches it applies to the third-party components |
| `sources/contrib/` | The source archives of the 27 third-party components linked into `libvlc.so`, as published by each project |
| `sources/SHA256SUMS` | Checksums of the archives above |
| `third-party/libvlc/build-native.sh` | The script that builds `libvlc.so`, `libvlcjni.so` and `libc++_shared.so` |
| `third-party/libvlc/patches/` | Drive Player's modifications to libvlcjni and VLC, as `git am` patches |
| `PATCHES.md` | What each patch solved and what it changes |
| `third-party/libvlc/aar/` | The Gradle build that packages the libraries and the Java bindings as an Android library (AAR) |
| `gradle/`, `gradlew` | The Gradle wrapper (Gradle 8.7) and the version entries the AAR build reads |

The layout of `third-party/libvlc/` and `gradle/` matches the Drive Player source tree, where the same
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

`patches/libvlcjni/` (4 patches) is applied to libvlcjni, and `patches/vlc/` (100 patches) to VLC after the patches
libvlcjni itself carries, all with `git am`. [PATCHES.md](PATCHES.md) lists each with the problem it solved and the
change it makes:

| What they concern | Patches |
|---|---|
| [License](PATCHES.md#license) | 2 |
| [Reading media through the app](PATCHES.md#reading-media-through-the-app) | 3 |
| [Opening and reading streams](PATCHES.md#opening-and-reading-streams) | 11 |
| [Video tracks and the app's window](PATCHES.md#video-tracks-and-the-apps-window) | 3 |
| [Audio](PATCHES.md#audio) | 12 |
| [Pause](PATCHES.md#pause) | 2 |
| [Seeking](PATCHES.md#seeking) | 15 |
| [Times and lengths](PATCHES.md#times-and-lengths) | 15 |
| [Elementary video streams](PATCHES.md#elementary-video-streams) | 9 |
| [Video size and pixel aspect](PATCHES.md#video-size-and-pixel-aspect) | 10 |
| [Video output](PATCHES.md#video-output) | 3 |
| [Hardware decoders](PATCHES.md#hardware-decoders) | 5 |
| [FFmpeg's decoders](PATCHES.md#ffmpegs-decoders) | 9 |
| [Ogg, with libVLC's own demuxer](PATCHES.md#ogg-with-libvlcs-own-demuxer) | 5 |

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
With `--env LIBVLC_VARIANT=ogg-avformat`, FFmpeg's demuxer opens Ogg instead of libVLC's, and libvorbis is not
built. With `--env LIBVLC_VARIANT=naked`, only the VLC patches the app cannot run without (0001 and 0002) are
applied, as 3.7.6-29-naked was built.

`build-native.sh` fetches the pinned libvlcjni and VLC commits and the component archives from their
upstream locations. To build from this repository's copies instead:

- Extract `sources/libvlcjni-*.tar.xz` to `work/src/libvlcjni` and `sources/vlc-*.tar.xz` to
  `work/src/libvlcjni/vlc`. These are the trees `build-native.sh` produces in its `fetch_sources` step,
  patches applied; run the remaining steps of `main` against them.
- Copy `sources/contrib/*` to `work/tarballs/`. VLC's contrib build uses the archives it finds there and
  verifies each against the SHA-512 it records in `contrib/src/<component>/SHA512SUMS`.

## Licenses

libVLC, libvlcjni and this build are distributed under the GNU Lesser General Public License, version 2.1
or later ([LICENSE](LICENSE)). Drive Player's build scripts and patches in this repository are provided
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
