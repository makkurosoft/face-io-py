import os
import cv2
import json
import numpy as np
import argparse
import face_recognition as fr

# 引数の処理
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input-dir', required=True, help='入力ディレクトリ')
args = parser.parse_args()

# JSONファイルのパス
datas_path = os.path.join(args.input_dir, 'datas.json')

# JSONファイルが存在しない場合、プログラムを終了
if not os.path.exists(datas_path):
    print('モデルが存在しません。')
    exit()

# モデルの読み込み
known_labels = []
known_encodings = []
with open(datas_path) as fp:
    datas = json.loads(fp.read())
    for (label, encoding) in datas:
        known_labels.append(label)
        known_encodings.append(encoding)

# キャプチャデバイス
capture = cv2.VideoCapture(0)
    
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

    # 顔が検出できたら処理
    predicted_labels = []
    for encoding in face_encodings:
        matches = fr.compare_faces(known_encodings, encoding)
        distances = fr.face_distance(known_encodings, encoding)
        best_match_index = np.argmin(distances)
        label = -1

        if matches[best_match_index]:
            label = known_labels[best_match_index]

        predicted_labels.append(label)
        

    # Display the results
    for (top, right, bottom, left), label in zip(face_locations, predicted_labels):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, str(label), (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # カメラ画像の表示
    cv2.imshow('Camera', frame)

    # Escキーで終了
    key = cv2.waitKey(50)
    if key == 27:
        break

# キャプチャをリリースして、ウィンドウをすべて閉じる
capture.release()
cv2.destroyAllWindows()