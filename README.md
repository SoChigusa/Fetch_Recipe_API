# README

## commands for test

``` bash
source venv/bin/activate
gunicorn -b :3000 main:app
```

## commands for deploy

``` bash
gcloud app deploy
gcloud app browse
```

### POST command

For local tests:

``` bash
curl -X POST -H "Content-Type: application/json" -d '{"video_id": "EvE5cYNXufY"}' http://localhost:3000/api/transcribe_youtube
curl -X POST -H "Content-Type: application/json" -d '{"video_id": "mmzoO7e4j-8"}' http://localhost:3000/api/extract_ingredients
```

For production environment:

``` bash
curl -X POST -H "Content-Type: application/json" -d '{"video_id": "EvE5cYNXufY"}' https://fetch-recipe-api.uk.r.appspot.com/api/transcribe_youtube
curl -X POST -H "Content-Type: application/json" -d '{"video_id": "mmzoO7e4j-8"}' https://fetch-recipe-api.uk.r.appspot.com/api/extract_ingredients
```
