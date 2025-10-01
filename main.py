import os
from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from flask_cors import CORS

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
            # Try to get English transcript first
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        except:
            # Fallback: get any available transcript
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            # Get the first available transcript (could be auto-generated or manual)
            transcript = next(iter(transcript_list)).fetch()

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

# This block is needed for Railway when using "python main.py" as start command
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
