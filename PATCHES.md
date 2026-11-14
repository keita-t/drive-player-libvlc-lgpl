# Patches

English | [日本語](PATCHES.ja.md)

This comparison build applies all four Java binding patches and only the two VLC patches the app cannot run without.
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
