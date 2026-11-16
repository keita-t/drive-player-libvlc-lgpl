<!-- source-sha256: fca0b1825c9f4f008a625f4518f65e2d3c3ef4f9a39750389bdccaeb1f8e00ed -->

# DrivePlayer 向け libVLC — 対応するソースコード

[English](README.md) | 日本語

このブランチ（`naked`）は、比較用ビルド `com.example.driveplayer.thirdparty:libvlc-lgpl`
3.7.6-29-naked の完全な対応ソースを保持します。GNU LGPL 2.1 またはそれより制約の少ない
ライセンスのソースを使う arm64-v8a 向けビルドです。アプリでは配布せず、VLC の必須パッチ 2 件と
Java bindings の全 4 件だけを適用します。アプリのビルドは `main` で追跡します。

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
| `sources/vlc-66455a98-drive-player-naked.tar.xz` | VLC media player 3.0 のコミット `66455a98c8c515796b4a192acaa125c5d68c76c8` に libvlcjni のパッチと DrivePlayer の VLC パッチ 0001・0002 だけを適用したソース。第三者コンポーネントに適用するパッチを含む VLC の contrib ビルドシステム（`contrib/src`）も収録しています |
| `sources/contrib/` | `libvlc.so` にリンクする第三者コンポーネント 27 個の、各プロジェクトが公開したソースアーカイブ |
| `sources/SHA256SUMS` | 上記アーカイブのチェックサム |
| `third-party/libvlc/build-native.sh` | `libvlc.so`、`libvlcjni.so`、`libc++_shared.so` をビルドするスクリプト |
| `third-party/libvlc/patches/` | libvlcjni と VLC に対する DrivePlayer の変更を `git am` 形式で収録したパッチ |
| `PATCHES.md`、`PATCHES.ja.md` | 各パッチが解決する問題と変更内容 |
| `third-party/libvlc/aar/` | ネイティブライブラリーと Java bindings を Android ライブラリー（AAR）に梱包する Gradle ビルド |
| `gradle/`、`gradlew` | Gradle wrapper（Gradle 8.7）と、AAR ビルドが読むバージョン設定 |

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
| アプリで使わない機能 | ストリーム出力（変換・録音・キャスト）、ネットワークアクセスと配信プロトコル、ディスク再生、Lua、タグ読み取り、サービス検出、fontconfig、`module_blacklist` に挙げたモジュールを除外します |

### パッチ

`patches/libvlcjni/` の 4 件を libvlcjni に適用し、`patches/vlc/` の 2 件を libvlcjni 自身のパッチの
後で VLC に適用します。いずれも `git am` を使用します。[PATCHES.ja.md](PATCHES.ja.md) に各問題と変更を
記載しています。

