import unittest
from fastapi.testclient import TestClient
from src.api.routes import app

class TestAPIRoutes(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_text_to_speech(self):
        response = self.client.post("/tts", json={"text": "Hello, world!", "language": "en-US", "emotion": "neutral"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("audio_content", response.json())

    def test_invalid_language(self):
        response = self.client.post("/tts", json={"text": "Hello, world!", "language": "invalid-lang", "emotion": "neutral"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Invalid language specified.")

    def test_missing_text(self):
        response = self.client.post("/tts", json={"language": "en-US", "emotion": "neutral"})
        self.assertEqual(response.status_code, 422)

    def test_emotional_tone(self):
        response = self.client.post("/tts", json={"text": "I'm so happy!", "language": "en-US", "emotion": "happy"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("audio_content", response.json())

if __name__ == "__main__":
    unittest.main()