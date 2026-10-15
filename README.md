# libVLC for Drive Player — corresponding source

This repository holds the complete corresponding source of the libVLC library that the Drive Player
Android app ships: `com.example.driveplayer.thirdparty:libvlc-lgpl`, a build of libVLC and its Java
bindings (libvlcjni) made from sources under the GNU Lesser General Public License 2.1 or more
permissive licenses only, for arm64-v8a.

Each published build of the library has a tag named after its version (`libvlc-lgpl-<version>`).
The tag holds exactly the sources, patches and build scripts that produced that build.

| Library version | Tag |
|---|---|
| 3.7.6-28 | `libvlc-lgpl-3.7.6-28` |
| 3.7.6-27 | `libvlc-lgpl-3.7.6-27` |
| 3.7.6-19 | `libvlc-lgpl-3.7.6-19` |
| 3.7.6-17 | `libvlc-lgpl-3.7.6-17` |
| 3.7.6-15 | `libvlc-lgpl-3.7.6-15` |
| 3.7.6-14 | `libvlc-lgpl-3.7.6-14` |
| 3.7.6-13 | `libvlc-lgpl-3.7.6-13` |
| 3.7.6-12 | `libvlc-lgpl-3.7.6-12` |
| 3.7.6-11 | `libvlc-lgpl-3.7.6-11` |
| 3.7.6-10 | `libvlc-lgpl-3.7.6-10` |
| 3.7.6-9 | `libvlc-lgpl-3.7.6-9` |
| 3.7.6-8 | `libvlc-lgpl-3.7.6-8` |
| 3.7.6-7 | `libvlc-lgpl-3.7.6-7` |
| 3.7.6-6 | `libvlc-lgpl-3.7.6-6` |
| 3.7.6-5 | `libvlc-lgpl-3.7.6-5` |
| 3.7.6-4 | `libvlc-lgpl-3.7.6-4` |
| 3.7.6-3 | `libvlc-lgpl-3.7.6-3` |
| 3.7.6-2 | `libvlc-lgpl-3.7.6-2` |
| 3.7.6-1 | `libvlc-lgpl-3.7.6-1` |

Builds made for comparison, which the app does not ship, have their corresponding source on the `variants` branch
and their tags there; the built library is attached to the GitHub release of each tag.

| Library version | Tag | What it is |
|---|---|---|
| 3.7.6-29-naked | `libvlc-lgpl-3.7.6-29-naked` | libVLC as upstream makes it, in this build's LGPL-only configuration, with only the patches the app cannot run without |

## Contents

| Path | What it is |
|---|---|
| `sources/libvlcjni-ddde54ff-drive-player.tar.xz` | libvlcjni at commit `ddde54fff93ab40c529a46eae80fe357ae0af97e`, with Drive Player's patches applied |
| `sources/vlc-66455a98-drive-player.tar.xz` | VLC media player 3.0 at commit `66455a98c8c515796b4a192acaa125c5d68c76c8`, with libvlcjni's patches and Drive Player's patches applied. It includes VLC's contrib build system (`contrib/src`), with the patches it applies to the third-party components |
| `sources/contrib/` | The source archives of the 27 third-party components linked into `libvlc.so`, as published by each project |
| `sources/SHA256SUMS` | Checksums of the archives above |
| `third-party/libvlc/build-native.sh` | The script that builds `libvlc.so`, `libvlcjni.so` and `libc++_shared.so` |
| `third-party/libvlc/patches/` | Drive Player's modifications to libvlcjni and VLC, as `git am` patches |
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
| GPL sources inside LGPL code | The renderer discoverer of the Java bindings and the yadif deinterlacing algorithm are removed (License patches below). |
| Features the app does not use | Stream output (transcoding, recording, casting), network access and streaming protocols, disc playback, Lua scripts, tag reading, service discovery, fontconfig, and the modules listed in `module_blacklist`. |

### Patches

`patches/libvlcjni/` is applied to libvlcjni, and `patches/vlc/` to VLC after the patches libvlcjni itself carries,
all with `git am`. Each patch's message describes its change in full. Numbers missing from the series were removed
or not adopted: 0010 and 0018 are in the tags of earlier versions, and 0020-0024, never built, in this
repository's history.

#### License

| Patch | Problem | Change |
|---|---|---|
| [`libvlcjni/0001`](third-party/libvlc/patches/libvlcjni/0001-build-the-bindings-without-the-renderer-discoverer.patch) | The renderer discoverer, `RendererDiscoverer.java`, is published under the GPL. | Its JNI part is removed, and the AAR build leaves the Java file out of the packaged sources. |
| [`vlc/0001`](third-party/libvlc/patches/vlc/0001-deinterlace-build-without-the-yadif-algorithm.patch) | The yadif deinterlacing algorithm is published under the GPL. | yadif is removed from the deinterlace module. |

