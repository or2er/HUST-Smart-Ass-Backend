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
### Making AI models
- POST `/upload/pdf`
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

- POST `/upload/yt`
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

### Ask AI model question
- POST `/question`
- Request (form-data)
```
    "id": <model-id>,
    "query": <question>
```
- Response (raw)
```
<OpenAI response>
```

## Websocket
Done the base but nothing has been done :D