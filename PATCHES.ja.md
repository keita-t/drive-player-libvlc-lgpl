<!-- source-sha256: 4512922d04621770f8fcaf76ba3f3ef419ee59e882cb075d458b12d8c07a3207 -->

# パッチ

[English](PATCHES.md) | 日本語

このビルドに含まれる libvlcjni と VLC に対する DrivePlayer の変更です。
`third-party/libvlc/patches/libvlcjni/` の 7 件を libvlcjni に、
`third-party/libvlc/patches/vlc/` の 130 件を libvlcjni 自身のパッチの後で VLC に適用します。
すべて `git am` 形式です。各パッチのメッセージに詳細を記載し、以下の表では解決する問題と変更内容を分類しています。
欠番は削除または不採用となったものです。0010 と 0018 は過去のバージョンのタグに、
一度もビルドしなかった 0020〜0024 はこのリポジトリの履歴に残っています。

このビルドはレシピの `ogg-libvlc` バリアントで、libVLC 自身の demuxer で Ogg を開くため、その demuxer のパッチ
（0033、0035〜0037、0059、0060、0116）がここで効果を持ちます（[libVLC 自身の demuxer を使う Ogg](#ogg-with-libvlcs-own-demuxer)）。
`main` のアプリのビルドは同じパッチを適用しますが、Ogg は FFmpeg の demuxer で開きます。

[README に戻る](README.ja.md)。

- [ライセンス](#license) (2)
- [アプリ経由のメディア読み取り](#reading-media-through-the-app) (3)
- [ストリームのオープンと読み取り](#opening-and-reading-streams) (16)
- [映像トラックとアプリのウィンドウ](#video-tracks-and-the-apps-window) (7)
- [音声](#audio) (13)
- [一時停止](#pause) (2)
- [シーク](#seeking) (20)
- [時刻と長さ](#times-and-lengths) (17)
- [映像エレメンタリーストリーム](#elementary-video-streams) (9)
- [映像寸法とピクセルアスペクト比](#video-size-and-pixel-aspect) (11)
- [映像出力](#video-output) (5)
- [ハードウェア decoder](#hardware-decoders) (6)
- [FFmpeg の decoder](#ffmpegs-decoders) (12)
- [libVLC 自身の demuxer を使う Ogg](#ogg-with-libvlcs-own-demuxer) (6)
- [MIDI とゲーム音楽](#midi-and-game-music) (7)
- [ログ](#the-log) (1)

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
| [`vlc/0039`](third-party/libvlc/patches/vlc/0039-imem-access-report-the-content-type-the-media-was-given.patch) | コールバック入力には名前も型もなく、名前や型から開く demuxer が拒否するため、H.264 や HEVC のエレメンタリーストリームを再生できませんでした。 | imem-content-type オプションでデータの型を指定し、コールバック入力がストリームの content type として報告します。未指定時は従来どおり報告しません。 |

<a id="opening-and-reading-streams"></a>

## ストリームのオープンと読み取り

| パッチ | 問題 | 変更内容 |
|---|---|---|
| [`vlc/0042`](third-party/libvlc/patches/vlc/0042-image-leave-an-input-typed-as-video-to-the-demuxer-of-its-stream.patch) | Motion JPEG のエレメンタリーストリームは JPEG 画像と同じ先頭を持つため、先に試される image demuxer が静止画として開いていました。 | 強制指定されていない限り、content type が動画を示す入力を image demuxer が辞退します。 |
| [`vlc/0050`](third-party/libvlc/patches/vlc/0050-demux-try-the-demuxer-a-media-s-type-names-first-without-forcing-it.patch) | audio/mpeg、audio/aac、video/MP2T、video/dv などの型に対応する demuxer が強制的に使われ、audio/mpeg とされた MP4 内の AAC など、実データと型が合わない入力が雑音になるか再生できませんでした。 | 型に対応する demuxer を強制せずに最初に試し、辞退した場合は他の demuxer を試します。 |
| [`vlc/0074`](third-party/libvlc/patches/vlc/0074-demux-name-the-vc-1-demuxer-by-the-type-of-a-vc-1-stream.patch) | video/vc1 を指定した VC-1 エレメンタリーストリームを MPEG video demuxer が開き、映像が表示されませんでした。 | NSV の型と同様に、この型を VC-1 demuxer に対応付けます。 |
| [`vlc/0075`](third-party/libvlc/patches/vlc/0075-avformat-open-a-format-ffmpeg-knows-by-its-extension-alone-by-its-type.patch) | FFmpeg が拡張子だけで識別する Motion Pixels（.mvi）などは、名前がなく型だけがあると MPEG-PS demuxer に渡り、再生できませんでした。 | 入力の video/x-mvi から形式を指定します。実データが一致しない場合は引き続き開けません。 |
| [`vlc/0110`](third-party/libvlc/patches/vlc/0110-avformat-probe-more-of-a-stream-whose-first-bytes-tell-no-format.patch) | 形式判定が先頭 2261 バイトに限られていました。FFmpeg は PVA を 2 個のパケットヘッダーで識別するため、最初の I ピクチャーが大きい途中開始ファイルなどでは 1 個しか見つからず、PS demuxer が音声だけを再生していました。 | 先頭で形式を判定できなければ、FFmpeg 自身の探索と同様に探索量を 4 倍ずつ増やし、最大 64 KiB を調べます。先頭で判定できる入力の処理は変わりません。 |
| [`vlc/0108`](third-party/libvlc/patches/vlc/0108-avformat-allow-seeking-to-the-end-of-the-stream.patch) | ストリーム末尾へのシークを範囲外として拒否し、FFmpeg がエラーと解釈していました。最終チャンクのデータをこのシークで飛ばす DTS-HD demuxer が開けず、PS demuxer で音声なしの再生になっていました。 | 末尾を超えるシークだけを拒否します。 |
| [`vlc/0045`](third-party/libvlc/patches/vlc/0045-es-open-loas-streams-of-aac-in-latm.patch) | LOAS（LATM 内の AAC。放送や FFmpeg の latm muxer で使われる形式）を VLC 自身の demuxer が開けず、FFmpeg では長さもシークもありませんでした。 | ES demuxer が先頭 3 フレームの連続した同期語を確認して LOAS と判定し、LATM として packetizer に渡します。長さとシーク位置はビットレートから求めます。 |
| [`vlc/0086`](third-party/libvlc/patches/vlc/0086-ps-tell-avs-video-from-mpeg-video.patch) | ストリームマップのないプログラムストリームでは映像の型がなく、AVS video（CAVS）が MPEG-2 decoder に渡され、表示されませんでした。データで型が分かるのはストリーム先頭の最初のパケットだけで、時刻を指定した開始（静止画を含む）は最初のパケットを読む前にシークするため、トラックが後のパケットで MPEG video と判定され、packetizer が終端までシーケンスヘッダーを待って画像が出ませんでした（時計は進みます）。 | マップから型を読み、マップがなければ MPEG video で予約されているシーケンスヘッダーの開始コードで AVS video を識別します。ストリーム先頭の probe が読む各映像の最初のパケットとストリームマップを保持し、どこから読み始めても同じ型にします。 |
| [`vlc/0041`](third-party/libvlc/patches/vlc/0041-avi-keep-the-fourcc-of-ut-video-variants-for-the-decoder.patch) | AVI demuxer が Ut Video の fourcc をすべて ULRA に置き換えていたため、fourcc で形式を識別する decoder が 4:2:0（ULY0）を RGBA と解釈し、出力できませんでした。 | SpeedHQ と同様に元の fourcc を保持します。 |
| [`vlc/0071`](third-party/libvlc/patches/vlc/0071-caf-read-apple-s-gsm-as-gsm-full-rate.patch) | CAF が Apple の GSM full rate を表す agsm を Microsoft GSM と解釈し、decoder が開始できず無音になっていました。 | MP4 demuxer と同じく GSM full rate として読み取ります。 |
| [`vlc/0085`](third-party/libvlc/patches/vlc/0085-avcodec-name-signed-8-bit-pcm-laid-out-by-channel.patch) | FFmpeg の demuxer が CDXL の音声をチャンネル別の符号付き 8 ビット PCM として渡しても、対応する fourcc がなく decoder を選べず、映像だけが再生されました。 | libavcodec の PCM decoder に対応する fourcc を定義します。 |
| [`vlc/0089`](third-party/libvlc/patches/vlc/0089-avi-read-a-stream-s-chunks-under-a-code-not-listed-when-no-index.patch) | インデックスがない AVI では、トラックの種類に登録されていないチャンクコード（Indeo の 00iv など）を飛ばし、途中で切れた AVI が音声だけの再生になっていました。 | インデックス読み込み時と同様に、既知のストリームのチャンクをコードによらず受け取ります。 |
| [`vlc/0090`](third-party/libvlc/patches/vlc/0090-avi-read-a-chunk-found-without-an-index-only-as-its-track-s-next.patch) | インデックスがない場合、次のチャンクの探索で途中のチャンクを飛ばしたため、音声を先に配置したファイルでは音声が先へ飛び、隙間が無音になりました。 | 探索で見つけたチャンクは、読み取り対象トラックの次のチャンクの場合だけ読み、他はインデックス登録だけを行います。 |
| [`vlc/0120`](third-party/libvlc/patches/vlc/0120-mkv-find-the-length-of-a-segment-without-walking-all-its-clusters.patch) | duration のない Matroska セグメントで、長さを得るため先頭クラスタから末尾まで各要素をシークと読み取りで走査していました。ライブ出力として書かれた約 1400 クラスタの 2 時間のファイルでは、再生前の読み取りに再生時間と同じだけかかりました。 | Cues の最後のクラスタからの走査を 8 要素で止め、それを超える場合や Cues がなければ末尾 1 MiB、次に 4 MiB を一括で読み、最後の完全なクラスタをメモリー上で探します。見つからなければ長さは不明のままにします。 |
| [`vlc/0131`](third-party/libvlc/patches/vlc/0131-ps-tell-HEVC-and-MPEG-4-Visual-from-MPEG-video-in-a-stream-with-no-map.patch) | FFmpeg が書かないストリームマップだけで PS の映像形式を判断していたため、.mpg にリマックスした HEVC と MPEG-4 Visual が MPEG video に渡り、表示されませんでした。MPEG-4 Visual の開始コードは AVS と誤認されました。 | マップがなければ、データ先頭のベースレイヤーの parameter set、delimiter、SEI で HEVC を、visual object sequence または object layer で MPEG-4 Visual を、AVS より先に判定します。MPEG-1 ヘッダーの後でも MPEG-2 と同様にパケットデータを探します。 |
| [`vlc/0134`](third-party/libvlc/patches/vlc/0134-ps-leave-a-track-s-language-unset-when-the-stream-map-states-none.patch) | ストリームマップが言語の descriptor（ISO 639）なしで挙げるストリームでは、初期化されていない descriptor の 3 バイトがトラックの言語になりました。descriptor のないマップで映像の型を示す監視カメラ・レコーダーのストリームは UTF-8 でない言語を持ち、bindings がトラックを読むと Java VM がアプリのプロセスを中断しました。 | マップを読む前に descriptor を初期化し、言語のないストリームのトラックは言語を持ちません。 |


<a id="video-tracks-and-the-apps-window"></a>

## 映像トラックとアプリのウィンドウ

| パッチ | 問題 | 変更内容 |
|---|---|---|
| [`vlc/0057`](third-party/libvlc/patches/vlc/0057-es_out-let-an-input-leave-its-video-tracks-unselected-until-one-is-asked-for.patch) | 入力は映像トラックを発見すると直ちに選択して decoder を作っていました。アプリはトラックの寸法を知ってからウィンドウを作るため、ウィンドウなしで開けない MediaCodec の代わりに FFmpeg が選ばれ、その後もソフトウェアでデコードしていました。 | 既定で有効な video-autoselect を追加します。無効なら、優先指定のない字幕と同様に、要求されるまで映像トラックを選択しません。 |
| [`vlc/0058`](third-party/libvlc/patches/vlc/0058-es_out-describe-a-track-before-announcing-it.patch) | 入力項目にフォーマットを記録する前にトラック追加を通知していたため、通知時に一覧を読むリスナーからトラックが見えないことがありました。 | 追加時とプログラムの再選択時に、情報を先に記録してから通知します。 |
| [`vlc/0070`](third-party/libvlc/patches/vlc/0070-es_out-have-a-demuxer-read-a-video-track-left-for-the-application-while-nothing-is-selected.patch) | video-autoselect を無効にしたとき、選択トラックも待つための長さもない入力が終了し、インデックスのない映像のみの AVI や fragmented MP4 が、アプリが選択する前の最初の demux で終わりました。 | 何も選択されていない間は、プログラムの映像トラックを demuxer には選択済みとして報告して読み進めます。実際に要求されるまでブロックに対応する decoder はありません。 |
| [`vlc/0115`](third-party/libvlc/patches/vlc/0115-decoder-drop-the-pictures-of-a-video-decoder-selected-mid-timeline-until-a-flush.patch) | 音声のため読み進んだ後でウィンドウができて映像を選ぶと、キーピクチャーではない現在位置から decoder にデータが渡り、参照画像がない壊れた映像や灰色の画面が表示され、再開始のシークまで残ることがありました。 | タイムラインにデータを供給した後の選択で作った映像 decoder は、フラッシュが実行されるまで画像を捨てます。シークがなければ最初に捨てた画像から 1 秒後に表示を始めます。要求時ではなくスレッドが decoder と出力を実際にフラッシュしてから解除し、その間に届く古い画像も防ぎます。demuxer が発見した時点で作る decoder の開始は従来どおりです。 |
| [`vlc/0117`](third-party/libvlc/patches/vlc/0117-lib-describe-the-transfer-function-of-a-video-track.patch) | アプリ自身で映像を描く場合、PQ や HLG を SDR としてそのまま表示すると色が薄く見えるため HDR の判定が必要です。入力項目にある伝達関数が libVLC のトラック情報には含まれていませんでした。 | 映像トラック情報に video_transfer_func_t の値として伝達関数を含めます。 |
| [`libvlcjni/0005`](third-party/libvlc/patches/libvlcjni/0005-describe-the-transfer-function-of-a-video-track.patch) | Java bindings の映像トラックにも伝達関数がなく、PQ や HLG の動画から取得した静止画を SDR と区別できませんでした。 | IMedia.VideoTrack.colorTransfer に 0117 の値を公開し、IMedia.VideoTrack.ColorTransfer に定数名を定義します。 |
| [`libvlcjni/0006`](third-party/libvlc/patches/libvlcjni/0006-hand-java-no-string-that-is-not-utf-8.patch) | libVLC が bindings に渡す文字列（トラックの名前と言語、メタデータ、タイトル）は `NewStringUTF` で Java の文字列になり、UTF-8 でないバイトは debuggable なプロセスを中断させます（CheckJNI）。bindings の検査は、2 バイト目以降の最上位ビットが立っていれば通し、文字の途中で終わる文字列も通していたため、Latin-1 や Windows-1251 で名付けた MP4 のトラックを読むとアプリのプロセスが中断しました。 | 2 バイト目以降は `10xxxxxx` だけを認め、文字列の終わりは数えません。そうした文字列は検査が拒んだ文字列と同じく null として渡し、アプリはトラックを自身の名前で示します。 |

<a id="audio"></a>

## 音声

| パッチ | 問題 | 変更内容 |
|---|---|---|
| [`vlc/0003`](third-party/libvlc/patches/vlc/0003-audiotrack-drain-until-the-written-audio-has-been-pl.patch) | Android 出力は AudioTrack への書き込みで drain を完了していたため、まだトラック内にある約 100 ms の音声がメディア末尾の一時停止や出力解放で切れていました。 | 書き込んだフレームまで playback head が到達するのを待ちます。待ち時間の上限は音声の長さに 200 ms を加えた値です。 |
| [`vlc/0004`](third-party/libvlc/patches/vlc/0004-input-check-for-drained-decoders-at-the-end-more-oft.patch) | decoder の drain 完了からストリーム終了の認識まで最大 100 ms かかっていました。 | drain 完了を 10 ms 間隔で確認します。 |
| [`vlc/0006`](third-party/libvlc/patches/vlc/0006-retain-pcm-at-delayed-audio-start.patch) | 音声出力の初期化が最初の PCM バッファーの期限に間に合わないと、再生前に冒頭が破棄されました。出力が遅延を報告する場合、その分だけ遅れたバッファーも捨てられたり、長時間クロックに合わせてリサンプリングされたりしました。 | 出力の作成・再開・フラッシュ後の最初のバッファーを保持して時刻を付け直し、一時停止とフラッシュを考慮して共有クロックも遅らせます。出力遅延が分かる場合はわずかな遅れでも実際に聞こえる時刻に合わせ、不明な場合は 60 ms の閾値を維持します。フラッシュ後も開始時と同じ処理を行い、早い最初のバッファーまでの時間は無音で埋めます。以降の遅延バッファーの破棄方針は従来どおりです。 |
| [`vlc/0034`](third-party/libvlc/patches/vlc/0034-audiotrack-keep-a-paused-output-paused-through-a-flush.patch) | 一時停止中のシークで AudioTrack がフラッシュ後に再生を始め、端末内に残る音がクリックとして聞こえました。 | フラッシュの間も出力を一時停止に保ちます。 |
| [`vlc/0061`](third-party/libvlc/patches/vlc/0061-decoder-end-a-drain-of-the-audio-output-when-a-seek-flushes-the-decoder.patch) | 入力末尾の音声 decoder が最大 2 秒間 drain する間、シークのフラッシュが待たされ、古い位置の音声が続き映像が止まりました。 | フラッシュで進行中の drain を中断します。新しい任意の drain_interrupt コールバックを AudioTrack 出力で実装し、途中で要求された一時停止は先に適用して出力を停止したままにします。 |
| [`vlc/0099`](third-party/libvlc/patches/vlc/0099-audiotrack-count-the-output-latency-the-playback-head-leaves-out.patch) | playback head による AudioTrack の位置にはその先の約 100〜130 ms の遅延が含まれず、書き込み前には遅延自体も不明でした。シーク後の音声が 35〜130 ms 遅れ、逆方向にリサンプリングされ、120 ms の無音が挿入される場合がありました。 | AudioTrack のタイムスタンプからヘッド以降の遅延を測り、次のリセット以降の遅延に含めます。位置はヘッド基準のままにし、書き込み前から遅延を報告します。 |
| [`vlc/0100`](third-party/libvlc/patches/vlc/0100-decoder-cut-the-audio-a-precise-seek-lands-before-its-target.patch) | 精密シークのプリロールで、目標より前から始まり目標より後まで続く音声ブロックが先頭から再生されました。680 ms 単位の GXF PCM は最大その長さだけ早く鳴り、クロックが引かれて映像が止まりました。遅れて届く Ogg Vorbis などもバッファリング終了後に目標以前の音声を出していました。 | PCM デコード時に目標以前の部分を切り、バッファリング終了時に目標へ到達していない音声トラックでは、到達するブロックが来るまで目標時刻を保持します。 |
| [`vlc/0101`](third-party/libvlc/patches/vlc/0101-decoder-drop-audio-of-a-timeline-a-pending-flush-discards.patch) | シークがフラッシュを予約してからスレッドが実行するまでに、古い音声が新しいタイムラインの最初の音声として扱われ、連続シークで多数の古い音声が再生されました。 | 映像の 0027 と同様に、decoder のフラッシュ中は音声を破棄します。 |
| [`vlc/0098`](third-party/libvlc/patches/vlc/0098-soxr-resample-into-16-bit-samples-without-dither.patch) | soxr は未指定時に 16 ビット出力へ TPDF ディザーを加えるため、デジタル無音が最下位ビットの雑音になりました。 | ディザーなしでリサンプリングします。 |
| [`vlc/0102`](third-party/libvlc/patches/vlc/0102-soxr-date-what-it-outputs-by-what-it-starts-with.patch) | SoX はフィルター用に入力を保持しますが（8 kHz で 43 ms、44.1 kHz で 13 ms）、出力ブロックに今回渡した入力の時刻を付けていたため、音声が早いと判断され、リサンプリングや無音挿入が起きました。 | 出力に含まれる音声の先頭に基づいて時刻を付けます。 |
| [`vlc/0097`](third-party/libvlc/patches/vlc/0097-wav-read-g726-in-frames-of-20-ms.patch) | WAV の G.726 を多くの場合 1 バイトずつ読み、毎秒 4000 フレームに時刻を付けていたため、リサンプリングが揺れて音程がずれました。1 バイトでは 3 ビットと 5 ビットの符号語も途中で切れます。 | 符号語 8 個の整数倍で 20 ms ずつ読み、シークもそのフレームの先頭に合わせます。 |
| [`vlc/0103`](third-party/libvlc/patches/vlc/0103-wav-read-4-bit-adpcm-at-the-rate-its-bits-make.patch) | WAV の Yamaha ADPCM と G.722 を FFmpeg に任せると、FFmpeg がヘッダーに実際の 2 倍のバイトレートを書くため、シークが指定時刻の 2 倍の位置へ移動しました。 | VLC の WAV demuxer で両形式を読み、1 サンプル 4 ビットから求めたレートでシークします。Yamaha ADPCM はヘッダーのアラインメント単位、G.722 は 20 ms 単位で読みます。Yamaha ADPCM decoder の状態はストリーム全体で継続するため、シーク後の区間は音量レベルがずれます。 |
| [`vlc/0118`](third-party/libvlc/patches/vlc/0118-audiotrack-go-on-without-the-dynamicsprocessing-effect-when-it-fails.patch) | Android 12 以降では各 AudioTrack に DynamicsProcessing を作ります（100% 超の増幅用で、欠落・失敗時はソフトウェア増幅で代替）。この効果の例外も出力エラーとして扱い、書き込みスレッドが停止して無音のままクロックだけ進みました。moto g64 5G（Android 15）では Dolby 効果が出力スレッド間を移動する際、コンストラクターの setEngineArchitecture が時折 UnsupportedOperationException を投げ、未書き込みのトラックを AudioFlinger が無効にしました。 | コンストラクター、setEnabled、setInputGainAllChannelsTo の例外を警告として記録し、出力エラーにはしません。効果なしで出力を続け、100% 超の音量にはソフトウェア増幅を使います。 |

<a id="pause"></a>

## 一時停止

| パッチ | 問題 | 変更内容 |
|---|---|---|
| [`vlc/0005`](third-party/libvlc/patches/vlc/0005-es_out-start-a-decoder-made-while-the-input-is-pause.patch) | 入力の一時停止後に作られた decoder が非停止状態で始まり、最初のデータページでトラックを発見する Ogg を start-paused で開くと、先読みした冒頭が再生されました。 | 一時停止中に追加されるトラックについて input_DecoderChangePause の FIXME が示すとおり、decoder を一時停止状態で開始します。 |
| [`vlc/0017`](third-party/libvlc/patches/vlc/0017-decoder-restore-paused-pictures-after-replacing-the-video-output.patch) | 一時停止中に映像トラックを再選択すると、映像出力ができる前に停止処理が行われ、出力が非停止状態で始まって最初の画像を捨てる場合がありました。 | 映像出力の取得・再初期化時に、停止状態の変更と直列化して現在の停止状態を適用します。停止中のシークやコマ送りが要求する画像は、バッファリング終了後も表示します。 |

<a id="seeking"></a>

## シーク

| パッチ | 問題 | 変更内容 |
|---|---|---|
| [`vlc/0013`](third-party/libvlc/patches/vlc/0013-ps-seek-to-a-time-by-the-timestamps-and-show-from-it-when-precise.patch) | MPEG-PS はバイト位置の比率でシークしていたため、開始時刻やビットレートの変動に応じて位置がずれました。約 0.8 Mb/s 以上で FFmpeg が書くように pack header の間隔が数秒あると、長さが分からず、クロックが停止し、シーク後に同じ時刻を繰り返しました。 | 基準トラックのタイムスタンプで探索します。精密シークと開始時刻指定では 1〜2 秒前からデコードして指定時刻から表示します。長さは任意のパケットから取得し、pack header の間は 50 バイト単位の mux rate でクロックを進め、PES パケット間も維持します。報告時刻は映像表示に使うクロックの時刻です。 |
| [`vlc/0062`](third-party/libvlc/patches/vlc/0062-ps-find-a-precise-seek-s-lead-by-the-video-s-own-timestamps.patch) | 精密シークの助走位置を基準トラックの時刻で探すと、LPCM 音声に対して映像の割合が小さい静止画 VOB などでは映像パケットが音声より 1 秒進んでおり、キーピクチャーを過ぎていました。 | 基準トラックから調べた長さの範囲で、最初の映像トラックのタイムスタンプから助走位置を探します。他のシークは変更しません。 |
| [`vlc/0014`](third-party/libvlc/patches/vlc/0014-ts-take-times-from-the-first-picture-and-decode-a-precise-seek-from-its-key-picture.patch) | MPEG-TS の時刻を最初の PCR から数えると、muxer の先行分だけ最初の画像より早く始まり、シークではデコードに必要なキーピクチャーを過ぎていました。 | 最初に提示する画像または音声を時刻の起点にします。精密シークはクロック基準で 2 秒前に移動し、そこからデコードして指定時刻から表示します。長さは提示タイムスタンプ間で求め、短いストリームでも負にならないようにします。 |
| [`vlc/0063`](third-party/libvlc/patches/vlc/0063-ts-count-the-pcrs-the-probe-reads-as-received.patch) | MPEG-TS の開始位置探索で読んだ PCR が受信済みとして数えられず、Blu-ray のように LPCM が大半を占めると、次の PCR より先に音声ブロックが来てクロックを失い、以降の時刻シークがすべてバイト位置にフォールバックしました。 | 通常の demux と同じく、探索で読んだ PCR も受信として数えます。 |
| [`vlc/0064`](third-party/libvlc/patches/vlc/0064-ts-search-a-time-by-the-clock-alone-when-the-program-has-one.patch) | MPEG-TS の時刻シークで、クロック参照のないパケットの DTS をクロックと解釈していました。DTS は mux delay だけ先行するため、2〜2.5 秒付近の精密シークが失敗してバイト位置に戻りました。 | クロック参照を持つプログラムでは、その参照だけで探索します。 |
| [`vlc/0016`](third-party/libvlc/patches/vlc/0016-input-process-the-start-time-seek-before-demuxing-pictures.patch) | 開始時刻へのシークが最初の demux 後に処理され、ソフトウェア decoder が冒頭を先に表示する場合がありました。 | 長さが分かり、音声か映像が選択されている場合、最初の demux 前に保留中の制御を処理します。最初の demux で時刻やトラックを調べる MPEG-PS や Ogg の探索は維持します。 |
| [`vlc/0027`](third-party/libvlc/patches/vlc/0027-decoder-drop-pictures-of-a-timeline-a-pending-flush-discards.patch) | シークは decoder にフラッシュ予定を設定するだけのため、実行前に MediaCodec の出力スレッドが古い画像をキューに入れ、シーク後の最初の画像と解釈されました。 | owner lock の下でフラッシュ状態を確認し、フラッシュ中の画像を破棄します。 |
| [`vlc/0028`](third-party/libvlc/patches/vlc/0028-decoder-cancel-a-pending-drain-when-flushing.patch) | 末尾の drain 要求がシーク後も残り、新しいタイムラインの途中で drain して MediaCodec が出力しなくなりました。また実行中の drain がシーク後の新しい要求に応答し、Monkey's Audio のように数パケットで読める入力で末尾近くにシークすると、新位置をデコードする前に完了と判断して約 1.5 秒後に終了しました。 | フラッシュで保留中の drain を取り消し、開始後にフラッシュされていない場合だけその要求に応答します。取り残された要求には次のタイムラインの末尾で応答します。 |
| [`vlc/0029`](third-party/libvlc/patches/vlc/0029-input-demux-on-demand-while-a-paused-picture-s-decoder-starves.patch) | 一時停止中はバッファーが満ちると demux が止まりますが、FFmpeg の frame threads、並べ替え、MediaCodec の遅延により、停止中のシークの画像を得るには追加データが必要なことがありました。 | decoder が要求された画像をまだ出しておらず入力を消費済みなら（ES_OUT_GET_AWAITED_PICTURE）、停止中も 5 ms ごとに 1 ブロックを demux します。 |
| [`vlc/0038`](third-party/libvlc/patches/vlc/0038-es_out-take-no-clock-reference-as-late-while-the-input-is-paused.patch) | 0029 のオンデマンド demux で到達したクロック参照を、クロック停止中も実時間と比較していました。トラック再選択後の MediaCodec MPEG-4 Part 2 などで処理に時間がかかると遅延と誤認し、クロックのリセットとフラッシュで必要なキーピクチャーと停止画像を失いました。 | コマ送り時と同様、一時停止中のクロック参照を遅延と判定しません。 |
| [`vlc/0031`](third-party/libvlc/patches/vlc/0031-decoder-owe-a-seek-s-picture-to-a-decoder-paused-before-it-showed.patch) | シーク直後に一時停止すると、シークで必要な画像の要求が解除され、古い位置が画面に残りました。 | シークでフラッシュされた映像 decoder は、先に一時停止されても 1 枚表示するまで画像要求を保持します。 |
| [`vlc/0092`](third-party/libvlc/patches/vlc/0092-vout-take-a-picture-without-a-date-with-a-flush-of-all-the-pictures.patch) | 映像出力のフラッシュで時刻のない画像が残りました。末尾で一時停止した入力がクロック参照なしで強制表示する画像などが、シーク後に再表示され、末尾が画面に残りました。 | 全画像のフラッシュでは時刻のない画像も取り除きます。 |
| [`vlc/0043`](third-party/libvlc/patches/vlc/0043-mp4-seek-a-fragment-s-samples-to-the-sync-sample-before-the-time.patch) | fragmented MP4 のフラグメント内シークが同期サンプルを考慮せず指定時刻のサンプルに移動し、次のフラグメントのキーピクチャーまで映像が出ませんでした。 | フラグメントの sample flags から指定時刻以前の最後の同期サンプルを見つけ、各トラックをそこへ移動します。精密シークでは指定時刻から表示します。 |
| [`vlc/0080`](third-party/libvlc/patches/vlc/0080-avformat-open-a-file-ffmpeg-cannot-seek-again-at-its-start.patch) | インデックスのない MSN webcam stream や Motion Pixels では FFmpeg が先頭から読んで時刻を探索し、失敗すると末尾に残るため、時刻指定で冒頭から再開すると終了しました。 | シーク失敗時に先頭で開き直します。先頭へのシークは成功し、他の位置へのシークでは先頭から再生を続けます。 |
| [`vlc/0136`](third-party/libvlc/patches/vlc/0136-avformat-play-a-format-FFmpeg-cannot-seek-in-from-its-start-alone.patch) | FFmpeg の Westwood VQA と THP の demuxer は、自身のシークも索引も、ファイルを探す timestamp も持ちません。FFmpeg が時刻を探してファイルを読み進め、VQA のシークは終端に、THP のシークは止まる画像や時刻から離れた画像に着地しました。 | 両形式は長さを述べない形式と同じく先頭からだけ再生します。長さを報告せず（アプリはシークバーを出しません）、先頭へのシークは FFmpeg のシークを使わずファイルを開き直し（0080）、他の位置へのシークは失敗して先頭から再生を続けます。demuxer の能力は FFmpeg の API にないため、形式を名前で挙げます。 |
| [`vlc/0093`](third-party/libvlc/patches/vlc/0093-avformat-seek-a-gxf-or-pva-file-to-the-key-picture-before-the-time.patch) | FFmpeg の GXF と PVA はキーピクチャーを考慮せず指定時刻の画像へシークしていました。PVA は時刻のある全パケットをキーとして索引に載せるため、表示が最大 1 秒遅れたり、末尾近くで何も表示しなくなったりしました。 | 指定時刻の 1、2、4…最大 16 秒前から読み、直前の最後のキーピクチャーを見つけて正確にシークします。指定時刻まではデコードだけを行います。 |
| [`vlc/0088`](third-party/libvlc/patches/vlc/0088-nsv-report-the-length-and-seek-a-time-by-the-file-header-or-to-the-start-without-one.patch) | NSV は読み取り開始位置を時刻の起点とし、時刻シークを拒否していました。再開始で先読みを失い、長さと同期フレーム位置を持つファイルヘッダーも飛ばすため、長さもシークもありませんでした。 | ヘッダーから長さと目次を読み、指定時刻以前の最後の同期フレームへ移動します。精密シークは指定時刻から表示します。ヘッダーがない入力は先頭へのシークだけを受け付け、シーク位置から時刻を付け直します。 |
| [`vlc/0111`](third-party/libvlc/patches/vlc/0111-avformat-correct-a-musepack-sv8-stream-s-length-and-seek-index-from-its-header.patch) | FFmpeg の Musepack SV8 は長さをパケット単位（44.1 kHz で 1.67 秒）で計算し、最大 1 パケット短く報告していました。シーク表の 2 番目の項目も 1 パケット早く索引付けされ、最初の 2 項目の間へのシークでは全音声が目標以前と判定されて末尾まで捨てられました。 | ストリームヘッダーのサンプル数とレートから長さを計算します。シーク前に表からシーク間隔を読み、誤配置された項目を正しいパケット時刻に登録します。 |
| [`vlc/0132`](third-party/libvlc/patches/vlc/0132-packetizer-take-a-block-s-discontinuity-once.patch) | discontinuity の印を持つブロック（シーク後の最初のブロック）は、packetizer を reset してから読みます。画像が完成するとブロックの残りが次の画像のために再び渡されますが、印が残っていたため、そのブロックが完成させた画像の後に 2 度目の reset が起きていました。小さいキー画像と次の画像の先頭が同じブロックにある位置へシークすると（黒い画像で始まるプログラムストリームの 2 kB のパケット）、H.264 と HEVC の packetizer はキー画像で得た復帰を失って次のキー画像まで全画像を捨て、MPEG video の packetizer は次の画像の先頭を捨てました。アプリはウィンドウが付くたびにシークするため、H.264 のプログラムストリームは最初の GOP の画像を表示しませんでした。 | reset した時点で印を外します。packetizer の共通処理（H.264、HEVC、MPEG video、MPEG-4 Visual、VC-1、AC-3、DTS、FLAC、MLP、MPEG audio、MPEG-4 audio）への変更です。 |
| [`vlc/0133`](third-party/libvlc/patches/vlc/0133-h264-date-the-picture-that-follows-the-first-one-after-a-discontinuity.patch) | 他の画像が始まったブロックの中で始まる画像は自身の時刻を持たず、H.264 の packetizer は前の画像から時刻を補います（復号時刻はフレームの長さ分、表示時刻は picture order count から）。discontinuity の後の最初の画像は、補う元の時刻を進めずに消していたため、0132 と同じ位置へのシークで、キー画像の次の参照画像が時刻なしで decoder に渡り、その画像が捨てられました。 | reset の後に設定された時刻はその画像自身のものとして、他の画像と同じく進めます。 |

<a id="times-and-lengths"></a>

## 時刻と長さ

| パッチ | 問題 | 変更内容 |
|---|---|---|
| [`vlc/0104`](third-party/libvlc/patches/vlc/0104-input-say-the-time-while-waiting-for-the-clock.patch) | 入力は demux 後だけ時刻を報告し、demuxer の最後の参照までクロックを待っていました。1 ページに 1 秒分書く FFmpeg の Ogg では時刻が 1 秒刻みとなり、最大 1.5 秒止まりました。 | 入力の待機中も demux 中と同じ頻度でクロックの再生位置を報告します。入力停止時には即座に待機を終え、次の読み取り時刻まで報告し続けないようにします。 |
| [`vlc/0078`](third-party/libvlc/patches/vlc/0078-es_out-report-the-time-the-clock-plays-past-the-demuxer-s-end.patch) | 入力時刻が demuxer の位置を超えず、数秒分の音声を 1 ブロックで渡す MPEG-4 ALS の単一 access unit や raw Shorten では再生中も冒頭のままでした。 | demuxer が末尾へ到達した後は、次のシークまで、長さを上限にクロックに合わせて時刻を進めます。 |
| [`vlc/0015`](third-party/libvlc/patches/vlc/0015-avformat-include-AMR-storage-framing-in-the-duration-estimate.patch) | raw AMR の長さをビットレートから推定する際、各チャンネルで 20 ms ごとに付く 1 バイトのフレーミングを数えず、長く見積もっていました。 | チャンネル当たり 400 bit/s のフレーミングを含めます。タイムスタンプやコンテナーの長さがある場合は引き続きそちらを優先します。 |
| [`vlc/0067`](third-party/libvlc/patches/vlc/0067-avformat-take-the-length-a-file-states-where-ffmpeg-reads-none.patch) | AMV の amvh、FLIC のフレーム数、OMA の lossless ATRAC の TLEN など、FFmpeg が読まない方法で記録された長さを取得できず、位置を表示できませんでした。 | FFmpeg が長さを返さない場合、ファイルに記録された長さを使います。 |
| [`vlc/0079`](third-party/libvlc/patches/vlc/0079-avformat-time-the-first-packet-of-a-format-that-carries-no-time.patch) | raw Shorten のように時刻を持たない形式では FFmpeg がどのパケットにも時刻を付けず、最初の時刻を待つ音声 decoder がファイル全体を捨てていました。 | トラックの最初のパケットに demuxer の現在時刻を付け、クロックもその位置に設定します。 |
| [`vlc/0083`](third-party/libvlc/patches/vlc/0083-avformat-hold-the-clock-until-each-track-played-has-had-a-time.patch) | 届いたパケットのトラックだけでクロックが進み、映像より数秒後に音声が配置される RealMedia では映像でクロックが始まって音声が遅れ、再生できませんでした。 | 選択中の音声・映像トラックに時刻付きパケットがまだない間、最大 10 秒クロックを保留します。 |
| [`vlc/0072`](third-party/libvlc/patches/vlc/0072-avi-keep-the-length-to-the-tick-not-the-second.patch) | AVI の長さを整数秒で保持し、最大 1 秒短くなり、1 秒未満のファイルでは長さがなくなりました。 | インデックスから得た長さを tick 精度で保持します。 |
| [`vlc/0076`](third-party/libvlc/patches/vlc/0076-avi-take-the-length-of-a-file-without-an-index-from-its-header.patch) | インデックスのない AVI に長さがありませんでした。 | ヘッダーのフレーム数とフレーム間隔から長さを得ます。シークは引き続きバイト位置の比率で行います。 |
| [`vlc/0084`](third-party/libvlc/patches/vlc/0084-avi-count-the-chunks-of-sound-of-variable-size-that-states-no-block.patch) | ブロックサイズ指定のない可変サイズの AVI 音声をバイト数で数え、On2 AVC は 1 チャンク約 100 秒として扱われて無音になりました。 | 読み取りとシークの両方でチャンク数を使います。 |
| [`vlc/0073`](third-party/libvlc/patches/vlc/0073-caf-report-the-time-and-the-length-to-the-tick-not-the-second.patch) | CAF はサンプル数をレートで割ってから時間単位へ変換していたため、時刻と長さが整数秒になりました。 | 時間単位へ拡大してから割り算を行います。 |
| [`vlc/0077`](third-party/libvlc/patches/vlc/0077-mp4-read-the-packets-of-a-qdm2-track-one-by-one.patch) | QDM2 のチャンク全体を最初のパケットの時刻を持つ 1 ブロックとして読み、全データが 1 チャンクのファイルでは再生中も時刻が冒頭に留まりました。 | FFmpeg と同様に sound description のバイト数を使い、1 パケットずつ読みます。 |
| [`vlc/0109`](third-party/libvlc/patches/vlc/0109-nuv-count-the-pictures-after-the-last-key-picture-into-the-length.patch) | NuppelVideo（MythTV）の長さがシーク表の最後のキーピクチャーまでとなり、その後の画像を含めませんでした。1 秒ごとにキーがある 6 秒のファイルが 5 秒と報告されました。 | 最後のキーピクチャーから末尾までフレームを読み、画像数を長さへ加えます。 |
| [`vlc/0044`](third-party/libvlc/patches/vlc/0044-voc-take-times-length-and-seeks-across-all-the-blocks.patch) | VOC の時刻、長さ、シークが現在のブロック内だけを対象とし、FFmpeg が 1 パケットずつブロックを書く場合に正しく扱えませんでした。 | 全ブロックを対象とし、時刻は最初のブロック、長さは最後の末尾（未到達なら推定）、シークはブロック単位で処理します。繰り返しブロックがあるファイルはシーク不可にします。 |
| [`vlc/0040`](third-party/libvlc/patches/vlc/0040-tta-take-the-length-from-the-samples-the-header-counts.patch) | TTA の最終フレームの残りサンプルも 1 フレーム分として数え、6 秒のファイルを 6.27 秒と報告していました。 | ヘッダーのサンプル数とサンプルレートから長さを求めます。 |
| [`vlc/0105`](third-party/libvlc/patches/vlc/0105-tta-say-the-time-of-the-frame-it-last-sent.patch) | TTA demuxer が最後に送ったフレームの次の時刻を報告し、約 1 秒進んでいました。 | 最後に送ったフレーム、またはシークで移動したフレームの時刻を報告します。 |
| [`vlc/0106`](third-party/libvlc/patches/vlc/0106-tta-seek-to-a-time-by-its-frames.patch) | TTA の時刻シークがバイト数の比率で移動し、そのバイトを含むフレーム先頭から再生するため、最大約 1 秒早く始まりました。 | 指定時刻を含むフレームへ移動し、精密シークでは指定時刻から再生します。各フレームに長さを与え、目標を含むフレームをプリロールとして捨てずに目標位置で切ります。 |
| [`vlc/0119`](third-party/libvlc/patches/vlc/0119-mpegvideo-time-an-untimed-reference-picture-by-its-group-s-timed-picture.patch) | PS は各パケット内で最初に始まる画像だけに時刻を付けます。DVD のほぼ静止した場面などで 1 pack に複数の画像が入ると、後の P ピクチャーに提示時刻がなく、decoder が DTS で早く表示しました。B ピクチャーが 2 枚なら 2 フレーム早くなり、インターレースの 25 fps MPEG-2 VOB で毎秒約 6 枚を遅延として捨てました。TS や Matroska の同じ映像では各画像に時刻があり発生しませんでした。 | GOP 内の時刻付きフレームの時刻と temporal reference（表示順の番号）を保持し、時刻のない参照画像を補完します。GOP の最初の参照画像が前の GOP の末尾 pack に入る場合もあるため、GOP ヘッダーで前の時刻と最後の参照番号を引き継ぎ、その GOP の時刻付き画像で更新します。フラッシュ後は初期化します。一定間隔でフレームを数えられない low-delay、フィールド画像、繰り返しフィールドのある GOP は従来どおりです。 |

<a id="elementary-video-streams"></a>

## 映像エレメンタリーストリーム

| パッチ | 問題 | 変更内容 |
|---|---|---|
| [`vlc/0053`](third-party/libvlc/patches/vlc/0053-mjpeg-time-a-file-of-pictures-at-a-rate-and-report-its-time.patch) | レート指定のない Motion JPEG ストリームを画像到着時刻で再生し、ファイルから読むと読み取り速度で進み、時刻も報告されませんでした。 | 他のエレメンタリーストリームを es-fps で扱うのと同様に、シーク可能な入力を毎秒 25 枚で時刻付けし、その時刻を報告します。 |
| [`vlc/0054`](third-party/libvlc/patches/vlc/0054-demux-find-an-elementary-video-stream-s-start-by-its-time.patch) | コンテナーのない H.264、HEVC、MPEG video、Motion JPEG、Dirac は時刻シークをすべて拒否し、時刻で先頭へ戻しても decoder だけがフラッシュされ読み取り位置が戻りませんでした。 | 開始位置を時刻で見つけ、そこから画像の時刻を付け直します。 |
| [`vlc/0055`](third-party/libvlc/patches/vlc/0055-demux-report-the-time-of-an-h.264-hevc-or-mpeg-video-stream.patch) | コンテナーのない H.264、HEVC、MPEG video が時刻を報告しませんでした。 | 位置シークで起点の時刻を失っている場合を除き、次の画像の時刻を報告します。 |
| [`vlc/0056`](third-party/libvlc/patches/vlc/0056-h26x-time-only-the-start-of-the-stream-for-the-packetizer.patch) | 各ブロックに開始時刻を付けると H.264 packetizer がそれを画像の DTS と解釈し、オフセットが蓄積しました。小さい画像のストリームが半分の速度で進んでから飛びました。 | 開始後の最初のブロックだけに時刻を付け、以降の画像は packetizer がフレームレートから時刻付けします。 |
| [`vlc/0082`](third-party/libvlc/patches/vlc/0082-vc1-report-the-time-of-a-vc-1-stream-and-find-its-start-by-its-time.patch) | コンテナーのない VC-1 ストリームは時刻を報告せず、時刻シークも拒否しました。 | 他のエレメンタリーストリームと同様に次の画像の時刻を報告し、開始位置を時刻で見つけます。 |
| [`vlc/0094`](third-party/libvlc/patches/vlc/0094-dirac-date-a-stream-timed-by-its-decoding-alone.patch) | raw Dirac demuxer は最初の画像の DTS だけを付け、packetizer がそこから画像に時刻を与えないため、Dirac や VC-2 のエレメンタリーストリームが表示されませんでした。 | 欠けた DTS を最後の DTS から補い、シーケンス末尾を越えて保持します。PTS のない画像は並べ替えモデルの遅延を加えて表示し、low delay 構文（VC-2）ではデコード時刻に表示します。 |
| [`vlc/0095`](third-party/libvlc/patches/vlc/0095-dirac-packetize-a-raw-stream-again-from-its-start-after-a-seek.patch) | シーク後、ストリームの起点時刻が不連続を表すシーケンス終了に付いてしまい、以降の画像に時刻が付きませんでした。 | demuxer を開くときと同様に、シーク後に packetizer を作り直します。 |
| [`vlc/0096`](third-party/libvlc/patches/vlc/0096-dirac-keep-the-timestamps-of-the-pictures-an-end-of-sequence-flushes.patch) | シーケンス終了時に、時刻付き画像も最後の出力単位の時刻に置き換えていました。FFmpeg の VC-2 encoder は各画像の後にシーケンスを終了するため、時刻が付かなくなりました。 | フラッシュ対象で時刻がない単位だけに前のタイムスタンプを使います。 |
| [`vlc/0127`](third-party/libvlc/patches/vlc/0127-vc1-time-a-picture-by-the-fields-it-shows.patch) | VC-1 のエレメンタリーストリームを 1 画像 1 フレームで数え、1 枚おきにフィールドを繰り返す 3:2 pulldown の映画が約 20% 速く再生されました（4.1 秒分のフィールドが 3.3 秒）。 | シーケンスヘッダーの pulldown フラグと画像ごとの繰り返しフィールド（RFF）・フレーム（RPTFRM）を読み、表示する長さに合わせて画像の時間を決めます。 |


<a id="video-size-and-pixel-aspect"></a>

## 映像寸法とピクセルアスペクト比

| パッチ | 問題 | 変更内容 |
|---|---|---|
| [`vlc/0007`](third-party/libvlc/patches/vlc/0007-mediacodec-retain-visible-dimensions-without-crop.patch) | 一部の MediaCodec decoder が crop 情報なしでマクロブロック境界にそろえた寸法を報告し、パディング込みで画面に合わせるため黒帯が出ました。 | 入力や SPS の表示寸法を符号化寸法と分けて保持し、crop がないか不正な場合に使います。有効な crop は引き続き優先します。 |
| [`libvlcjni/0004`](third-party/libvlc/patches/libvlcjni/0004-expose-current-input-track-formats.patch) | MPEG-PS と MPEG-TS は decoder が寸法とピクセルアスペクト比を知る前にトラックを識別するため、解析済みメタデータにゼロ寸法が残りました。 | IMedia.getTracksSnapshot() で、デコード中に得た寸法、ピクセルアスペクト比、向きを含む入力の現在のフォーマットを読み取ります。 |
| [`vlc/0008`](third-party/libvlc/patches/vlc/0008-mkv-preserve-display-aspect-ratio.patch) | Matroska の表示比率（DisplayUnit=3）を逆向きに適用し、384×288 を 16:9 で表示する画像のピクセル比が 3:4 になりました。 | 表示比率を画像比率で割り、4:3 のピクセル比を得ます。 |
| [`vlc/0009`](third-party/libvlc/patches/vlc/0009-mediacodec-read-undeclared-pixel-aspect.patch) | MediaCodec の出力フォーマットにピクセルアスペクト比がなく、コンテナーに比率がない H.264 や HEVC が正方形ピクセルのままでした。 | 現在の SPS からピクセルアスペクト比を読みます。コンテナーの比率がある場合は引き続きそちらを優先します。 |
| [`vlc/0011`](third-party/libvlc/patches/vlc/0011-mediacodec-request-the-opaque-output-after-parsing-the-codec-configuration.patch) | ウィンドウは最初の画像より前の出力開始時に比率を知りますが、MediaCodec が SPS 読み取り前に opaque 出力を 1:1 で開いていました。 | codec configuration を解析してから opaque 出力を要求します。 |
| [`vlc/0012`](third-party/libvlc/patches/vlc/0012-mediacodec-open-the-mpeg-2-opaque-output-with-the-aspect-of-its-first-sequence-header.patch) | 比率が最初のシーケンスヘッダーで初めて分かる MPEG-1/2 でも同じ問題がありました。 | 最初のブロックのシーケンスヘッダーを解析してから opaque 出力を要求し、MediaCodec を開始します。 |
| [`vlc/0048`](third-party/libvlc/patches/vlc/0048-mediacodec-take-an-mpeg-4-part-2-aspect-from-its-video-object-layer.patch) | MediaCodec の出力フォーマットに sample aspect がなく、OGM 内などコンテナーに比率がない MPEG-4 Part 2 が正方形に表示されました。 | extra data の video object layer header から比率を読みます。なければ出力と codec の開始を最初のブロックまで遅らせ、そこで読み取ります。 |
| [`vlc/0051`](third-party/libvlc/patches/vlc/0051-avformat-take-the-codec-s-pixel-aspect-when-the-stream-states-none.patch) | FFmpeg demuxer が映像のピクセルアスペクト比を stream からしか読まず、未設定の GXF や MXF では MediaCodec が正方形で開くか、ウィンドウが形を決めた後に開いていました。 | stream の比率を使い、なければ codec parameters の比率を使います。 |
| [`vlc/0059`](third-party/libvlc/patches/vlc/0059-ogg-leave-the-header-packets-of-an-oggds-stream-out-of-its-data.patch) | OggDS の最初のページへ戻るシークで comment packet がデータとして decoder に渡り、最初のブロックの video object layer から比率を取る MediaCodec MPEG-4 Part 2 出力が比率を得られませんでした。 | header とマークされたパケットは、従来どおりクロックを更新した後で破棄します。 |
| [`vlc/0060`](third-party/libvlc/patches/vlc/0060-ogg-state-a-theora-picture-s-size-and-aspect-from-its-identification-header.patch) | Ogg demuxer が decoder に記述されるまで Theora トラックの寸法を設定せず、ウィンドウ作成後に decoder を作る 0057 では、トラックからウィンドウの形を決められませんでした。 | theora decoder と同じく identification header からフレーム、その中の画像、ピクセルアスペクト比を記述します。 |
| [`vlc/0112`](third-party/libvlc/patches/vlc/0112-nsv-have-the-h.264-packetizer-read-the-stream-s-parameter-sets.patch) | NSV が H.264 トラックを packetize 済みとして渡し、parameter sets を packetizer が読まなかったため、自分で解析しない MediaCodec の adaptive playback が SPS の比率を取得できず、アナモルフィック映像が正方形になりました。 | MPEG-TS と同様に未 packetize として渡し、H.264 packetizer が SPS の比率を読みます。 |

<a id="video-output"></a>

## 映像出力

| パッチ | 問題 | 変更内容 |
|---|---|---|
| [`libvlcjni/0003`](third-party/libvlc/patches/libvlcjni/0003-cancel-surface-initialization-on-view-release.patch) | ビューの切り離しがテクスチャー初期化と競合して未作成の Surface を使う場合があり、接続されなかったコールバック looper も生き残りました。 | テクスチャーと Surface を一緒に公開し、切り離しで初期化を取り消します。モニターを保持せずにコールバックスレッドの終了を待ちます。 |
| [`vlc/0019`](third-party/libvlc/patches/vlc/0019-android-display-crop-public-software-output-to-visible-pixels.patch) | Android の公開ソフトウェアウィンドウには crop API がなく、dav1d の AV1 バッファーなどのアラインメント用パディングが静止画の黒い余白になりました。 | 表示領域をウィンドウのフォーマットとして交渉し、converter が切り抜きます。decoder の格納領域、アラインメント、プールの所有権を維持します。 |
| [`vlc/0025`](third-party/libvlc/patches/vlc/0025-opengl-convert-full-range-yuv-without-expanding-its-range-again.patch) | OpenGL の YUV→RGB 行列は limited range を拡張するため、MJPEG など full range の入力は二重に拡張され、黒と白がつぶれました。 | full range の入力には full range の行列を選びます。 |
| [`vlc/0114`](third-party/libvlc/patches/vlc/0114-vout-select-the-subtitles-of-a-picture-forced-on-screen-at-the-time-it-is-shown.patch) | 字幕を画像の時刻で選んでいました。再生開始やシーク後の最初の画像はバッファリング中に強制表示され、後続画像より最大 0.6 秒先の時刻を持つため、表示前に到着した現在位置の字幕を終了済みとして削除し、キュー内へのシークで次の字幕まで表示されない場合がありました。 | 再生中に強制表示する画像の字幕は実際の表示時刻で選びます。一時停止中は従来どおり停止時刻で選びます。 |
| [`vlc/0128`](third-party/libvlc/patches/vlc/0128-opengl-place-the-picture-in-an-Android-window-s-buffer-at-the-size-it-has-when-drawn.patch) | Android の TextureView は直ちにバッファーをリサイズしますが、OpenGL 出力の配置更新は 25〜40 ms 遅れ、その間に描いた画像が picture-in-picture 移行時に隅だけ拡大されたり、隅に小さく表示されたりしました。 | eglQuerySurface で取得した手元のバッファー寸法に配置を合わせて毎回描画します。出力側でバッファーをリサイズするだけでは、driver が次のバッファーを取得する時点を選ぶため解決しません。 |


<a id="hardware-decoders"></a>

## ハードウェア decoder

| パッチ | 問題 | 変更内容 |
|---|---|---|
| [`vlc/0026`](third-party/libvlc/patches/vlc/0026-mediacodec-hand-a-vp9-profile-the-codec-does-not-state-to-the-next-decoder.patch) | MediaCodec が MIME type だけで VP9 decoder を選び、10/12 ビット非対応の codec が Profile 2 の入力を消費してから失敗するため、次の decoder は後のキーフレームから開始しました。 | 最初のフレームの profile を読み、codec が対応を明示しなければ入力をキューに入れる前に次の decoder（FFmpeg）へ渡します。 |
| [`vlc/0030`](third-party/libvlc/patches/vlc/0030-mediacodec-hand-mpeg-4-part-2-with-b-vops-to-the-next-decoder.patch) | ハードウェア MPEG-4 Part 2 decoder が Advanced Simple profile を報告しながら B-VOP の代わりに前の参照画像を出すことがあり、検出する通知もありませんでした。 | video object layer で B-VOP を許可する入力（low_delay が未設定）は、キューへ入力する前に FFmpeg へ渡します。 |
| [`vlc/0046`](third-party/libvlc/patches/vlc/0046-mediacodec-hand-h.263-version-2-pictures-to-the-next-decoder-when-the-codec-states-no-profile-of-it.patch) | Baseline だけを報告する H.263 codec が version 2 の拡張 picture type を受け付けて入力消費後に失敗し、引き継いだ decoder が次の intra picture までの画像を失いました。 | 最初の picture header を読み、version 2 で対応 profile が報告されていなければ入力をキューに入れる前に次の decoder へ渡します。 |
| [`vlc/0047`](third-party/libvlc/patches/vlc/0047-mediacodec-start-a-deferred-mpeg-2-output-at-a-sequence-header.patch) | 遅延開始する MPEG-2 出力が最初のブロックで開き、FFmpeg の GXF シーク後など GOP の途中から始まると sequence header がないため、正方形で開き、未デコードの画像を参照しました。 | extra data の sequence header があれば比率を使い、なければ sequence header か intra picture のあるブロックまで開始を待ちます。 |
| [`vlc/0052`](third-party/libvlc/patches/vlc/0052-mediacodec-begin-mpeg-2-after-a-flush-at-a-sequence-header-or-intra-picture-too.patch) | 即時に開いた MPEG-2 出力やフラッシュ後のストリームが次のブロックから再開し、FFmpeg の GXF のようにキー画像が分からない demuxer では MediaCodec が参照画像を持たず、一時停止中のシークで画像を待ち続けました。 | 開始とフラッシュ後には、picture header から判定した intra picture または sequence header を待ちます。intra picture なしで更新する入力は 128 ブロック後に開始します。 |
| [`vlc/0137`](third-party/libvlc/patches/vlc/0137-mpeg4video-leave-stuffing-out-of-the-pictures.patch) | 固定レートの encoder が画像の後に書く stuffing（開始コード `0x1C3` と `0xFF` の並び）を、MPEG-4 Visual の packetizer が次の画像の先頭として溜めたため、プログラムストリームのように packetizer が画像を組み立て直す入力では、全画像が stuffing で始まるブロックとして decoder に渡りました。MediaTek の MediaCodec の MPEG-4 decoder（`c2.mtk.mpeg4.decoder`）は最初のそうしたブロックから画像を出さなくなり、固定レートの MPEG-4 Visual のプログラムストリームが最初の数枚の後に止まりました（先頭からの再生、シーク、静止画）。 | stuffing は packetizer が見つけた時点で捨てます。AVI や MP4 は画像とその後の stuffing を 1 つのパケットで運び、従来どおり stuffing はブロックの末尾にあります。 |

<a id="ffmpegs-decoders"></a>

## FFmpeg の decoder

| パッチ | 問題 | 変更内容 |
|---|---|---|
| [`vlc/0049`](third-party/libvlc/patches/vlc/0049-avcodec-state-key-pictures-to-ffmpeg-s-video-decoders.patch) | FFmpeg の映像 decoder にキーピクチャー情報を渡さず、Flash Screen Video 2 の参照画像が必要なフレームが失敗し、PNG、ZeroCodec、PDV が全パケットを前画像との差分として扱いました。 | intra picture のフラグがあるブロックを key packet として渡します。 |
| [`vlc/0091`](third-party/libvlc/patches/vlc/0091-avcodec-lend-pictures-read-only-so-that-a-decoder-draws-over-a-copy.patch) | 前画像に上書きして次のフレームを作る decoder（Flash Screen Video、QuickTime RLE、RPZA、Microsoft RLE と Video 1、FLIC など）が表示待ちの貸出画像を更新し、先のフレームやシーク後の先の時刻を表示しました。 | 貸出画像の plane を読み取り専用にし、decoder が前画像を新しい画像へコピーしてから描くようにします。 |
| [`vlc/0068`](third-party/libvlc/patches/vlc/0068-avcodec-render-into-a-decoder-s-own-buffer-when-it-asks-for-more-than-the-picture.patch) | 画像より広いフレームを要求する decoder（周囲に余白を持つ Dirac など）を assertion だけで検査し、貸出画像の plane の外へ書き込んで色や形が崩れました。 | その decoder には専用バッファーを渡し、画像をコピーして取り出します。 |
| [`vlc/0069`](third-party/libvlc/patches/vlc/0069-avcodec-copy-a-frame-out-of-a-lent-picture-whose-planes-the-decoder-moved.patch) | plane のポインターを画像内で移動して返す decoder（行を逆順で読む AMV など）の画像を貸したときのまま表示し、上下が逆になりました。 | フレームをコピーして取り出し、decoder が返した方向に行を読みます。 |
| [`vlc/0081`](third-party/libvlc/patches/vlc/0081-avcodec-show-planar-gbr-with-alpha-as-planar-gbr.patch) | Lagarith、Ut Video、HuffYUV などが RGB+alpha をデコードする planar GBR+alpha に対応する chroma がなく、全画像が捨てられました。 | alpha を除いた planar GBR として扱い、decoder 自身のバッファーへデコードしてコピーします。 |
| [`vlc/0113`](third-party/libvlc/patches/vlc/0113-avcodec-decode-mimic-without-direct-rendering.patch) | MSN webcam の MIMIC は過去 16 枚を参照して保持するため、出力の画像へ直接デコードすると数枚でプールを使い切り、クロックだけが進みながら空き画像を待ち続けました。 | 直接描画から除外済みの codec と同様、decoder 自身のバッファーへデコードして出力へコピーします。 |
| [`vlc/0066`](third-party/libvlc/patches/vlc/0066-avcodec-decode-lossless-jpeg-with-the-decoder-of-motion-jpeg.patch) | libavcodec は lossless JPEG を Motion JPEG decoder で扱いますが、VLC が要求した codec id では見つからず、映像が表示されませんでした。 | lossless JPEG の decoder がなければ Motion JPEG decoder を要求します。 |
| [`vlc/0065`](third-party/libvlc/patches/vlc/0065-mp4-read-the-color-table-a-palettized-quicktime-picture-describes.patch) | palettized QuickTime の sample description にある色テーブルを読まず、Apple Graphics（SMC）が全画像を黒く描き、後続の pasp、fiel box も失われました。 | libavcodec の形式でトラックの palette に色テーブルを読み、その後の box も読みます。 |
| [`vlc/0135`](third-party/libvlc/patches/vlc/0135-avcodec-show-each-palettized-picture-through-its-own-palette.patch) | palette 化した画像（PAL8）を PAL8 のまま出力したため、出力の形式を決めた最初の画像の palette を出力の変換器が持ち続け、palette が変わっても出力を作り直しませんでした。画像ごとに palette を変える decoder の後の画像が最初の palette の色で描かれ、場面ごとに palette を持つ VQA の動画は崩れた緑の画像になりました。colour chunk で palette を変える FLIC も同様でした。 | palette 化した画像を RGB32 で出力し、各画像を復号した palette で decoder から写します（direct rendering は palette 化した画像を受けません）。demuxer が述べる palette は従来どおり最初のパケットと一緒に decoder に渡します。 |
| [`vlc/0087`](third-party/libvlc/patches/vlc/0087-avparser-packetize-avs-video-split-across-blocks.patch) | FFmpeg parser の packetizer が VP9 専用で、PS パケットが画像の途中で切れる AVS video が decoder に完全な画像として渡らず、表示されませんでした。 | AVS video にも対応し、複数ブロックにまたがるフレームをまとめ、開始ブロックの時刻を使います。 |
| [`vlc/0107`](third-party/libvlc/patches/vlc/0107-avcodec-time-a-picture-of-an-intra-only-codec-by-its-decoding.patch) | composition offset のない MP4 は DTS だけを持ち、packetizer のない codec は PTS なしで libavcodec に届きます。パケットを自分で扱う APV は画像にも時刻を付けず、すべて捨てられました。 | intra-only codec はデコード順に表示するため、PTS のないブロックには DTS を PTS として渡します。 |
| [`vlc/0129`](third-party/libvlc/patches/vlc/0129-avcodec-keep-the-pictures-frame-threads-hold-from-coming-out-too-late.patch) | frame threads はスレッド数−1 個の後続パケットまで画像を保持します。低フレームレートの VP3/NSV や MIMIC では出力が遅れて表示できず、音声だけが進み画像が止まりました。 | VP3、Theora、MIMIC では frame threads を使いません。レートが分かる入力では保持が 0.25 秒以内になる数に制限します。 |


<a id="ogg-with-libvlcs-own-demuxer"></a>

## libVLC 自身の demuxer を使う Ogg

このビルドでは FFmpeg が Ogg を開き Vorbis をデコードするため、libVLC 自身の Ogg demuxer はリンクしません。
この節のパッチと[映像寸法とピクセルアスペクト比](#video-size-and-pixel-aspect)の 0059・0060 は、
3.7.6-37 までのビルドと同じく libvorbis とその demuxer を使う `ogg-libvlc` バリアント用に保持しています。
0032 は Speex decoder の変更で、FFmpeg demuxer を使うこのビルドでも有効です。

| パッチ | 問題 | 変更内容 |
|---|---|---|
| [`vlc/0032`](third-party/libvlc/patches/vlc/0032-speex-flush-only-bits-that-were-initialized.patch) | 最初の Speex パケットより前にシークすると、未初期化の bits をリセットしてクラッシュしました。 | header で初期化済みの場合だけ、フラッシュ時に bits をリセットします。 |
| [`vlc/0033`](third-party/libvlc/patches/vlc/0033-ogg-keep-the-logical-streams-at-the-physical-end-so-that-a-seek-back-finds-them.patch) | 末尾で chained group を探すため論理ストリームを削除し、その後のシークがすべて失敗しました。 | 物理的な末尾でも論理ストリームを保持し、シーク時に終了状態をリセットします。 |
| [`vlc/0035`](third-party/libvlc/patches/vlc/0035-oggseek-search-pages-for-a-time-before-estimating-from-the-bitrate.patch) | 単一の音声ストリームを nominal bitrate の推定でシークし、可変ビットレートの Vorbis、Speex、FLAC では大きく外れ、小さいファイルでは末尾を越えました。 | 先に granule position でページを探索し、探索できない場合だけビットレート推定を使います。 |
| [`vlc/0036`](third-party/libvlc/patches/vlc/0036-ogg-time-flac-packets-by-their-frame-headers.patch) | Ogg はページの最後のパケットにだけ時刻を付けますが、FLAC は 1 ページに約 1 秒入り、パケット時刻が補間されないため、シーク後の音声がクロックに 1 秒遅れて捨てられました。 | Vorbis、Opus、Speex と同様に、FLAC の frame header のサンプル数から各パケットに時刻を付けます。 |
| [`vlc/0037`](third-party/libvlc/patches/vlc/0037-oggseek-read-to-the-end-when-probing-the-length.patch) | 長さ探索で読み取った範囲の途中から始まる最後のページを最後まで読まず、以前のページの時刻を使っていました。 | 毎回末尾まで読み、最大の granule position を使います。 |
| [`vlc/0116`](third-party/libvlc/patches/vlc/0116-ogg-hold-the-clock-until-each-stream-played-has-had-a-time.patch) | demuxer が時刻のあるストリームだけから最小 PCR を選びました。Theora+Vorbis では最初の音声ページが 1 秒分の映像の後に来るため、映像だけでクロックが進み、音声の前にバッファリングが終わって音声が約 0.5 秒遅れました。音声出力がクロックを戻し、開始約 1.5 秒で時刻が 0.4 秒戻り、画像が 0.6 秒止まりました。 | 選択中の音声・映像のいずれかにまだ時刻がない間、他が 10 秒以内なら PCR をタイムラインの先頭に保持します。FFmpeg demuxer に対する 0083 と同じ方針です。 |

<a id="midi-and-game-music"></a>

## MIDI とゲーム音楽

MIDI は VLC の `fluidsynth` モジュール経由で FluidLite とアプリ指定の SoundFont を使って再生します。
ゲーム機の音楽は VLC の `gme` モジュール経由で Game_Music_Emu を使って再生します。

| パッチ | 問題 | 変更内容 |
|---|---|---|
| [`vlc/0121`](third-party/libvlc/patches/vlc/0121-smf-keep-the-state-of-the-channels-and-the-notes-sounding-across-a-seek.patch) | MIDI のシークで synthesizer の program が初期化され、全チャンネルがピアノになり、controller、pitch bend、sustain が失われ、指定位置をまたぐ音も鳴りませんでした。 | シークごとに先頭から読み、到達時にチャンネル状態のメッセージを送ります。その時点で鳴っている音も、打楽器チャンネルを除いて再開します。 |
| [`vlc/0122`](third-party/libvlc/patches/vlc/0122-fluidsynth-stop-every-voice-and-reset-every-channel-on-a-flush.patch) | フラッシュで音を release しても sustain pedal 下の音は鳴り続け、シーク前の音と reverb が新しい位置に重なりました。 | MIDI system reset と同様に synthesizer をリセットし、全 voice を止め、各チャンネルと effect を初期化します。 |
| [`vlc/0123`](third-party/libvlc/patches/vlc/0123-gme-play-every-track-of-a-file-in-turn-from-its-start-only.patch) | Game_Music_Emu は最初のトラックを無音になるまで再生し、ループ曲では終わりませんでした。他のトラックもファイル全体の長さを持つタイトルとして報告されました。 | ファイルを 1 項目として全トラックを順に再生します。終了は同ライブラリーの player と同様に、指定長、導入部＋2 ループ、または 150 秒の後でフェードします。長さは報告せず、先頭へのシークだけを受け付けます。サイズのない gzip 圧縮 VGZ は最大 16 MiB まで読みます。 |
| [`vlc/0124`](third-party/libvlc/patches/vlc/0124-contrib-fluidlite-count-the-references-to-a-sample-atomically.patch) | FluidLite のサンプル使用 voice 数が通常の加減算だったため、別スレッドの synthesizer が SoundFont を共有すると計数を失い、正の値が残って SoundFont を削除できませんでした。 | 参照数をアトミックに管理します。 |
| [`vlc/0125`](third-party/libvlc/patches/vlc/0125-fluidsynth-share-one-SoundFont-among-the-synthesizers-of-the-process.patch) | 各 synthesizer が SoundFont を個別にロードし、GeneralUser GS では約 90 MB を使いました。再生中に次のトラックを準備すると二重に保持・ロードし、SH-02M の SF3 ではロードに 3 秒かかりました。 | パスで指定した SoundFont をプロセスごとに一度だけ読み、同じパスの synthesizer 間で共有し、最後の利用者が解放したときに削除します。 |
| [`vlc/0126`](third-party/libvlc/patches/vlc/0126-contrib-fluidlite-take-the-loop-of-a-compressed-sample-as-a-SoundFont-2-sample-s.patch) | 圧縮サンプル（SF3）のデコード後、末尾の直後で終わるループや先頭から始まるループを不正と判断して移動し、SF3 化した GeneralUser GS の 920 ループ中 50 個（grand piano を含む）が変わりました。 | デコードしたサンプルのループを、非圧縮サンプルと同じ基準で検査します。 |
| [`vlc/0130`](third-party/libvlc/patches/vlc/0130-smf-land-a-seek-at-the-time-asked-for-not-at-the-next-event.patch) | MIDI シークで指定時刻までのイベントを読んだ後、次のイベントの時刻から tick を数えたため、イベントの間隔が広いファイルでは 1 秒以上先に着地し、その間の音を飛ばしました。 | 次のイベントが指定時刻より後なら、指定時刻から tick を数えます。 |

<a id="the-log"></a>

## ログ

| パッチ | 問題 | 変更 |
|---|---|---|
| [`libvlcjni/0007`](third-party/libvlc/patches/libvlcjni/0007-write-an-instance-s-log-to-a-file-the-application-names.patch) | libVLC は選んだものと行ったことをログでしか伝えず、ログは logcat に出ます。libVLC の debug レベルほど多く書くプロセスの行は、読み手が遅れると logd が読み飛ばすため、ログを読み戻すアプリの試験が行を取りこぼしました。 | `LibVLC.setLogFile(path, level)` で、インスタンスのログを logcat の代わりにファイルへ追記させます。各行は logcat の `threadtime` 形式（`VLC` タグ）で、1 回の書き込みで書きます。インスタンスの解放前に callback を外します。アプリの試験が使い、アプリ自身は使いません。 |
