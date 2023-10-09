from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO
from time import sleep
from threading import Thread
from queue import Queue, Empty
from functions.pdf_processing import pdfUpload
from functions.yt_processing import ytUpload
from functions.model_processing import ModelProcessing

app = Flask(__name__)
sio = SocketIO(app, cors_allowed_origins='*')

CORS(app)
import wsevent_handler

tasks = Queue()

def loop():
    while True:
        try:
            task = tasks.get_nowait()
            task()
        except Empty:
            pass

        sleep(1)

Thread(target=loop, daemon=True).start()

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

    # # debugging..
    # return {
    #     "id": data["id"],
    #     "text": data["text"]
    # }
    docu = ModelProcessing(data)
    def execute():
        docu.process()
    
    tasks.put(execute)
    return {
        "id": docu.id,
        "text": docu.text
    }

@app.post('/query')
def onQuery():
    cnt = request.form
    docu = ModelProcessing({"id": cnt["id"]})
    docu.process()
    return docu.query(cnt["query"])

if __name__ == '__main__':
    sio.run(app, port=8000, debug=True)

