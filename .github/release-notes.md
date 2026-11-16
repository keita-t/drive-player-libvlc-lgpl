A comparison build of libVLC for the DrivePlayer app, which the app does not ship: `com.example.driveplayer.thirdparty:libvlc-lgpl` 3.7.6-49-ogg-libvlc, libVLC 3.0 and its Java bindings (libvlcjni) built from sources under the GNU Lesser General Public License 2.1 or more permissive licenses only, for arm64-v8a. It is built by the recipe's `ogg-libvlc` variant (`LIBVLC_VARIANT=ogg-libvlc`) on branch `ogg-libvlc`: the same patches as 3.7.6-49, the build the app ships, with libVLC's own Ogg demuxer opening Ogg and libvorbis and VLC's Vorbis decoder built, where the app's build uses FFmpeg's demuxer and decoder. It replaces 3.7.6-37 as the build of this branch, whose bindings lack the API binding patches 0005-0007 add.

Its complete corresponding source is the tag `libvlc-lgpl-3.7.6-49-ogg-libvlc` (branch `ogg-libvlc`); see its README. The archive was built by the repository's GitHub Actions (`build.yml`) from the recipe that tag holds.

Maintained documentation: [English](https://github.com/keita-t/drive-player-libvlc-lgpl/blob/ogg-libvlc/README.md) / [日本語](https://github.com/keita-t/drive-player-libvlc-lgpl/blob/ogg-libvlc/README.ja.md). Patch descriptions: [English](https://github.com/keita-t/drive-player-libvlc-lgpl/blob/libvlc-lgpl-3.7.6-49-ogg-libvlc/PATCHES.md) / [日本語](https://github.com/keita-t/drive-player-libvlc-lgpl/blob/libvlc-lgpl-3.7.6-49-ogg-libvlc/PATCHES.ja.md).

`libvlc-lgpl-3.7.6-49-ogg-libvlc.tar.xz` holds the AAR and its Maven metadata (`repository/com/example/driveplayer/thirdparty/libvlc-lgpl/3.7.6-49-ogg-libvlc/`) and the native output (`versions/3.7.6-49-ogg-libvlc/out/`: the stripped libraries, the Java bindings, each component's license files and `build-info.txt`).

SHA-256: `44ec8c60fc19dd6f169e157596e1bf09dcfd69194fefeafe9556a197ab69d5c1`
