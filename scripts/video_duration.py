import subprocess
import json
import shlex
import os # osモジュールをインポート

def get_video_info(input_path: str) -> tuple[float, bool]:
    """
    ffprobeを使って動画の長さと音声トラックの有無を取得します。

    Returns:
        (float, bool): (動画の長さ(秒), 音声トラックの有無) のタプル。
                       エラー時は (None, None)。
    """
    command = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        input_path
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        duration = float(data.get('format', {}).get('duration', 0.0))
        
        # streamsリストを調べて、codec_typeが'audio'のものが存在するかチェック
        has_audio = any(stream.get('codec_type') == 'audio' for stream in data.get('streams', []))
        
        return duration, has_audio

    except FileNotFoundError:
        print("エラー: ffprobeコマンドが見つかりません。FFmpegがインストールされ、PATHが通っているか確認してください。")
        return None, None
    except Exception as e:
        print(f"動画情報の取得中に予期せぬエラーが発生しました: {e}")
        return None, None


def change_video_duration_ffmpeg(input_path: str, output_path: str, target_duration: float):
    """
    FFmpegを直接呼び出し、音声の有無を自動判定して動画の長さを変更します。
    """
    # 1. 元の動画の長さと音声の有無を取得
    duration_info = get_video_info(input_path)
    if duration_info[0] is None:
        return # エラーメッセージはget_video_info内で表示済み
    
    original_duration, has_audio = duration_info

    if original_duration == 0:
        print("エラー: 元の動画の長さが0秒のため、処理を中止します。")
        return

    print(f"元の動画の長さ: {original_duration:.2f} 秒")
    print(f"音声トラックの有無: {'あり' if has_audio else 'なし'}")
    print(f"目標の動画の長さ: {target_duration:.2f} 秒")
    
    # 2. 速度変更の倍率を計算
    speed_factor = original_duration / target_duration
    print(f"適用する再生速度: {speed_factor:.2f} 倍")

    # 3. 音声の有無に応じてFFmpegコマンドを動的に組み立て
    command = ["ffmpeg", "-i", input_path]
    
    if has_audio:
        # --- 音声がある場合のコマンド ---
        print("音声と映像の両方の速度を変更します。")
        video_filter = f"setpts=PTS/{speed_factor}"
        
        # atempoフィルタは一度に適用できる倍率に制限があるため、安全に連結する
        audio_filters = []
        temp_speed = speed_factor
        while temp_speed > 100.0:
            audio_filters.append("atempo=100.0")
            temp_speed /= 100.0
        while temp_speed < 0.5:
            audio_filters.append("atempo=0.5")
            temp_speed /= 0.5
        audio_filters.append(f"atempo={temp_speed}")
        audio_filter = ",".join(audio_filters)
        
        command.extend([
            "-filter_complex", f"[0:v]{video_filter}[v];[0:a]{audio_filter}[a]",
            "-map", "[v]",
            "-map", "[a]"
        ])
    else:
        # --- 音声がない場合のコマンド ---
        print("映像のみの速度を変更します。")
        video_filter = f"setpts=PTS/{speed_factor}"
        command.extend([
            "-vf", video_filter  # -vf は映像フィルタを直接指定する簡単な方法
        ])

    # 共通の出力オプションを追加
    command.extend(["-y", output_path])
    
    print("\n実行するFFmpegコマンド:")
    try:
        print(shlex.join(command))
    except AttributeError:
        print(" ".join(f"'{arg}'" for arg in command))

    # 4. コマンドを実行
    print("\nFFmpegによる変換処理を開始します...")
    try:
        # stderrをリアルタイムで表示しないようにPIPEに送る
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"\n処理が完了しました！ 動画を '{output_path}' に保存しました。")
    except subprocess.CalledProcessError as e:
        print("\nFFmpegの実行中にエラーが発生しました。")
        print(f"エラー出力:\n{e.stderr}")