#### Reading media through the app

| Patch | Problem | Change |
|---|---|---|
| [`libvlcjni/0002`](third-party/libvlc/patches/libvlcjni/0002-add-a-media-read-through-java-callbacks.patch) | The app answered reads through a file descriptor of its own (Android's proxy file descriptor). Such a descriptor cannot be torn down when the app's process is killed while libVLC waits on a read, and keeps a CPU core busy until the device restarts. | `org.videolan.libvlc.MediaInput`, and a `Media` constructor that reads through its Java callbacks (`libvlc_media_new_callbacks`). |
| [`vlc/0002`](third-party/libvlc/patches/vlc/0002-imem-access-report-seekable-callbacks-as-fast-seekable.patch) | A callback input was read through the prefetch filter's large background reads. | A callback input that answers seeks is read like a file (fast-seekable). |

#### Audio

| Patch | Problem | Change |
|---|---|---|
| [`vlc/0003`](third-party/libvlc/patches/vlc/0003-audiotrack-drain-until-the-written-audio-has-been-pl.patch) | The Android output ended its drain once the audio was written to the `AudioTrack`. What the track still held, some 100 ms, was cut by the pause at the end of the media and by the output's release. | The drain waits until the playback head reaches the frames written, bounded by the time they take and 200 ms. |
| [`vlc/0004`](third-party/libvlc/patches/vlc/0004-input-check-for-drained-decoders-at-the-end-more-oft.patch) | The end of a stream was noticed up to 100 ms after its decoders drained. | The input checks for drained decoders every 10 ms. |
| [`vlc/0006`](third-party/libvlc/patches/vlc/0006-retain-pcm-at-delayed-audio-start.patch) | When audio output initialization missed the first PCM buffer's deadline, the late-buffer policy discarded the start of the media before anything played. | The first buffer after the output is created, restarted or flushed is kept and retimed, and the shared input clock is delayed with it, accounting for pause and flushing. Later late buffers keep the original drop policy. |
| [`vlc/0034`](third-party/libvlc/patches/vlc/0034-audiotrack-keep-a-paused-output-paused-through-a-flush.patch) | A seek while paused flushed the `AudioTrack` output and played it again, sounding what the device still held: a click. | The output stays paused through a flush. |

#### Pause

| Patch | Problem | Change |
|---|---|---|
| [`vlc/0005`](third-party/libvlc/patches/vlc/0005-es_out-start-a-decoder-made-while-the-input-is-pause.patch) | A decoder made after its input paused started unpaused. Ogg finds its streams in its first data pages, so an Ogg track opened paused (`start-paused`) played the start it had buffered. | A decoder made while its input is paused starts paused, as `input_DecoderChangePause`'s FIXME describes for a track added while paused. |
| [`vlc/0017`](third-party/libvlc/patches/vlc/0017-decoder-restore-paused-pictures-after-replacing-the-video-output.patch) | A video track reselected while paused could handle its pause before its video output existed. The output then started unpaused and could discard the first picture. | The current pause is applied when the video output is acquired or reinitialized, serialized with pause changes. The pictures a paused seek or frame step asks for are shown even after buffering ends. |

#### Seeking, times and lengths

| Patch | Problem | Change |
|---|---|---|
| [`vlc/0013`](third-party/libvlc/patches/vlc/0013-ps-seek-to-a-time-by-the-timestamps-and-show-from-it-when-precise.patch) | MPEG-PS: a seek moved to a share of the bytes, landing off by the stream's start offset and its uneven bitrate. With pack headers seconds apart, as FFmpeg writes them above about 0.8 Mb/s, there was no length, the clock stood still between them and repeated after a seek. | Seeks search by the time track's timestamps. A precise seek or start time lands one to two seconds before the time and shows from it. The length is found on any packet. The clock advances between pack headers by the mux rate, counted in its units of 50 bytes, and is kept across PES packets. The time reported is that of the clock the pictures are shown by. |
| [`vlc/0014`](third-party/libvlc/patches/vlc/0014-ts-take-times-from-the-first-picture-and-decode-a-precise-seek-from-its-key-picture.patch) | MPEG-TS: times were taken from the first PCR, ahead of the first picture by the muxer's lead, and a seek landed past the key picture the time is decoded from. | Times start at the first picture or sound due. A precise seek lands two seconds early by the clock, decodes from there and shows from the time. The length is taken between presentation timestamps, so a short stream cannot have a negative length. |
| [`vlc/0015`](third-party/libvlc/patches/vlc/0015-avformat-include-AMR-storage-framing-in-the-duration-estimate.patch) | Raw AMR stores one byte of framing per channel every 20 ms, which the bitrate estimate left out, overestimating the length. | The estimate includes the 400 bits/s per channel of framing. Timestamp and container lengths still win. |
| [`vlc/0016`](third-party/libvlc/patches/vlc/0016-input-process-the-start-time-seek-before-demuxing-pictures.patch) | A start-time seek was queued but processed after the first demux, so a software decoder could show the beginning first. | Queued controls are processed before the first demux when the length is known and an audio or video stream is selected. Inputs that find their timeline or streams on the first demux (MPEG-PS, Ogg) keep that probe. |
| [`vlc/0027`](third-party/libvlc/patches/vlc/0027-decoder-drop-pictures-of-a-timeline-a-pending-flush-discards.patch) | A seek only marks a decoder flushing. Until its thread flushes the module, MediaCodec's output thread could queue a picture from before the seek, which was taken as the first one after it. | Pictures are discarded while the decoder is flushing, checked under the owner lock. |
| [`vlc/0028`](third-party/libvlc/patches/vlc/0028-decoder-cancel-a-pending-drain-when-flushing.patch) | A drain asked for at the end of the input survived a seek's flush, and the decoder drained in the middle of the new timeline. MediaCodec then output nothing. | A flush cancels the pending drain. |
| [`vlc/0029`](third-party/libvlc/patches/vlc/0029-input-demux-on-demand-while-a-paused-picture-s-decoder-starves.patch) | Paused, the input stops demuxing once buffered, but FFmpeg's frame threads, reordering or MediaCodec's latency can need more input before the picture a paused seek asks for. | While a decoder still owes that picture and has consumed its input (`ES_OUT_GET_AWAITED_PICTURE`), the paused input demuxes one block every 5 ms. |
| [`vlc/0038`](third-party/libvlc/patches/vlc/0038-es_out-take-no-clock-reference-as-late-while-the-input-is-paused.patch) | The paused input's on-demand demuxing (0029) reached clock references that were compared with the wall clock while the clock stood still. Once a decoder took long enough, as MediaCodec's MPEG-4 Part 2 decoder does after a video track is selected again, one was taken as late: the clock was reset, the decoders flushed, and the paused picture lost with the key picture it was decoded from. | No clock reference is taken as late while the input is paused, as while stepping frames. |
| [`vlc/0031`](third-party/libvlc/patches/vlc/0031-decoder-owe-a-seek-s-picture-to-a-decoder-paused-before-it-showed.patch) | A pause right after a seek reset the picture the seek was owed, and the old position stayed on screen. | A video decoder flushed by a seek is owed a picture until it shows one, also when it is paused first. |

#### Video size and pixel aspect

| Patch | Problem | Change |
|---|---|---|
| [`vlc/0007`](third-party/libvlc/patches/vlc/0007-mediacodec-retain-visible-dimensions-without-crop.patch) | Some MediaCodec decoders report macroblock-aligned dimensions without crop fields; fitting the padded size added black bars. | Visible dimensions from the input or SPS are kept apart from the coded ones and used when crop fields are missing or invalid. Valid crop fields still win. |
| [`libvlcjni/0004`](third-party/libvlc/patches/libvlcjni/0004-expose-current-input-track-formats.patch) | MPEG-PS and MPEG-TS tracks are identified before the decoder learns their size and pixel aspect, and parsed metadata cached zero dimensions. | `IMedia.getTracksSnapshot()` reads the input's current formats, with the size, pixel aspect and orientation found while decoding. |
| [`vlc/0008`](third-party/libvlc/patches/vlc/0008-mkv-preserve-display-aspect-ratio.patch) | Matroska's display aspect (`DisplayUnit=3`) was applied inverted: a 384x288 picture shown as 16:9 got 3:4 pixels. | The display aspect is divided by the picture's aspect, giving 4:3. |
| [`vlc/0009`](third-party/libvlc/patches/vlc/0009-mediacodec-read-undeclared-pixel-aspect.patch) | MediaCodec's output format has no pixel aspect, so H.264 or HEVC without a container aspect kept square pixels. | The pixel aspect is read from the current SPS. A container's aspect still wins. |
| [`vlc/0011`](third-party/libvlc/patches/vlc/0011-mediacodec-request-the-opaque-output-after-parsing-the-codec-configuration.patch) | A window learns the aspect an output opens with before the first picture, and MediaCodec opened its opaque output at 1:1 before reading the SPS. | The codec configuration is parsed before the opaque output is requested. |
| [`vlc/0012`](third-party/libvlc/patches/vlc/0012-mediacodec-open-the-mpeg-2-opaque-output-with-the-aspect-of-its-first-sequence-header.patch) | The same for MPEG-1/2, whose aspect is only known from the first sequence header. | The opaque output is requested, and MediaCodec started, once the first block's sequence header is parsed. |

#### Video output

| Patch | Problem | Change |
|---|---|---|
| [`libvlcjni/0003`](third-party/libvlc/patches/libvlcjni/0003-cancel-surface-initialization-on-view-release.patch) | Detaching views could race the bindings' texture initialization and use a Surface not yet made; unattached callback loopers stayed alive. | The texture and its Surface are published together, detaching cancels pending initialization, and the callback thread is joined without holding its monitor. |
| [`vlc/0019`](third-party/libvlc/patches/vlc/0019-android-display-crop-public-software-output-to-visible-pixels.patch) | Android's public software windows have no crop API, so coded padding, such as dav1d's aligned AV1 buffers, showed as black margins in stills. | The visible rectangle is negotiated as the window's format and the converter applies the crop, keeping decoder storage, alignment and pool ownership. |
| [`vlc/0025`](third-party/libvlc/patches/vlc/0025-opengl-convert-full-range-yuv-without-expanding-its-range-again.patch) | The OpenGL output's YUV to RGB matrices expand a limited range. A full-range source, such as MJPEG, was expanded twice, clipping its blacks and whites. | The full-range matrices are chosen when the source is full range. |

#### Hardware decoders

| Patch | Problem | Change |
|---|---|---|
| [`vlc/0026`](third-party/libvlc/patches/vlc/0026-mediacodec-hand-a-vp9-profile-the-codec-does-not-state-to-the-next-decoder.patch) | MediaCodec picks a VP9 decoder by MIME type. One without 10/12-bit support failed on Profile 2 after consuming input, and the next decoder started at a later key frame. | The first frame's profile is read; when the codec does not state it, the stream goes to the next decoder (FFmpeg) before any input is queued. |
| [`vlc/0030`](third-party/libvlc/patches/vlc/0030-mediacodec-hand-mpeg-4-part-2-with-b-vops-to-the-next-decoder.patch) | A hardware MPEG-4 Part 2 decoder can output the previous reference picture in place of each B-VOP while stating the Advanced Simple profile, and nothing reports it. | A stream whose video object layer allows B-VOPs (`low_delay` unset) goes to FFmpeg before any input is queued. |

#### Ogg, with libVLC's own demuxer

| Patch | Problem | Change |
|---|---|---|
| [`vlc/0032`](third-party/libvlc/patches/vlc/0032-speex-flush-only-bits-that-were-initialized.patch) | A seek before the first Speex packet reset bits that were not initialized, and crashed. | Bits are reset on a flush only once the headers initialized them. |
| [`vlc/0033`](third-party/libvlc/patches/vlc/0033-ogg-keep-the-logical-streams-at-the-physical-end-so-that-a-seek-back-finds-them.patch) | At the end of a file the demuxer deleted its logical streams to look for a chained group, and every later seek failed. | At the physical end the streams are kept, and a seek resets their end state. |
| [`vlc/0035`](third-party/libvlc/patches/vlc/0035-oggseek-search-pages-for-a-time-before-estimating-from-the-bitrate.patch) | A single audio stream was sought by an estimate from its nominal bitrate: far off for variable-bitrate Vorbis, Speex and FLAC, and past the end of a small file. | Pages are searched by granule first; the estimate is used only where searching cannot be done. |
| [`vlc/0036`](third-party/libvlc/patches/vlc/0036-ogg-time-flac-packets-by-their-frame-headers.patch) | Ogg times only a page's last packet, and a FLAC page can hold a second. FLAC packets were not interpolated, so after a seek the audio came a second behind its clock and was dropped. | Each FLAC packet is timed by the samples its frame header states, as Vorbis, Opus and Speex packets are. |
| [`vlc/0037`](third-party/libvlc/patches/vlc/0037-oggseek-read-to-the-end-when-probing-the-length.patch) | The length probe stopped short of a last page that starts before the bytes it read, and took an earlier page's time. | It reads to the end each time and takes the greatest granule. |

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

The recipe also builds a variant for comparison, with `--env LIBVLC_VARIANT=ogg-avformat`: FFmpeg's
demuxer opens Ogg instead of libVLC's, and libvorbis is not built. It uses the same sources; the app
ships the default build.

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
