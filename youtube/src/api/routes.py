from datetime import datetime
from flask import Flask, request, jsonify
from src.services.youtube_service import YouTubeService
from src.services.content_generator_service import ContentGeneratorService
from src.models.api_models import ErrorResponse
from src.services.gemini_service import GeminiService

app = Flask(__name__)

# Initialize services
youtube_service = YouTubeService()
content_generator = ContentGeneratorService()
gemini_service = GeminiService()

@app.errorhandler(404)
def not_found(error):
    return jsonify(ErrorResponse(
        error="Not Found",
        message="The requested endpoint was not found",
        status_code=404
    ).dict()), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify(ErrorResponse(
        error="Internal Server Error",
        message="An unexpected error occurred",
        status_code=500
    ).dict()), 500

@app.route('/api/v1/trending/keywords', methods=['GET'])
def get_trending_keywords():
    try:
        limit = min(int(request.args.get('limit', 20)), 50)
        
        result = gemini_service.generate_trendings(limit=limit)
        return jsonify(result.dict())
        
    except ValueError as e:
        return jsonify(ErrorResponse(
            error="Bad Request",
            message=str(e),
            status_code=400
        ).dict()), 400
    except Exception as e:
        return jsonify(ErrorResponse(
            error="Internal Server Error", 
            message=str(e),
            status_code=500
        ).dict()), 500

@app.route('/api/v1/videos/search', methods=['GET'])
def search_trending_videos():
    """
    Search for top trending videos based on keywords
    Query Parameters:
    - keyword: search keyword (required)
    - limit: number of videos to return (default: 5, max: 10)
    """
    try:
        keyword = request.args.get('keyword')
        if not keyword:
            return jsonify(ErrorResponse(
                error="Bad Request",
                message="keyword parameter is required",
                status_code=400
            ).dict()), 400
        
        limit = min(int(request.args.get('limit', 5)), 10)
        
        result = youtube_service.search_trending_videos(keyword, max_results=limit)
        return jsonify(result.dict())
        
    except ValueError as e:
        return jsonify(ErrorResponse(
            error="Bad Request",
            message=str(e),
            status_code=400
        ).dict()), 400
    except Exception as e:
        return jsonify(ErrorResponse(
            error="Internal Server Error",
            message=str(e),
            status_code=500
        ).dict()), 500

@app.route('/api/v1/videos/<video_id>', methods=['GET'])
def get_video_details(video_id):
    """Get detailed information for a specific video"""
    try:
        video = youtube_service.get_video_by_id(video_id)
        if not video:
            return jsonify(ErrorResponse(
                error="Not Found",
                message=f"Video with ID {video_id} not found",
                status_code=404
            ).dict()), 404
        
        return jsonify(video.dict())
        
    except Exception as e:
        return jsonify(ErrorResponse(
            error="Internal Server Error",
            message=str(e),
            status_code=500
        ).dict()), 500

@app.route('/api/v1/content/quick-ideas', methods=['POST'])
def generate_quick_ideas():
    """
    Generate quick content ideas without full script
    Request Body:
    {
        "video_id": "YouTube video ID"
    }
    """
    try:
        data = request.get_json()
        if not data or 'video_id' not in data:
            return jsonify(ErrorResponse(
                error="Bad Request",
                message="video_id is required in request body", 
                status_code=400
            ).dict()), 400
        
        video_id = data['video_id']
        
        # Get video details
        video = youtube_service.get_video_by_id(video_id)
        if not video:
            return jsonify(ErrorResponse(
                error="Not Found",
                message=f"Video with ID {video_id} not found",
                status_code=404
            ).dict()), 404
        
        # Generate only content ideas
        content_ideas = content_generator.generate_content_ideas(video)
        
        return jsonify({
            "original_video": video.dict(),
            "content_ideas": [idea.dict() for idea in content_ideas],
            "generated_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify(ErrorResponse(
            error="Internal Server Error",
            message=str(e),
            status_code=500
        ).dict()), 500

@app.route('/api/v1/content/generate', methods=['POST'])
def generate_content():
    """
    Generate complete content ideas and scripts based on a reference video
    Request Body:
    {
        "video_id": "YouTube video ID"
    }
    """
    try:
        data = request.get_json()
        if not data or 'video_id' not in data:
            return jsonify(ErrorResponse(
                error="Bad Request", 
                message="video_id is required in request body",
                status_code=400
            ).dict()), 400
        
        video_id = data['video_id']
        
        # Extract video ID from URL if provided
        if 'youtube.com/watch?v=' in video_id:
            video_id = video_id.split('v=')[1].split('&')[0]
        elif 'youtu.be/' in video_id:
            video_id = video_id.split('youtu.be/')[1].split('?')[0]
        
        result = content_generator.generate_content_scripts(video_id)
        return jsonify(result.dict())
        
    except ValueError as e:
        return jsonify(ErrorResponse(
            error="Bad Request",
            message=str(e),
            status_code=400
        ).dict()), 400
    except Exception as e:
        return jsonify(ErrorResponse(
            error="Internal Server Error",
            message=str(e),
            status_code=500
        ).dict()), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)