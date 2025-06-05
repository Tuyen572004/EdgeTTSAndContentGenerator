import unittest
from src.services.tts_service import TTSService

class TestTTSService(unittest.TestCase):

    def setUp(self):
        self.tts_service = TTSService()

    def test_text_to_speech(self):
        text = "Hello, world!"
        language = "en-US"
        tone = "neutral"
        result = self.tts_service.convert_text_to_speech(text, language, tone)
        self.assertIsNotNone(result)
        self.assertTrue(result['success'])
        self.assertIn('audio_content', result)

    def test_multi_language_support(self):
        text = "Bonjour le monde!"
        language = "fr-FR"
        tone = "neutral"
        result = self.tts_service.convert_text_to_speech(text, language, tone)
        self.assertIsNotNone(result)
        self.assertTrue(result['success'])
        self.assertIn('audio_content', result)

    def test_emotional_tones(self):
        text = "I'm so happy to see you!"
        language = "en-US"
        tone = "happy"
        result = self.tts_service.convert_text_to_speech(text, language, tone)
        self.assertIsNotNone(result)
        self.assertTrue(result['success'])
        self.assertIn('audio_content', result)

    def test_invalid_language(self):
        text = "This should fail."
        language = "invalid-lang"
        tone = "neutral"
        result = self.tts_service.convert_text_to_speech(text, language, tone)
        self.assertIsNotNone(result)
        self.assertFalse(result['success'])
        self.assertIn('error', result)

if __name__ == '__main__':
    unittest.main()