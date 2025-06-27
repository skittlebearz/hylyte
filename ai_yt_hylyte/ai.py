import os
import re
import json
from typing import List, Dict, Optional
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class VideoAnalyzer:
    def __init__(self):
        """Initialize the video analyzer with OpenAI client."""
        self.openai_client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    
    def analyze_transcript(self, transcript: List[Dict], video_title: str = "", custom_prompt: str = None) -> List[Dict]:
        """
        Analyze transcript with OpenAI to find highlights.
        
        Args:
            transcript: List of transcript segments with 'start' and 'text' keys
            video_title: Title of the video for context
            custom_prompt: Optional custom prompt to override the default
        
        Returns:
            List of highlight dictionaries with timestamp, description, and significance
        """
        formatted_transcript = self._format_transcript_for_analysis(transcript)
        
        # Use custom prompt if provided, otherwise use default
        if custom_prompt:
            prompt = custom_prompt.format(
                video_title=video_title,
                transcript=formatted_transcript
            )
        else:
            prompt = self._get_default_prompt(video_title, formatted_transcript)
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert video content analyst. You excel at identifying the most engaging and important moments in video content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # Extract and parse the JSON response
            content = response.choices[0].message.content
            return self._parse_highlights_response(content)
                
        except Exception as e:
            raise Exception(f"Error analyzing highlights with OpenAI: {e}")
    
    def _format_transcript_for_analysis(self, transcript: List[Dict]) -> str:
        """Format transcript into a readable string for OpenAI analysis."""
        formatted_lines = []
        for entry in transcript:
            start_time = entry['start']
            text = entry['text']
            # Convert seconds to MM:SS format
            minutes = int(start_time // 60)
            seconds = int(start_time % 60)
            timestamp = f"{minutes:02d}:{seconds:02d}"
            formatted_lines.append(f"[{timestamp}] {text}")
        
        return "\n".join(formatted_lines)
    
    def _get_default_prompt(self, video_title: str, formatted_transcript: str) -> str:
        """Get the default prompt for highlight analysis."""
        return f"""
        Analyze the following YouTube video transcript and identify the most interesting highlights.
        
        Video Title: {video_title}
        
        Transcript:
        {formatted_transcript}
        
        Please identify 5-10 key highlights from this video. For each highlight:
        1. Provide a brief description of what happens
        2. Include the exact timestamp (MM:SS format)
        3. Explain why this moment is significant or interesting
        
        Format your response as a JSON array with the following structure:
        [
            {{
                "timestamp": "MM:SS",
                "description": "Brief description of the highlight",
                "significance": "Why this moment is important or interesting",
                "start_seconds": float
            }}
        ]
        
        Focus on moments that are:
        - Particularly informative or educational
        - Emotionally engaging or surprising
        - Key turning points or revelations
        - Memorable quotes or statements
        - Important demonstrations or examples
        """
    
    def _parse_highlights_response(self, content: str) -> List[Dict]:
        """Parse the OpenAI response to extract highlights."""
        import json
        
        # Try to extract JSON from the response
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            try:
                highlights = json.loads(json_match.group())
                return highlights
            except json.JSONDecodeError:
                pass
        
        # Fallback: try to parse the entire response as JSON
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            raise Exception("Could not parse highlights from OpenAI response")

# Example usage and prompt templates
class PromptTemplates:
    """Collection of prompt templates for different analysis types."""
    
    @staticmethod
    def educational_highlights():
        """Template for educational content analysis."""
        return """
        Analyze the following educational video transcript and identify the most valuable learning moments.
        
        Video Title: {video_title}
        
        Transcript:
        {transcript}
        
        Please identify 5-8 key learning highlights from this video. For each highlight:
        1. Provide a brief description of the concept or lesson
        2. Include the exact timestamp (MM:SS format)
        3. Explain why this is an important learning moment
        
        Format your response as a JSON array with the following structure:
        [
            {{
                "timestamp": "MM:SS",
                "description": "Brief description of the learning moment",
                "significance": "Why this concept is important to understand",
                "start_seconds": float
            }}
        ]
        
        Focus on:
        - Key concepts and definitions
        - Step-by-step explanations
        - Important examples and demonstrations
        - Critical insights and revelations
        - Practical applications
        """
    
    @staticmethod
    def entertainment_highlights():
        """Template for entertainment content analysis."""
        return """
        Analyze the following entertainment video transcript and identify the most entertaining moments.
        
        Video Title: {video_title}
        
        Transcript:
        {transcript}
        
        Please identify 5-10 most entertaining highlights from this video. For each highlight:
        1. Provide a brief description of what happens
        2. Include the exact timestamp (MM:SS format)
        3. Explain why this moment is entertaining or memorable
        
        Format your response as a JSON array with the following structure:
        [
            {{
                "timestamp": "MM:SS",
                "description": "Brief description of the entertaining moment",
                "significance": "Why this moment is entertaining or memorable",
                "start_seconds": float
            }}
        ]
        
        Focus on:
        - Funny or humorous moments
        - Surprising revelations
        - Emotional reactions
        - Memorable quotes
        - Engaging storytelling
        """
    
    @staticmethod
    def technical_highlights():
        """Template for technical content analysis."""
        return """
        Analyze the following technical video transcript and identify the most important technical insights.
        
        Video Title: {video_title}
        
        Transcript:
        {transcript}
        
        Please identify 5-8 key technical highlights from this video. For each highlight:
        1. Provide a brief description of the technical concept
        2. Include the exact timestamp (MM:SS format)
        3. Explain why this technical insight is important
        
        Format your response as a JSON array with the following structure:
        [
            {{
                "timestamp": "MM:SS",
                "description": "Brief description of the technical concept",
                "significance": "Why this technical insight is important",
                "start_seconds": float
            }}
        ]
        
        Focus on:
        - Technical explanations and concepts
        - Code examples and demonstrations
        - Best practices and tips
        - Common pitfalls and solutions
        - Performance optimizations
        """

# Utility functions for external use
def analyze_video_highlights(transcript: List[Dict], video_title: str = "", custom_prompt: str = None) -> List[Dict]:
    """
    Convenience function to analyze video highlights.
    
    Args:
        transcript: List of transcript segments
        video_title: Title of the video
        custom_prompt: Optional custom prompt template
    
    Returns:
        List of highlight dictionaries
    """
    analyzer = VideoAnalyzer()
    return analyzer.analyze_transcript(transcript, video_title, custom_prompt)

def get_prompt_template(template_type: str = "default") -> str:
    """
    Get a prompt template by type.
    
    Args:
        template_type: Type of template ("default", "educational", "entertainment", "technical")
    
    Returns:
        Prompt template string
    """
    templates = PromptTemplates()
    
    if template_type == "educational":
        return templates.educational_highlights()
    elif template_type == "entertainment":
        return templates.entertainment_highlights()
    elif template_type == "technical":
        return templates.technical_highlights()
    else:
        # Return a generic template
        return """
        Analyze the following video transcript and identify the most interesting highlights.
        
        Video Title: {video_title}
        
        Transcript:
        {transcript}
        
        Please identify 5-10 key highlights from this video. For each highlight:
        1. Provide a brief description of what happens
        2. Include the exact timestamp (MM:SS format)
        3. Explain why this moment is significant or interesting
        
        Format your response as a JSON array with the following structure:
        [
            {{
                "timestamp": "MM:SS",
                "description": "Brief description of the highlight",
                "significance": "Why this moment is important or interesting",
                "start_seconds": float
            }}
        ]
        """

if __name__ == "__main__":
    # Example usage
    analyzer = VideoAnalyzer()
    print(analyzer.model)
    
    # Example transcript data
    sample_transcript = [
        {"start": 0, "text": "Hello and welcome to this tutorial."},
        {"start": 5, "text": "Today we'll learn about Python programming."},
        {"start": 10, "text": "This is a very important concept."}
    ]
    
    # Test with default prompt
    try:
        highlights = analyzer.analyze_transcript(sample_transcript, "Sample Video")
        print("Highlights found:", len(highlights))
        for highlight in highlights:
            print(f"[{highlight['timestamp']}] {highlight['description']}")
    except Exception as e:
        print(f"Error: {e}")
