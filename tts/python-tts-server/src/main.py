from flask import Flask, request, jsonify, send_file
import asyncio
from services.tts_service import TTSService

app = Flask(__name__)
tts_service = TTSService()

@app.route('/synthesize', methods=['POST'])
def synthesize():
    """Simple TTS endpoint"""
    data = request.json
    text = data.get('text', '')
    language = data.get('language', 'en-US')
    gender = data.get('gender', 'female')
    emotion = data.get('emotion', 'neutral')
    
    if not text:
        return jsonify({'error': 'Text required'}), 400
    
    try:
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        audio_file = loop.run_until_complete(
            tts_service.text_to_speech(text, language, gender, emotion)
        )
        loop.close()
        
        return send_file(audio_file, as_attachment=True, download_name='tts.mp3')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)