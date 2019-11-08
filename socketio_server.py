#!/usr/bin/env python
#coding: utf-8

import os
import cv2
import base64
import timeit
from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit
from engineio.payload import Payload

Payload.max_decode_packets = 1000

app = Flask(__name__)
app.secret_key = "secret"
socketio = SocketIO(app, async_mode='gevent', ping_timeout=30, ping_interval=15)

cap = cv2.VideoCapture(0)
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 15]

user_no = 1
def getImgSrt():
    #start = timeit.default_timer()
    ret, frame = cap.read()
    if ret:
        #cv2.imshow('video', frame)
        ret, buf = cv2.imencode('.jpg', frame, encode_param)
        if ret:
            jpg_as_text = base64.b64encode(buf)
            #cv2.waitKey(1)
            #stop = timeit.default_timer()
            #print(stop - start)
            return jpg_as_text


@app.before_request
def before_request():
    global user_no
    if 'session' in session and 'user-id' in session:
        pass
    else:
        session['session'] = os.urandom(24)
        session['username'] = 'user'+str(user_no)
        user_no += 1

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect', namespace='/mynamespace')
def connect():
    emit("response", {'data': 'Connected', 'username': session['username']})

@socketio.on('disconnect', namespace='/mynamespace')
def disconnect():
    session.clear()
    print "Disconnected"

@socketio.on("request", namespace='/mynamespace')
def request(message):
    emit("response", {'data': message['data'], 'username': session['username']}, broadcast=True)

@socketio.on("imgRequest", namespace='/mynamespace')
def imgRequest(message):
    imgString = getImgSrt()
    emit("imgResponse", {'data': 'data:image/jpg;base64, '+imgString}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000)