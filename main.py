import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

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
            # Try to get transcript
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            full_text = ' '.join([entry['text'] for entry in transcript_list])
            
            return jsonify({
                "success": True,
                "video_id": video_id,
                "transcript": full_text,
                "length": len(full_text)
            })
            
        except TranscriptsDisabled:
            return jsonify({
                "success": False,
                "error": "Transcripts are disabled for this video"
            }), 400
            
        except NoTranscriptFound:
            return jsonify({
                "success": False,
                "error": "No transcript found for this video"
            }), 400
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "type": type(e).__name__
        }), 500

@app.route('/', methods=['GET'])
def health():
    return jsonify({"status": "YouTube Transcript Service is running!"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
