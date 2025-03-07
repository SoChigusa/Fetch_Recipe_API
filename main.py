from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv('.env.local')
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)

@app.route('/_ah/health')
def health_check():
    return 'OK', 200

@app.route("/api/transcribe_youtube", methods=["POST"])
def transcribe_youtube():
    data = request.get_json()
    if not data or "video_id" not in data:
        return jsonify({"error": "video_id is required"}), 400

    video_id = data["video_id"]
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([t["text"] for t in transcript_list])
        return jsonify({"transcript": transcript})
    except Exception as e:
        return jsonify({"error": f"Transcript retrieval failed: {str(e)}"}), 500

@app.route("/api/extract_ingredients", methods=["POST"])
def extract_ingredients():
    data = request.get_json()
    if not data or "video_id" not in data:
        return jsonify({"error": "video_id is required"}), 400

    video_id = data["video_id"]
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        recipe_text = " ".join([t["text"] for t in transcript_list])
    except Exception as e:
        return jsonify({"error": f"Transcript retrieval failed: {str(e)}"}), 500

    # .env.local から環境変数を読み込む
    load_dotenv('.env.local')
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        return jsonify({"error": "OPENAI_API_KEY environment variable is not set"}), 500


    # ChatGPT へのシステム・ユーザーメッセージの定義
    system_message = {
        "role": "system",
        "content": "You are a recipe analysis assistant. When given a recipe text, extract all the ingredients and their corresponding quantities. Your output must be in English and strictly follow the JSON format below:\n"
        "["
        "    {"
        "        \"ingredient\": <ingredient name>,"
        "        \"quantity\": <quantity>"
        "    },"
        "..."
        "]"
        "\n\n"
        "Return only the JSON list; do not include any additional commentary or text."
    }
    user_message = {
        "role": "user",
        "content": recipe_text
    }

    try:
        response = client.chat.completions.create(model="gpt-3.5-turbo",
        messages=[system_message, user_message],
        temperature=0.5)
        assistant_message = response.choices[0].message.content
        return jsonify({"ingredients": assistant_message})
    except Exception as e:
        return jsonify({"error": f"OpenAI API call failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)