from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from typing import Optional
from src.models.api_models import VideoMetadata, TrendingVideosResponse
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os



class YouTubeService:
    def __init__(self):
        load_dotenv()  # Load environment variables from .env file
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY environment variable not set")
        
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
    
    def search_trending_videos(self, keyword: str, max_results: int = 5) -> TrendingVideosResponse:
        """Search for trending videos based on keyword"""
        try:
            # Search for videos
            search_request = self.youtube.search().list(
                part='snippet',
                q=keyword,
                type='video',
                order='viewCount',  # Order by view count for trending
                maxResults=max_results,
                # recent trending videos can be filtered by publishedAfter : 72 hours
                publishedAfter=(datetime.now() - timedelta(days=3)).isoformat("T") + "Z"  # Last 72 hours
            )
            search_response = search_request.execute()
            
            videos = []
            for item in search_response.get('items', []):
                video_id = item['id']['videoId']
                
                # Get detailed video statistics
                video_details = self._get_video_details(video_id)
                if video_details:
                    videos.append(video_details)
            
            return TrendingVideosResponse(
                videos=videos,
                search_keyword=keyword,
                total_results=len(videos),
                generated_at=datetime.now()
            )
            
        except Exception as e:
            raise Exception(f"Error searching videos: {str(e)}")
    
    def _get_video_details(self, video_id: str) -> Optional[VideoMetadata]:
        """Get detailed information for a specific video"""
        try:
            request = self.youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=video_id
            )
            response = request.execute()
            
            if not response.get('items'):
                return None
            
            item = response['items'][0]
            snippet = item['snippet']
            statistics = item['statistics']
            content_details = item['contentDetails']
            
            return VideoMetadata(
                video_id=video_id,
                title=snippet['title'],
                channel_name=snippet['channelTitle'],
                channel_id=snippet['channelId'],
                description=snippet['description'],
                thumbnail_url=snippet['thumbnails'].get('high', {}).get('url', ''),
                duration=content_details['duration'],
                view_count=int(statistics.get('viewCount', 0)),
                like_count=int(statistics.get('likeCount', 0)),
                comment_count=int(statistics.get('commentCount', 0)),
                published_at=snippet['publishedAt'],
                tags=snippet.get('tags', []),
                url=f"https://www.youtube.com/watch?v={video_id}"
            )
            
        except Exception as e:
            print(f"Error getting video details for {video_id}: {e}")
            return None
    
    def get_video_transcript(self, video_id: str) -> Optional[str]:
        """Get transcript for a video"""
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Try to get English transcript first
            for lang_code in ['en', 'en-US', 'en-GB']:
                try:
                    transcript = transcript_list.find_transcript([lang_code])
                    transcript_data = transcript.fetch()
                    return " ".join([entry['text'] for entry in transcript_data])
                except NoTranscriptFound:
                    continue
            
            # If no English, try auto-generated
            try:
                transcript = transcript_list.find_generated_transcript(['en'])
                transcript_data = transcript.fetch()
                return " ".join([entry['text'] for entry in transcript_data])
            except NoTranscriptFound:
                return None
                
        except (TranscriptsDisabled, Exception):
            return None
    
    def get_video_by_id(self, video_id: str) -> Optional[VideoMetadata]:
        """Get single video details by ID"""
        return self._get_video_details(video_id)