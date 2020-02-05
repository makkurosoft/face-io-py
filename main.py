import os
import cv2
import json
import time
import argparse
import requests
import numpy as np
import face_recognition as fr
from collections import Counter

def urljoin(scheme, netloc, path):
    return f'{scheme}://{netloc}/{path}'

WEBAPI_SCHEME = 'https'
WEBAPI_NETLOC = 'umaru.work'
WEBAPI_IN_PATH = 'face-io-web/attendance/in'
WEBAPI_OUT_PATH = 'face-io-web/attendance/out'
WEBAPI_IN_URL = urljoin(WEBAPI_SCHEME, WEBAPI_NETLOC, WEBAPI_IN_PATH)
WEBAPI_OUT_URL = urljoin(WEBAPI_SCHEME, WEBAPI_NETLOC, WEBAPI_OUT_PATH)

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

# ラベルのログ
log_labels = []
last_sent_label = -1

while True:
    # キャプチャデバイスからフレームを取得
    ret, frame = capture.read()
    # 縮小
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    # BGR -> RGB
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    # sent
    sent = False
    rectangle_colors = {False: (0, 0, 255), True: (0, 255, 0)}

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
            if log_labels and log_labels[-1] != label:
                log_labels = []
                sent = False
            log_labels.append(label)
            
            if label == last_sent_label:
                sent = True

            if label != last_sent_label and len(log_labels) == 3:
                unixtime = time.time()
                data = {'label': label, 'date': unixtime}
                requests.post(WEBAPI_IN_URL, data=data)
                last_sent_label = label
                sent = True

    # Display the results
    for (top, right, bottom, left) in face_locations:
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), rectangle_colors[sent], 4)

    # カメラ画像の表示
    cv2.imshow('Camera', frame)

    # Escキーで終了
    key = cv2.waitKey(50)
    if key == 27:
        break

# キャプチャをリリースして、ウィンドウをすべて閉じる
capture.release()
cv2.destroyAllWindows()