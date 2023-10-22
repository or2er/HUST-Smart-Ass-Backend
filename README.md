# SoICT Hackathon 2023 - Backend module
1000USD will be in our hands.

## Initialization

### Install dependencies
```
pip install -r requirements.txt
```

### Run server
```
python server.py
```
Default port is `8000`.

## API

### Interact with chatbot

- import method `chat` from `modules/chat.py`

- Usage
```
output: str = chat("Hello") # long time to execute
```

- Run file `demo.py` to run a demo in terminal

### Making models based on documents
#### POST `/upload/pdf`
- Request (form-data)
```
    "file": <file>
```
- Output (JSON)
```
{
    "id": <model_id>,
    "text": <pdf text>
}
```

#### POST `/upload/yt`
- Request (form-data)
```
    "id": <youtube video id (e.g: 8j20gSdBPy4)>
```
- Output (JSON)
```
{
    "id": <model id>,
    "text": <transcript text>
}
```

### Question-related
#### Ask model question/ask chatbot
- Client event (Event name: `post-msg`)
    + Send the message to `id`.
```
<id>                # "chat": Chatbot related, <document_id>: Document related
<msg>               # User messages
```

- Server event (Event name: `get-msg`)
    + Represent the message.
```
<id>                # "chat": Chatbot related, <document_id>: Document related
<sender>            # 0: AI | 1: User
<response_msg>      # AI's response
```

#### Load previous messages
- Client event (Event name: `post-past-msg`)
    + Request previous messages send in `id`.
    + This event will respond with `num` response `get-msg`.
```
<id>                # "chat": Chatbot related, <document_id>: Document related
<num>               # number of messages need to fetch
```

### Progress tracking
- Client event (Event name: `post-prog`)
    + Request completion rate of a document.
```
<id>                # <document_id>: Document related
```

- Server event (Event name: `get-prog`)
    + Respond with the completion rate of a document.
    + This event will trigger when the rate changes, or when the client requested with `post-prog`.
```
<id>                # <document_id>: Document related
<completion_rate>   # Represented as a float in range [0,1].
```

### Other event
- Server event (Event name: `get-join`)
    + Notify if you have successfully connect to the server.
```
connected
```