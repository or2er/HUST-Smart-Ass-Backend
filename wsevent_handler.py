from flask import request
from flask_socketio import emit
try:
    from __main__ import sio
except ImportError:
    from server import sio

def logInfo(msg):
    print(f"[sid={request.sid}]: {msg}.")

def updateProgress(taskName, data):
    emit("get-prog", taskName, data)

@sio.on("connect")
def onConnect():
    emit("get-join", "connected")
    logInfo("connected, test data sent")

@sio.on("disconnect")
def onDisconnect():
    logInfo("disconnected")


