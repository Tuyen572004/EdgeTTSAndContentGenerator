def validate_text_input(text):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Input must be a non-empty string.")

def format_language_code(language):
    if len(language) != 2:
        raise ValueError("Language code must be 2 characters long.")
    return language.lower()

def validate_emotional_tone(tone):
    valid_tones = ['neutral', 'happy', 'sad', 'angry', 'excited']
    if tone not in valid_tones:
        raise ValueError(f"Invalid tone. Choose from: {', '.join(valid_tones)}")