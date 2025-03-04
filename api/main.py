from fastapi import FastAPI
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
import os
from dotenv import load_dotenv
from openai import OpenAI

app = FastAPI()

class TranscribeYoutubeRequest(BaseModel):
  video_id: str

@app.post("/transcribe_youtube")
async def transcribe_youtube(request: TranscribeYoutubeRequest):
  transcript_list = YouTubeTranscriptApi.get_transcript(request.video_id)
  transcript = " ".join([t["text"] for t in transcript_list])
  return transcript

@app.post("/extract_ingredients")
async def extract_ingredients(request: TranscribeYoutubeRequest):
  
  transcript_list = YouTubeTranscriptApi.get_transcript(request.video_id)
  recipe_text = " ".join([t["text"] for t in transcript_list])

  load_dotenv('.env.local')
  OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
  if not OPENAI_API_KEY:
    raise Exception("OPENAI_API_KEY environment variable is not set")

  # ① OpenAIのAPIキーを設定
  client = OpenAI(api_key=OPENAI_API_KEY)

  # ③ ChatGPTに対してどんな役割でどう応答してほしいか、システムメッセージで指定
  system_message = {
      "role": "system",
      "content": "あなたは優秀なレシピ解析アシスタントです。ユーザーの投稿したレシピテキストから、使用されている食材とおおよその分量（または目安）を抽出し、日本語で一覧にしてください。"
  }

  # ④ ユーザーメッセージとしてレシピを入力
  user_message = {
      "role": "user",
      "content": recipe_text
  }

  # ⑤ ChatCompletion APIを呼び出し
  response = client.chat.completions.create(model="gpt-3.5-turbo",  # GPT-4にする場合は "gpt-4"
  messages=[system_message, user_message],
  temperature=0.5)

  # ⑥ 応答の取り出し
  assistant_message = response.choices[0].message.content
  return assistant_message