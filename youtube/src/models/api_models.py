from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class TrendingKeyword(BaseModel):
    keyword: str

class TrendingKeywordsResponse(BaseModel):
    keywords: List[TrendingKeyword]
    generated_at: datetime
    region: str = "US"

class VideoMetadata(BaseModel):
    video_id: str
    title: str
    channel_name: Optional[str] = None
    channel_title: Optional[str] = None  # Added this field
    channel_id: str
    description: str
    thumbnail_url: str
    duration: str
    view_count: int
    like_count: int
    comment_count: int
    published_at: Optional[datetime] = None  # Changed to datetime
    tags: List[str] = []
    url: str
    transcript: Optional[str] = None  # Added transcript field

class TrendingVideosResponse(BaseModel):
    videos: List[VideoMetadata]
    search_keyword: str
    total_results: int
    generated_at: datetime

class ContentIdea(BaseModel):
    title: str
    description: str
    target_audience: str
    estimated_duration: str
    content_type: str

class ScriptSegment(BaseModel):
    segment_type: str
    duration: str
    content: str
    notes: str
    min_start: Optional[int] = None
    min_end: Optional[int] = None

class VideoScript(BaseModel):
    title: str
    total_duration: str
    segments: List[ScriptSegment]
    thumbnail_suggestions: List[str]
    seo_tags: List[str]

class ContentAnalysis(BaseModel):
    content_type: str = "general"
    primary_category: str = "entertainment"
    tone: str = "neutral"
    target_audience: str = "general audience"
    content_style: str = "informational"
    keywords: List[str] = []
    themes: List[str] = []
    engagement_potential: str = "medium"
    recommended_approach: str = "informational_engaging"
    content_depth: str = "intermediate"
    emotional_hooks: List[str] = []
    trending_elements: List[str] = []
    improvement_opportunities: List[str] = []
    competitive_advantages: List[str] = []
    content_gaps: List[str] = []

class MarketPosition(BaseModel):
    competition_level: str = "medium"
    opportunity_score: str = "6"

class TrendingOpportunities(BaseModel):
    current_trends: List[str] = []
    viral_potential: str = "medium"

class OriginalVideoMetadataBrief(BaseModel):
    title: str
    description: str = ""
    view_count: int = 0
    duration: str = "Unknown"
    published_at: str = "Unknown"
    channel_title: str = "Unknown"
    video_id: str

class ContentGenerationResponse(BaseModel):
    content_analysis: ContentAnalysis
    generated_ideas: List[ContentIdea]
    detailed_scripts: List[VideoScript]

class ErrorResponse(BaseModel):
    error: str
    message: str
    status_code: int