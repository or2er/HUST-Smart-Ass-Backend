import flask
from flask_cors import CORS
from flask_socketio import SocketIO

app = flask.Flask(__name__)
sio = SocketIO(app, cors_allowed_origins='*')

CORS(app)
import wsevent_handler

@app.route('/')
def index():
    return "Hi THT i'm alive so pls give me Điểm rèn luyện or else i'll not function as intended pls"

if __name__ == '__main__':
    sio.run(app, port=8000, debug=True)

