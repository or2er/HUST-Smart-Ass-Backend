from server import sio

def update_progress(task_id, data):
    sio.emit("get-prog", (task_id, data))