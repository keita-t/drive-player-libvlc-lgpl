# Patches

English | [日本語](PATCHES.ja.md)

This comparison build applies all seven Java binding patches and only the three VLC patches the app and its tests cannot run
without: 0117 adds the transfer function to libVLC's track description, which binding patch 0005 reads.
Other VLC behaviour is upstream's. Patches are applied with `git am`; their commit messages give the full details.

Back to the [README](README.md).

## License

| Patch | Problem | Change |
|---|---|---|
| [`libvlcjni/0001`](third-party/libvlc/patches/libvlcjni/0001-build-the-bindings-without-the-renderer-discoverer.patch) | The renderer discoverer, `RendererDiscoverer.java`, is published under the GPL. | Its JNI part is removed, and the AAR build leaves the Java file out of the packaged sources. |
| [`vlc/0001`](third-party/libvlc/patches/vlc/0001-deinterlace-build-without-the-yadif-algorithm.patch) | The yadif deinterlacing algorithm is published under the GPL. | yadif is removed from the deinterlace module. |

## Reading media through the app

| Patch | Problem | Change |
|---|---|---|
| [`libvlcjni/0002`](third-party/libvlc/patches/libvlcjni/0002-add-a-media-read-through-java-callbacks.patch) | The app answered reads through a file descriptor of its own (Android's proxy file descriptor). Such a descriptor cannot be torn down when the app's process is killed while libVLC waits on a read, and keeps a CPU core busy until the device restarts. | `org.videolan.libvlc.MediaInput`, and a `Media` constructor that reads through its Java callbacks (`libvlc_media_new_callbacks`). |
| [`vlc/0002`](third-party/libvlc/patches/vlc/0002-imem-access-report-seekable-callbacks-as-fast-seekable.patch) | A callback input was read through the prefetch filter's large background reads. | A callback input that answers seeks is read like a file (fast-seekable). |

## Bindings

| Patch | Problem | Change |
|---|---|---|
| [`libvlcjni/0003`](third-party/libvlc/patches/libvlcjni/0003-cancel-surface-initialization-on-view-release.patch) | Detaching views could race the bindings' texture initialization and use a Surface not yet made; unattached callback loopers stayed alive. | The texture and its Surface are published together, detaching cancels pending initialization, and the callback thread is joined without holding its monitor. |
| [`libvlcjni/0004`](third-party/libvlc/patches/libvlcjni/0004-expose-current-input-track-formats.patch) | MPEG-PS and MPEG-TS tracks are identified before the decoder learns their size and pixel aspect, and parsed metadata cached zero dimensions. | `IMedia.getTracksSnapshot()` reads the input's current formats, with the size, pixel aspect and orientation found while decoding. |
| [`vlc/0117`](third-party/libvlc/patches/vlc/0117-lib-describe-the-transfer-function-of-a-video-track.patch) | An application that draws a track's pictures itself has to know whether they are HDR to show them in SDR: a PQ or HLG picture drawn as it is looks washed out. The input item's track held the transfer function the demuxer or the decoder found, but the track description libVLC gives an application left it out. | The video track description carries the transfer function, as libVLC's `video_transfer_func_t` value. |
| [`libvlcjni/0005`](third-party/libvlc/patches/libvlcjni/0005-describe-the-transfer-function-of-a-video-track.patch) | The bindings' video track had no transfer function either: the app's stills of a PQ or HLG video could not be told from SDR ones. | `IMedia.VideoTrack.colorTransfer` carries 0117's value, with libVLC's values named in `IMedia.VideoTrack.ColorTransfer`. |
| [`libvlcjni/0006`](third-party/libvlc/patches/libvlcjni/0006-hand-java-no-string-that-is-not-utf-8.patch) | The strings libVLC hands the bindings (a track's name and language, meta, titles) become Java strings through `NewStringUTF`, and bytes that are not UTF-8 abort a debuggable process (CheckJNI). The bindings' check passed a character whose following bytes merely had their top bit set, and a string that ended inside a character: an MP4 track named in Latin-1 or Windows-1251 aborted the app's process when it read the tracks. | Only `10xxxxxx` bytes continue a character, and the end of the string does not. Such a string is handed over as null, as the strings the check refused already were; the app names the track itself. |
| [`libvlcjni/0007`](third-party/libvlc/patches/libvlcjni/0007-write-an-instance-s-log-to-a-file-the-application-names.patch) | libVLC tells what it chose and did only in its log, which goes to logcat, and logd drops the lines of a process that logs as much as libVLC's debug level does whenever its reader falls behind: the app's tests that read the log back missed lines. | `LibVLC.setLogFile(path, level)` has an instance append its log to a file in place of logcat, each line in logcat's `threadtime` form under the `VLC` tag and written at once. The callback is removed before the instance is released. The app's tests use it; the app does not. |
