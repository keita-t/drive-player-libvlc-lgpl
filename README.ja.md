<!-- source-sha256: 9a2518d12741c5c4179101471348b7ed274ab3dc93e20c92f7b106189275eaee -->

# DrivePlayer 向け libVLC — 対応するソースコード

[English](README.md) | 日本語

このリポジトリは、Android アプリ DrivePlayer が配布する libVLC ライブラリー
`com.example.driveplayer.thirdparty:libvlc-lgpl` の完全な対応ソースを保持します。
libVLC と Java bindings（libvlcjni）を、GNU Lesser General Public License 2.1 またはそれより
制約の少ないライセンスのソースだけから、arm64-v8a 向けにビルドしています。

公開ビルドにはバージョンに対応する `libvlc-lgpl-<version>` タグを付け、実際に使ったソース、
パッチ、ビルドスクリプトを保持します。管理対象の各ブランチでは、最新の公開ビルドを
GitHub Release で入手できる状態に保ちます。3.7.6-49 以降の Release は公開したまま残します。
それより前のビルドの Release は、ここに挙げたものを除いて取り下げました。タグは残っています。

| ライブラリーのバージョン | タグ | ブランチ | 内容 |
|---|---|---|---|
| 3.7.6-49 | [`libvlc-lgpl-3.7.6-49`](https://github.com/keita-t/drive-player-libvlc-lgpl/releases/tag/libvlc-lgpl-3.7.6-49) | [`main`](https://github.com/keita-t/drive-player-libvlc-lgpl/tree/main) | アプリが配布するビルド。[main/PATCHES.ja.md](https://github.com/keita-t/drive-player-libvlc-lgpl/blob/main/PATCHES.ja.md) のパッチを含み、タグの GitHub Release にビルド済みライブラリーを添付しています |
| 3.7.6-37 | [`libvlc-lgpl-3.7.6-37`](https://github.com/keita-t/drive-player-libvlc-lgpl/releases/tag/libvlc-lgpl-3.7.6-37) | [`ogg-libvlc`](https://github.com/keita-t/drive-player-libvlc-lgpl/tree/ogg-libvlc) | libVLC 自身の Ogg demuxer と libvorbis を使う最新の公開済みビルド。当初は通常のアプリ用ビルドとして公開しました |
| 3.7.6-29-naked | [`libvlc-lgpl-3.7.6-29-naked`](https://github.com/keita-t/drive-player-libvlc-lgpl/releases/tag/libvlc-lgpl-3.7.6-29-naked) | [`naked`](https://github.com/keita-t/drive-player-libvlc-lgpl/tree/naked) | アプリの動作に必須の VLC パッチと Java bindings のパッチだけを含む比較用ビルド |

各ブランチはレシピとバージョンを独立して追跡するため、最新 Release のバージョン番号をそろえる必要は
ありません。`ogg-libvlc` は既存の 3.7.6-37 タグ、`naked` は 3.7.6-29-naked タグから分岐します。
旧 `variants` ブランチは履歴として保持し、新しい比較用ビルドはそれぞれの専用ブランチで管理します。
既存タグとバイナリーの名前・内容は維持します。

## 内容

| パス | 内容 |
|---|---|
| `sources/libvlcjni-ddde54ff-drive-player.tar.xz` | libvlcjni のコミット `ddde54fff93ab40c529a46eae80fe357ae0af97e` に DrivePlayer のパッチを適用したソース |
| `sources/vlc-66455a98-drive-player.tar.xz` | VLC media player 3.0 のコミット `66455a98c8c515796b4a192acaa125c5d68c76c8` に libvlcjni と DrivePlayer のパッチを適用したソース。第三者コンポーネントに適用するパッチを含む VLC の contrib ビルドシステム（`contrib/src`）も収録しています |
| `sources/contrib/` | `libvlc.so` にリンクする第三者コンポーネント 28 個の、各プロジェクトが公開したソースアーカイブ |
| `sources/SHA256SUMS` | 上記アーカイブのチェックサム |
| `third-party/libvlc/build-native.sh` | `libvlc.so`、`libvlcjni.so`、`libc++_shared.so` をビルドするスクリプト |
| `third-party/libvlc/patches/` | libvlcjni と VLC に対する DrivePlayer の変更を `git am` 形式で収録したパッチ |
| `PATCHES.md`、`PATCHES.ja.md` | 各パッチが解決する問題と変更内容 |
| `third-party/libvlc/aar/` | ネイティブライブラリーと Java bindings を Android ライブラリー（AAR）に梱包する Gradle ビルド |
| `gradle/`、`gradlew` | Gradle wrapper（Gradle 8.13）と、AAR ビルドが読むバージョン設定 |

`third-party/libvlc/` と `gradle/` の配置は DrivePlayer のソースツリーと同じで、同じファイルを
変更せずに使用しています。

## 変更内容と理由

VideoLAN が Maven Central で公開する `org.videolan.android:libvlc-all` とは、GPL のコンポーネントを
含まないこと、アプリで使わない機能を除外すること、アプリが依存する動作のためのソースパッチを持つことの
3 点が異なります。

### 除外するもの

| 対象 | ビルドでの保証方法 |
|---|---|
| GPL の第三者コンポーネント | `build-native.sh` の `contrib_packages` で明示した一覧から選び、VLC contrib の GPL・GPLv3 ガードを有効にします。FFmpeg の GPL、version 3、non-free がすべて無効であることも確認します |
| GPL の VLC モジュール | `module_blacklist` でリンク対象から外し、リンクするモジュールに GPL の宣言があればビルドを停止します |
| LGPL コード内の GPL ソース | Java bindings の renderer discoverer と yadif デインターレース処理を削除します（[ライセンス関連パッチ](PATCHES.ja.md#license)） |
| libVLC 自身の Ogg demuxer と libvorbis | FFmpeg が Ogg を開き、Vorbis をデコードします。Ogg demuxer を `module_blacklist` でリンク対象から外し、libvorbis はビルドしません |
| アプリで使わない機能 | ストリーム出力（変換・録音・キャスト）、ネットワークアクセスと配信プロトコル、ディスク再生、Lua、タグ読み取り、サービス検出、fontconfig、`module_blacklist` に挙げたモジュールを除外します |

### パッチ

`patches/libvlcjni/` の 7 件を libvlcjni に適用し、`patches/vlc/` の 130 件を libvlcjni 自身のパッチの
後で VLC に適用します。いずれも `git am` を使用します。[PATCHES.ja.md](PATCHES.ja.md) に各問題と変更を
記載しています。

| 分類 | パッチ数 |
|---|---|
| [ライセンス](PATCHES.ja.md#license) | 2 |
| [アプリ経由のメディア読み取り](PATCHES.ja.md#reading-media-through-the-app) | 3 |
| [ストリームのオープンと読み取り](PATCHES.ja.md#opening-and-reading-streams) | 16 |
| [映像トラックとアプリのウィンドウ](PATCHES.ja.md#video-tracks-and-the-apps-window) | 7 |
| [音声](PATCHES.ja.md#audio) | 13 |
| [一時停止](PATCHES.ja.md#pause) | 2 |
| [シーク](PATCHES.ja.md#seeking) | 20 |
| [時刻と長さ](PATCHES.ja.md#times-and-lengths) | 17 |
| [映像エレメンタリーストリーム](PATCHES.ja.md#elementary-video-streams) | 9 |
| [映像寸法とピクセルアスペクト比](PATCHES.ja.md#video-size-and-pixel-aspect) | 11 |
| [映像出力](PATCHES.ja.md#video-output) | 5 |
| [ハードウェア decoder](PATCHES.ja.md#hardware-decoders) | 6 |
| [FFmpeg の decoder](PATCHES.ja.md#ffmpegs-decoders) | 12 |
| [libVLC 自身の demuxer を使う Ogg](PATCHES.ja.md#ogg-with-libvlcs-own-demuxer)（0032 を除き `ogg-libvlc` バリアントのみ） | 6 |
| [MIDI とゲーム音楽](PATCHES.ja.md#midi-and-game-music) | 7 |
| [ログ](PATCHES.ja.md#the-log)（アプリの試験が使い、アプリ自身は使わない） | 1 |

## ビルド

ネイティブライブラリーは VideoLAN の Android ビルドイメージ内でビルドします。NDK r29 と VLC が想定する
ツールを含むイメージを、次の digest に固定しています。

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

`work/out/` にライブラリー、Java bindings、ビルド記録 `build-info.txt`（リビジョン、コンポーネントの
バージョン、リンクしたモジュール）が出力されます。続いて JDK 21 と platform 36 を含む Android SDK を使い、
`ANDROID_HOME` を設定して AAR を梱包します。

```bash
./gradlew -p third-party/libvlc/aar publish \
    -Plibvlc.nativeOutput="$PWD/work/out" \
    -Plibvlc.repository="$PWD/repository"
```

レシピは同じソースから比較用バリアントもビルドできます。アプリが配布するのは既定のビルドです。
`--env LIBVLC_VARIANT=ogg-libvlc` では FFmpeg の代わりに libVLC の Ogg demuxer を使い、libvorbis と
VLC の Vorbis decoder もビルドします。これは 3.7.6-37 までの既定の構成です。
`--env LIBVLC_VARIANT=naked` では、VLC のパッチをアプリに必須の 0001 と 0002 に限定します。
3.7.6-29-naked と同じ選び方ですが、このレシピでは Ogg は既定ビルド同様に FFmpeg で開き、
3.7.6-29-naked では libVLC 自身の demuxer で開いていた点が異なります。

`build-native.sh` は固定した libvlcjni・VLC のコミットと各コンポーネントのアーカイブを上流から取得します。
このリポジトリに収録したコピーを使う場合は、次のように準備します。

- `sources/libvlcjni-*.tar.xz` を `work/src/libvlcjni`、`sources/vlc-*.tar.xz` を
  `work/src/libvlcjni/vlc` に展開します。これらは `fetch_sources` が生成するパッチ適用済みのツリーなので、
  `main` の残りの手順をそのツリーに対して実行します。
- `sources/contrib/*` を `work/tarballs/` にコピーします。VLC contrib はそこにあるアーカイブを使い、
  `contrib/src/<component>/SHA512SUMS` に記録した SHA-512 と照合します。

## ブランチ・文書・Release の保守

レシピとパッチの変更は、そのビルドのブランチで行います。このブランチ（`main`）は既定のレシピを使い、
`ogg-libvlc` と `naked` の README はそれぞれのバージョンとビルドオプションを説明します。
文書チェックなどの共通変更は、ソースアーカイブをマージせずに 3 ブランチすべてへ適用します。

英語を標準とし、`README.md` と `README.ja.md`、`PATCHES.md` と `PATCHES.ja.md` をそれぞれ同じ変更で
更新します。翻訳を確認してから、次を実行します。

```bash
python3 scripts/check_docs.py --update
python3 scripts/check_docs.py
python3 -m unittest discover -s tests
```

チェックでは、英語原文の SHA-256 を日本語文書に記録し、原文更新の未反映、パッチ一覧、リンク、
ビルドコマンドを検査します。翻訳の意味の正しさは判定しないため、ハッシュを更新する前に両言語を
レビューしてください。GitHub Actions が 3 ブランチで検査を実行します。

ビルドは GitHub Actions で行います。`build.yml` は、`build/<version>` ブランチの push または手動実行で、
ブランチのレシピを VideoLAN のイメージでビルドします。ビルドする内容は `scripts/build_settings.py` が読み、
バージョンは `gradle/libs.versions.toml`、バリアントとイメージの digest は `.github/libvlc-build.json` から取ります。
実行は、Release に添付するアーカイブ（`libvlc-lgpl-<version>.tar.xz`）、ビルドの対応ソース（`sources/`：
パッチを適用した libvlcjni と VLC のツリー、contrib のアーカイブ）、`build-info.txt` を、artifact
`libvlc-lgpl-<version>` として 90 日間保持します。DrivePlayer の `libvlc_build.sh ci-build` は、自身のレシピから
ビルドブランチを push し、実行の完了を待って、試験のために artifact をインストールします。

試験を終えたビルドは、同じ実行から公開します。ビルドのブランチに、実行がビルドしたレシピ、実行の `sources/` と
`sources/SHA256SUMS`、日英 README の Release 表、`.github/release-branches.json` のそのブランチの項目、
`.github/release-notes.md` の Release notes（ブランチ、ソースタグ、ビルドオプション、アーカイブの内容、SHA-256）を
コミットします。そのコミットに `libvlc-lgpl-<version>` タグを付けて push し、公開します。

```bash
gh workflow run publish.yml -f tag='libvlc-lgpl-<version>' -f run='<build.yml run ID>'
```

`publish.yml` は、実行がタグのレシピで成功したことと、タグの `sources/` が実行のものであることを確認してから、
実行のアーカイブを添付した Release を `libvlc-lgpl <version> (<branch>)` の題名で作成します。`main` の Release は
リポジトリ全体の Latest になります。その後ブランチを push し、残り 2 ブランチの `.github/release-branches.json` に
タグを記録します。各ブランチの最新の安定版 Release とバイナリーを少なくとも 1 つ公開状態に保ち、この保守作業で
過去の Release は削除しません。日次・手動チェックで、公開状態、添付ファイル、タグがブランチの履歴に含まれること、
リポジトリ全体の Latest が `main` の Release であることを確認します。

## ライセンス

libVLC、libvlcjni、このビルドは GNU Lesser General Public License 2.1 以降（[LICENSE](LICENSE)）で
配布します。このリポジトリの DrivePlayer のビルドスクリプトとパッチも同じライセンスです。
`sources/contrib/` の第三者コンポーネントは、それぞれのアーカイブに記載されたライセンスで配布します。

| ライセンス | コンポーネント |
|---|---|
| GNU LGPL 2.1 以降 | FFmpeg、libdvbpsi、libebml、libmatroska、GNU FriBidi、GNU libiconv、libplacebo、libsoxr、mpg123、FluidLite、Game_Music_Emu（LGPL の Nuked YM2612 emulator を使用し、アーカイブ内の GPL MAME emulator はビルドしません） |
| BSD 2-Clause | dav1d、OpenJPEG |
| BSD 3-Clause | libogg、libtheora、libvpx、libFLAC、Opus、Speex |
| MIT | HarfBuzz（Old MIT）、libxml2 |
| ISC | libass |
| FreeType Project License | FreeType |
| Independent JPEG Group License | libjpeg |
| PNG Reference Library License version 2 | libpng |
| zlib License | zlib |
| Boost Software License 1.0 | UTF8-CPP |
| GSM license（制約の少ないライセンス） | libgsm |
| Public domain または MIT | FluidLite のアーカイブに含まれる stb_vorbis |

Android アプリは libvlcjni の Java API を通じ、共有ライブラリー `libvlc.so` と `libvlcjni.so` としてだけ
libVLC をリンクします。そのため、これらのソースから作った変更版に置き換えられます。
