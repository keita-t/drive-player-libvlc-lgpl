<!-- source-sha256: c4c1fc3d872f24f42a46967ccda3ef0d4199866188f24be665e8b11c0e6397ba -->

# パッチ

[English](PATCHES.md) | 日本語

このブランチの比較用ビルドには、Java bindings の 7 件と、アプリとその試験に必須の VLC パッチ 3 件だけを適用します。
0117 は、binding のパッチ 0005 が読む伝達関数を libVLC のトラックの記述に加えます。
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
| [`vlc/0117`](third-party/libvlc/patches/vlc/0117-lib-describe-the-transfer-function-of-a-video-track.patch) | アプリ自身で映像を描く場合、PQ や HLG を SDR としてそのまま表示すると色が薄く見えるため HDR の判定が必要です。入力項目にある伝達関数が libVLC のトラック情報には含まれていませんでした。 | 映像トラック情報に video_transfer_func_t の値として伝達関数を含めます。 |
| [`libvlcjni/0005`](third-party/libvlc/patches/libvlcjni/0005-describe-the-transfer-function-of-a-video-track.patch) | Java bindings の映像トラックにも伝達関数がなく、PQ や HLG の動画から取得した静止画を SDR と区別できませんでした。 | IMedia.VideoTrack.colorTransfer に 0117 の値を公開し、IMedia.VideoTrack.ColorTransfer に定数名を定義します。 |
| [`libvlcjni/0006`](third-party/libvlc/patches/libvlcjni/0006-hand-java-no-string-that-is-not-utf-8.patch) | libVLC が bindings に渡す文字列（トラックの名前と言語、メタデータ、タイトル）は `NewStringUTF` で Java の文字列になり、UTF-8 でないバイトは debuggable なプロセスを中断させます（CheckJNI）。bindings の検査は、2 バイト目以降の最上位ビットが立っていれば通し、文字の途中で終わる文字列も通していたため、Latin-1 や Windows-1251 で名付けた MP4 のトラックを読むとアプリのプロセスが中断しました。 | 2 バイト目以降は `10xxxxxx` だけを認め、文字列の終わりは数えません。そうした文字列は検査が拒んだ文字列と同じく null として渡し、アプリはトラックを自身の名前で示します。 |
| [`libvlcjni/0007`](third-party/libvlc/patches/libvlcjni/0007-write-an-instance-s-log-to-a-file-the-application-names.patch) | libVLC は選んだものと行ったことをログでしか伝えず、ログは logcat に出ます。libVLC の debug レベルほど多く書くプロセスの行は、読み手が遅れると logd が読み飛ばすため、ログを読み戻すアプリの試験が行を取りこぼしました。 | `LibVLC.setLogFile(path, level)` で、インスタンスのログを logcat の代わりにファイルへ追記させます。各行は logcat の `threadtime` 形式（`VLC` タグ）で、1 回の書き込みで書きます。インスタンスの解放前に callback を外します。アプリの試験が使い、アプリ自身は使いません。 |
