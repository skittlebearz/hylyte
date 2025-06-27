#!/usr/bin/env python3
"""
Example usage of the video processor functions
"""

from video_processor import extract_clip, get_video_info, format_time


def example_basic_usage():
    """Example of basic clip extraction"""
    print("🎬 Basic Clip Extraction Example")
    print("=" * 40)
    
    # Example video file (replace with your actual video path)
    input_video = "sample_video.mp4"
    output_clip = "output_clip.mp4"
    
    # Extract a 10-second clip starting at 30 seconds
    start_time = 30.0  # 30 seconds
    end_time = 40.0    # 40 seconds
    
    print(f"Input: {input_video}")
    print(f"Output: {output_clip}")
    print(f"Time range: {start_time}s - {end_time}s")
    print()
    
    # Get video info first
    info = get_video_info(input_video)
    if info:
        print(f"📹 Video Info:")
        print(f"   Duration: {info['duration_formatted']}")
        print(f"   Resolution: {info['width']}x{info['height']}")
        print(f"   FPS: {info['fps']}")
        print()
    
    # Extract the clip
    success = extract_clip(input_video, output_clip, start_time, end_time)
    
    if success:
        print("✅ Example completed successfully!")
    else:
        print("❌ Example failed!")


def example_multiple_clips():
    """Example of extracting multiple clips"""
    print("\n🎬 Multiple Clips Example")
    print("=" * 40)
    
    input_video = "sample_video.mp4"
    
    # Define multiple clips to extract
    clips = [
        {"start": 10.0, "end": 15.0, "output": "clip1.mp4"},
        {"start": 45.0, "end": 52.0, "output": "clip2.mp4"},
        {"start": 120.0, "end": 130.0, "output": "clip3.mp4"},
    ]
    
    for i, clip in enumerate(clips, 1):
        print(f"Extracting clip {i}: {clip['start']}s - {clip['end']}s")
        success = extract_clip(
            input_video, 
            clip['output'], 
            clip['start'], 
            clip['end']
        )
        if success:
            print(f"   ✅ Clip {i} saved as {clip['output']}")
        else:
            print(f"   ❌ Failed to extract clip {i}")
        print()


def example_time_formatting():
    """Example of time formatting utilities"""
    print("\n⏰ Time Formatting Examples")
    print("=" * 40)
    
    times = [30.5, 125.0, 3661.0, 7200.0]
    
    for seconds in times:
        formatted = format_time(seconds)
        print(f"{seconds:6.1f} seconds = {formatted}")


if __name__ == "__main__":
    print("🚀 Video Processor Examples")
    print("=" * 50)
    
    # Note: These examples assume you have a video file named "sample_video.mp4"
    # Replace with your actual video file path
    
    example_time_formatting()
    
    # Uncomment these to run the actual video processing examples
    # (Make sure you have a video file to test with)
    
    # example_basic_usage()
    # example_multiple_clips()
    
    print("\n💡 To run the actual examples:")
    print("1. Place a video file in the same directory")
    print("2. Update the file paths in the example functions")
    print("3. Uncomment the function calls above")
    print("4. Run: python example_usage.py") 