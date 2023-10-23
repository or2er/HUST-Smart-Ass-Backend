# SoICT Hackathon 2023 - Backend module
1000USD will be in our hands.

## Initialization

### Install dependencies
```
pip install -r requirements.txt
```

### Setup `.env` file, `credentials.json` file

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

### Documents
#### Make PDF models
- Request (form-data, POST `/upload/pdf`)
```
    "file": <file>          # PDF file
```
- Response (JSON)
```
{
    "id": <model_id>,       # Document ID
    "text": <pdf text>      # Scanned text 
}
```

#### Make YouTube transcript models
- Request (form-data, POST `/upload/yt`)
```
    "id": <youtube id>      # YouTube video ID (e.g: 8j20gSdBPy4)
```
- Response (JSON)
```
{
    "id": <model_id>,       # Document ID
    "text": <yt text>       # YouTube's transcript text
}
```

### Task/Note
#### Create Task
- Request (form-data, POST `/task/create`)
```
    "name": <name>          # Task's name
    "details": <details>    # Task's details
    "type": <type>          # Task's type (daily, one-time, ...)
    "time": <time>          # Task's time (seconds [0-86399], or UNIX time)
    "priority": <priority>  # Task's priority
```
- Response (JSON)
```
{
    "msg": <status>         # "ok"
}
```
#### Read Tasks
- Request (form-data, POST `/task/read`)
```
    <empty>
```
- Response (JSON)
```
{
    "msg": <status>,        # "ok"
    "data": [
        {
            "name": <name>          # Task's name
            "details": <details>    # Task's details
            "type": <type>          # Task's type (daily, one-time, ...)
            "time": <time>          # Task's time (seconds [0-86399], or UNIX time)
            "priority": <priority>  # Task's priority
        },
        {
            ...
        }
    ]
}
```

#### Create Note
- Request (form-data, POST `/note/create`)
```
    "name": <name>          # Note's name
    "details": <details>    # Note's details
    "priority": <priority>  # Note's priority
```
- Response (JSON)
```
{
    "msg": <status>         # "ok"
}
```
#### Read Notes
- Request (form-data, POST `/note/read`)
```
    <empty>
```
- Response (JSON)
```
{
    "msg": <status>,        # "ok"
    "data": [
        {
            "name": <name>          # Note's name
            "details": <details>    # Note's details
            "priority": <priority>  # Note's priority
        },
        {
            ...
        }
    ]
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