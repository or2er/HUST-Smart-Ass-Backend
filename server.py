import json
import os
import pickle
from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from pydantic import BaseModel,conlist
from typing import List,Optional
import pandas as pd
from core.recommend_model import recommend,output_recommended_recipes

app = Flask(__name__)
CORS(app)

sio = SocketIO(app, cors_allowed_origins='*')

from time import sleep
from threading import Thread
from queue import Queue, Empty
from functions.pdf_processing import pdfUpload
from functions.yt_processing import ytUpload

from functions.document import DocumentModel
from functions.task import Task
from functions.note import Note
from modules.chat import chat

tasks = Queue()
docu_cache: dict[str, DocumentModel] = {}
msg_cache: dict[str, list()] = {}
task_cache = []
note_cache = []

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
    docu_cache[data["id"]] = DocumentModel(data)
    def execute():
        docu_cache[data["id"]].process()
    
    tasks.put(execute)
    return {
        "id": data["id"],
        "text": data["text"]
    }



# ================
def load_task():
    global task_cache
    if task_cache == []:
        if os.path.exists(f"data/task.pkl"):
            with open(f"data/task.pkl", 'rb') as fr:
                try:
                    while True:
                       task_cache.append(pickle.load(fr))
                except EOFError:
                    pass
        else:
            # dirty hax
            with open(f"data/task.pkl", 'wb') as fp:
                pickle.dump(Task(), fp)

@app.post('/task/create')
def task_create():
    task = Task(request.form)
    global task_cache
    load_task()
    task_cache.append(task)
    with open(f"data/task.pkl", 'ab') as fp:
        pickle.dump(task, fp)
    return {
        "msg": "ok"
    }

@app.post('/task/read')
def task_read():
    load_task()
    return {
        "msg": "ok",
        "data": json.loads(json.dumps(task_cache, default=vars))
    }



# ================
def load_note():
    global note_cache
    if note_cache == []:
        if os.path.exists(f"data/note.pkl"):
            with open(f"data/note.pkl", 'rb') as fr:
                try:
                    while True:
                       note_cache.append(pickle.load(fr))
                except EOFError:
                    pass
        else:
            # dirty hax
            with open(f"data/note.pkl", 'wb') as fp:
                pickle.dump(Note(), fp)

@app.post('/note/create')
def note_create():
    note = Note(request.form)
    global note_cache
    load_note()
    note_cache.append(note)
    print(note.details)
    with open(f"data/note.pkl", 'ab') as fp:
        pickle.dump(note, fp)
    return {
        "msg": "ok"
    }

@app.post('/note/read')
def note_read():
    load_note()
    return {
        "msg": "ok",
        "data": json.loads(json.dumps(note_cache, default=vars))
    }



dataset=pd.read_csv('Data/dataset.csv',compression='gzip')
class params(BaseModel):
    n_neighbors:int=5
    return_distance:bool=False

class PredictionIn(BaseModel):
    nutrition_input:conlist(float, min_length=9, max_length=9)
    ingredients:list[str]=[]
    params:Optional[params]


class Recipe(BaseModel):
    Name:str
    CookTime:str
    PrepTime:str
    TotalTime:str
    RecipeIngredientParts:list[str]
    Calories:float
    FatContent:float
    SaturatedFatContent:float
    CholesterolContent:float
    SodiumContent:float
    CarbohydrateContent:float
    FiberContent:float
    SugarContent:float
    ProteinContent:float
    RecipeInstructions:list[str]

class PredictionOut(BaseModel):
    output: Optional[List[Recipe]] = None

from functions.recommendation import Generator,Person

@app.post("/predict")
def update_item():
    prediction_input = request.json
    print(prediction_input)
    recommendation_dataframe=recommend(dataset,prediction_input["nutrition_input"])
    output=output_recommended_recipes(recommendation_dataframe)
    if output is None:
        return {"output":None}
    else:
        return {"output":output}

@app.post('/recommend')
def get_recommend():
    input_form = request.form
    meals_calories_perc = {'breakfast': 0.35, 'lunch': 0.40, 'dinner': 0.25}
    person = Person(age=float(input_form['age']),
                    height=float(input_form['height']),
                    weight=float(input_form['weight']),
                    gender=input_form['gender'],
                    activity=input_form['activity'],
                    meals_calories_perc=meals_calories_perc,
                    weight_loss=int(input_form['weight_loss']))
    output = person.generate_recommendations()
    if output is None:
        return {"output":None}
    else:
        return {"output":output}


# ================
def load_docu(id):
    global docu_cache   
    if docu_cache.get(id) == None:
        docu_cache[id] = DocumentModel({"id": id, "type": "query"})
        docu_cache[id].process()

@sio.on("post-prog")
def check_progress(task_id):
    load_docu(task_id)
    emit("get-prog", (task_id, docu_cache[task_id].processing_status))



# ================
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
    with open(f"data/chat_{id}.pkl", 'ab') as fp:
        pickle.dump([sender, msg], fp)

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



# ================
@sio.on("connect")
def onConnect():
    emit("get-join", "connected")
    logInfo("connected, test data sent")

@sio.on("disconnect")
def onDisconnect():
    logInfo("disconnected")

if __name__ == '__main__':
    sio.run(app, port=8000, debug=True)

