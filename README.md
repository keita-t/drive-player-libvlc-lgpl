# libVLC for Drive Player — corresponding source of comparison builds

This branch, `variants`, holds the complete corresponding source of builds of
`com.example.driveplayer.thirdparty:libvlc-lgpl` that are made for comparison and that the Drive Player Android app
does not ship. Each is built from the same recipe as an app build, as one of its variants, and is published here so
that the app's development can test against it without building it: its tag (`libvlc-lgpl-<version>`) holds exactly
the sources, patches and build scripts that produced it, and the GitHub release of that tag carries the built
library. The sources of the builds the app ships are on `main`.

| Library version | Tag | What it is |
|---|---|---|
| 3.7.6-29-naked | `libvlc-lgpl-3.7.6-29-naked` | libVLC as upstream makes it, in this build's LGPL-only configuration, with only the patches the app cannot run without |

## 3.7.6-29-naked

The `naked` variant of the 3.7.6-29 recipe: the same pinned libvlcjni and VLC, the same components, configuration
and modules as the app's 3.7.6-29, but of Drive Player's VLC patches only the two the app cannot run without — the
LGPL-only configuration (`vlc/0001`) and its callback input read as a file (`vlc/0002`) — and the four patches of
the Java bindings, whose API the app calls. Everything else behaves as upstream's libVLC does, so the app can be run
against it to see what one of its own patches changes, or whether a fault comes from upstream.

### Contents

| Path | What it is |
|---|---|
| `sources/libvlcjni-ddde54ff-drive-player.tar.xz` | libvlcjni at commit `ddde54fff93ab40c529a46eae80fe357ae0af97e`, with Drive Player's patches applied (the same archive as the app's builds on `main`) |
| `sources/vlc-66455a98-drive-player-naked.tar.xz` | VLC media player 3.0 at commit `66455a98c8c515796b4a192acaa125c5d68c76c8`, with libvlcjni's patches and Drive Player's `vlc/0001` and `vlc/0002` applied. It includes VLC's contrib build system (`contrib/src`), with the patches it applies to the third-party components |
| `sources/contrib/` | The source archives of the 27 third-party components linked into `libvlc.so`, as published by each project |
| `sources/SHA256SUMS` | Checksums of the archives above |
| `third-party/libvlc/build-native.sh` | The script that builds `libvlc.so`, `libvlcjni.so` and `libc++_shared.so`; `LIBVLC_VARIANT=naked` selects this build (`NAKED_VLC_PATCHES`) |
| `third-party/libvlc/patches/` | The patches this build applies, as `git am` patches |
| `third-party/libvlc/aar/` | The Gradle build that packages the libraries and the Java bindings as an Android library (AAR) |
| `gradle/`, `gradlew` | The Gradle wrapper (Gradle 8.7) and the version entries the AAR build reads |

The release `libvlc-lgpl-3.7.6-29-naked` carries `libvlc-lgpl-3.7.6-29-naked.tar.xz`: the AAR and its Maven metadata
under `repository/com/example/driveplayer/thirdparty/libvlc-lgpl/3.7.6-29-naked/`, and under
`versions/3.7.6-29-naked/out/` the stripped libraries, the Java bindings, each component's license files and
`build-info.txt` (revisions, patches, component versions, linked modules). Drive Player installs it with
`./local_build.sh --libvlc-version 3.7.6-29-naked --fetch-libvlc`, which checks the archive's SHA-256 against the
one its checkout records.

### What was changed, and why

#### Left out

| What | How the build ensures it |
|---|---|
| Third-party components under the GPL | Components are chosen from an explicit list (`contrib_packages` in `build-native.sh`), and VLC's contrib system runs with its GPL and GPLv3 guards on. FFmpeg's configuration is checked to have its GPL, version 3 and non-free parts disabled. |
| VLC modules under the GPL | They are not linked (`module_blacklist`), and the build stops if any linked module declares the GPL. |
| GPL sources inside LGPL code | The renderer discoverer of the Java bindings and the yadif deinterlacing algorithm are removed (License patches below). |
| Features the app does not use | Stream output (transcoding, recording, casting), network access and streaming protocols, disc playback, Lua scripts, tag reading, service discovery, fontconfig, and the modules listed in `module_blacklist`. |

#### Patches

`patches/libvlcjni/` is applied to libvlcjni, and `patches/vlc/` to VLC after the patches libvlcjni itself carries,
all with `git am`. Each patch's message describes its change in full. The app's builds on `main` carry further VLC
patches; this build leaves them out.

##### License

| Patch | Problem | Change |
|---|---|---|
| [`libvlcjni/0001`](third-party/libvlc/patches/libvlcjni/0001-build-the-bindings-without-the-renderer-discoverer.patch) | The renderer discoverer, `RendererDiscoverer.java`, is published under the GPL. | Its JNI part is removed, and the AAR build leaves the Java file out of the packaged sources. |
| [`vlc/0001`](third-party/libvlc/patches/vlc/0001-deinterlace-build-without-the-yadif-algorithm.patch) | The yadif deinterlacing algorithm is published under the GPL. | yadif is removed from the deinterlace module. |

##### Reading media through the app

| Patch | Problem | Change |
|---|---|---|
| [`libvlcjni/0002`](third-party/libvlc/patches/libvlcjni/0002-add-a-media-read-through-java-callbacks.patch) | The app answered reads through a file descriptor of its own (Android's proxy file descriptor). Such a descriptor cannot be torn down when the app's process is killed while libVLC waits on a read, and keeps a CPU core busy until the device restarts. | `org.videolan.libvlc.MediaInput`, and a `Media` constructor that reads through its Java callbacks (`libvlc_media_new_callbacks`). |
| [`vlc/0002`](third-party/libvlc/patches/vlc/0002-imem-access-report-seekable-callbacks-as-fast-seekable.patch) | A callback input was read through the prefetch filter's large background reads. | A callback input that answers seeks is read like a file (fast-seekable). |

##### Bindings

| Patch | Problem | Change |
|---|---|---|
| [`libvlcjni/0003`](third-party/libvlc/patches/libvlcjni/0003-cancel-surface-initialization-on-view-release.patch) | Detaching views could race the bindings' texture initialization and use a Surface not yet made; unattached callback loopers stayed alive. | The texture and its Surface are published together, detaching cancels pending initialization, and the callback thread is joined without holding its monitor. |
| [`libvlcjni/0004`](third-party/libvlc/patches/libvlcjni/0004-expose-current-input-track-formats.patch) | MPEG-PS and MPEG-TS tracks are identified before the decoder learns their size and pixel aspect, and parsed metadata cached zero dimensions. | `IMedia.getTracksSnapshot()` reads the input's current formats, with the size, pixel aspect and orientation found while decoding. |

### Build

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

The libraries, the Java bindings and a record of the build (`build-info.txt`) are left in `work/out/`. The AAR is
then packaged with JDK 21 and an Android SDK with platform 36 (`ANDROID_HOME` set):

```bash
./gradlew -p third-party/libvlc/aar publish \
    -Plibvlc.nativeOutput="$PWD/work/out" \
    -Plibvlc.repository="$PWD/repository" \
    -Plibvlc.variant=naked
```

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
