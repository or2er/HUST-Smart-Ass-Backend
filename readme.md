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
### Post PDF file
- POST `/pdf/upload`
- Request (form-data)
```
{
    "file": <file>
}
```
- Output (JSON)
```
{
    "id": <base64 id>,
    "text": <pdf text>
}
```

### Ask PDF question
- POST `/pdf/query`
- Request (JSON)
```
{
    "id": <base64 id>,
    "query": <question>
}
```
- Response (raw)
```
<OpenAI response>
```

## Websocket
Done the base but nothing has been done :D