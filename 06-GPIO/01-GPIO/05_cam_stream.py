#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Jetson Nano USB/CSI Camera Web Streamer
---------------------------------------
這個程式會建立一個簡單的網頁伺服器，讓您透過瀏覽器即時觀看 Webcam 畫面。
適用於 SSH 連線 (無螢幕) 的環境。

使用方法:
1. 安裝 Flask: sudo pip3 install flask opencv-python
2. 執行程式: python3 05_cam_stream.py
3. 在電腦瀏覽器開啟: http://192.168.55.1:5000
"""

import cv2
from flask import Flask, Response

app = Flask(__name__)

# 設定攝影機來源
# 如果是 USB Webcam，通常是 0 或 1
# 如果是 CSI Camera (Raspberry Pi Camera v2)，建議使用 GStreamer pipeline (下面註解掉的那行)
CAMERA_INDEX = 0

def gstreamer_pipeline(
    sensor_id=0,
    capture_width=1280,
    capture_height=720,
    display_width=640,
    display_height=360,
    framerate=30,
    flip_method=0,
):
    return (
        "nvarguscamerasrc sensor-id=%d ! "
        "video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            sensor_id,
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )

def generate_frames():
    # 嘗試開啟相機
    # 優先嘗試一般 USB 模式
    cap = cv2.VideoCapture(CAMERA_INDEX)
    
    # 如果打不開，嘗試 GStreamer 模式 (針對 CSI 相機)
    if not cap.isOpened():
        print("USB Camera 沒反應，嘗試使用 CSI Camera GStreamer Pipeline...")
        cap = cv2.VideoCapture(gstreamer_pipeline(), cv2.CAP_GSTREAMER)

    if not cap.isOpened():
        print("錯誤: 無法開啟攝影機")
        return

    # 設定解析度 (USB Webcam 支援的話)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("相機已啟動，開始串流...")

    while True:
        success, frame = cap.read()
        if not success:
            break
        
        # 將影像編碼為 JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        # 串流格式 (Multipart MJPEG)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

@app.route('/')
def index():
    # 回傳串流影像
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # 啟動 Web Server，Port 5000
    # host='0.0.0.0' 代表允許外部連線
    app.run(host='0.0.0.0', port=5000, debug=True)
