from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp
import tempfile
import os
from google.cloud import storage
from google.cloud.speech import RecognitionConfig, RecognitionAudio
from google.cloud.speech_v1 import SpeechClient
from dotenv import load_dotenv

app = FastAPI()

class TranscribeYoutubeRequest(BaseModel):
    youtube_url: str

# 環境変数から Cloud Storage のバケット名を取得
load_dotenv('.env.local')
BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME")
if not BUCKET_NAME:
    raise Exception("GCS_BUCKET_NAME environment variable is not set")

@app.post("/transcribe_youtube")
async def transcribe_youtube(request: TranscribeYoutubeRequest):
    # 1. 一時ディレクトリを作成して音声をダウンロード
    with tempfile.TemporaryDirectory() as tmpdir:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(tmpdir, '%(id)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'postprocessor_args': ['-ac', '1'],
            'quiet': True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(request.youtube_url, download=True)
                video_id = info.get("id")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to download audio: {str(e)}")

        # 2. ダウンロードされた WAV ファイルのパスを取得
        audio_file = os.path.join(tmpdir, f"{video_id}.wav")
        if not os.path.exists(audio_file):
            raise HTTPException(status_code=500, detail="Audio file not found after download.")

        # 3. Google Cloud Storage に音声ファイルをアップロード
        try:
            storage_client = storage.Client()
            bucket = storage_client.bucket(BUCKET_NAME)
            destination_blob_name = f"transcriptions/{video_id}.wav"
            blob = bucket.blob(destination_blob_name)
            blob.upload_from_filename(audio_file)
            gcs_uri = f"gs://{BUCKET_NAME}/{destination_blob_name}"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload to Cloud Storage: {str(e)}")

        # 4. Cloud Speech-to-Text API を利用して文字起こし
        try:
            speech_client = SpeechClient()
            audio = RecognitionAudio(uri=gcs_uri)
            config = RecognitionConfig(
                # encoding=AudioEncoding.LINEAR16,
                # sample_rate_hertz=44100,  # 音声ファイルのサンプルレートに合わせる
                language_code="en-US",
                enable_automatic_punctuation=True,
            )
            operation = speech_client.long_running_recognize(config=config, audio=audio)
            response = operation.result(timeout=600)
            transcript = " ".join([result.alternatives[0].transcript for result in response.results])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Speech-to-Text error: {str(e)}")

        return {"transcript": transcript}