from typing import List, Dict, Any, Optional
import traceback
from datetime import datetime
from pydantic import ValidationError

from src.models.api_models import (
    VideoMetadata, ContentIdea, ScriptSegment, VideoScript,
    ContentGenerationResponse, ContentAnalysis  # Removed non-existent imports
)
from src.services.youtube_service import YouTubeService
from src.services.gemini_service import GeminiService

class ContentGeneratorService:
    def __init__(self):
        self.youtube_service = YouTubeService()
        self.gemini_service = GeminiService()

    def _parse_gemini_dict(self, data: Any, model_class: type, default_on_error: bool = True) -> Any:
        """Helper to parse dictionary data into a Pydantic model, with error handling."""
        if not isinstance(data, dict):
            print(f"Warning: Expected dict for {model_class.__name__}, got {type(data)}. Returning default.")
            return model_class() if default_on_error else None
        try:
            return model_class(**data)
        except ValidationError as e:
            print(f"Error validating data for {model_class.__name__}: {e}. Data: {data}")
            return model_class() if default_on_error else None

    def _model_to_dict(self, model):
        """Convert Pydantic model to dict using the appropriate method based on version"""
        if hasattr(model, 'model_dump'):
            return model.model_dump(exclude_none=True)
        elif hasattr(model, 'dict'):
            return model.dict(exclude_none=True)
        else:
            return dict(model)
        
    def generate_content_ideas(self, video_id: str) -> List[ContentIdea]:
        """Generate content ideas based on a video ID, returning a list of ContentIdea models."""
        
        # Step 0: Get original video details
        original_video: Optional[VideoMetadata] = self.youtube_service.get_video_by_id(video_id)

        if not original_video:
            print(f"Error: Video with ID {video_id} not found or failed to fetch.")
            raise ValueError(f"Video with ID {video_id} not found.")

        print(f"Processing video: {original_video.title}")

        # Step 1: Analyze the original video content
        print("Step 1: Analyzing video content...")
        gemini_analysis_raw = self.gemini_service.analyze_video_content(
            video_title=original_video.title,
            video_description=original_video.description,
            transcript=original_video.transcript)
        content_analysis_model = self._parse_gemini_dict(gemini_analysis_raw, ContentAnalysis)
        if not content_analysis_model:
            content_analysis_model = ContentAnalysis()
        print(f"Content analysis completed: {content_analysis_model.content_type}")
        # Step 2: Generate content ideas
        print("Step 2: Generating content ideas...")
        gemini_ideas_raw_list = self.gemini_service.generate_content_ideas(
            original_title=original_video.title,
            content_analysis=gemini_analysis_raw,
            transcript=original_video.transcript
        )
        generated_ideas_models: List[ContentIdea] = []
        if isinstance(gemini_ideas_raw_list, list) and gemini_ideas_raw_list:
            for idea_raw in gemini_ideas_raw_list:
                idea_model = self._parse_gemini_dict(idea_raw, ContentIdea)
                if idea_model:
                    generated_ideas_models.append(idea_model)
        if not generated_ideas_models:
            print("Warning: No content ideas were generated or parsed successfully. Using a default.")
            # Fixed: Remove hook and difficulty_level fields
            default_idea = ContentIdea(
                title="Default Idea", 
                description="Could not generate specific idea.",
                target_audience="General audience",
                estimated_duration="1-2 minutes",
                content_type="tutorial"
            )
            generated_ideas_models.append(default_idea)

    def generate_content_script(self, video_id: str) -> ContentGenerationResponse:
        """AI-driven content generation using Gemini AI, returning a Pydantic model."""
        try:
            # Step 0: Get original video details
            original_video: Optional[VideoMetadata] = self.youtube_service.get_video_by_id(video_id)

            if not original_video:
                print(f"Error: Video with ID {video_id} not found or failed to fetch.")
                raise ValueError(f"Video with ID {video_id} not found.")

            print(f"Processing video: {original_video.title}")

            # Step 1: Analyze the original video content
            print("Step 1: Analyzing video content...")
            gemini_analysis_raw = self.gemini_service.analyze_video_content(
                video_title=original_video.title,
                video_description=original_video.description,
                transcript=original_video.transcript
            )
            content_analysis_model = self._parse_gemini_dict(gemini_analysis_raw, ContentAnalysis)
            if not content_analysis_model:
                content_analysis_model = ContentAnalysis()

            print(f"Content analysis completed: {content_analysis_model.content_type}")

            # Step 2: Generate content ideas
            print("Step 2: Generating content ideas...")
            gemini_ideas_raw_list = self.gemini_service.generate_content_ideas(
                original_title=original_video.title,
                content_analysis=gemini_analysis_raw,
                transcript=original_video.transcript
            )

            generated_ideas_models: List[ContentIdea] = []
            if isinstance(gemini_ideas_raw_list, list) and gemini_ideas_raw_list:
                first_idea_raw = gemini_ideas_raw_list[0]
                idea_model = self._parse_gemini_dict(first_idea_raw, ContentIdea)
                if idea_model:
                    generated_ideas_models.append(idea_model)
            
            if not generated_ideas_models:
                print("Warning: No content ideas were generated or parsed successfully. Using a default.")
                # Fixed: Remove hook and difficulty_level fields
                default_idea = ContentIdea(
                    title="Default Idea", 
                    description="Could not generate specific idea.",
                    target_audience="General audience",
                    estimated_duration="1-2 minutes",
                    content_type="tutorial"
                )
                generated_ideas_models.append(default_idea)

            # Step 3: Generate script for the first valid idea
            if not generated_ideas_models or not generated_ideas_models[0]:
                raise ValueError("No valid content idea available to generate script.")
            
            current_idea_model = generated_ideas_models[0]
            print(f"Step 3: Generating script for idea: {current_idea_model.title}")

            # Convert model to dict using version-compatible method
            gemini_script_raw = self.gemini_service.generate_detailed_script(
                content_idea=self._model_to_dict(current_idea_model),
                content_analysis=gemini_analysis_raw,
                original_transcript=original_video.transcript
            )
            detailed_script_model = self._parse_gemini_dict(gemini_script_raw, VideoScript)
            if not detailed_script_model:
                # Create a default script
                default_segments = [
                    ScriptSegment(
                        segment_type="intro",
                        duration="30 seconds",
                        content="Welcome to our video!",
                        notes="High energy opening"
                    ),
                    ScriptSegment(
                        segment_type="main_content",
                        duration="1 minute",
                        content="Main content here...",
                        notes="Keep audience engaged"
                    ),
                    ScriptSegment(
                        segment_type="conclusion",
                        duration="30 seconds",
                        content="Thanks for watching!",
                        notes="Summarize key points"
                    )
                ]
                detailed_script_model = VideoScript(
                    title="Error Script", 
                    total_duration="2 minutes",
                    segments=default_segments,
                    thumbnail_suggestions=["Default thumbnail"],
                    seo_tags=["default", "video"]
                )

            # Step 4: Construct the simplified response using only available models
            response = ContentGenerationResponse(
                content_analysis=content_analysis_model,
                generated_ideas=generated_ideas_models,
                detailed_scripts=[detailed_script_model] if detailed_script_model else []
            )

            print("Content generation completed successfully!")
            return response

        except ValueError as ve:
            print(f"ValueError during content generation: {ve}")
            traceback.print_exc()
            raise
        except ValidationError as ve_pydantic:
            print(f"Pydantic Validation Error during content generation: {ve_pydantic}")
            traceback.print_exc()
            raise Exception(f"Data validation error: {str(ve_pydantic)}")
        except Exception as e:
            print(f"Unexpected error generating content: {e}")
            traceback.print_exc()
            raise Exception(f"Error generating content: {str(e)}")