| 分類 | パッチ数 |
|---|---|
| [ライセンス](PATCHES.ja.md#license) | 2 |
| [アプリ経由のメディア読み取り](PATCHES.ja.md#reading-media-through-the-app) | 2 |
| [Java bindings](PATCHES.ja.md#bindings) | 2 |

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
    --env LIBVLC_VARIANT=naked \
    registry.videolan.org/vlc-debian-android@sha256:5f041ff50465aea803b93855d463f4b98f1d9f3be6628e304af2bf3fded6f98e \
    bash /recipe/build-native.sh
```

`work/out/` にライブラリー、Java bindings、ビルド記録 `build-info.txt`（リビジョン、コンポーネントの
バージョン、リンクしたモジュール）が出力されます。続いて JDK 21 と platform 36 を含む Android SDK を使い、
`ANDROID_HOME` を設定して AAR を梱包します。

```bash
./gradlew -p third-party/libvlc/aar publish \
    -Plibvlc.nativeOutput="$PWD/work/out" \
    -Plibvlc.repository="$PWD/repository" \
    -Plibvlc.variant=naked
```

このブランチのネイティブビルドには `LIBVLC_VARIANT=naked`、AAR 梱包には `-Plibvlc.variant=naked` を
上記コマンドのとおり指定します。3.7.6-29-naked のレシピを維持し、VLC の 0001・0002 と
Java bindings の全 4 件だけを適用します。現在の main の naked オプションと異なり、
この過去のビルドは libVLC 自身の Ogg demuxer と libvorbis を使います。収録した VLC アーカイブにも
これらのパッチだけを適用しています。

`build-native.sh` は固定した libvlcjni・VLC のコミットと各コンポーネントのアーカイブを上流から取得します。
このリポジトリに収録したコピーを使う場合は、次のように準備します。

- `sources/libvlcjni-*.tar.xz` を `work/src/libvlcjni`、`sources/vlc-*.tar.xz` を
  `work/src/libvlcjni/vlc` に展開します。これらは `fetch_sources` が生成するパッチ適用済みのツリーなので、
  `main` の残りの手順をそのツリーに対して実行します。
- `sources/contrib/*` を `work/tarballs/` にコピーします。VLC contrib はそこにあるアーカイブを使い、
  `contrib/src/<component>/SHA512SUMS` に記録した SHA-512 と照合します。

## ブランチ・文書・Release の保守

レシピとパッチの変更は、そのビルドのブランチで行います。このブランチ（`naked`）は過去のレシピを保持し、
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

新しい Release では、対応する完全なソースを対象ブランチにコミットし、そのコミットに
`libvlc-lgpl-<version>` タグを付けます。そのタグのレシピでバイナリーアーカイブをビルド・検証し、
既存 Release のアーカイブ配置を維持したうえで、対象ブランチを指定して公開します。

```bash
branch=ogg-libvlc # main, ogg-libvlc or naked
tag='libvlc-lgpl-<version>'
gh release create "$tag" "$tag.tar.xz" --verify-tag --target "$branch" \
    --title "libvlc-lgpl ${tag#libvlc-lgpl-} ($branch)" --notes-file release-notes.md --latest=false
```

実行前に `<version>` を実際のバージョン（必要なバリアント接尾辞を含む）に置き換えます。
Release notes にはブランチ、ソースタグ、ビルドオプション、アーカイブの内容、SHA-256 を記載します。
`main` には `--latest=true`、比較用には `--latest=false` を使います。3 ブランチすべての
`.github/release-branches.json` の該当項目と、日英 README の Release 表を更新します。
各ブランチの最新の安定版 Release とバイナリーを少なくとも 1 つ公開状態に保ち、この保守作業で過去の
Release は削除しません。日次・手動チェックで、公開状態、添付ファイル、タグがブランチの履歴に含まれること、
リポジトリ全体の Latest が `main` の Release であることを確認します。

## ライセンス

libVLC、libvlcjni、このビルドは GNU Lesser General Public License 2.1 以降（[LICENSE](LICENSE)）で
配布します。このリポジトリの DrivePlayer のビルドスクリプトとパッチも同じライセンスです。
`sources/contrib/` の第三者コンポーネントは、それぞれのアーカイブに記載されたライセンスで配布します。

| ライセンス | コンポーネント |
|---|---|
| GNU LGPL 2.1 以降 | FFmpeg、libdvbpsi、libebml、libmatroska、GNU FriBidi、GNU libiconv、libplacebo、libsoxr、mpg123 |
| BSD 2-Clause | dav1d、OpenJPEG |
| BSD 3-Clause | libogg、libvorbis、libtheora、libvpx、libFLAC、Opus、Speex |
| MIT | HarfBuzz（Old MIT）、libxml2 |
| ISC | libass |
| FreeType Project License | FreeType |
| Independent JPEG Group License | libjpeg |
| PNG Reference Library License version 2 | libpng |
| zlib License | zlib |
| Boost Software License 1.0 | UTF8-CPP |
| GSM license（制約の少ないライセンス） | libgsm |

Android アプリは libvlcjni の Java API を通じ、共有ライブラリー `libvlc.so` と `libvlcjni.so` としてだけ
libVLC をリンクします。そのため、これらのソースから作った変更版に置き換えられます。
