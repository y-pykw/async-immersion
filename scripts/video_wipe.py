
import cv2
import numpy as np
from tqdm import tqdm
import os

def create_line_wipe_from_video(input_path, output_path):
    """
    入力動画から、時間進行に連動したラインワイプ効果の動画を生成する。

    時刻tにおけるスキャンラインの位置を`pos`とすると、入力動画のフレーム`pos`の
    縦一列の色が、出力動画の左側から`pos`までを塗りつぶす。

    Args:
        input_path (str): 入力動画のファイルパス。
        output_path (str): 出力する動画のファイルパス (.mp4など)。
    """
    # 1. 入力動画を読み込み、プロパティを取得
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"エラー: 動画ファイルが開けませんでした: {input_path}")
        return

    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"入力動画の情報: {w}x{h}, {fps:.2f} FPS, {total_frames} フレーム")

    if total_frames == 0:
        print("エラー: 動画にフレームが含まれていません。")
        cap.release()
        return

    # 2. 動画書き出しの設定
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(output_path, fourcc, fps, (w, h))
    if not writer.isOpened():
        print(f"エラー: 動画ファイルを開けませんでした: {output_path}")
        cap.release()
        return

    # 3. フレームごとに処理を実行
    print("動画を生成中...")
    for frame_idx in tqdm(range(total_frames), desc="フレーム処理"):
        ret, frame = cap.read()
        if not ret:
            print("警告: フレームの読み込みに失敗しました。処理を中断します。")
            break

        # --- ここからが効果の核心部分 ---
        
        # 現在のフレーム番号(frame_idx)を、画面の横座標(x)にマッピングする
        # 動画の進行度 (0.0 ~ 1.0) に応じて、スキャンラインの位置(t)を 0 ~ w-1 に決定
        # 動画の進行度を計算
        if total_frames > 1:
            progress = frame_idx / (total_frames - 1)
        else:
            progress = 1.0

        # ★★ 変更点 1: スキャンラインの位置 t を逆にする ★★
        # progressが0.0 -> tはw-1, progressが1.0 -> tは0
        t = w - 1 - int(progress * (w - 1))
        # 稀な浮動小数点誤差を考慮して範囲内に収める
        t = np.clip(t, 0, w - 1)

        output_frame = frame.copy()

        # ★★ 変更点 2: スキャンラインより右側を塗りつぶす ★★
        if t < w - 1:
            # スキャンライン(x=t)の色を取得
            color_line = frame[:, t:t+1]
            # tより右側 (x > t) を塗りつぶす
            output_frame[:, t+1:w] = color_line

        # 4. 生成したフレームを動画に書き込む
        writer.write(output_frame)

    # 5. リソースを解放
    cap.release()
    writer.release()
    print(f"動画の生成が完了しました: {output_path}")

