from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import json
import uuid
from datetime import datetime
from dotenv import load_dotenv
import openai
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
import ffmpeg
import tempfile
import shutil

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Enable CORS
CORS(app)

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Create uploads directory
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_video_id(url):
    """Extract video ID from YouTube URL"""
    try:
        yt = YouTube(url)
        return yt.video_id
    except Exception as e:
        print(f"Error extracting video ID: {e}")
        return None


def download_youtube_video(url, output_path):
    """Download YouTube video to local file"""
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        
        if not stream:
            raise Exception("No suitable video stream found")
        
        # Download to the specified path
        stream.download(output_path=output_path, filename=f"{yt.video_id}.mp4")
        
        video_path = os.path.join(output_path, f"{yt.video_id}.mp4")
        return video_path, yt.title
        
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None, None


def get_transcript(video_id, language='en'):
    """Get transcript for YouTube video"""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        return transcript
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None


def analyze_transcript_with_ai(transcript, user_prompt):
    """Use OpenAI to analyze transcript and find highlights based on user prompt"""
    try:
        # Convert transcript to text with timestamps
        transcript_text = ""
        for entry in transcript:
            start_time = entry['start']
            text = entry['text']
            transcript_text += f"[{start_time:.2f}s] {text}\n"
        
        # Create AI prompt
        ai_prompt = f"""
        Analyze the following video transcript and identify moments that match this user request: "{user_prompt}"
        
        Return a JSON array of highlights, where each highlight contains:
        - start_time: timestamp in seconds where the highlight begins
        - end_time: timestamp in seconds where the highlight ends (should be 5-15 seconds long)
        - description: brief description of what happens in this highlight
        - relevance_score: number from 1-10 indicating how well this matches the user's request
        
        Focus on moments that directly relate to the user's request. Each highlight should be a meaningful, self-contained moment.
        
        Transcript:
        {transcript_text}
        
        Return only valid JSON, no additional text.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert video editor who identifies the most relevant moments in video content based on user requests."},
                {"role": "user", "content": ai_prompt}
            ],
            temperature=0.3
        )
        
        highlights = json.loads(response.choices[0].message.content)
        return highlights
        
    except Exception as e:
        print(f"Error analyzing transcript: {e}")
        return []


def create_highlight_video(video_path, highlights, output_path):
    """Create highlight video from the original video and highlights"""
    try:
        if not highlights:
            return None
        
        # Create temporary directory for clips
        temp_dir = tempfile.mkdtemp()
        clip_files = []
        
        # Extract each highlight as a separate clip
        for i, highlight in enumerate(highlights):
            start_time = highlight['start_time']
            end_time = highlight['end_time']
            duration = end_time - start_time
            
            clip_filename = f"clip_{i}.mp4"
            clip_path = os.path.join(temp_dir, clip_filename)
            
            # Extract clip using FFmpeg
            stream = ffmpeg.input(video_path, ss=start_time, t=duration)
            stream = ffmpeg.output(stream, clip_path, acodec='aac', vcodec='libx264')
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            clip_files.append(clip_path)
        
        # Create file list for concatenation
        file_list_path = os.path.join(temp_dir, 'file_list.txt')
        with open(file_list_path, 'w') as f:
            for clip_file in clip_files:
                f.write(f"file '{clip_file}'\n")
        
        # Concatenate all clips
        highlight_video_path = os.path.join(output_path, f"highlight_{uuid.uuid4()}.mp4")
        
        stream = ffmpeg.input(file_list_path, f='concat', safe=0)
        stream = ffmpeg.output(stream, highlight_video_path, c='copy')
        ffmpeg.run(stream, overwrite_output=True, quiet=True)
        
        # Clean up temporary files
        shutil.rmtree(temp_dir)
        
        return highlight_video_path
        
    except Exception as e:
        print(f"Error creating highlight video: {e}")
        return None


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/highlight-video', methods=['POST'])
def highlight_video():
    """Main endpoint to create highlight video from YouTube URL"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        youtube_url = data.get('url')
        user_prompt = data.get('prompt')
        
        if not youtube_url:
            return jsonify({'error': 'youtube_url is required'}), 400
        
        if not user_prompt:
            return jsonify({'error': 'user_prompt is required'}), 400
        
        print(f"Processing video: {youtube_url}")
        print(f"User prompt: {user_prompt}")
        
        # Step 1: Extract video ID
        video_id = get_video_id(youtube_url)
        if not video_id:
            return jsonify({'error': 'Invalid YouTube URL'}), 400
        
        # Step 2: Download video
        video_path, video_title = download_youtube_video(youtube_url, UPLOAD_FOLDER)
        if not video_path:
            return jsonify({'error': 'Failed to download video'}), 500
        
        # Step 3: Get transcript
        transcript = get_transcript(video_id)
        if not transcript:
            return jsonify({'error': 'Failed to get transcript'}), 500
        
        # Step 4: Analyze transcript with AI
        highlights = analyze_transcript_with_ai(transcript, user_prompt)
        if not highlights:
            return jsonify({'error': 'Failed to analyze transcript'}), 500
        
        # Step 5: Create highlight video
        highlight_video_path = create_highlight_video(video_path, highlights, UPLOAD_FOLDER)
        if not highlight_video_path:
            return jsonify({'error': 'Failed to create highlight video'}), 500
        
        # Step 6: Clean up original video
        try:
            os.remove(video_path)
        except:
            pass
        
        # Return success response
        return jsonify({
            'success': True,
            'video_title': video_title,
            'highlights': highlights,
            'highlight_video_path': highlight_video_path,
            'message': 'Highlight video created successfully'
        }), 200
        
    except Exception as e:
        print(f"Error in highlight-video endpoint: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download generated highlight video"""
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("🚀 Starting Hylyte Backend Server...")
    print("📍 Server will run on http://localhost:5000")
    print("🔗 API endpoint: POST /api/highlight-video")
    print("💡 Make sure to set your OPENAI_API_KEY in .env file")
    app.run(debug=True, host='0.0.0.0', port=5000) 