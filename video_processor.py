
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi

"""
Video Processor - Simple FFmpeg-based video clip extraction
"""

import ffmpeg
import os
import argparse
from pathlib import Path


def extract_clip(input_path: str, output_path: str, start_time: float, end_time: float) -> bool:
    """
    Extract a clip from a video file using FFmpeg.
    
    Args:
        input_path: Path to the input video file
        output_path: Path where the output clip will be saved
        start_time: Start time in seconds
        end_time: End time in seconds
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Calculate duration
        duration = end_time - start_time
        
        # Create the FFmpeg command
        stream = ffmpeg.input(input_path, ss=start_time, t=duration)
        stream = ffmpeg.output(stream, output_path, acodec='aac', vcodec='libx264')
        
        # Run the command
        ffmpeg.run(stream, overwrite_output=True, quiet=True)
        
        print(f"✅ Successfully extracted clip: {output_path}")
        print(f"   Duration: {duration:.2f} seconds ({start_time:.2f}s - {end_time:.2f}s)")
        return True
        
    except ffmpeg.Error as e:
        print(f"❌ FFmpeg error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def format_time(seconds: float) -> str:
    """Convert seconds to HH:MM:SS format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def get_video_info(input_path: str) -> dict | None:
    """
    Get basic information about a video file.
    
    Args:
        input_path: Path to the video file
    
    Returns:
        dict | None: Video information including duration, resolution, etc.
    """
    try:
        probe = ffmpeg.probe(input_path)
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        
        duration = float(probe['format']['duration'])
        
        return {
            'duration': duration,
            'duration_formatted': format_time(duration),
            'width': int(video_info['width']),
            'height': int(video_info['height']),
            'fps': eval(video_info['r_frame_rate']),
            'codec': video_info['codec_name']
        }
        
    except Exception as e:
        print(f"❌ Error getting video info: {e}")
        return None

def get_video_id(url):
    # Extracts the video ID from a YouTube URL
    return YouTube(url).video_id

def fetch_transcript(video_id, language='en'):
    # Fetches the transcript for the given video ID
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        return transcript
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None

def print_transcript_with_timestamps(transcript):
    for entry in transcript:
        start = entry['start']
        text = entry['text']
        print(f"[{start:.2f}s] {text}")

    #url = input("Enter YouTube video URL: ")
    #video_id = get_video_id(url)
    #transcript = fetch_transcript(video_id)
    #if transcript:
    #    print_transcript_with_timestamps(transcript)
    #else:
    #    print("Transcript not available for this video.")
