import re
import logging
from datetime import datetime
from typing import Optional

def extract_video_id(url_or_id: str) -> str:
    """Extract YouTube video ID from URL or return ID if already clean"""
    if 'youtube.com/watch?v=' in url_or_id:
        return url_or_id.split('v=')[1].split('&')[0]
    elif 'youtu.be/' in url_or_id:
        return url_or_id.split('youtu.be/')[1].split('?')[0]
    else:
        return url_or_id

def validate_video_id(video_id: str) -> bool:
    """Validate YouTube video ID format"""
    pattern = r'^[a-zA-Z0-9_-]{11}$'
    return bool(re.match(pattern, video_id))

def format_duration(seconds: int) -> str:
    """Format duration from seconds to readable format"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"