from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/get-transcript', methods=['POST'])
def get_transcript():
    try:
        data = request.get_json()
        video_id = data.get('video_id')
        
        if not video_id:
            return jsonify({"error": "Missing 'video_id' in request body"}), 400

        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        except:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = next(transcript_list._transcripts.values()).fetch()

        full_text = ' '.join([entry['text'] for entry in transcript])
        
        return jsonify({
            "success": True,
            "video_id": video_id,
            "transcript": full_text
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

@app.route('/', methods=['GET'])
def health():
    return jsonify({"status": "YouTube Transcript Service is running!"})

# Remove the if __name__ == '__main__': block
# Railway will handle running the app
