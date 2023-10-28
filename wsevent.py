from flask import request
from flask_socketio import emit

try:
    from __main__ import sio
except ImportError:
    from server import sio

def update_progress(id, val):
    sio.emit("get-prog", (id, val))