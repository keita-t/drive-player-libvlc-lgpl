<!-- source-sha256: 0d56c05e7e4c0140a246e085b5ee2c4614aa08b5c0d5928f926490cbeb82941a -->

# パッチ

[English](PATCHES.md) | 日本語

このブランチの比較用ビルドには、Java bindings の 4 件と、アプリの動作に必須の VLC パッチ 2 件だけを適用します。
VLC の他の動作は上流のままです。各パッチは `git am` で適用し、詳細はパッチのコミットメッセージに記載しています。

[README に戻る](README.ja.md)。

<a id="license"></a>

## ライセンス

| パッチ | 問題 | 変更内容 |
|---|---|---|
| [`libvlcjni/0001`](third-party/libvlc/patches/libvlcjni/0001-build-the-bindings-without-the-renderer-discoverer.patch) | レンダラー検出機能の RendererDiscoverer.java は GPL で公開されています。 | JNI 側の機能を削除し、AAR のビルドでもこの Java ファイルを梱包対象から除外します。 |
| [`vlc/0001`](third-party/libvlc/patches/vlc/0001-deinterlace-build-without-the-yadif-algorithm.patch) | yadif デインターレース処理は GPL で公開されています。 | deinterlace モジュールから yadif を除外します。 |

<a id="reading-media-through-the-app"></a>

## アプリ経由のメディア読み取り

| パッチ | 問題 | 変更内容 |
|---|---|---|
| [`libvlcjni/0002`](third-party/libvlc/patches/libvlcjni/0002-add-a-media-read-through-java-callbacks.patch) | アプリ独自の Android proxy file descriptor で読み取りに応じると、libVLC が読み取り待ちの間にアプリのプロセスを終了しても解放できず、端末を再起動するまで CPU の 1 コアを使い続けました。 | org.videolan.libvlc.MediaInput と、その Java コールバック経由で読み取る Media コンストラクター（libvlc_media_new_callbacks）を追加します。 |
| [`vlc/0002`](third-party/libvlc/patches/vlc/0002-imem-access-report-seekable-callbacks-as-fast-seekable.patch) | コールバック入力に対して prefetch フィルターがバックグラウンドで大量に先読みしていました。 | シークに応じるコールバック入力を、ファイルと同じ高速シーク可能な入力として扱います。 |

<a id="bindings"></a>

## Java bindings

| パッチ | 問題 | 変更内容 |
|---|---|---|
| [`libvlcjni/0003`](third-party/libvlc/patches/libvlcjni/0003-cancel-surface-initialization-on-view-release.patch) | ビューの切り離しがテクスチャー初期化と競合して未作成の Surface を使う場合があり、接続されなかったコールバック looper も生き残りました。 | テクスチャーと Surface を一緒に公開し、切り離しで初期化を取り消します。モニターを保持せずにコールバックスレッドの終了を待ちます。 |
| [`libvlcjni/0004`](third-party/libvlc/patches/libvlcjni/0004-expose-current-input-track-formats.patch) | MPEG-PS と MPEG-TS は decoder が寸法とピクセルアスペクト比を知る前にトラックを識別するため、解析済みメタデータにゼロ寸法が残りました。 | IMedia.getTracksSnapshot() で、デコード中に得た寸法、ピクセルアスペクト比、向きを含む入力の現在のフォーマットを読み取ります。 |
