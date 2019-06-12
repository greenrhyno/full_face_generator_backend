#!/usr/bin/env python
from flask import Flask, render_template, Response
import numpy as np
import cv2
import base64
from flask_socketio import SocketIO, emit, send
from time import sleep
from threading import Thread

THREAD = Thread()

APP = Flask(__name__)
SIO = SocketIO(APP)

CAM = cv2.VideoCapture(0)

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
            success, frame = CAM.read()
            _, jpeg = cv2.imencode('.jpg', frame)
            encoded_img = "data:image/jpg;base64," + str(base64.b64encode(jpeg.tobytes()).decode())
            SIO.emit('video_frame', {'frame': encoded_img}, namespace='/socket-test')
            sleep(self.delay)
            
    def run(self):
        """Default run method"""
        self.get_data()


@APP.route('/')
def index():
    return render_template('index.html')

def gen(camera):
    while camera.isOpened():
        success, frame = camera.read()
        ret, jpeg = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
    CAM.release()


@APP.route('/video_feed')
def video_feed():
    return Response(gen(CAM),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@SIO.on('connect', namespace='/socket-test')
def connect_socket():
    """Handle socket connection"""
    global THREAD

    # Start thread
    if not THREAD.isAlive():
        THREAD = VideoStreamThread()
        THREAD.start()


@SIO.on('client_connect', namespace='/socket-test')
def signal_client_connection(data):
    print('\nClient CONNECTED: ' + str(data))
    send('Backend -- socket connected.')


if __name__ == '__main__':
    SIO.run(APP)
    # app.run(host='0.0.0.0', debug=True)
