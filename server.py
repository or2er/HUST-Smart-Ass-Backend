import os
import pickle
from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit

app = Flask(__name__)
CORS(app)

sio = SocketIO(app, cors_allowed_origins='*')

from time import sleep
from threading import Thread
from queue import Queue, Empty
from functions.pdf_processing import pdfUpload
from functions.yt_processing import ytUpload
from functions.model_processing import ModelProcessing

from modules.chat import chat

tasks = Queue()
docu_cache = {}
msg_cache = {}

def loop():
    while True:
        try:
            task = tasks.get_nowait()
            print("New task!")
            task()
        except Empty:
            pass

        sleep(1)

Thread(target=loop, daemon=True).start()

def load_docu(id):
    global docu_cache
    if docu_cache.get(id) == None:
        docu_cache[id] = ModelProcessing({"id": id, "type": "query"})
        docu_cache[id].process()

def load_msg(id):
    global msg_cache
    if msg_cache.get(id) == None:
        msg_cache[id] = []
        if os.path.exists(f"data/chat_{id}.pkl"):
            with open(f"data/chat_{id}.pkl", 'rb') as fr:
                try:
                    while True:
                        msg_cache[id].append(pickle.load(fr))
                except EOFError:
                    pass
        else:
            # dirty hax
            with open(f"data/chat_{id}.pkl", 'wb') as fp:
                pickle.dump([0, "init"], fp)

def append_msg(id, sender, msg):
    global msg_cache
    load_msg(id)
    msg_cache[id].append([sender, msg])
    with open(f"data/chat_{id}.pkl", 'wb') as fp:
        pickle.dump([sender, msg], fp)

def logInfo(msg):
    print(f"[sid={request.sid}]: {msg}.")

@app.route('/')
def index():
    return "Hi THT i'm alive so pls give me Điểm rèn luyện or else i'll not function as intended pls"

@app.post('/upload/<type>')
def onUpload(type):
    if type == "pdf":
        data = pdfUpload(request)
    elif type == "yt":
        data = ytUpload(request)
    if data == None:
        return "An error occured"

    global docu_cache
    docu_cache[data["id"]] = ModelProcessing(data)
    def execute():
        docu_cache[data["id"]].process()
    
    tasks.put(execute)
    return {
        "id": data["id"],
        "text": data["text"]
    }

@sio.on("post-prog")
def check_progress(task_id):
    load_docu(task_id)
    emit("get-prog", (task_id, docu_cache[task_id].processing_status))

@sio.on("post-past-msg")
def on_load_past_msg(id, num):
    load_msg(id)
    print(len(msg_cache[id]))
    for msg in msg_cache[id][-int(num):]:
        emit("get-msg", (id, msg[0], msg[1]))

@sio.on("post-msg")
def on_msg_received(id: str, msg: str):
    append_msg(id, 1, msg)
    if id == "chat":
        res = chat(msg)
    else:
        load_docu(id)
        res = docu_cache[id].query(msg)
    append_msg(id, 0, res)
    emit("get-msg", (id, 0, res))

@sio.on("connect")
def onConnect():
    emit("get-join", "connected")
    logInfo("connected, test data sent")

@sio.on("disconnect")
def onDisconnect():
    logInfo("disconnected")

if __name__ == '__main__':
    sio.run(app, port=8000, debug=True)

