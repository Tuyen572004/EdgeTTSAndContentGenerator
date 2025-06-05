# YouTube Content API

A comprehensive API for YouTube content analysis and video content generation. This API provides three main endpoints for content creators to discover trending keywords, search popular videos, and generate content ideas based on existing videos.

## 🚀 Features

- 🔥 **Trending Keywords**: Get trending keywords for content creation across different categories
- 🎥 **Video Search**: Search top trending videos by keywords with detailed metadata
- 🚀 **Content Generation**: Generate complete content ideas and scripts based on reference videos
- 📊 **Analytics**: Competitive analysis and trending elements extraction
- 🎯 **Multi-format Output**: JSON responses with structured data for easy integration

## 📋 Prerequisites

- Python 3.8 or higher
- YouTube Data API v3 key
- Git (optional)

## 🛠️ Installation & Setup

### Method 1: Manual Setup

1. **Clone or Download the Repository**
   ```bash
   cd "d:\SEMESTER 6TH\THIET KE PHAN MEM\DemoGemini\youtube"
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   ```

3. **Activate Virtual Environment**
   
   **Windows:**
   ```bash
   venv\Scripts\activate
   ```
   
   **macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set Up Environment Variables**
   ```bash
   # Copy the example environment file
   copy .env.example .env
   
   # Edit .env file and add your YouTube API key
   notepad .env
   ```

6. **Get YouTube API Key**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable YouTube Data API v3
   - Create credentials (API Key)
   - Copy the API key to your `.env` file:
   ```
   YOUTUBE_API_KEY=your_actual_api_key_here
   ```

### Method 2: Quick Setup Script (Windows)

Create a `setup.bat` file:
```batch
@echo off
echo Setting up YouTube Content API...

python -m venv venv
call venv\Scripts\activate

pip install -r requirements.txt

copy .env.example .env
echo.
echo Setup complete!
echo Please edit .env file with your YouTube API key
echo Run 'run.bat' to start the server
pause
```

## 🏃‍♂️ Running the Application

### Development Mode

1. **Activate Virtual Environment** (if not already activated)
   ```bash
   # Windows
   venv\Scripts\activate

   
   # macOS/Linux  
   source venv/bin/activate
   ```

2. **Start the Server**
   ```bash
   python src/app.py
   ```

3. **Alternative: Using Flask Command**
   ```bash
   set FLASK_APP=src/app.py
   set FLASK_ENV=development
   flask run --host=0.0.0.0 --port=5000
   ```

4. **Quick Run Script** (Create `run.bat` for Windows)
   ```batch
   @echo off
   call venv\Scripts\activate
   python src/app.py
   pause
   ```

### Production Mode

```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 src.app:app
```

### Docker Method

1. **Build and Run with Docker**
   ```bash
   docker build -t youtube-content-api .
   docker run -p 5000:5000 --env-file .env youtube-content-api
   ```

2. **Using Docker Compose**
   ```bash
   docker-compose up -d
   ```

## 🧪 Testing the API

### Health Check
```bash
curl http://localhost:5000/api/v1/health
```

### Using PowerShell (Windows)
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/v1/health" -Method GET
```

### Expected Response
```json
{
  "status": "healthy",
  "service": "YouTube Content API",
  "version": "1.0.0"
}
```

## 📡 API Endpoints

### 1. Get Trending Keywords
```http
GET /api/v1/trending/keywords?limit=10&category=technology
```

**Example using curl:**
```bash
curl "http://localhost:5000/api/v1/trending/keywords?limit=5"
```

**Example using PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/v1/trending/keywords?limit=5" -Method GET
```

### 2. Search Trending Videos
```http
GET /api/v1/videos/search?keyword=programming&limit=5
```

**Example:**
```bash
curl "http://localhost:5000/api/v1/videos/search?keyword=python%20tutorial&limit=5"
```

### 3. Generate Content Ideas
```http
POST /api/v1/content/generate
Content-Type: application/json

{
  "video_id": "dQw4w9WgXcQ"
}
```

**Example using curl:**
```bash
curl -X POST "http://localhost:5000/api/v1/content/generate" \
     -H "Content-Type: application/json" \
     -d '{"video_id":"dQw4w9WgXcQ"}'
```

**Example using PowerShell:**
```powershell
$body = @{
    video_id = "dQw4w9WgXcQ"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/v1/content/generate" -Method POST -Body $body -ContentType "application/json"
```

## 🔧 Configuration

### Environment Variables (.env file)
```bash
# YouTube API Configuration
YOUTUBE_API_KEY=your_youtube_api_key_here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000

# Logging
LOG_LEVEL=INFO
```

### Available Categories for Trending Keywords
- `technology`
- `lifestyle` 
- `entertainment`
- `education`
- `health`

## 🐛 Troubleshooting

### Common Issues

1. **"YouTube API service not initialized"**
   - Check if `YOUTUBE_API_KEY` is set in `.env` file
   - Verify the API key is valid
   - Ensure YouTube Data API v3 is enabled

2. **"Module not found" errors**
   - Make sure virtual environment is activated
   - Install requirements: `pip install -r requirements.txt`

3. **Port already in use**
   - Change port in `.env` file: `PORT=5001`
   - Or kill the process using the port

4. **API quota exceeded**
   - YouTube API has daily limits
   - Wait for quota reset or use a different API key

### Debug Mode

Run with debug information:
```bash
set FLASK_DEBUG=True
set LOG_LEVEL=DEBUG
python src/app.py
```

## 📁 Project Structure

```
youtube-content-api/
├── src/
│   ├── api/
│   │   └── routes.py           # API endpoints
│   ├── services/
│   │   ├── youtube_service.py  # YouTube API integration
│   │   ├── trending_service.py # Trending keywords logic
│   │   └── content_generator_service.py # Content generation
│   ├── models/
│   │   └── api_models.py       # Pydantic models
│   └── app.py                  # Main application
├── requirements.txt            # Dependencies
├── .env.example               # Environment template
├── Dockerfile                 # Docker configuration
└── README.md                  # This file
```

## 🚀 Quick Start Commands

```bash
# Complete setup and run
git clone <repository-url>
cd youtube-content-api
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env
# Edit .env with your API key
python src/app.py
```

## 📖 API Documentation

Once the server is running, you can test the endpoints:

- **Health Check**: `GET http://localhost:5000/api/v1/health`
- **Trending Keywords**: `GET http://localhost:5000/api/v1/trending/keywords`
- **Search Videos**: `GET http://localhost:5000/api/v1/videos/search?keyword=YOUR_KEYWORD`
- **Generate Content**: `POST http://localhost:5000/api/v1/content/generate`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

If you encounter any issues:

1. Check the troubleshooting section above
2. Verify your YouTube API key is valid
3. Ensure all dependencies are installed
4. Check the console output for error messages

For additional help, please create an issue in the repository.