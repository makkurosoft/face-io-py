import os
import cv2
import json
import numpy as np
import argparse
import face_recognition as fr

# 引数の処理
parser = argparse.ArgumentParser()
parser.add_argument('-od', '--output-dir', required=True, help='出力ディレクトリ')
parser.add_argument('-ol', '--output-label', required=True, help='出力ラベル')
args = parser.parse_args()

# 保存する特徴量
save_datas = []

# 出力ディレクトリが存在しなければ、作成
os.makedirs(args.output_dir, exist_ok=True)

# JSONファイルのパス
datas_path = os.path.join(args.output_dir, 'datas.json')

# JSONファイルが存在する場合は結合
if os.path.exists(datas_path):
    with open(datas_path) as fp:
        save_datas = json.loads(fp.read())

# キャプチャデバイス
capture = cv2.VideoCapture(0)
# 最初の何枚かは破棄
save_count = -3
    
while True:
    # キャプチャデバイスからフレームを取得
    ret, frame = capture.read()
    # 縮小
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    # BGR -> RGB
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # 顔検出
    face_locations = fr.face_locations(rgb_small_frame)
    face_encodings = fr.face_encodings(rgb_small_frame, face_locations)

    # 顔が検出できたら追加
    if len(face_encodings) == 1:
        if save_count >= 0:
            save_datas.append([args.output_label, face_encodings[0].tolist()])
        save_count += 1

    # カメラ画像の表示
    cv2.imshow('Camera', frame)

    # 複数枚集まったら終了
    if save_count >= 3:
        break

    # Escキーで終了
    key = cv2.waitKey(50)
    if key == 27:
        break

# キャプチャをリリースして、ウィンドウをすべて閉じる
capture.release()
cv2.destroyAllWindows()

# JSONファイルに書き出し
with open(datas_path, 'w') as fp:
    json.dump(save_datas, fp, separators=(',', ':'))