import google.generativeai as genai
import json
from dotenv import load_dotenv
from typing import Dict, Any, List
from src.models.api_models import TrendingKeywordsResponse, TrendingKeyword
from datetime import datetime
import os

class GeminiService:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=self.api_key)
        
        # Try different model names based on what's available in Google Cloud
        model_names_to_try = [
            'models/gemini-1.5-flash',
            'models/gemini-1.5-pro', 
            'models/gemini-pro',
            'models/gemini-1.0-pro',
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            'gemini-pro',
            'gemini-1.0-pro'
        ]
        
        self.model = None
        for model_name in model_names_to_try:
            try:
                print(f"Trying model: {model_name}")
                self.model = genai.GenerativeModel(model_name)
                # Test the model with a simple request
                test_response = self.model.generate_content("Hello")
                print(f"✓ Successfully connected to model: {model_name}")
                break
            except Exception as e:
                print(f"✗ Failed to connect to {model_name}: {e}")
                continue
        
        if not self.model:
            # List available models for debugging
            self.list_available_models()
            raise Exception("Could not connect to any Gemini model")
        
        # Set generation config for better responses
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 4096,
        }
    
    def _clean_json_response(self, response_text: str) -> str:
        """Clean and extract JSON from Gemini response"""
        if not response_text:
            return "{}"
        
        # Remove markdown formatting
        if response_text.startswith('```json'):
            response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
        elif response_text.startswith('```'):
            response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
        
        # Clean up extra whitespace and newlines
        response_text = response_text.strip()
        
        # Try to extract valid JSON by finding the first complete JSON object/array
        try:
            # For objects starting with {
            if response_text.startswith('{'):
                brace_count = 0
                for i, char in enumerate(response_text):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            # Found complete JSON object
                            return response_text[:i+1]
            
            # For arrays starting with [
            elif response_text.startswith('['):
                bracket_count = 0
                for i, char in enumerate(response_text):
                    if char == '[':
                        bracket_count += 1
                    elif char == ']':
                        bracket_count -= 1
                        if bracket_count == 0:
                            # Found complete JSON array
                            return response_text[:i+1]
        except Exception as e:
            print(f"Error extracting JSON: {e}")
        
        return response_text
    
    def list_available_models(self):
        """List all available models for debugging"""
        try:
            print("\n=== Available Gemini Models ===")
            models = genai.list_models()
            
            for model in models:
                print(f"Model: {model.name}")
                if hasattr(model, 'supported_generation_methods'):
                    print(f"  Supported methods: {model.supported_generation_methods}")
                    if 'generateContent' in model.supported_generation_methods:
                        print(f"  ✓ Supports generateContent")
                    else:
                        print(f"  ✗ Does not support generateContent")
                else:
                    print(f"  ? Unknown supported methods")
                print()
                
        except Exception as e:
            print(f"Error listing models: {e}")
    
    def generate_trendings(self, limit: int = 20) -> TrendingKeywordsResponse:
        try:
            prompt = f"""Get {limit} trending keywords for currently short trending YouTube content creation.

Respond in this exact JSON format:
[
    "keyword1",
    "keyword2", 
    "keyword3"
]

Only return valid JSON array with {limit} keywords, no other text."""

            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
    
            result = response.text.strip()
            if not result:
                raise ValueError("Empty response from Gemini service")
                
            # Clean and parse the response
            cleaned_response = self._clean_json_response(result)
            print(f"Gemini trending response: {cleaned_response[:200]}...")
            
            # Try to parse JSON
            trending_keywords = json.loads(cleaned_response)
    
            # Ensure trending_keywords is a list
            if not isinstance(trending_keywords, list):
                print(f"Warning: Expected list but got {type(trending_keywords)}")
                trending_keywords = []
                
            # Limit to the specified number of keywords
            trending_keywords = trending_keywords[:limit]
            
            # Convert strings to TrendingKeyword objects (only keyword field needed)
            keyword_objects = []
            for keyword in trending_keywords:
                if isinstance(keyword, str):
                    keyword_obj = TrendingKeyword(keyword=keyword)
                    keyword_objects.append(keyword_obj)
            
            return TrendingKeywordsResponse(
                keywords=keyword_objects,
                generated_at=datetime.now(),
                region="US"
            )
            
        except Exception as e:
            # Fallback with simple keywords
            fallback_keywords = ["AI Tools", "Short Content", "Tutorial", "Gaming", "Tech"]
            keyword_objects = [
                TrendingKeyword(keyword=kw)
                for kw in fallback_keywords[:limit]
            ]
            
            return TrendingKeywordsResponse(
                keywords=keyword_objects,
                generated_at=datetime.now(),
                region="US"
            )
    
    def analyze_video_content(self, video_title: str, video_description: str, transcript: str = None) -> Dict[str, Any]:
        """Analyze video content using Gemini AI"""
        
        analysis_prompt = f"""
Analyze this YouTube video and provide insights:

Title: {video_title}
Description: {video_description[:300] if video_description else "No description"}
Transcript: {transcript[:500] if transcript else "Not available"}

Based on this content, determine:
1. Content type (tutorial, review, entertainment, lifestyle, news, gaming, cooking, technology, or other)
2. Tone (neutral, cheerful, sad, funny, dramatic, etc.)
3. Target audience
4. Key topics/keywords (3-5 words)
5. Engagement potential (high, medium, or low)
6. Best content approach (tutorial, story, comparison, analysis, entertainment)

Respond in this exact JSON format:
{{
    "content_type": "tutorial",
    "tone": "educational", 
    "target_audience": "description here",
    "keywords": ["keyword1", "keyword2", "keyword3"],
    "engagement_potential": "medium",
    "recommended_approach": "tutorial"
}}

Only return valid JSON, no other text.
"""
        
        try:
            response = self.model.generate_content(
                analysis_prompt,
                generation_config=self.generation_config
            )
            
            response_text = self._clean_json_response(response.text)
            print(f"Gemini analysis response: {response_text[:200]}...")
            
            analysis = json.loads(response_text)
            
            if not isinstance(analysis, dict):
                print(f"Warning: Expected dict but got {type(analysis)}")
                analysis = {}
            
            # Return simplified analysis that matches your ContentAnalysis model
            full_analysis = {
                "content_type": analysis.get("content_type", "general"),
                "primary_category": analysis.get("content_type", "entertainment"),
                "tone": analysis.get("tone", "neutral"),
                "target_audience": analysis.get("target_audience", "general audience"),
                "content_style": "informational",
                "keywords": analysis.get("keywords", []) if isinstance(analysis.get("keywords"), list) else [],
                "themes": analysis.get("keywords", []) if isinstance(analysis.get("keywords"), list) else [],
                "engagement_potential": analysis.get("engagement_potential", "medium"),
                "recommended_approach": analysis.get("recommended_approach", "informational_engaging"),
                "content_depth": "intermediate",
                "emotional_hooks": [],
                "trending_elements": analysis.get("keywords", [])[:2] if isinstance(analysis.get("keywords"), list) else [],
                "improvement_opportunities": [],
                "competitive_advantages": [],
                "content_gaps": []
            }
            
            return full_analysis
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return self._get_default_analysis()
        except Exception as e:
            print(f"Error analyzing content with Gemini: {e}")
            return self._get_default_analysis()
    
    def generate_content_ideas(self, original_title: str, content_analysis: Dict[str, Any], transcript: str = None) -> List[Dict[str, Any]]:
        """Generate content ideas using Gemini AI - ONLY 1 VIDEO"""
        
        if not isinstance(content_analysis, dict):
            print(f"Warning: content_analysis is not a dict: {type(content_analysis)}")
            content_analysis = {}
        
        ideas_prompt = f"""
Create 1 YouTube video idea based on this original video:

Original Title: {original_title}
Content Type: {content_analysis.get('content_type', 'general')}
Target Audience: {content_analysis.get('target_audience', 'general')}

Create 1 unique video idea that builds on this topic but offers new value.

Respond in this exact JSON format:
[
    {{
        "title": "Compelling title for the video",
        "description": "What this video covers",
        "target_audience": "who this targets",
        "estimated_duration": "1-2 minutes",
        "content_type": "tutorial"
    }}
]

Only return valid JSON array with 1 object, no other text.
"""
        
        try:
            response = self.model.generate_content(
                ideas_prompt,
                generation_config=self.generation_config
            )
            response_text = self._clean_json_response(response.text)
            print(f"Gemini ideas response: {response_text[:200]}...")
            
            ideas = json.loads(response_text)
            
            if not isinstance(ideas, list):
                print(f"Warning: Expected list but got {type(ideas)}")
                return self._get_default_content_ideas(original_title, content_analysis)
            
            validated_ideas = []
            for idea in ideas:
                if isinstance(idea, dict):
                    validated_ideas.append(idea)
                else:
                    print(f"Warning: Invalid idea format: {type(idea)}")
            
            return validated_ideas if validated_ideas else self._get_default_content_ideas(original_title, content_analysis)
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error in ideas: {e}")
            return self._get_default_content_ideas(original_title, content_analysis)
        except Exception as e:
            print(f"Error generating content ideas with Gemini: {e}")
            return self._get_default_content_ideas(original_title, content_analysis)

    def generate_detailed_script(self, content_idea: Dict[str, Any], content_analysis: Dict[str, Any], original_transcript: str = None) -> Dict[str, Any]:
        """Generate detailed video script using Gemini AI with timing"""
        
        if not isinstance(content_idea, dict):
            print(f"Warning: content_idea is not a dict: {type(content_idea)}")
            content_idea = {}
        
        if not isinstance(content_analysis, dict):
            print(f"Warning: content_analysis is not a dict: {type(content_analysis)}")
            content_analysis = {}
        
        title = content_idea.get('title', 'Video Title')
        target_audience = content_idea.get('target_audience', 'general')
        duration = content_idea.get('estimated_duration', '1-2 minutes')
        content_type = content_idea.get('content_type', 'tutorial')
        
        script_prompt = f"""
    Create a video script for this idea:

    Title: {title}
    Target Audience: {target_audience}
    Duration: {duration}
    Type: {content_type}

    Create a script with intro, main content, and conclusion. Include specific timing for each segment.

    Respond in this exact JSON format:
    {{
        "title": "Video title here",
        "total_duration": "2.5 minutes",
        "segments": [
            {{
                "segment_type": "intro",
                "duration": "30 seconds", 
                "content": "Welcome back! Today we are going to explore...",
                "notes": "High energy opening, make eye contact"
            }},
            {{
                "segment_type": "main_content",
                "duration": "90 seconds",
                "content": "Main content script here...",
                "notes": "Keep audience engaged, use examples"
            }},
            {{
                "segment_type": "conclusion",
                "duration": "30 seconds",
                "content": "That's a wrap! Hope this helped...",
                "notes": "Summarize key points, call to action"
            }}
        ],
        "thumbnail_suggestions": ["suggestion 1", "suggestion 2"],
        "seo_tags": ["tag1", "tag2", "tag3"]
    }}

    Only return valid JSON, no other text.
    """
        
        try:
            response = self.model.generate_content(
                script_prompt,
                generation_config=self.generation_config
            )
            
            if not response or not response.text:
                print("Warning: Empty response from Gemini")
                return self._get_default_script(content_idea, content_analysis)
            
            response_text = self._clean_json_response(response.text)
            print(f"Gemini script response: {response_text[:200]}...")
            
            script = json.loads(response_text)
            
            if not isinstance(script, dict):
                print(f"Warning: Expected dict but got {type(script)}")
                return self._get_default_script(content_idea, content_analysis)
            
            if 'segments' not in script or not isinstance(script['segments'], list):
                print("Warning: Invalid script format - missing or invalid segments")
                return self._get_default_script(content_idea, content_analysis)
            
            valid_segments = []
            for segment in script.get('segments', []):
                if isinstance(segment, dict):
                    valid_segments.append(segment)
                else:
                    print(f"Warning: Invalid segment format: {type(segment)}")
            
            if not valid_segments:
                print("Warning: No valid segments found")
                return self._get_default_script(content_idea, content_analysis)
            
            script['segments'] = valid_segments
            script['title'] = script.get('title', title)
            script['total_duration'] = script.get('total_duration', duration)
            script['thumbnail_suggestions'] = script.get('thumbnail_suggestions', [])
            script['seo_tags'] = script.get('seo_tags', [])
            
            return script
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error in script: {e}")
            return self._get_default_script(content_idea, content_analysis)
        except Exception as e:
            print(f"Error generating script with Gemini: {e}")
            return self._get_default_script(content_idea, content_analysis)
    def _get_default_analysis(self) -> Dict[str, Any]:
        """Fallback analysis if Gemini fails"""
        return {
            "content_type": "general",
            "primary_category": "entertainment",
            "tone": "neutral",
            "target_audience": "general audience",
            "content_style": "informational",
            "keywords": ["general", "content"],
            "themes": ["general"],
            "engagement_potential": "medium",
            "recommended_approach": "informational_engaging",
            "content_depth": "intermediate",
            "emotional_hooks": [],
            "trending_elements": ["general"],
            "improvement_opportunities": [],
            "competitive_advantages": [],
            "content_gaps": []
        }
    
    def _get_default_content_ideas(self, title: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fallback content ideas if Gemini fails - ONLY 1 VIDEO"""
        if not isinstance(analysis, dict):
            analysis = {}
        
        return [
            {
                "title": f"My Take on {title[:30]}",
                "description": "A unique perspective on the original content",
                "target_audience": analysis.get("target_audience", "general audience"),
                "estimated_duration": "1-2 minutes",
                "content_type": analysis.get("content_type", "tutorial")
            }
        ]
    
    def _get_default_script(self, idea: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback script if Gemini fails"""
        if not isinstance(idea, dict):
            idea = {}
        
        return {
            "title": idea.get("title", "Default Title"),
            "total_duration": "1-2 minutes",
            "segments": [
                {
                    "segment_type": "intro",
                    "duration": "30 seconds",
                    "content": "Welcome back! Today we're diving into an exciting topic...",
                    "notes": "High energy opening, make eye contact with camera"
                },
                {
                    "segment_type": "main_content",
                    "duration": "45s - 1.5 minutes",
                    "content": "Let me break this down for you step by step...",
                    "notes": "Use examples, keep engagement high"
                },
                {
                    "segment_type": "conclusion",
                    "duration": "30 seconds",
                    "content": "That's everything you need to know! Hope this was helpful...",
                    "notes": "Summarize key takeaways"
                }
            ],
            "thumbnail_suggestions": ["Bold title text", "High contrast colors", "Clear value proposition"],
            "seo_tags": ["tutorial", "guide", "how to", "tips"]
        }