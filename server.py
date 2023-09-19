from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO
from time import sleep
from threading import Thread
from queue import Queue, Empty
from functions.pdf_processing import pdfUpload, PDFProcessing

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

@app.post('/pdf/upload')
def onPDFUpload():
    data = pdfUpload(request)
    if data == None:
        return "An error occured"
    pdf = PDFProcessing(data)
    def execute():
        pdf.process()
    
    tasks.put(execute)
    return {
        "id": pdf.id,
        "text": pdf.text
    }


@app.post('/pdf/query')
def onPDFQuery():
    cnt = request.json
    pdf = PDFProcessing({"id": cnt["id"], "text": ""})
    pdf.process()
    return pdf.query(cnt["query"])

if __name__ == '__main__':
    sio.run(app, port=8000, debug=True)

