# README

## commands for test

``` bash
source venv/bin/activate
uvicorn main:app --reload
curl http://127.0.0.1:8000/
```

### POST command

``` bash
# curl -X POST -H "Content-Type: application/json" -d '{"youtube_url": "https://www.youtube.com/watch?v=EvE5cYNXufY"}' http://localhost:8000/transcribe_youtube
curl -X POST -H "Content-Type: application/json" -d '{"video_id": "EvE5cYNXufY"}' http://localhost:8000/transcribe_youtube
curl -X POST -H "Content-Type: application/json" -d '{"video_id": "mmzoO7e4j-8"}' http://localhost:8000/extract_ingredients
```
