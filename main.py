import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

import yt_dlp
import tempfile
import whisper  # or use faster-whisper if you want GPU speed

app = Flask(__name__)
CORS(app)

# Load Whisper model once (can be 'base', 'small', 'medium', 'large')
whisper_model = whisper.load_model("small")

def download_audio(video_url):
    """Download audio and return file path"""
    tmpdir = tempfile.mkdtemp()
    filepath = os.path.join(tmpdir, "audio.mp3")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": filepath,
        "quiet": True,
        "noplaylist": True,
        "extractaudio": True,
        "audioformat": "mp3",
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
    return filepath

@app.route('/get-transcript', methods=['POST'])
def get_transcript():
    try:
        data = request.get_json()
        video_id = data.get('video_id')

        if not video_id:
            return jsonify({"error": "Missing 'video_id' in request body"}), 400

        # Try YouTubeTranscriptAPI first
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            full_text = ' '.join([entry['text'] for entry in transcript_list])
            return jsonify({
                "success": True,
                "video_id": video_id,
                "method": "youtube_transcript_api",
                "transcript": full_text,
                "length": len(full_text)
            })

        except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable):
            # Fallback: use Whisper
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            audio_path = download_audio(video_url)
            result = whisper_model.transcribe(audio_path, fp16=False)
            full_text = result["text"]

            return jsonify({
                "success": True,
                "video_id": video_id,
                "method": "whisper",
                "transcript": full_text,
                "length": len(full_text)
            })

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
