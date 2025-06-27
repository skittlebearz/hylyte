# Hylyte Backend

Flask backend for creating AI-powered video highlights from YouTube videos.

## Features

- Download YouTube videos using pytube
- Extract transcripts using youtube-transcript-api
- AI-powered highlight detection using OpenAI GPT-4
- Video clip extraction and concatenation using FFmpeg
- RESTful API endpoints

## Setup

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp env.example .env
   # Edit .env and add your OpenAI API key
   ```

4. **Install FFmpeg** (if not already installed):
   ```bash
   # On Arch Linux
   sudo pacman -S ffmpeg
   
   # On Ubuntu/Debian
   sudo apt install ffmpeg
   
   # On macOS
   brew install ffmpeg
   ```

## Running the Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### POST /api/highlight-video

Create a highlight video from a YouTube URL.

**Request Body:**
```json
{
  "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "user_prompt": "Find moments where the speaker talks about AI"
}
```

**Response:**
```json
{
  "success": true,
  "video_title": "Video Title",
  "highlights": [
    {
      "start_time": 30.5,
      "end_time": 45.2,
      "description": "Speaker discusses AI applications",
      "relevance_score": 9
    }
  ],
  "highlight_video_path": "uploads/highlight_uuid.mp4",
  "message": "Highlight video created successfully"
}
```

### GET /api/health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

### GET /api/download/<filename>

Download a generated highlight video.

## Example Usage

```bash
# Test the API
curl -X POST http://localhost:5000/api/highlight-video \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "user_prompt": "Find the most exciting moments"
  }'
```

## Project Structure

```
backend/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── env.example        # Environment variables template
├── README.md          # This file
└── uploads/           # Generated videos (created automatically)
```

## Dependencies

- Flask: Web framework
- Flask-CORS: Cross-origin resource sharing
- pytube: YouTube video downloader
- youtube-transcript-api: YouTube transcript extraction
- openai: OpenAI API client
- python-dotenv: Environment variable management
- ffmpeg-python: FFmpeg wrapper
- requests: HTTP library 