#!/usr/bin/env python
from flask import Flask, render_template, Response
import numpy as np
import cv2

app = Flask(__name__)

cap = cv2.VideoCapture(0)

@app.route('/')
def index():
    return render_template('index.html')


def gen(camera):
    while camera.isOpened():
        success, frame = camera.read()
        ret, jpeg = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
    cap.release()


@app.route('/video_feed')
def video_feed():
    return Response(gen(cap),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
