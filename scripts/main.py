# --- ここからコードの使用例 ---
import os
from video_duration import change_video_duration_ffmpeg
from video_wipe import create_line_wipe_from_video


if __name__ == '__main__':
    # 動画の長さを変更
    input_video = "INPUT VIDEO PATH"
    process_video = "PROCESSING VIDEO PATH"
    output_path = "OUTPUT VIDEO PATH"

    target_seconds = 15.0

    if not os.path.exists(input_video):
        print(f"テスト用の動画 '{input_video}' が見つかりません。")

    else:
        change_video_duration_ffmpeg(
            input_video,
            process_video,
            target_seconds
        )

        create_line_wipe_from_video(
            input_path=process_video,
            output_path=output_path
        )

        