#!/usr/bin/env python
from flask import Flask, render_template, Response
import numpy as np
import cv2
import base64
from flask_socketio import SocketIO, emit, send
from time import sleep
from threading import Thread

THREAD = Thread()
DET_THREAD = Thread()

APP = Flask(__name__)
SIO = SocketIO(APP)

CAM = cv2.VideoCapture(0)

# @APP.route('/')
# def index():
#     return render_template('index.html')

# @APP.route('/video_feed')
# def video_feed():
#     return Response(gen(CAM),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')

# def gen(camera):
#     while camera.isOpened():
#         success, frame = camera.read()
#         ret, jpeg = cv2.imencode('.jpg', frame)
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
#     CAM.release()

""" Live Stream Functions and Thread"""

class VideoStreamThread(Thread):
    """Stream data on thread"""
    def __init__(self):
        self.delay = .06
        super(VideoStreamThread, self).__init__()

    def get_data(self):
        """
        Get data and emit to socket
        """
        global CAM
        while CAM.isOpened():
            _, frame = CAM.read()
            _, jpeg = cv2.imencode('.jpg', frame)
            encoded_img = "data:image/jpg;base64," + str(base64.b64encode(jpeg.tobytes()).decode())
            SIO.emit('video_frame', { 'frame': encoded_img }, namespace='/live-stream')
            sleep(self.delay)
            
    def run(self):
        """Default run method"""
        self.get_data()


@SIO.on('connect', namespace='/live-stream')
def connect_socket():
    """Handle socket connection"""
    global THREAD

    # Start thread
    if not THREAD.isAlive():
        THREAD = VideoStreamThread()
        THREAD.start()



class DetectionStreamThread(Thread):
    """Stream data on thread"""
    def __init__(self):
        self.delay = 4
        super(DetectionStreamThread, self).__init__()

    def get_data(self):
        """
        Get data and emit to socket
        """
        count = 0
        while count < 4:
            jpeg = cv2.imread('brule1.jpg')
            print(str(type(jpeg)))
            encoded_img = "data:image/jpg;base64," + str(base64.b64encode(jpeg.tobytes()).decode())
            SIO.emit('detection', {'image': encoded_img, 'name': 'Dr. Steve Brule'}, namespace='/detections')
            count += 1
            sleep(self.delay)
            
    def run(self):
        """Default run method"""
        self.get_data()

@SIO.on('connect', namespace='/detections')
def start_detection_stream():
    """Handle socket connection"""
    global DET_THREAD

    # Start thread
    if not DET_THREAD.isAlive():
        DET_THREAD = DetectionStreamThread()
        DET_THREAD.start()


if __name__ == '__main__':
    SIO.run(APP)
    # app.run(host='0.0.0.0', debug=True)
