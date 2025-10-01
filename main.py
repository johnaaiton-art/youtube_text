import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/get-transcript', methods=['POST'])
def get_transcript():
    try:
        # Import here to avoid any module loading issues
        from youtube_transcript_api import YouTubeTranscriptApi
        
        data = request.get_json()
        video_id = data.get('video_id')
        
        if not video_id:
            return jsonify({"error": "Missing 'video_id' in request body"}), 400
        
        # Simple approach: just get the transcript
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Combine all text entries
        full_text = ' '.join([entry['text'] for entry in transcript_data])
        
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

@app.route('/test', methods=['GET'])
def test_import():
    """Test endpoint to check if library is working"""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        return jsonify({
            "status": "Library imported successfully",
            "methods": dir(YouTubeTranscriptApi)
        })
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
